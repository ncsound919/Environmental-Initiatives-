"""Tests for the deterministic scaffolder. No network, no LLM, deterministic."""

import json
import py_compile
from pathlib import Path

from cheetah_scaffold import (
    IMPL_MARK,
    SHAPES,
    build_scaffold,
    detect_shape,
    goal_exports,
    project_name,
)


def test_detect_shape():
    assert detect_shape("Create lib/math.js exporting add with vitest tests") == "node-lib"
    assert detect_shape("Build a CLI that reads two args") == "node-cli"
    assert detect_shape("Create an Express REST API with /users routes") == "express-api"
    assert detect_shape("Build a React app with a dashboard component") == "react-vite"
    assert detect_shape("Create a python package with pyproject") == "python-pkg"
    assert detect_shape("A FastAPI service exposing /health") == "fastapi-service"
    assert detect_shape("do the thing") == "node-lib"
    assert detect_shape("anything", requested="react-vite") == "react-vite"


def test_project_name():
    assert project_name("Create lib/math.js exporting add") == "math"
    assert project_name("Create cli.js that reads args") == "cli"
    assert project_name('Build a tool called "Widgetizer" that works') == "widgetizer"
    assert project_name("") == "app"


def test_goal_exports():
    assert goal_exports("exporting add(a,b), sub(a,b), mul(a,b) with tests") == ["add", "sub", "mul"]
    assert goal_exports("exporting unique(nums) and chunk(arr, size)") == ["unique", "chunk"]
    assert goal_exports("no exports named here") == []


def _by_path(files):
    return {f["output"]: f["rendered"] for f in files}


def test_node_lib_scaffold(tmp_path: Path):
    plan = build_scaffold("Create lib/math.js exporting add(a,b) and sub(a,b) with vitest tests")
    assert plan["shape"] == "node-lib"
    assert plan["name"] == "math"
    files = _by_path(plan["files"])
    assert "package.json" in files and "src/index.ts" in files and "src/index.test.ts" in files
    # every file is valid JSON where applicable
    json.loads(files["package.json"])
    json.loads(files["tsconfig.json"])
    # stubs are fail-closed and the guard test references them
    assert IMPL_MARK in files["src/index.ts"]
    assert "add" in files["src/index.ts"] and "sub" in files["src/index.ts"]
    assert IMPL_MARK in files["src/index.test.ts"]
    assert 'from "./index"' in files["src/index.test.ts"]
    # write it out and assert the JSON round-trips on disk
    for rel, body in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    assert (tmp_path / "src" / "index.test.ts").exists()


def test_node_cli_does_not_duplicate_main():
    plan = build_scaffold("build a CLI exporting main and run", shape="node-cli")
    src = _by_path(plan["files"])["src/cli.ts"]
    assert src.count("export function main") == 1


def test_express_scaffold_imports_match_files():
    plan = build_scaffold("Create an Express API exporting listUsers and createUser", shape="express-api")
    files = _by_path(plan["files"])
    assert "createApp" in files["src/app.ts"]
    assert 'from "./app"' in files["src/app.test.ts"]
    assert "listUsers" in files["src/routes.ts"]
    assert 'from "./routes"' in files["src/routes.test.ts"]
    # the advertised start script has a real entry and an emit-capable tsconfig
    assert "src/server.ts" in files
    assert 'from "./app"' in files["src/server.ts"]
    assert '"outDir": "dist"' in files["tsconfig.json"]
    pkg = json.loads(files["package.json"])
    assert "build" in pkg["scripts"]
    assert "@types/express" in pkg["devDependencies"]


def test_react_scaffold_has_jsx():
    plan = build_scaffold("Build a React app", shape="react-vite")
    files = _by_path(plan["files"])
    assert "react-jsx" in files["tsconfig.json"]
    assert "App.tsx" in " ".join(files.keys())
    assert IMPL_MARK in files["src/App.test.ts"]


