"""Decision-gated scaffold: JEV decides, Cheetah renders.

JEV (TypeSafe System One; wire-compatible LocalJev) answers bounded typed
questions -- choice / noul / score -- over a ``state``. This module:

  1. builds a System One request over the scaffold's decision surface
     (project shape, strict TypeScript, implementation-guard tests);
  2. posts it to ``CHEETAH_JEV_URL/v1/systemone``;
  3. maps the answers onto ``build_scaffold`` knobs (shape, strict, tests);
  4. renders the deterministic file set (zero LLM tokens);
  5. returns the full decision ledger so output is reproducible and auditable.

Honesty contract (same as Dev-Brain ``jevClient.ts``): a non-2xx, timeout, or
malformed answer yields ``source="offline"`` with the real error and falls back
to the deterministic regex classifier. A decision is never fabricated, and an
explicit ``shape``/``strict``/``tests`` argument always wins over JEV. The
rendered files are byte-identical given the same decisions -- the model never
writes code, it only picks between enumerated options.

Env:
  CHEETAH_JEV_URL       default http://127.0.0.1:8080
  CHEETAH_JEV_TIMEOUT   seconds per request, default 10
  CHEETAH_JEV_ENABLED   set to "0" to force the offline path
"""

from __future__ import annotations

import json
import os
import time
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional, Tuple

from cheetah_scaffold import SHAPES, build_scaffold

IMPL_MARK = "NOT IMPLEMENTED"

DEFAULT_JEV_URL = "http://127.0.0.1:8080"
RETRYABLE_STATUS = {429, 529}
MAX_ATTEMPTS = 3

_SHAPE_DESCRIPTIONS: Dict[str, str] = {
    "node-lib": "TypeScript library: package.json, tsconfig, src/index.ts with the named exports",
    "node-cli": "TypeScript CLI: package.json with a bin entry, src/cli.ts with a main()",
    "express-api": "Express REST API: app.ts createApp() and routes.ts registerRoutes()",
    "react-vite": "React 19 + Vite SPA: index.html, src/main.tsx, src/App.tsx",
    "python-pkg": "Python package (src layout): pyproject.toml, package __init__ with the named functions",
    "fastapi-service": "FastAPI service: app/main.py with /health and a handle() stub",
    "full-stack": "Full-stack monorepo: web/ React 19 + Vite frontend and api/ Express backend as npm workspaces",
    "crud-api": "CRUD API: entity DSL schema → zod validation + real CRUD routes + deterministic in-memory store + seeds (express/fastapi)",
    "generic": "No runnable envelope detected; NOTES.md only (honest: nothing inferred)",
}


def jev_settings() -> Dict[str, Any]:
    return {
        "base_url": (os.environ.get("CHEETAH_JEV_URL") or DEFAULT_JEV_URL).rstrip("/"),
        "timeout": float(os.environ.get("CHEETAH_JEV_TIMEOUT") or 10),
        "enabled": os.environ.get("CHEETAH_JEV_ENABLED") != "0",
    }


def _post_systemone(payload: Dict[str, Any], base_url: str, timeout: float) -> Tuple[int, Dict[str, Any]]:
    """POST a System One payload. Returns (status, parsed_json). Raises on transport error."""
    url = f"{base_url}/v1/systemone"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read()
        return resp.status, json.loads(body.decode("utf-8"))


def _noul_decision(answer: Optional[Dict[str, Any]], default: bool) -> bool:
    if not answer or answer.get("type") != "noul":
        return default
    try:
        return float(answer.get("noul") or 0) >= 0.5
    except (TypeError, ValueError):
        return default


def _shape_decision(answer: Optional[Dict[str, Any]]) -> Optional[str]:
    if not answer or answer.get("type") != "choice":
        return None
    choice = answer.get("choice")
    if choice in SHAPES:
        return choice
    return None


def build_decision_request(goal: str) -> Dict[str, Any]:
    """Build the bounded System One request over the scaffold's decision surface."""
    state: Dict[str, Any] = {
        "task": "Choose how to scaffold a project for the goal.",
        "goal": (goal or "").strip()[:1200],
        "available_shapes": list(SHAPES),
    }
    criteria: Dict[str, str] = {}
    for shape in SHAPES:
        criteria[shape] = _SHAPE_DESCRIPTIONS.get(shape, shape)
    questions: Dict[str, Any] = {
        "shape": {
            "type": "choice",
            "instructions": "Which project shape best fits the goal? Pick exactly one.",
            "criteria": criteria,
        },
        "strict": {
            "type": "noul",
            "instructions": "Should the scaffold emit strict TypeScript config (TS shapes only)?",
            "criteria": {
                "true": "strict: true, fail on any type error",
                "false": "strict: false, lenient",
            },
        },
        "tests": {
            "type": "noul",
            "instructions": "Should the scaffold emit implementation-guard tests that fail while stubs are un-implemented?",
            "criteria": {
                "true": "emit guard tests",
                "false": "omit tests",
            },
        },
    }
    return {"model": "jev-latest", "state": state, "questions": questions}


