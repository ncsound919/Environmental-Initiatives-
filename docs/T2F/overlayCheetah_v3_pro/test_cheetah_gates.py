"""Tests for the open-source toolchain gate layer.

Deterministic by construction: python gates (compileall) run for real; node
gates (tsc/eslint/npm scripts) are mocked so they don't depend on a workspace
having node_modules installed. SKIP/ERROR paths are exercised against a real
toolchain detection.
"""

import json
from pathlib import Path
from unittest import mock

from cheetah_gates import (
    GATES,
    _node_exec,
    _node_run,
    detect_toolchain,
    run_gate,
    verify_workspace,
)


def _write(base: Path, rel: str, content: str) -> Path:
    p = base / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def test_detect_empty_dir(tmp_path: Path):
    tc = detect_toolchain(str(tmp_path))
    assert tc["package_manager"] == "npm"
    assert tc["lockfile"] is None
    assert tc["scripts"] == {}
    assert tc["tsconfig"] is False
    assert tc["python"]  # host python exists


def test_detect_pnpm_and_scripts(tmp_path: Path):
    _write(tmp_path, "pnpm-lock.yaml", "")
    _write(tmp_path, "package.json", json.dumps({
        "scripts": {"test": "vitest run", "build": "vite build"},
    }))
    tc = detect_toolchain(str(tmp_path))
    assert tc["package_manager"] == "pnpm"
    assert tc["lockfile"] == "pnpm-lock.yaml"
    assert tc["scripts"] == {"test": "vitest run", "build": "vite build"}


def test_detect_bun_lock(tmp_path: Path):
    _write(tmp_path, "bun.lock", "")
    tc = detect_toolchain(str(tmp_path))
    assert tc["package_manager"] == "bun"


def test_node_command_builders():
    assert _node_run("pnpm", "test") == ["pnpm", "run", "test"]
    assert _node_run("bun", "test") == ["bun", "run", "test"]
    assert _node_run("yarn", "test") == ["yarn", "test"]
    assert _node_run("npm", "test") == ["npm", "run", "test"]
    assert _node_exec("pnpm", ["tsc", "--noEmit"]) == ["pnpm", "exec", "tsc", "--noEmit"]
    assert _node_exec("bun", ["vitest", "run"]) == ["bun", "exec", "vitest", "run"]
    assert _node_exec("npm", ["tsc"]) == ["npx", "--no-install", "tsc"]


def test_verify_empty_all_gates_honest(tmp_path: Path):
    res = verify_workspace(str(tmp_path))
    assert res["passed"] is True
    # every gate must report a valid status and none may fake a FAIL
    assert all(g["status"] in ("PASS", "SKIP") for g in res["gates"])
    assert res["counts"].get("FAIL", 0) == 0
    assert res["counts"].get("ERROR", 0) == 0
    assert res["counts"].get("TIMEOUT", 0) == 0
    assert res["unknown_gates"] == []


def test_build_gate_compileall_pass(tmp_path: Path):
    _write(tmp_path, "src/ok.py", "def add(a, b):\n    return a + b\n")
    tc = detect_toolchain(str(tmp_path))
    result = run_gate(tc, "build")
    assert result["status"] == "PASS"
    assert "compileall" in result["runner"]


def test_build_gate_compileall_fail(tmp_path: Path):
    _write(tmp_path, "src/bad.py", "def broken(:\n    pass\n")
    tc = detect_toolchain(str(tmp_path))
    result = run_gate(tc, "build")
    assert result["status"] == "FAIL"
    assert result["output_tail"]


def test_verify_fails_on_broken_python(tmp_path: Path):
    _write(tmp_path, "src/bad.py", "def broken(:\n")
    res = verify_workspace(str(tmp_path))
    assert res["passed"] is False
    assert res["counts"].get("FAIL", 0) >= 1


def test_unknown_gate_reported(tmp_path: Path):
    res = verify_workspace(str(tmp_path), gates=["nope"])
    assert res["unknown_gates"] == ["nope"]
    assert res["gates"] == []


def _launched(mock_run):
    """Strip the Windows `cmd /c` wrapper if present."""
    args = mock_run.call_args.args[0]
    return args[2:] if len(args) >= 2 and args[:2] == ["cmd", "/c"] else args


def test_declared_test_script_uses_package_manager(tmp_path: Path):
    _write(tmp_path, "package-lock.json", "{}")
    _write(tmp_path, "package.json", json.dumps({"scripts": {"test": "node -e 'console.log(1)'"}}))
    tc = detect_toolchain(str(tmp_path))
    fake = mock.Mock(returncode=0, stdout="ok\n", stderr="")
    with mock.patch("cheetah_gates.subprocess.run", return_value=fake) as run:
        result = run_gate(tc, "test")
    assert result["status"] == "PASS"
    assert _launched(run) == ["npm", "run", "test"]