def test_python_pkg_scaffold_compiles(tmp_path: Path):
    plan = build_scaffold("Create a python package exporting normalize and clamp", shape="python-pkg")
    files = _by_path(plan["files"])
    for rel, body in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    for py in tmp_path.rglob("*.py"):
        py_compile.compile(str(py), doraise=True)
    init = next(tmp_path.glob("src/*/__init__.py"))
    assert "NotImplementedError" in init.read_text(encoding="utf-8")


def test_fastapi_scaffold_compiles(tmp_path: Path):
    plan = build_scaffold("A FastAPI service exposing /health", shape="fastapi-service")
    files = _by_path(plan["files"])
    for rel, body in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    py_compile.compile(str(tmp_path / "app" / "main.py"), doraise=True)
    assert "/health" in files["app/main.py"]


def test_generic_scaffold_is_honest():
    plan = build_scaffold("x", shape="generic")
    files = _by_path(plan["files"])
    assert "NOTES.md" in files
    assert plan["notes"], "generic shape must say it inferred nothing runnable"


def test_determinism():
    a = build_scaffold("Create lib/math.js exporting add with vitest tests")
    b = build_scaffold("Create lib/math.js exporting add with vitest tests")
    assert a == b


def test_full_stack_scaffold_is_complete(tmp_path: Path):
    plan = build_scaffold("Build a full stack app with a react frontend and express api",
                          shape="full-stack")
    assert plan["shape"] == "full-stack"
    files = _by_path(plan["files"])
    # workspaces monorepo root
    root_pkg = json.loads(files["package.json"])
    assert root_pkg["workspaces"] == ["web", "api"]
    assert "build" in root_pkg["scripts"] and "test" in root_pkg["scripts"]
    # both workspaces present
    assert "web/src/App.tsx" in files and "web/src/main.tsx" in files
    assert "api/src/app.ts" in files and "api/src/routes.ts" in files
    assert "api/src/server.ts" in files and 'from "./app"' in files["api/src/server.ts"]
    assert IMPL_MARK in files["web/src/App.tsx"]
    assert IMPL_MARK in files["api/src/app.ts"]
    # guard tests exist and reference the stub files
    assert IMPL_MARK in files["api/src/app.test.ts"]
    assert 'from "./app"' in files["api/src/app.test.ts"]
    assert "react-jsx" in files["web/tsconfig.json"]
    assert "outDir" in files["api/tsconfig.json"]
    # determinism
    again = build_scaffold("Build a full stack app with a react frontend and express api",
                           shape="full-stack")
    assert plan == again


def test_full_stack_no_tests_omits_guards():
    plan = build_scaffold("full stack app", shape="full-stack", tests=False)
    files = _by_path(plan["files"])
    assert not any("test.ts" in f or ".test." in f for f in files)
    web_pkg = json.loads(files["web/package.json"])
    assert "test" not in web_pkg["scripts"]


def test_detect_shape_full_stack():
    assert detect_shape("Build a full stack app") == "full-stack"
    assert detect_shape("full-stack monorepo with an api") == "full-stack"
    assert detect_shape("Build a React app") == "react-vite"
    assert detect_shape("Create an Express REST API") == "express-api"


def test_every_shape_builds():
    for shape in SHAPES:
        plan = build_scaffold("build something useful", shape=shape)
        assert plan["shape"] == shape
        assert plan["files"], f"{shape} produced no files"
        assert plan["name"]


def test_crud_api_shape_detected():
    assert detect_shape("Build a CRUD API for invoices") == "crud-api"
    assert detect_shape("postgres data model for a shop") == "crud-api"


def test_crud_api_scaffold_with_schema():
    schema = "entity User {\n  id string pk\n  email string unique\n}\n"
    plan = build_scaffold("Build a users CRUD API", schema=schema)
    assert plan["shape"] == "crud-api"
    files = _by_path(plan["files"])
    assert "src/routes.ts" in files and "src/zod.ts" in files
    assert "NOT IMPLEMENTED" not in files["src/routes.ts"]


def test_crud_api_scaffold_without_schema_is_honest():
    plan = build_scaffold("Build a CRUD API", shape="crud-api")
    files = _by_path(plan["files"])
    assert "NOTES.md" in files
    assert any("schema" in n.lower() for n in plan["notes"])