def _ledger_choice(answer: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    entry: Dict[str, Any] = {"source": "localjev"}
    if answer:
        entry["type"] = answer.get("type")
        entry["choice"] = answer.get("choice")
        probs = answer.get("probabilities") or {}
        entry["probability"] = probs.get(answer.get("choice")) if isinstance(probs, dict) else None
        entry["confidence"] = answer.get("confidence")
    return entry


def _ledger_noul(answer: Optional[Dict[str, Any]], decision: bool) -> Dict[str, Any]:
    entry: Dict[str, Any] = {"source": "localjev", "type": "noul", "decision": decision}
    if answer:
        entry["value"] = answer.get("noul")
        entry["confidence"] = answer.get("confidence")
    return entry


def decide_scaffold(goal: str, name: Optional[str] = None, shape: Optional[str] = None,
                    strict: Optional[bool] = None, tests: Optional[bool] = None) -> Dict[str, Any]:
    """Render a deterministic scaffold, gated by JEV decisions where not pinned.

    Pinned args (``shape``/``strict``/``tests``) always win. If nothing is
    pinned, every knob is decided; if all three are pinned, no HTTP call is made.
    On any JEV failure the render falls back to the deterministic classifier.
    """
    settings = jev_settings()
    started = time.time()
    pinned = shape in SHAPES and strict is not None and tests is not None

    decisions: List[Dict[str, Any]] = []
    error: Optional[str] = None
    model: Optional[str] = None
    got_answers = False
    source = "offline"

    if pinned:
        resolved_shape, strict_val, tests_val = shape, strict, tests
        for ident, val in (("shape", shape), ("strict", strict_val), ("tests", tests_val)):
            decisions.append({"id": ident, "source": "pinned", "decision": val})
    elif not settings["enabled"]:
        resolved_shape = shape if shape in SHAPES else None
        strict_val = strict if strict is not None else True
        tests_val = tests if tests is not None else True
        error = "JEV disabled (CHEETAH_JEV_ENABLED=0)"
    else:
        payload = build_decision_request(goal)
        answers: Optional[Dict[str, Any]] = None
        last_status = 0
        last_error = ""
        for attempt in range(MAX_ATTEMPTS):
            if attempt > 0:
                time.sleep(min(0.3, 0.2 * attempt))
            try:
                status, body = _post_systemone(payload, settings["base_url"], settings["timeout"])
                last_status = status
                if status in RETRYABLE_STATUS:
                    last_error = f"HTTP {status} (transient overload; retrying)"
                    continue
                if status != 200:
                    last_error = f"POST /v1/systemone -> HTTP {status}"
                    break
                if not isinstance(body.get("answers"), dict):
                    last_error = "Jev response missing answers"
                    break
                answers = body["answers"]
                model = body.get("model")
                source = "localjev"
                break
            except urllib.error.HTTPError as exc:
                last_status = exc.code
                if exc.code in RETRYABLE_STATUS:
                    last_error = f"HTTP {exc.code} (transient overload; retrying)"
                    continue
                last_error = f"POST /v1/systemone -> HTTP {exc.code}"
                break
            except Exception as exc:
                last_error = str(exc) or "request failed"
                break

        if answers is None:
            error = last_error or "no answers received"
            resolved_shape = shape if shape in SHAPES else None
            strict_val = strict if strict is not None else True
            tests_val = tests if tests is not None else True
        else:
            got_answers = True
            source = "localjev"
            if shape in SHAPES:
                resolved_shape = shape
                decisions.append({"id": "shape", "source": "pinned", "decision": shape})
            else:
                pick = _shape_decision(answers.get("shape"))
                if pick is None:
                    resolved_shape = None
                    decisions.append({
                        "id": "shape", "source": "offline", "decision": None,
                        "error": "JEV shape answer malformed or not in SHAPES",
                        "raw": answers.get("shape"),
                    })
                else:
                    resolved_shape = pick
                    decisions.append({"id": "shape", **_ledger_choice(answers.get("shape"))})
            strict_val = strict if strict is not None else _noul_decision(answers.get("strict"), True)
            tests_val = tests if tests is not None else _noul_decision(answers.get("tests"), True)
            if strict is not None:
                decisions.append({"id": "strict", "source": "pinned", "decision": strict_val})
            else:
                decisions.append({"id": "strict", **_ledger_noul(answers.get("strict"), strict_val)})
            if tests is not None:
                decisions.append({"id": "tests", "source": "pinned", "decision": tests_val})
            else:
                decisions.append({"id": "tests", **_ledger_noul(answers.get("tests"), tests_val)})

    plan = build_scaffold(goal, name=name, shape=resolved_shape,
                          strict=bool(strict_val), tests=bool(tests_val))

    if not got_answers and not pinned:
        # Deterministic fallback: same as plain /scaffold with the decided knobs.
        # Record the *effective* shape (regex classifier result) so the ledger
        # always matches what was actually rendered.
        for ident, val in (("shape", plan["shape"]), ("strict", strict_val), ("tests", tests_val)):
            decisions.append({"id": ident, "source": "offline", "decision": val})

    return {
        "ok": True,
        "source": source,
        "model": model,
        "latency_ms": int((time.time() - started) * 1000),
        "decisions": decisions,
        "error": error,
        **plan,
    }