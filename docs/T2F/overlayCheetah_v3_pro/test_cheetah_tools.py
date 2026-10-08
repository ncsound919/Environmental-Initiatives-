"""Tests for Cheetah's deterministic toolchain: fixes, test synthesis, templates,
context. No network, no LLM."""

import json
from pathlib import Path

from cheetah_agent import Workspace
from cheetah_context import build_context
from cheetah_fixes import apply_fixes, plan_fixes
from cheetah_templates import generate_for_goal, generate_template, kinds_for_goal
from cheetah_tests import parse_signatures, synth_tests, synthesize_tests_for_file


def _write(root: Path, rel: str, body: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")


# --- fixes -------------------------------------------------------------------

def test_plan_fixes_is_conservative_and_mechanical(tmp_path: Path):
    _write(tmp_path, "package.json", json.dumps({"name": "x", "version": "1.0.0"}))
    _write(tmp_path, "src/index.ts", "import { unused } from \"./util\";\nimport { used } from \"./other\";\nexport const v = used;\n")
    _write(tmp_path, "src/index.test.ts", "export const t = 1;")

    plan = plan_fixes(str(tmp_path))
    by = {e["path"]: e for e in plan["edits"]}

    # ESM detected -> type: module; test script + devDeps added
    pkg = json.loads(by["package.json"]["content"])
    assert pkg["type"] == "module"
    assert pkg["scripts"]["test"] == "vitest run"
    assert "vitest" in pkg["devDependencies"]
    # tsconfig + .gitignore + README created
    assert "tsconfig.json" in by and ".gitignore" in by and "README.md" in by
    # unused import pruned, used import kept
    src = by["src/index.ts"]["content"]
    assert "unused" not in src
    assert "used" in src
    assert src.endswith("\n")


def test_plan_fixes_survives_invalid_package_json(tmp_path: Path):
    _write(tmp_path, "package.json", "{ not json")
    plan = plan_fixes(str(tmp_path))
    assert any("not valid JSON" in n for n in plan["notes"])
    assert all(e["path"] != "package.json" for e in plan["edits"])


def test_apply_fixes_writes_via_workspace(tmp_path: Path):
    _write(tmp_path, "src/a.ts", "export const a = 1;")
    r = apply_fixes(str(tmp_path))
    assert "tsconfig.json" in r["written"]
    assert (tmp_path / "tsconfig.json").exists()


# --- test synthesis ----------------------------------------------------------

def test_parse_and_synth_ts():
    src = 'export function add(a: number, b: number): number { throw new Error("NOT IMPLEMENTED"); }\nexport const sub = (a, b) => a - b;\n'
    sigs = parse_signatures(src, "ts")
    assert [s["name"] for s in sigs] == ["add", "sub"]
    out = synth_tests(src, "src/index.ts")
    assert out["path"] == "src/index.test.ts"
    assert "implements add" in out["content"]
    assert "boundary(add)" in out["content"]
    assert "NOT IMPLEMENTED" in out["content"]


def test_synth_tests_for_file_contains_root(tmp_path: Path):
    _write(tmp_path, "src/lib.ts", "export function go(n: number) { throw new Error(\"NOT IMPLEMENTED\"); }\n")
    out = synthesize_tests_for_file(str(tmp_path), "src/lib.ts")
    assert out["path"] == "src/lib.test.ts"
    assert "go" in out["exports"]
    escaped = synthesize_tests_for_file(str(tmp_path), "../outside.ts")
    assert escaped["path"] == ""


def test_synth_python():
    src = "def normalize(text):\n    raise NotImplementedError('NOT IMPLEMENTED')\n"
    out = synth_tests(src, "src/pkg/mod.py")
    assert out["path"].startswith("tests/")
    assert "normalize" in out["exports"]


# --- templates ---------------------------------------------------------------

def test_kinds_and_templates():
    assert "express-route" in kinds_for_goal("add a CRUD route for users")
    assert "react-component" in kinds_for_goal("build a dashboard component")
    comp = generate_template("react-component", "user")
    assert comp["path"] == "src/components/User.tsx"
    assert "NOT IMPLEMENTED" not in comp["content"]
    route = generate_template("express-route", "user", {"entity": "user"})
    assert "NOT IMPLEMENTED" in route["content"]
    multi = generate_for_goal("add an express CRUD route for users")
    assert any(f["kind"] == "express-route" for f in multi)


# --- context -----------------------------------------------------------------

def test_build_context_reads_real_files(tmp_path: Path):
    _write(tmp_path, "package.json", json.dumps({"scripts": {"test": "vitest run"}}))
    _write(tmp_path, "src/math.ts", "export function add(a, b) { return a + b; }\n")
    _write(tmp_path, "src/math.test.ts", "import { add } from './math';\n")
    ctx = build_context(str(tmp_path), "add a math helper")
    assert "src/math.ts" in ctx["context"]
    assert "add" in ctx["context"]
    assert "test" in ctx["context"].lower()
    assert ctx["count"] >= 1
