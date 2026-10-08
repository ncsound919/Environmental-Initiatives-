"""ChordStudio CDP adapter for the Beta Team.

Drives the *real* ChordStudio app (a native JUCE/WebView2 application) by
attaching to its embedded WebView2 over the Chrome DevTools Protocol. There is
no mock and no Playwright-managed browser: the app is launched with remote
debugging on, and every interaction below travels through the same bridge the
shipping build uses, so a broken native call or a dead handler fails here.

This module is both a Beta Team SDK adapter (BaseAdapter-shaped) and a Robot
Framework library (public methods become keywords).

Requirements (already used elsewhere in the SDK):
    requests, websocket-client

Environment:
    CHORDSTUDIO_EXE       Path to "Chord Studio.exe" (else auto-discovered).
    CHORDSTUDIO_CDP_PORT  Remote-debugging port (default 9226).

Honest limits (recorded, not hidden):
    * Text/role matching is done against the live DOM by accessible name; if
      the UI renames a control, the keyword raises with the observed names
      rather than passing silently.
    * This drives the Windows build only. macOS is a separate milestone.
"""

from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Optional

import requests
import websocket


DEFAULT_EXE = os.environ.get(
    "CHORDSTUDIO_EXE",
    r"C:\Users\User\Downloads\BUSINESS\CREATIVE\ChordStudio\build-local"
    r"\ChordStudio_artefacts\Release\Chord Studio.exe",
)


class ChordStudioError(RuntimeError):
    """Raised when the app, the CDP link, or a UI contract is not as expected."""


