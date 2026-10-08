"""Tests for the contract-first CRUD engine. No network, no LLM, deterministic."""

import json
import py_compile
from pathlib import Path

from cheetah_schema import (
    build_crud_plan,
    parse_schema,
    wants_crud,
)

SCHEMA = """\
entity User {
  id string pk
  email string unique
  age int optional
  role Role
}

enum Role { admin member guest }
"""


def _files(plan):
    return {f["output"]: f["rendered"] for f in plan["files"]}


def test_parse_schema_ir():
    ir = parse_schema(SCHEMA)
    assert [m.name for m in ir.models] == ["User"]
    assert ir.enums == {"Role": ["admin", "member", "guest"]}
    user = ir.models[0]
    by_name = {f.name: f for f in user.fields}
    assert by_name["id"].pk is True
    assert by_name["email"].unique is True
    assert by_name["age"].optional is True
    assert by_name["role"].type == "Role"


def test_parse_schema_rejects_bad_input():
    for bad in ("entity A {}", "entity 1A { x string }", "entity A { x }",
                "entity A { x wibble }", "entity A { x int bogusmod }"):
        try:
            parse_schema(bad)
            raise AssertionError(f"expected ValueError for: {bad!r}")
        except ValueError:
            pass
    try:
        parse_schema("")
        raise AssertionError("expected ValueError for empty schema")
    except ValueError:
        pass


def test_plan_error_on_bad_schema():
    plan = build_crud_plan("build crud", "entity A {}", framework="express")
    assert plan["ok"] is False
    assert "schema parse failed" in plan["error"]


def test_plan_error_on_bad_framework():
    plan = build_crud_plan("build crud", SCHEMA, framework="nope")
    assert plan["ok"] is False
    assert "framework" in plan["error"]


def test_express_plan_shape_and_manifest(tmp_path: Path):
    plan = build_crud_plan("build a users crud api", SCHEMA, framework="express")
    assert plan["ok"] is True
    assert plan["shape"] == "crud-api"
    assert plan["framework"] == "express"
    assert plan["models"] == ["User"]
    files = _files(plan)
    # core envelope present
    for rel in ("package.json", "tsconfig.json", "src/zod.ts", "src/store.ts",
                "src/routes.ts", "src/app.ts", "src/client.ts", "src/openapi.yaml",
                "src/routes.test.ts", "prisma/schema.prisma", "cheetah.schema",
                "cheetah.manifest.json"):
        assert rel in files, rel
    json.loads(files["package.json"])
    json.loads(files["tsconfig.json"])
    # real CRUD is present, not a stub
    assert "NOT IMPLEMENTED" not in files["src/routes.ts"]
    assert "registerRoutes" in files["src/routes.ts"]
    assert 'email: "email-" + i' in files["src/store.ts"]  # deterministic seed
    assert "safeParse" in files["src/routes.ts"]  # zod validation
    # manifest matches generated files
    manifest = json.loads(files["cheetah.manifest.json"])
    assert set(manifest["generated"]) == set(files.keys()) - {"cheetah.manifest.json"}


def test_express_crud_determinism():
    a = build_crud_plan("crud", SCHEMA, framework="express")
    b = build_crud_plan("crud", SCHEMA, framework="express")
    assert a == b


def test_openapi_covers_models():
    plan = build_crud_plan("crud api", SCHEMA, framework="express")
    yaml = _files(plan)["src/openapi.yaml"]
    assert "/users" in yaml
    assert "/users/{id}" in yaml
    assert "UserCreate" in yaml


def test_fastapi_plan_compiles(tmp_path: Path):
    plan = build_crud_plan("users crud", SCHEMA, framework="fastapi")
    assert plan["ok"] is True
    files = _files(plan)
    for rel, body in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    for py in tmp_path.rglob("*.py"):
        py_compile.compile(str(py), doraise=True)
    assert "NOT IMPLEMENTED" not in files["app/routes.py"]
    assert "seed()" in files["app/store.py"]
    assert "class Role(str, Enum)" in files["app/schemas.py"]
    assert "TestClient" in files["tests/test_api.py"]


def test_wants_crud():
    assert wants_crud("Build a CRUD API for invoices")
    assert wants_crud("postgres data model for a shop")
    assert wants_crud("Build a React app with a dashboard component") is False


def test_relation_stored_as_pk_reference():
    schema = "entity Post {\n  id string pk\n  title string\n  author User optional\n}\nentity User {\n  id string pk\n  email string\n}\n"
    plan = build_crud_plan("posts", schema, framework="express")
    store = _files(plan)["src/store.ts"]
    zod = _files(plan)["src/zod.ts"]
    # relation is an optional pk reference, honestly documented
    assert "author: z.string().min(1).optional()" in zod
    assert "author: string | undefined" in store or "author" in store


def test_no_tests_omits_test_files():
    plan = build_crud_plan("crud", SCHEMA, framework="express", tests=False)
    files = _files(plan)
    assert "src/routes.test.ts" not in files
    pkg = json.loads(files["package.json"])
    assert "test" not in pkg["scripts"]
    plan2 = build_crud_plan("crud", SCHEMA, framework="fastapi", tests=False)
    files2 = _files(plan2)
    assert not any(f.startswith("tests/") for f in files2)
    assert "pytest" not in files2["requirements.txt"]


def test_multiple_models_and_enum_validation():
    schema = "entity User {\n  id string pk\n  role Role\n}\nenum Role { a b c }\nentity Post {\n  id int pk\n  title string unique\n}"
    plan = build_crud_plan("blog", schema, framework="express")
    files = _files(plan)
    assert "/users" in files["src/openapi.yaml"] and "/posts" in files["src/openapi.yaml"]
    assert "z.enum([\"a\", \"b\", \"c\"])" in files["src/zod.ts"]