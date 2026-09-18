#!/usr/bin/env python3
"""
AutoCoder (LLM-free release)
- Lightweight runtime: reads YAML tasks and renders Jinja2 templates into /out
- No LLM dependencies included
"""

from pathlib import Path
import argparse, time, json, subprocess, shutil
from typing import Dict, Any
import yaml
from jinja2 import Environment, FileSystemLoader, Undefined

ROOT = Path(__file__).resolve().parent
TPL_DIR = ROOT / "templates"
TASK_DIR = ROOT / "tasks"
OUT_DIR = ROOT / "out"
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# Base context applied to all templates; ensures common vars like app_name exist
BASE_CONTEXT = {
    "app_name": "BeatGame",
    "rigs": [{"name": "MPC"}, {"name": "Keyboard Workstation"}, {"name": "Hybrid"}],
    "parameter_count": 20,
    "parameters": [
        {"name": "Family"},
        {"name": "Mode"},
        {"name": "Key"},
        {"name": "Tempo"},
        {"name": "Bars"},
        {"name": "Structure Template"},
        {"name": "GrooveId"},
        {"name": "Swing"},
        {"name": "Pocket"},
        {"name": "Humanize"},
        {"name": "Density"},
        {"name": "Reharms"},
        {"name": "Signature Strength"},
        {"name": "Velocity Curve"},
        {"name": "Accent Bias"},
        {"name": "Note Length Bias"},
        {"name": "Quantize Strength"},
        {"name": "Section Variation %"},
        {"name": "Variant Toggle"},
        {"name": "Seed"},
    ],
    "view_modes": ["top-down", "angled"],
    "zoom_levels": [25, 50, 75, 100, 150, 200],
    "export_formats": ["MIDI SMF", "arrangement.json", "DAW Profiles"],
    "daw_profiles": ["FL Studio", "Ableton Live", "Logic Pro", "BandLab"],
    "seed_range": [0, 999999],
    "ppq": 960,
    "tempo_range": [60, 200],
    "content_root": "Overlay_Audio_Center_MIDI_Arranger/Content",
    "algorithm": "random.Random",
    "max_parameters": 20,
    "knob_styles": ["circular", "linear"],
    "slider_styles": ["vertical", "horizontal"],
    "deferred": True,
    "test_cases": ["parameter_validation", "midi_generation", "export_formats"],
    "max_bars": 8,
    "midi_channels": 16,
    "note_range": "C2-C8",
    "window_title": "BeatGame - MIDI-First Beat Maker",
    "default_width": 1200,
    "default_height": 800,
    "midi_ppq": 960,
}


def load_yaml(p: Path) -> Dict[str, Any]:
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def render_file(env: Environment, tpl_name: str, context: Dict[str, Any]) -> str:
    tpl = env.get_template(tpl_name)
    return tpl.render(**context)


def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(text)


def run(cmd: list[str]) -> int:
    try:
        return subprocess.run(cmd, check=False).returncode
    except FileNotFoundError:
        return 127


def build_apk_wrapper(out_dir: str, use_docker: bool = True) -> int:
    """
    Attempt to build an APK using generated build scripts or Docker.
    Behavior:
      - If `build_and_cache.sh` exists in `out_dir`, run it.
      - Else if Docker is available and use_docker=True, run the official Buildozer container
        mounting `out_dir` as the project directory and invoke `buildozer android debug`.
      - Else attempt a native `buildozer android debug` (only works on Linux with buildozer installed).
    Returns the subprocess exit code (0 indicates success).
    """
    out_path = Path(out_dir)
    script = out_path / "build_and_cache.sh"
    if script.exists():
        return run(["bash", str(script)])

    # If user requested Docker and docker is available, use the Buildozer docker image
    if use_docker and shutil.which("docker"):
        cmd = [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{str(out_path)}:/home/user/project",
            "-w",
            "/home/user/project",
            "kivy/buildozer:latest",
            "/bin/bash",
            "-c",
            "buildozer android debug",
        ]
        return run(cmd)

    # Fallback: attempt native buildozer (must be running on Linux with buildozer installed)
    return run(["buildozer", "android", "debug"])