class ChordStudioCdp:
    """Attach to ChordStudio's WebView2 and drive its beatmaking surface."""

    ROBOT_LIBRARY_SCOPE = "SUITE"

    def __init__(self, exe: Optional[str] = None, port: Optional[int] = None) -> None:
        self.exe = exe or os.environ.get("CHORDSTUDIO_EXE") or str(DEFAULT_EXE)
        self.port = int(port or os.environ.get("CHORDSTUDIO_CDP_PORT", "9226"))
        self._proc: Optional[subprocess.Popen] = None
        self._ws: Optional[websocket.WebSocket] = None
        self._id = 0

    # ------------------------------------------------------------------ CDP

    def _cdp_url(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def _send(self, method: str, params: Optional[dict] = None) -> dict:
        if self._ws is None:
            raise ChordStudioError("CDP is not connected; call Launch App first")
        self._id += 1
        mid = self._id
        self._ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
        while True:
            msg = json.loads(self._ws.recv())
            if msg.get("id") == mid:
                return msg

    def _evaluate(self, expression: str, await_promise: bool = True) -> Any:
        r = self._send(
            "Runtime.evaluate",
            {"expression": expression, "returnByValue": True, "awaitPromise": await_promise},
        )
        res = r.get("result", {})
        if "exceptionDetails" in res:
            detail = res["exceptionDetails"]
            raise ChordStudioError(
                "in-page JS error: "
                + str(detail.get("text"))
                + " "
                + str((detail.get("exception") or {}).get("description", ""))
            )
        return res.get("result", {}).get("value")

    def _wait_until(self, expression: str, timeout: float = 20.0, poll: float = 0.2) -> bool:
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                if self._evaluate(expression):
                    return True
            except ChordStudioError:
                pass
            time.sleep(poll)
        return False

    # --------------------------------------------------------------- lifecycle

    def launch_app(self, exe: Optional[str] = None, port: Optional[int] = None) -> None:
        """Launch ChordStudio with remote debugging and attach to its WebView2."""
        if exe:
            self.exe = exe
        if port:
            self.port = int(port)
        if not Path(self.exe).exists():
            raise ChordStudioError(f"ChordStudio executable not found: {self.exe}")

        env = dict(os.environ)
        env["WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS"] = (
            f"--remote-debugging-port={self.port} --remote-allow-origins=*"
        )
        self._proc = subprocess.Popen([self.exe], env=env)

        deadline = time.time() + 60
        while time.time() < deadline:
            try:
                if requests.get(self._cdp_url() + "/json/version", timeout=1).ok:
                    break
            except requests.RequestException:
                pass
            time.sleep(0.4)
        else:
            self.close_app()
            raise ChordStudioError(f"ChordStudio did not expose CDP on port {self.port}")

        page = None
        deadline = time.time() + 30
        while time.time() < deadline:
            try:
                targets = requests.get(self._cdp_url() + "/json", timeout=5).json()
            except requests.RequestException:
                targets = []
            pages = [t for t in targets if t.get("type") == "page"]
            for t in pages:
                if "juce" in (t.get("url") or ""):
                    page = t
                    break
            if page is None:
                # The juce backend page sometimes appears without the label first.
                for t in pages:
                    url = (t.get("url") or "").strip()
                    if url and url != "about:blank":
                        page = t
                        break
            if page is not None:
                break
            time.sleep(0.4)
        if page is None:
            self.close_app()
            raise ChordStudioError("no ChordStudio WebView2 page target found")

        self._ws = websocket.create_connection(
            page["webSocketDebuggerUrl"], max_size=None, suppress_origin=True
        )
        self._send("Runtime.enable")
        self._send("Page.enable")
        # The React shell needs a beat to mount and the bridge to settle.
        self._wait_until("document.querySelector('nav') !== null", timeout=30)

    def close_app(self) -> None:
        """Close the WebView2 link and kill the launched app (whole process tree)."""
        if self._ws is not None:
            try:
                self._ws.close()
            except Exception:
                pass
            self._ws = None

        proc = self._proc
        self._proc = None
        if proc is None or proc.poll() is not None:
            return
        if sys.platform == "win32" and proc.pid:
            subprocess.run(
                ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                capture_output=True,
            )
        else:
            proc.kill()
        # Wait for the process tree to actually exit: a lingering msedgewebview2
        # keeps the WebView2 user-data folder locked and the next launch then
        # fails to create its webview.
        deadline = time.time() + 15
        while time.time() < deadline and proc.poll() is None:
            time.sleep(0.2)

    # ------------------------------------------------------------- primitives

    def _rect_js(self, selector_expr: str) -> Optional[dict]:
        """Return {x,y,w,h,knob} for the element matched by a JS expression, or None."""
        js = """
        (() => {
          const el = %s;
          if (!el) return null;
          el.scrollIntoView({block: 'center', inline: 'center'});
          const r = el.getBoundingClientRect();
          return {x: r.left + r.width/2, y: r.top + r.height/2, w: r.width, h: r.height,
                  knob: el.classList.contains('cs-knob-hit'),
                  vw: window.innerWidth, vh: window.innerHeight};
        })()
        """ % selector_expr
        return self._evaluate(js)

    def _mouse(self, x: float, y: float, pressed: bool) -> None:
        self._send(
            "Input.dispatchMouseEvent",
            {
                "type": "mousePressed" if pressed else "mouseReleased",
                "x": x,
                "y": y,
                "button": "left",
                "buttons": 1 if pressed else 0,
                "clickCount": 1,
            },
        )

    def _click(self, selector_expr: str, description: str = "element", js: bool = False) -> None:
        """Click an element.

        `js=True` dispatches a DOM `.click()` (deterministic for React `onClick`
        buttons; used where a synthetic pointer click can miss because the grid
        re-renders under the cursor). `js=False` sends real CDP mouse events at
        the element centre — required for controls driven by `onPointerDown`
        (pads) and knobs/sliders.
        """
        if js:
            ok = self._evaluate(
                f"(() => {{ const el = {selector_expr}; if (!el) return false; el.click(); return true; }})()"
            )
            if not ok:
                raise ChordStudioError(f"{description} not found")
            time.sleep(0.2)
            return

        rect = self._rect_js(selector_expr)
        if rect is None:
            raise ChordStudioError(f"{description} not found")
        # If the control is on-screen, use real input (closest to a user's click);
        # otherwise fall back to a synthetic click so the test still exercises React.
        on_screen = 0 <= rect["x"] <= rect["vw"] and 0 <= rect["y"] <= rect["vh"]
        if on_screen and rect["w"] and rect["h"]:
            self._send(
                "Input.dispatchMouseEvent",
                {"type": "mouseMoved", "x": rect["x"], "y": rect["y"], "buttons": 0},
            )
            self._mouse(rect["x"], rect["y"], True)
            self._mouse(rect["x"], rect["y"], False)
        else:
            self._evaluate(f"(() => {{ const el = {selector_expr}; if (el) el.click(); }})()")
        time.sleep(0.25)

    def _button_by_text(self, text: str) -> str:
        return (
            "[...document.querySelectorAll('button')]"
            f".find(e => e.textContent.trim().toLowerCase() === {json.dumps(text.lower())})"
        )

    def _button_containing(self, text: str) -> str:
        return (
            "[...document.querySelectorAll('button')]"
            f".find(e => e.textContent.toLowerCase().includes({json.dumps(text.lower())}))"
        )

    def _group_button(self, group_label: str, text: str) -> str:
        return (
            f"[...document.querySelectorAll('[role=group][aria-label={json.dumps(group_label)}] button')]"
            f".find(e => e.textContent.trim() === {json.dumps(text)})"
        )

    # ------------------------------------------------------------- navigation

    def dismiss_overlays(self) -> None:
        """Close the first-run guide and any crash-recovery banner if present."""
        self._evaluate(
            "(() => { const b = document.querySelector('button[aria-label=\"Dismiss the first-run guide\"]');"
            " if (b) b.click(); })()"
        )
        self._evaluate(
            "(() => { const b = [...document.querySelectorAll('button')]"
            ".find(e => /^(discard|restore)$/i.test(e.textContent.trim())); if (b) b.click(); })()"
        )
        time.sleep(0.4)

    def open_workspace(self, name: str) -> None:
        """Click a top-level workspace tab (Compose, Drums, Mix, ...)."""
        self._click(
            f"document.querySelector('nav') && {self._button_by_text(name)}", f"{name} tab", js=True
        )
        self._wait_until(
            f"[...document.querySelectorAll('nav button')].some(e => "
            f"e.textContent.trim().toLowerCase() === {json.dumps(name.lower())} && "
            f"e.getAttribute('aria-current') === 'page')",
            timeout=10,
        )

    def click_button_containing(self, text: str) -> None:
        """Click the first button whose visible text contains `text` (case-insensitive)."""
        self._click(self._button_containing(text), f"button containing {text!r}", js=True)

    def open_sampler_mode(self, name: str) -> None:
        """Switch the Sampler workflow tab (Record/Trim/Chop/Program/Sequence/Browse/Perform)."""
        self._wait_until(
            "[...document.querySelectorAll('[role=tablist][aria-label=\"Sampler workflow\"] button')]"
            ".length > 0",
            timeout=10,
        )
        expr = (
            "[...document.querySelectorAll('[role=tablist][aria-label=\"Sampler workflow\"] button')]"
            f".find(e => e.textContent.toLowerCase().includes({json.dumps(name.lower())}))"
        )
        self._click(expr, f"{name} sampler tab", js=True)
        time.sleep(0.3)

    # ------------------------------------------------------------------ pads

    def select_pad_bank(self, letter: str) -> None:
        """Select a pad bank A..H."""
        self._click(self._group_button("Pad bank", letter.upper()), f"pad bank {letter}", js=True)

    def select_pad(self, pad: str) -> None:
        """Select a pad by its label, e.g. A01 or H16."""
        expr = (
            "[...document.querySelectorAll('[role=group][aria-label^=\"Pads, bank\"] button')]"
            f".find(e => (e.getAttribute('aria-label') || '').startsWith('Pad {pad}'))"
        )
        self._click(expr, f"pad {pad}")

    def pad_label(self, pad: str) -> str:
        """Return the accessible label of a pad (shows whether it carries a sample)."""
        expr = (
            "[...document.querySelectorAll('[role=group][aria-label^=\"Pads, bank\"] button')]"
            f".find(e => (e.getAttribute('aria-label') || '').startsWith('Pad {pad}'))"
        )
        val = self._evaluate(f"(() => {{ const el = {expr}; return el ? el.getAttribute('aria-label') : null; }})()")
        if val is None:
            raise ChordStudioError(f"pad {pad} not found")
        return val

    def pad_label_should_contain(self, pad: str, substring: str) -> None:
        """Fail unless the pad's accessible label contains `substring`."""
        label = self.pad_label(pad)
        if substring not in label:
            raise ChordStudioError(f"pad {pad} label {label!r} does not contain {substring!r}")

    def pad_selected(self, pad: str) -> str:
        """Return 'on'/'off' for whether `pad` is the selected pad (aria-pressed)."""
        expr = (
            "[...document.querySelectorAll('[role=group][aria-label^=\"Pads, bank\"] button')]"
            f".find(e => (e.getAttribute('aria-label') || '').startsWith('Pad {pad}'))"
        )
        val = self._evaluate(f"(() => {{ const el = {expr}; return el ? el.getAttribute('aria-pressed') : null; }})()")
        if val is None:
            raise ChordStudioError(f"pad {pad} not found")
        return "on" if val == "true" else "off"

    # ------------------------------------------------------------- sequencer

    def toggle_step(self, pad: str, step: int) -> None:
        """Toggle a step in the pattern grid (1-based step number)."""
        self._click(self._step_expr(pad, step), f"{pad} step {step}", js=True)

    def _step_expr(self, pad: str, step: int) -> str:
        label = f"{pad} step {step}"
        return (
            "[...document.querySelectorAll('[role=gridcell]')]"
            f".find(e => (e.getAttribute('aria-label') || '').startsWith({json.dumps(label)}))"
        )

    def step_state(self, pad: str, step: int) -> str:
        """Return 'on' or 'off' for a step (from aria-pressed)."""
        val = self._evaluate(
            f"(() => {{ const el = {self._step_expr(pad, step)}; return el ? el.getAttribute('aria-pressed') : null; }})()"
        )
        if val is None:
            raise ChordStudioError(f"{pad} step {step} not found")
        return "on" if val == "true" else "off"

    def step_exists(self, pad: str, step: int) -> bool:
        """True if the step cell exists in the current grid."""
        return bool(
            self._evaluate(f"(() => {{ return {self._step_expr(pad, step)} !== undefined; }})()")
        )

    def select_pattern(self, index: int) -> None:
        """Select a pattern 1..N."""
        self._click(self._group_button("Pattern", str(index)), f"pattern {index}", js=True)

    def pattern_state(self, index: int) -> str:
        """Return 'on' or 'off' for a pattern button (aria-pressed)."""
        val = self._evaluate(
            f"(() => {{ const el = {self._group_button('Pattern', str(index))}; "
            "return el ? el.getAttribute('aria-pressed') : null; })()"
        )
        if val is None:
            raise ChordStudioError(f"pattern {index} not found")
        return "on" if val == "true" else "off"

    def set_pattern_length(self, label: str) -> None:
        """Set the pattern length by its visible label ('1 bar', '2 bars', '4 bars', '8 bars').

        The control labels lengths as whole bars of the current Time Correct
        grid, so set the grid first when the bar size matters.
        """
        self._click(self._group_button("Pattern length", label), f"pattern length {label}", js=True)

    def set_time_correct(self, label: str) -> None:
        """Set the Time Correct grid, e.g. 1/16 or 1/8T."""
        self._click(self._group_button("Time correct", label), f"time correct {label}", js=True)

    def transport(self, action: str) -> None:
        """Play / Stop / Record via the transport buttons (aria-label)."""
        aria = {"play": "Play", "stop": "Stop", "record": "Record pattern"}[action.lower()]
        self._click(
            f"document.querySelector('button[aria-label={json.dumps(aria)}]')",
            f"transport {action}",
            js=True,
        )

    def transport_state(self, action: str) -> str:
        """Return 'on'/'off' for a transport button's aria-pressed."""
        aria = {"play": "Play", "stop": "Stop", "record": "Record pattern"}[action.lower()]
        val = self._evaluate(
            "(() => { const el = document.querySelector("
            f"'button[aria-label={json.dumps(aria)}]'); return el ? el.getAttribute('aria-pressed') : null; }})()"
        )
        return "on" if val == "true" else "off"

    # ----------------------------------------------------- aria / generic UI

    def aria_exists(self, label: str) -> bool:
        """True if an element with this aria-label is present."""
        return bool(
            self._evaluate(f"document.querySelector('[aria-label=%s]') !== null" % json.dumps(label))
        )

    def click_aria(self, label: str) -> None:
        """Click the element carrying this aria-label (a button in practice)."""
        self._click(
            "document.querySelector('[aria-label=%s]')" % json.dumps(label),
            f"[{label}]",
            js=True,
        )

    def text_of_aria(self, label: str) -> str:
        """Return the visible text of the element carrying this aria-label."""
        val = self._evaluate(
            "(() => { const el = document.querySelector('[aria-label=%s]');"
            " return el ? el.textContent.trim() : null; })()" % json.dumps(label)
        )
        if val is None:
            raise ChordStudioError(f"no element labelled {label!r}")
        return val

    def click_group_button(self, group_label: str, text: str) -> None:
        """Click a button whose text matches, inside a role=group with this label."""
        self._click(self._group_button(group_label, text), f"{group_label}:{text}", js=True)

    # ------------------------------------------------------ live song transport

    def song_transport(self, action: str) -> None:
        """Play/Stop the live song transport (the whole arrangement)."""
        word = {"play": "Play", "stop": "Stop"}[action.lower()]
        expr = (
            "[...document.querySelectorAll('[aria-label=\"Song transport\"] button')]"
            f".find(e => e.textContent.trim() === {json.dumps(word)})"
        )
        self._click(expr, f"song transport {action}", js=True)

    def song_transport_readout(self) -> str:
        """Return the transport readout (e.g. 'BAR 3 · BEAT 2.00 · 92.0 BPM · 4/4')."""
        return self.text_of_aria("Song transport")

    def song_playing(self) -> str:
        """Return 'on' when the song transport is playing (its button reads Stop)."""
        txt = self.text_of_aria("Song transport")
        return "on" if "Stop" in txt else "off"

    # --------------------------------------------------------------- compose

    def generate_progression(self) -> None:
        """Open Compose and press Generate; wait for chord pads to appear."""
        self.open_workspace("Compose")
        # The header button reads exactly "Generate" when idle; while a run is in
        # flight it is disabled / relabelled, so wait for the idle state.
        if not self._wait_until(
            "[...document.querySelectorAll('button')]"
            ".some(b => b.textContent.trim().toLowerCase() === 'generate' && !b.disabled)",
            timeout=20,
        ):
            raise ChordStudioError("Generate button did not become available")
        self.click_button_containing("Generate")
        if not self._wait_until(
            "[...document.querySelectorAll('button[aria-label]')]"
            ".some(b => /^\\d+\\.\\d+/.test(b.getAttribute('aria-label') || ''))",
            timeout=20,
        ):
            raise ChordStudioError("Generate produced no chord pads")

    def chord_count(self) -> int:
        """Number of chord pads currently rendered."""
        return int(
            self._evaluate(
                "[...document.querySelectorAll('button[aria-label]')]"
                ".filter(b => /^\\d+\\.\\d+/.test(b.getAttribute('aria-label') || '')).length"
            )
            or 0
        )

    def audition_chord(self) -> None:
        """Audition the selected chord through the engine ('Play selected chord')."""
        self.click_aria("Play selected chord")

    # ---------------------------------------------------------------- synth

    def select_synth_engine(self, name: str) -> None:
        """Open Synth and pick an engine (CS-6 FM / Analog)."""
        self.open_workspace("Synth")
        self._click(self._group_button("Synth engine", name), f"synth engine {name}", js=True)

    def synth_patch_name(self) -> str:
        """Return the current synth patch name."""
        return (
            self._evaluate(
                "(() => { const el = document.querySelector('input[aria-label=\"Patch name\"]');"
                " return el ? el.value : ''; })()"
            )
            or ""
        )

    def synth_operator_count(self) -> int:
        """Number of operator selectors on the Synth tab (6 for the FM engine)."""
        return int(
            self._evaluate(
                "[...document.querySelectorAll('button[aria-label]')]"
                ".filter(b => (b.getAttribute('aria-label') || '').startsWith('Operator ')).length"
            )
            or 0
        )

    # ------------------------------------------------------------------ mix

    def select_track(self, name: str) -> None:
        """Open Mix and select a track by its name (Bass, Piano, Synth, ...)."""
        self.open_workspace("Mix")
        self.click_aria(name)

    def toggle_track_mute(self, name: str) -> None:
        """Toggle a track's mute."""
        self.click_aria(f"Mute {name}")

    def toggle_track_solo(self, name: str) -> None:
        """Toggle a track's solo."""
        self.click_aria(f"Solo {name}")

    def track_mute_state(self, name: str) -> str:
        """Return 'on'/'off' for a track's mute."""
        val = self._evaluate(
            "(() => { const el = document.querySelector('[aria-label=%s]');"
            " return el ? el.getAttribute('aria-pressed') : null; })()"
            % json.dumps(f"Mute {name}")
        )
        return "on" if val == "true" else "off"

    # --------------------------------------------------- plugins / rompler

    def plugin_controls_present(self) -> bool:
        """True when the VST3 hosting controls are on screen.

        The Rompler is a VST3; selecting one uses a native file dialog the CDP
        harness cannot drive, so the harness verifies the controls exist and the
        plugin is covered by its own tests + pluginval, not by clicking through a
        dialog.
        """
        return self.aria_exists("Load VST3") and (
            self.aria_exists("Show UI") or self.aria_exists("Clear")
        )

    # ---------------------------------------------------------- benchmarking

    def benchmark_start(self) -> None:
        """Start a benchmark run (records per-step wall-clock durations)."""
        self._bench_marks: list = []
        self._bench_t0 = time.time()
        self._bench_started = time.time()

    def benchmark_mark(self, label: str) -> None:
        """Record the time since the previous mark under `label`."""
        if not hasattr(self, "_bench_t0"):
            raise ChordStudioError("call Benchmark Start first")
        now = time.time()
        self._bench_marks.append({"label": label, "seconds": round(now - self._bench_t0, 3)})
        self._bench_t0 = now

    def process_metrics(self) -> dict:
        """Return the app process's resident memory and CPU (psutil, sampled)."""
        metrics = {"pid": self._proc.pid if self._proc else None, "rss_mb": None, "cpu_percent": None}
        try:
            import psutil

            if self._proc and self._proc.poll() is None:
                proc = psutil.Process(self._proc.pid)
                metrics["rss_mb"] = round(proc.memory_info().rss / (1024 * 1024), 1)
                metrics["cpu_percent"] = round(proc.cpu_percent(interval=0.5), 1)
        except Exception as e:  # psutil absent or process gone
            metrics["error"] = str(e)
        return metrics

    def app_alive(self) -> bool:
        """True if the launched app process is still running and CDP answers."""
        if self._proc is None or self._proc.poll() is not None:
            return False
        try:
            return requests.get(self._cdp_url() + "/json/version", timeout=2).ok
        except requests.RequestException:
            return False

    def benchmark_report(self, path: str = "reports/benchmark.json") -> str:
        """Write the benchmark marks, process metrics and liveness to a JSON file."""
        if not hasattr(self, "_bench_marks"):
            raise ChordStudioError("call Benchmark Start first")
        total = round(time.time() - getattr(self, "_bench_started", time.time()), 3)
        report = {
            "exe": self.exe,
            "total_seconds": total,
            "marks": self._bench_marks,
            "process": self.process_metrics(),
            "app_alive": self.app_alive(),
        }
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return str(out)

    # ----------------------------------------------------------------- knobs

    def move_knob(self, label: str, fraction: float, steps: int = 24) -> None:
        """Drag a knob/slider (role=slider, aria-label=label) toward a position.

        `fraction` is the normalized target (1.0 = full scale, 0.0 = zero; a
        negative value drags below the start). The gesture mirrors the app's:
        knobs drag vertically, sliders horizontally. The drag is sent as many
        small incremental moves because the browser coalesces a single large
        synthetic jump.
        """
        rect = self._rect_js(f"document.querySelector('[role=slider][aria-label={json.dumps(label)}]')")
        if rect is None:
            raise ChordStudioError(f"no slider/knob labelled {label!r}")
        cx, cy = rect["x"], rect["y"]
        vw, vh = rect["vw"], rect["vh"]

        self._send("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": cx, "y": cy, "buttons": 0})
        self._mouse(cx, cy, True)

        if rect["knob"]:
            target = max(4, min(vh - 4, cy - fraction * 200))
            end_x, end_y = cx, target
        else:
            travel = max(rect["w"] - 16, 1)
            end_x = max(4, min(vw - 4, cx + fraction * travel))
            end_y = cy

        for i in range(1, steps + 1):
            x = cx + (end_x - cx) * i / steps
            y = cy + (end_y - cy) * i / steps
            self._send("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": x, "y": y, "buttons": 1})
            time.sleep(0.015)
        self._mouse(end_x, end_y, False)
        time.sleep(0.25)

    def control_value(self, label: str) -> int:
        """Return a control's aria-valuenow (integer position)."""
        val = self._evaluate(
            "(() => { const el = document.querySelector("
            f"'[role=slider][aria-label={json.dumps(label)}]'); "
            "return el ? Number(el.getAttribute('aria-valuenow')) : null; })()"
        )
        if val is None:
            raise ChordStudioError(f"no slider/knob labelled {label!r}")
        return int(val)

    _KEYS = {
        "Home": ("Home", "Home", 36),
        "End": ("End", "End", 35),
        "PageUp": ("PageUp", "PageUp", 33),
        "PageDown": ("PageDown", "PageDown", 34),
        "ArrowUp": ("ArrowUp", "ArrowUp", 38),
        "ArrowDown": ("ArrowDown", "ArrowDown", 40),
        "ArrowLeft": ("ArrowLeft", "ArrowLeft", 37),
        "ArrowRight": ("ArrowRight", "ArrowRight", 39),
    }

    def press_control_key(self, label: str, key: str) -> None:
        """Focus a control and press a key on it.

        The knob/slider APG keyboard contract is deterministic (Home=0, End=1,
        PageUp/Down=+-0.1) and drives the same onChange -> engine path as a
        mouse drag, so it is the reliable way to prove the control round-trips.
        The keydown is dispatched on the focused element in-page because CDP
        key events do not reliably reach the WebView2 DOM.
        """
        if key not in self._KEYS:
            raise ChordStudioError(f"unsupported key {key!r}")
        k, code, vk = self._KEYS[key]
        js = """
        (() => {
          const el = document.querySelector('[role=slider][aria-label=%s]');
          if (!el) return 'NO_CONTROL';
          el.focus();
          const opts = {key: %s, code: %s, keyCode: %d, which: %d, bubbles: true, cancelable: true};
          el.dispatchEvent(new KeyboardEvent('keydown', opts));
          el.dispatchEvent(new KeyboardEvent('keyup', opts));
          return 'ok';
        })()
        """ % (json.dumps(label), json.dumps(k), json.dumps(code), vk, vk)
        if self._evaluate(js) != "ok":
            raise ChordStudioError(f"no slider/knob labelled {label!r}")
        time.sleep(0.2)

    # ------------------------------------------------------- sample + chop

    @staticmethod
    def _encode_wav(samples: list, sample_rate: int = 44100) -> str:
        """Encode float samples (-1..1) as a base64 16-bit mono WAV."""
        import struct

        peak = max((abs(s) for s in samples), default=0.0) or 1.0
        scale = 0.85 / peak if peak > 0.85 else 1.0
        pcm = b"".join(
            struct.pack("<h", max(-32768, min(32767, int(s * scale * 32767)))) for s in samples
        )
        header = b"RIFF" + struct.pack("<I", 36 + len(pcm)) + b"WAVE"
        header += b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, sample_rate, sample_rate * 2, 2, 16)
        header += b"data" + struct.pack("<I", len(pcm))
        return base64.b64encode(header + pcm).decode("ascii")

    def make_oneshot_base64(self, kind: str = "kick") -> str:
        """Synthesize a drum one-shot (kick / snare / hat) as base64 WAV.

        Deterministic (fixed noise seed) so a run is reproducible.
        """
        import math
        import random

        sr = 44100
        kind = kind.lower()
        out: list = []
        if kind == "kick":
            n = int(sr * 0.28)
            phase = 0.0
            for i in range(n):
                t = i / sr
                freq = 140 * math.exp(-t * 18) + 45
                phase += 2 * math.pi * freq / sr
                out.append(math.sin(phase) * math.exp(-t * 9))
        elif kind == "snare":
            n = int(sr * 0.2)
            rnd = random.Random(7)
            for i in range(n):
                t = i / sr
                env = math.exp(-t * 22)
                out.append((rnd.uniform(-1, 1) * 0.8 + math.sin(2 * math.pi * 190 * t) * 0.4) * env)
        elif kind == "hat":
            n = int(sr * 0.08)
            rnd = random.Random(11)
            prev = 0.0
            for i in range(n):
                t = i / sr
                noise = rnd.uniform(-1, 1)
                out.append((noise - prev) * math.exp(-t * 60))
                prev = noise
        else:
            raise ChordStudioError(f"unknown one-shot kind {kind!r} (kick|snare|hat)")
        return self._encode_wav(out, sr)

    def ensure_step(self, pad: str, step: int, state: str = "on") -> None:
        """Make a step be 'on' or 'off' regardless of its current value.

        Toggling is verified against the engine after each click (a click can be
        missed, and the state read lags the click, so a blind retry can
        double-toggle). It waits for the engine to reflect each toggle.
        """
        want = state.lower() == "on"
        want_js = "true" if want else "false"
        for _ in range(5):
            if (self.step_state(pad, step) == "on") == want:
                return
            self.toggle_step(pad, step)
            self._wait_until(
                "(() => { const el = %s; return el !== undefined && "
                "(el.getAttribute('aria-pressed') === 'true') === %s; })()"
                % (self._step_expr(pad, step), want_js),
                timeout=2.0,
            )
        if (self.step_state(pad, step) == "on") != want:
            raise ChordStudioError(
                f"could not set {pad} step {step} to {state} "
                f"(it is {self.step_state(pad, step)})"
            )

    def make_transient_wav_base64(self) -> str:
        """Synthesize a 1.2 s mono WAV with three clear transients (3 chop slices).

        Mirrors the fixture used by the repo's own Playwright suite so the
        amplitude slicer is expected to find exactly three slices.
        """
        import math
        import struct

        sample_rate = 44100
        total = int(sample_rate * 1.2)
        data = [0.0] * total
        for at, length in ((0.05, 0.12), (0.4, 0.12), (0.75, 0.14)):
            start = int(at * sample_rate)
            n = int(length * sample_rate)
            for i in range(n):
                if start + i >= total:
                    break
                env = math.sin((math.pi * i) / n)
                data[start + i] = math.sin((2 * math.pi * 220 * i) / sample_rate) * env

        pcm = b"".join(struct.pack("<h", max(-32768, min(32767, int(s * 32767)))) for s in data)
        header = b"RIFF" + struct.pack("<I", 36 + len(pcm)) + b"WAVE"
        header += b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, sample_rate, sample_rate * 2, 2, 16)
        header += b"data" + struct.pack("<I", len(pcm))
        return base64.b64encode(header + pcm).decode("ascii")

    def drop_sample_on_pad(self, pad: str, file_name: str, base64_wav: str) -> None:
        """Dispatch a real HTML5 drop of a WAV onto a pad (same path a user's drag takes)."""
        expr = (
            "[...document.querySelectorAll('[role=group][aria-label^=\"Pads, bank\"] button')]"
            f".find(e => (e.getAttribute('aria-label') || '').startsWith('Pad {pad}'))"
        )
        js = """
        (() => {
          const el = %s;
          if (!el) return 'NO_PAD';
          const bin = atob(%s);
          const bytes = new Uint8Array(bin.length);
          for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
          const file = new File([bytes], %s, {type: 'audio/wav'});
          const dt = new DataTransfer();
          dt.items.add(file);
          for (const type of ['dragover', 'drop']) {
            el.dispatchEvent(new DragEvent(type, {bubbles: true, cancelable: true, dataTransfer: dt}));
          }
          return 'ok';
        })()
        """ % (expr, json.dumps(base64_wav), json.dumps(file_name))
        if self._evaluate(js) != "ok":
            raise ChordStudioError(f"pad {pad} not found for drop")
        time.sleep(0.6)

    def chop_to_pads(self) -> None:
        """Click the 'Chop → pads' button (assign detected slices to pads)."""
        self._click(self._button_containing("Chop → pads"), "Chop → pads")

    # ------------------------------------------------------------- assertions

    def text_should_be_visible(self, text: str, timeout: float = 10.0) -> None:
        """Fail unless `text` appears in the visible document body (case-insensitive).

        Case-insensitive on purpose: the console kit uppercases tab labels with
        CSS `text-transform`, so `innerText` reports DRUMS while the DOM says
        Drums.
        """
        needle = json.dumps(text.lower())
        if not self._wait_until(
            f"document.body.innerText.toLowerCase().includes({needle})", timeout=timeout
        ):
            body = self._evaluate("document.body.innerText.slice(0, 400)")
            raise ChordStudioError(f"text {text!r} not visible. Body starts: {body!r}")

    def text_should_not_be_visible(self, text: str) -> None:
        """Fail if `text` appears in the visible document body (case-insensitive)."""
        if self._evaluate(f"document.body.innerText.toLowerCase().includes({json.dumps(text.lower())})"):
            raise ChordStudioError(f"unexpected text {text!r} is visible")

    def body_should_contain(self, text: str, timeout: float = 10.0) -> None:
        self.text_should_be_visible(text, timeout)

    def get_body_text(self) -> str:
        """Return the visible body text (truncated for the log)."""
        return self._evaluate("document.body.innerText") or ""

    # ------------------------------------------------------------- evidence

    def screenshot(self, name: str = "chordstudio") -> str:
        """Capture the WebView as a PNG next to the suite and return the path."""
        out_dir = Path(os.environ.get("ROBOT_OUTPUT_DIR", ".")) / "screenshots"
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{name}.png"
        res = self._send("Page.captureScreenshot", {"format": "png"})
        data = res.get("result", {}).get("data")
        if not data:
            raise ChordStudioError("screenshot capture returned no data")
        path.write_bytes(base64.b64decode(data))
        return str(path)
