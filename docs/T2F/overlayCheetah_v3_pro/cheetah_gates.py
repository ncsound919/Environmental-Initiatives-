"""Open-source toolchain gates for Overlay Cheetah V3 Pro+.

Accuracy contract: verification is delegated to the real tools that exist in
the workspace -- tsc, eslint, prettier, ruff, mypy, pytest, the declared
build/typecheck scripts -- instead of Cheetah's regex approximations. Every
gate runs with the correct package manager (pnpm/bun/yarn/npm, detected from
the lockfile) and reports an honest status:

  PASS     tool ran and exited 0
  FAIL     tool ran and exited non-zero (output tail included)
  SKIP     tool/script is not applicable in this workspace (never a fake pass)
  ERROR    tool is declared but missing / could not be executed
  TIMEOUT  exceeded the per-gate timeout

Stdlib only. No network. No LLM. Callers that want the root confined to a
sandbox must do so before invoking -- the gates execute in ``root`` as given.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

GATES = ("test", "typecheck", "lint", "format", "build", "e2e", "drift")

_LOCKFILE_MANAGER: Dict[str, str] = {
    "pnpm-lock.yaml": "pnpm",
    "bun.lock": "bun",
    "bun.lockb": "bun",
    "yarn.lock": "yarn",
    "package-lock.json": "npm",
}

_ESLINT_CONFIGS = (".eslintrc", ".eslintrc.json", ".eslintrc.js", ".eslintrc.cjs",
                   "eslint.config.js", "eslint.config.mjs", "eslint.config.ts")
_PRETTIER_CONFIGS = (".prettierrc", ".prettierrc.json", ".prettierrc.yaml",
                     ".prettierrc.yml", ".prettierrc.js", "prettier.config.js")
_RUFF_CONFIGS = ("ruff.toml", ".ruff.toml")


def _venv_python(base: Path) -> Optional[Path]:
    if os.name == "nt":
        cand = base / ".venv" / "Scripts" / "python.exe"
    else:
        cand = base / ".venv" / "bin" / "python"
    return cand if cand.is_file() else None


def _which(name: str) -> bool:
    return shutil.which(name) is not None


def detect_toolchain(root: str) -> Dict[str, Any]:
    """Read the workspace on disk and report what verification tooling exists."""
    base = Path(root).resolve()
    lock = next((n for n in _LOCKFILE_MANAGER if (base / n).is_file()), None)
    manager = _LOCKFILE_MANAGER.get(lock, "npm") if lock else "npm"

    pkg: Dict[str, Any] = {}
    pkg_path = base / "package.json"
    if pkg_path.is_file():
        try:
            parsed = json.loads(pkg_path.read_text(encoding="utf-8"))
            if isinstance(parsed, dict):
                pkg = parsed
        except (json.JSONDecodeError, UnicodeDecodeError):
            pkg = {"_error": "package.json unreadable"}
    scripts = pkg.get("scripts") if isinstance(pkg.get("scripts"), dict) else {}
    deps = {
        **({} if not isinstance(pkg.get("dependencies"), dict) else pkg.get("dependencies", {})),
        **({} if not isinstance(pkg.get("devDependencies"), dict) else pkg.get("devDependencies", {})),
    }

    python = str(_venv_python(base)) if _venv_python(base) else ("python" if _which("python") else None)

    def _has_glob(pattern: str) -> bool:
        try:
            return next(base.rglob(pattern), None) is not None
        except (PermissionError, OSError):
            return False

    has_tests = (
        bool(list(base.glob("test_*.py")) or list(base.glob("*_test.py")))
        or (base / "tests").is_dir()
        or any(_has_glob(p) for p in ("*.test.ts", "*.test.tsx", "*.test.js", "*.test.jsx"))
    )
    playwright_config = any((base / c).exists() for c in (
        "playwright.config.ts", "playwright.config.js", "playwright.config.mjs", "playwright.config.tsx"))
    has_e2e_dir = (base / "e2e").is_dir() or (base / "tests" / "e2e").is_dir()
    has_python_src = _has_glob("*.py")
    has_node_src = any(_has_glob(p) for p in ("*.ts", "*.tsx", "*.js", "*.jsx", "*.mjs", "*.cjs"))

    return {
        "root": str(base),
        "package_manager": manager,
        "lockfile": lock,
        "node": _which("node"),
        "python": python,
        "package_json": pkg if isinstance(pkg, dict) and "_error" not in pkg else None,
        "scripts": scripts,
        "deps": deps,
        "tsconfig": (base / "tsconfig.json").is_file(),
        "pyproject": (base / "pyproject.toml").is_file(),
        "vitest_config": (base / "vitest.config.ts").is_file() or (base / "vitest.config.js").is_file(),
        "playwright_config": playwright_config,
        "has_e2e_dir": has_e2e_dir,
        "eslint_config": any((base / c).exists() for c in _ESLINT_CONFIGS),
        "prettier_config": any((base / c).exists() for c in _PRETTIER_CONFIGS),
        "ruff_config": any((base / c).exists() for c in _RUFF_CONFIGS) or (base / "pyproject.toml").is_file(),
        "mypy_config": any((base / c).exists() for c in ("mypy.ini", ".mypy.ini")) or (base / "pyproject.toml").is_file(),
        "has_test_files": has_tests,
        "has_python_src": has_python_src,
        "has_node_src": has_node_src,
    }


def _node_run(manager: str, script: str) -> List[str]:
    if manager == "pnpm":
        return ["pnpm", "run", script]
    if manager == "bun":
        return ["bun", "run", script]
    if manager == "yarn":
        return ["yarn", script]
    return ["npm", "run", script]


def _node_exec(manager: str, args: Sequence[str]) -> List[str]:
    if manager == "pnpm":
        return ["pnpm", "exec", *args]
    if manager == "bun":
        return ["bun", "exec", *args]
    if manager == "yarn":
        return ["yarn", *args]
    return ["npx", "--no-install", *args]


_probe_cache: Dict[Tuple[str, str], bool] = {}


def _py_module(python: Optional[str], module: str, root: str) -> bool:
    if not python:
        return False
    key = (python, module)
    if key in _probe_cache:
        return _probe_cache[key]
    ok = False
    try:
        proc = subprocess.run(
            [python, "-c", f"import {module}"], cwd=root,
            capture_output=True, text=True, timeout=30,
        )
        ok = proc.returncode == 0
    except Exception:
        ok = False
    _probe_cache[key] = ok
    return ok


def _run(cmd: Sequence[str], root: str, timeout: float) -> Dict[str, Any]:
    launched = list(cmd)
    # Windows: node tooling ships as .cmd/.ps1 shims that CreateProcess cannot
    # launch directly. Resolve the real file and wrap it in the right host.
    if os.name == "nt":
        resolved = shutil.which(launched[0])
        if resolved:
            lower = resolved.lower()
            if lower.endswith((".cmd", ".bat")):
                launched = ["cmd", "/c", *launched]
            elif lower.endswith(".ps1"):
                launched = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                            "-File", resolved, *launched[1:]]
    started = time.time()
    try:
        proc = subprocess.run(
            launched, cwd=root, capture_output=True, text=True, timeout=timeout,
        )
    except FileNotFoundError:
        return {"status": "ERROR", "detail": f"binary missing: {cmd[0]}", "exit_code": None,
                "duration_sec": round(time.time() - started, 2), "output_tail": ""}
    except subprocess.TimeoutExpired:
        return {"status": "TIMEOUT", "detail": f"exceeded {int(timeout)}s", "exit_code": None,
                "duration_sec": round(time.time() - started, 2), "output_tail": ""}
    tail = (proc.stdout + "\n" + proc.stderr)[-4000:]
    return {"status": "PASS" if proc.returncode == 0 else "FAIL",
            "detail": f"exit={proc.returncode}",
            "exit_code": proc.returncode,
            "duration_sec": round(time.time() - started, 2),
            "output_tail": tail}


def _skip(reason: str) -> Dict[str, Any]:
    return {"status": "SKIP", "detail": reason, "exit_code": None,
            "duration_sec": 0.0, "output_tail": ""}


def run_drift_gate(root: str) -> Dict[str, Any]:
    """Regenerate a cheetah_schema workspace from its committed schema and diff
    every generated file byte-for-byte. FAIL on any drift — the oasts-style
    guarantee that committed artifacts match what the engine would emit."""
    base = Path(root).resolve()
    manifest_p = base / "cheetah.manifest.json"
    schema_p = base / "cheetah.schema"
    if not (manifest_p.is_file() and schema_p.is_file()):
        return _skip("no cheetah.schema/cheetah.manifest.json — not a schema-generated workspace")
    try:
        mf = json.loads(manifest_p.read_text(encoding="utf-8"))
        schema_text = schema_p.read_text(encoding="utf-8")
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return {"gate": "drift", "runner": "", "status": "ERROR",
                "detail": f"unreadable cheetah manifest/schema: {exc}",
                "exit_code": None, "duration_sec": 0.0, "output_tail": ""}
    from cheetah_schema import build_crud_plan
    plan = build_crud_plan(str(mf.get("goal") or ""), schema_text,
                           framework=str(mf.get("framework") or "express"),
                           name=mf.get("name"))
    if not plan.get("ok"):
        return {"gate": "drift", "runner": "", "status": "ERROR",
                "detail": f"regeneration failed: {plan.get('error')}",
                "exit_code": None, "duration_sec": 0.0, "output_tail": ""}
    generated = {f["output"]: f["rendered"] for f in plan["files"]}
    diffs: List[str] = []
    for rel in mf.get("generated", []):
        disk = base / rel
        if not disk.is_file():
            diffs.append(f"missing: {rel}")
            continue
        try:
            on_disk = disk.read_text(encoding="utf-8")
        except Exception:
            diffs.append(f"unreadable: {rel}")
            continue
        if on_disk != generated.get(rel):
            diffs.append(f"drift: {rel}")
    if diffs:
        return {"gate": "drift", "runner": "regenerate && diff", "status": "FAIL",
                "detail": f"{len(diffs)} generated file(s) drifted from the committed schema",
                "exit_code": 1, "duration_sec": 0.0, "output_tail": "\n".join(diffs[:8])}
    return {"gate": "drift", "runner": "regenerate && diff", "status": "PASS",
            "detail": f"{len(mf.get('generated', []))} generated file(s) byte-identical",
            "exit_code": 0, "duration_sec": 0.0, "output_tail": ""}


def run_gate(toolchain: Dict[str, Any], gate: str,
             timeout: Optional[float] = None) -> Dict[str, Any]:
    """Run one verification gate against a detected toolchain."""
    timeout = timeout if timeout is not None else float(os.environ.get("CHEETAH_GATE_TIMEOUT") or 300)
    base = Path(toolchain["root"])
    manager = toolchain["package_manager"]
    scripts = toolchain.get("scripts") or {}
    python = toolchain.get("python")

    if gate == "test":
        if scripts.get("test"):
            cmd = _node_run(manager, "test")
            return {"gate": gate, "runner": " ".join(cmd), **_run(cmd, str(base), timeout)}
        if toolchain.get("vitest_config"):
            cmd = _node_exec(manager, ["vitest", "run"])
            return {"gate": gate, "runner": " ".join(cmd), **_run(cmd, str(base), timeout)}
        if toolchain.get("has_test_files") or toolchain.get("pyproject"):
            if not _py_module(python, "pytest", str(base)):
                return {"gate": gate, "runner": "pytest", **(
                    _skip("python test files present but pytest is not installed")
                    if not toolchain.get("has_test_files")
                    else {"status": "ERROR", "detail": "python tests present but pytest not installed",
                          "exit_code": None, "duration_sec": 0.0, "output_tail": ""})}
            cmd = [python, "-m", "pytest", "-q"]
            return {"gate": gate, "runner": " ".join(cmd), **_run(cmd, str(base), timeout)}
        return {"gate": gate, "runner": "", **_skip("no test runner detected (scripts.test, vitest, pytest)")}

    if gate == "typecheck":
        if scripts.get("typecheck"):
            cmd = _node_run(manager, "typecheck")
            return {"gate": gate, "runner": " ".join(cmd), **_run(cmd, str(base), timeout)}
        if toolchain.get("tsconfig") and toolchain.get("has_node_src"):
            cmd = _node_exec(manager, ["tsc", "--noEmit"])
            return {"gate": gate, "runner": " ".join(cmd), **_run(cmd, str(base), timeout)}
        if toolchain.get("mypy_config") and toolchain.get("has_python_src") and _py_module(python, "mypy", str(base)):
            cmd = [python, "-m", "mypy", "."]
            return {"gate": gate, "runner": " ".join(cmd), **_run(cmd, str(base), timeout)}
        return {"gate": gate, "runner": "", **_skip("no typecheck tooling (scripts.typecheck, tsconfig, mypy)")}

    if gate == "lint":
        if scripts.get("lint"):
            cmd = _node_run(manager, "lint")
            return {"gate": gate, "runner": " ".join(cmd), **_run(cmd, str(base), timeout)}
        if toolchain.get("eslint_config") and toolchain.get("has_node_src"):
            cmd = _node_exec(manager, ["eslint", "."])
            return {"gate": gate, "runner": " ".join(cmd), **_run(cmd, str(base), timeout)}
        if toolchain.get("ruff_config") and toolchain.get("has_python_src") and _py_module(python, "ruff", str(base)):
            cmd = [python, "-m", "ruff", "check", "."]
            return {"gate": gate, "runner": " ".join(cmd), **_run(cmd, str(base), timeout)}
        return {"gate": gate, "runner": "", **_skip("no lint tooling (scripts.lint, eslint, ruff)")}

    if gate == "format":
        if scripts.get("format"):
            cmd = _node_run(manager, "format")
            return {"gate": gate, "runner": " ".join(cmd), **_run(cmd, str(base), timeout)}
        if toolchain.get("has_node_src") and toolchain.get("prettier_config"):
            cmd = _node_exec(manager, ["prettier", "--check", "."])
            return {"gate": gate, "runner": " ".join(cmd), **_run(cmd, str(base), timeout)}
        if toolchain.get("has_python_src") and _py_module(python, "black", str(base)):
            cmd = [python, "-m", "black", "--check", "."]
            return {"gate": gate, "runner": " ".join(cmd), **_run(cmd, str(base), timeout)}
        return {"gate": gate, "runner": "", **_skip("no format tooling for this workspace's languages")}

    if gate == "build":
        if scripts.get("build"):
            cmd = _node_run(manager, "build")
            return {"gate": gate, "runner": " ".join(cmd), **_run(cmd, str(base), timeout)}
        if toolchain.get("python") and toolchain.get("has_python_src"):
            dirs = [d for d in ("src", "app", "tests") if (base / d).is_dir()]
            if dirs:
                cmd = [python, "-m", "compileall", "-q", *dirs]
                return {"gate": gate, "runner": " ".join(cmd), **_run(cmd, str(base), timeout)}
        return {"gate": gate, "runner": "", **_skip("no build target (scripts.build, python src/app/tests)")}

    if gate == "e2e":
        if toolchain.get("playwright_config") and toolchain.get("has_e2e_dir"):
            cmd = _node_exec(manager, ["playwright", "test"])
            return {"gate": gate, "runner": " ".join(cmd), **_run(cmd, str(base), timeout)}
        return {"gate": gate, "runner": "",
                **_skip("no playwright config + e2e dir (SKIP — never a fake pass)")}

    if gate == "drift":
        return run_drift_gate(str(base))

    return {"gate": gate, "runner": "", **_skip(f"unknown gate: {gate}")}


def verify_workspace(root: str, gates: Optional[Sequence[str]] = None,
                     timeout: Optional[float] = None) -> Dict[str, Any]:
    """Run the requested gate battery (default: all known gates) against root."""
    requested = list(gates) if gates else list(GATES)
    unknown = [g for g in requested if g not in GATES]
    toolchain = detect_toolchain(root)
    results = [run_gate(toolchain, g, timeout=timeout) for g in requested if g in GATES]
    counts: Dict[str, int] = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    passed = counts.get("FAIL", 0) == 0 and counts.get("ERROR", 0) == 0 and counts.get("TIMEOUT", 0) == 0
    return {
        "ok": True,
        "passed": passed,
        "root": toolchain["root"],
        "toolchain": toolchain,
        "gates": results,
        "counts": counts,
        "unknown_gates": unknown,
    }