def test_tsconfig_typecheck_uses_no_install_npx(tmp_path: Path):
    _write(tmp_path, "tsconfig.json", "{}")
    _write(tmp_path, "src/index.ts", "export const x = 1;\n")
    tc = detect_toolchain(str(tmp_path))
    fake = mock.Mock(returncode=0, stdout="", stderr="")
    with mock.patch("cheetah_gates.subprocess.run", return_value=fake) as run:
        result = run_gate(tc, "typecheck")
    assert result["status"] == "PASS"
    assert _launched(run) == ["npx", "--no-install", "tsc", "--noEmit"]


def test_pnpm_test_script_command(tmp_path: Path):
    _write(tmp_path, "pnpm-lock.yaml", "")
    _write(tmp_path, "package.json", json.dumps({"scripts": {"test": "vitest run"}}))
    tc = detect_toolchain(str(tmp_path))
    fake = mock.Mock(returncode=0, stdout="", stderr="")
    with mock.patch("cheetah_gates.subprocess.run", return_value=fake) as run:
        run_gate(tc, "test")
    assert _launched(run) == ["pnpm", "run", "test"]


def test_missing_runner_error(tmp_path: Path):
    _write(tmp_path, "package.json", json.dumps({"scripts": {"test": "x"}}))
    tc = detect_toolchain(str(tmp_path))
    # package manager binary is present on this host, but the script will fail;
    # simulate a missing binary to assert the ERROR branch.
    with mock.patch("cheetah_gates.subprocess.run", side_effect=FileNotFoundError("no such file")):
        result = run_gate(tc, "test")
    assert result["status"] == "ERROR"
    assert "binary missing" in result["detail"]


def test_e2e_gate_skips_without_playwright(tmp_path: Path):
    tc = detect_toolchain(str(tmp_path))
    result = run_gate(tc, "e2e")
    assert result["status"] == "SKIP"
    assert "playwright" in result["detail"]


def test_e2e_gate_runs_playwright(tmp_path: Path):
    _write(tmp_path, "playwright.config.ts", "export default {};\n")
    _write(tmp_path, "e2e/smoke.spec.ts", "import { test } from '@playwright/test';\n")
    tc = detect_toolchain(str(tmp_path))
    assert tc["playwright_config"] is True and tc["has_e2e_dir"] is True
    fake = mock.Mock(returncode=0, stdout="ok\n", stderr="")
    with mock.patch("cheetah_gates.subprocess.run", return_value=fake) as run:
        result = run_gate(tc, "e2e")
    assert result["status"] == "PASS"
    assert _launched(run) == ["npx", "--no-install", "playwright", "test"]


def test_drift_gate_skips_without_schema(tmp_path: Path):
    tc = detect_toolchain(str(tmp_path))
    result = run_gate(tc, "drift")
    assert result["status"] == "SKIP"


def test_drift_gate_pass_when_byte_identical(tmp_path: Path):
    plan = _schema_plan()
    for f in plan["files"]:
        _write(tmp_path, f["output"], f["rendered"])
    tc = detect_toolchain(str(tmp_path))
    result = run_gate(tc, "drift")
    assert result["status"] == "PASS"


def test_drift_gate_fails_on_edited_generated_file(tmp_path: Path):
    plan = _schema_plan()
    for f in plan["files"]:
        _write(tmp_path, f["output"], f["rendered"])
    # hand-edit a generated artifact -> drift must FAIL, not fake a pass
    routes = tmp_path / "src" / "routes.ts"
    routes.write_text(routes.read_text(encoding="utf-8") + "\n// hand-edit\n", encoding="utf-8")
    tc = detect_toolchain(str(tmp_path))
    result = run_gate(tc, "drift")
    assert result["status"] == "FAIL"
    assert "drift" in result["output_tail"]


def test_drift_gate_fails_on_missing_generated_file(tmp_path: Path):
    plan = _schema_plan()
    for f in plan["files"]:
        _write(tmp_path, f["output"], f["rendered"])
    (tmp_path / "src" / "zod.ts").unlink()
    tc = detect_toolchain(str(tmp_path))
    result = run_gate(tc, "drift")
    assert result["status"] == "FAIL"
    assert "missing" in result["output_tail"]


def _schema_plan():
    from cheetah_schema import build_crud_plan
    schema = "entity User {\n  id string pk\n  email string unique\n}\n"
    plan = build_crud_plan("Build a users CRUD API", schema, framework="express")
    assert plan["ok"]
    return plan