def handle_task(
    task_path: Path, format_code: bool = True, run_tests: bool = False
) -> dict:
    env = Environment(
        loader=FileSystemLoader(TPL_DIR),
        undefined=Undefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    spec = load_yaml(task_path)
    task_id = spec.get("task_id", task_path.stem)
    files = spec.get("files", [])
    results = {"task_id": task_id, "generated": [], "errors": []}

    for f in files:
        tpl = f["template"]
        out_rel = f["output"]
        # Merge base context with per-file context; per-file keys override BASE_CONTEXT.
        file_ctx = f.get("context", {}) or {}
        ctx = dict(BASE_CONTEXT)
        ctx.update(file_ctx)
        try:
            rendered = render_file(env, tpl, ctx)
            out_path = OUT_DIR / out_rel
            write_text(out_path, rendered)
            results["generated"].append(str(out_rel))

            # Write an intermediate progress report for this task so external monitors can read live progress.
            try:
                total_files = len(files) if files else 1
                progress_pct = (len(results["generated"]) / total_files) * 100.0
                report = {
                    "task_id": task_id,
                    "generated": results["generated"],
                    "errors": results["errors"],
                    "percent": progress_pct,
                    "current": out_rel,
                }
                REPORTS_DIR.mkdir(parents=True, exist_ok=True)
                with (REPORTS_DIR / f"{task_id}.json").open(
                    "w", encoding="utf-8"
                ) as rf:
                    json.dump(report, rf, indent=2)
            except Exception:
                # Non-fatal: continue generation even if writing report fails
                pass

        except Exception as e:
            results["errors"].append({"file": out_rel, "error": str(e)})
            # Also write a report reflecting the error so monitor sees it immediately.
            try:
                total_files = len(files) if files else 1
                progress_pct = (len(results["generated"]) / total_files) * 100.0
                report = {
                    "task_id": task_id,
                    "generated": results["generated"],
                    "errors": results["errors"],
                    "percent": progress_pct,
                    "current": out_rel,
                }
                REPORTS_DIR.mkdir(parents=True, exist_ok=True)
                with (REPORTS_DIR / f"{task_id}.json").open(
                    "w", encoding="utf-8"
                ) as rf:
                    json.dump(report, rf, indent=2)
            except Exception:
                pass

    # format with black if available
    if format_code:
        run(["python", "-m", "black", str(OUT_DIR)])

    # optional pytest run
    if run_tests:
        run(["python", "-m", "pytest", str(OUT_DIR)])

    # write a report
    report_path = REPORTS_DIR / f"{task_id}.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    return results


def scan_once(format_code: bool, run_tests: bool):
    for p in TASK_DIR.glob("*.yaml"):
        done_flag = p.with_suffix(".done")
        if done_flag.exists():
            continue
        res = handle_task(p, format_code, run_tests)
        done_flag.write_text("ok")
        print(
            f"[AutoCoder] Task {p.name} -> {len(res['generated'])} files, {len(res['errors'])} errors."
        )


def watch_loop(interval: float, format_code: bool, run_tests: bool):
    print(f"[AutoCoder] Watching {TASK_DIR} every {interval}s. Ctrl+C to stop.")
    while True:
        scan_once(format_code, run_tests)
        time.sleep(interval)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        type=str,
        default=None,
        help="Output directory for generated files",
    )
    ap.add_argument(
        "--once", action="store_true", help="Process pending tasks once and exit"
    )
    ap.add_argument(
        "--interval", type=float, default=3.0, help="Watch interval seconds"
    )
    ap.add_argument("--no-format", action="store_true", help="Skip code formatting")
    ap.add_argument("--test", action="store_true", help="Run pytest after generation")
    ap.add_argument(
        "--apk",
        action="store_true",
        help="Render APK packaging files (buildozer.spec, build wrapper, CI workflow) using autocoder tasks",
    )
    ap.add_argument(
        "--auto-build",
        action="store_true",
        help="If running on Linux with Docker available, attempt to build the APK automatically after generation",
    )
    ap.add_argument(
        "--use-docker",
        action="store_true",
        help="Force use of Docker for building the APK (when auto-building)",
    )
    args = ap.parse_args()

    # Allow overriding the global OUT_DIR from the CLI.
    global OUT_DIR
    if args.out:
        OUT_DIR = Path(args.out)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # If requested, generate APK packaging files (task must exist in TASK_DIR).
    if getattr(args, "apk", False):
        apk_task = TASK_DIR / "generate_mobile_dj_app.yaml"
        if apk_task.exists():
            res = handle_task(
                apk_task, format_code=not args.no_format, run_tests=args.test
            )
            print(
                f"[AutoCoder][APK] Task {apk_task.name} -> {len(res['generated'])} files, {len(res['errors'])} errors."
            )
            # Optionally attempt to build the generated project into an APK
            if getattr(args, "auto_build", False):
                print(
                    "[AutoCoder][APK] Auto-build requested; attempting to build APK..."
                )
                build_code = build_apk_wrapper(
                    str(OUT_DIR), use_docker=getattr(args, "use_docker", True)
                )
                if build_code == 0:
                    print("[AutoCoder][APK] APK build completed successfully.")
                else:
                    print(f"[AutoCoder][APK] APK build exited with code {build_code}.")
        else:
            print(f"[AutoCoder][APK] APK task file not found: {apk_task}")

        # If --once was requested, exit after handling APK generation/build.
        if args.once:
            return

    if args.once:
        scan_once(format_code=not args.no_format, run_tests=args.test)
    else:
        watch_loop(args.interval, format_code=not args.no_format, run_tests=args.test)


if __name__ == "__main__":
    main()
