"""Contract-first CRUD engine for Overlay Cheetah V3 Pro+.

Why this exists: the historical scaffolder emits *stubs* for routes/models and
relies on an LLM to fill them. But the CRUD envelope (model -> validation ->
routes -> client -> mock data -> tests) is *mechanical*: given a data model it
can be generated correctly, deterministically, and completely with zero LLM
tokens. This module is that generation.

Input (deterministic DSL, no LLM):

    entity User {
      id string pk
      email string unique
      age int optional
      role Role
    }

    enum Role { admin member guest }

    entity Post {
      title string
      author User        # many-to-one relation: stores the referenced pk
    }

Supported field types: string, int, float, bool, datetime, uuid, any declared
enum name, or any declared entity name (relation). Modifiers per field:
pk, unique, optional, list.

Output (``build_crud_plan``), per framework:

  express   -> prisma/schema.prisma, src/models.ts, src/zod.ts, src/store.ts
               (deterministic in-memory store + seed), src/app.ts,
               src/routes.ts (REAL CRUD with zod validation), src/client.ts
               (typed fetch client), src/openapi.yaml, src/routes.test.ts
               (real integration tests), build config, manifest.
  fastapi   -> app/schemas.py (pydantic), app/store.py, app/routes.py,
               app/main.py, tests/test_api.py, requirements.txt, pyproject.

Honesty contract: relations are emitted but the store resolves them to plain
pk references (no join semantics are invented); seeds are deterministic
(derived from field names + a counter — never random); tests assert real
behaviour. The plan also emits a ``cheetah.schema`` + ``cheetah.manifest.json``
so the ``drift`` verify gate can regenerate and diff byte-for-byte.

Stdlib only. No network. No LLM.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

VERSION = "4.2.0-schema"

_KNOWN_TYPES = {"string", "int", "float", "bool", "datetime", "uuid"}
_MODIFIERS = {"pk", "unique", "optional", "list"}
_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

_ENTITY_RE = re.compile(r"entity\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{([^}]*)\}", re.I)
_ENUM_RE = re.compile(r"enum\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{([^}]*)\}", re.I)

_CRUD_HINT = re.compile(
    r"\b(crud( api)?|postgres|sqlite|database schema|data model|entities)\b|"
    r"\b(storage|persist|repository)\b", re.I)

FRAMEWORKS = ("express", "fastapi")


# ---------------------------------------------------------------------------
# IR
# ---------------------------------------------------------------------------

@dataclass
class Field:
    name: str
    type: str
    pk: bool = False
    unique: bool = False
    optional: bool = False
    list: bool = False


@dataclass
class Model:
    name: str
    fields: List[Field] = field(default_factory=list)


@dataclass
class SchemaIR:
    models: List[Model] = field(default_factory=list)
    enums: Dict[str, List[str]] = field(default_factory=dict)


def _plural(name: str) -> str:
    if name.endswith(("s", "x", "z", "ch", "sh")):
        return name + "es"
    if name.endswith("y") and len(name) > 1 and name[-2] not in "aeiou":
        return name[:-1] + "ies"
    return name + "s"


def _pascal(name: str) -> str:
    parts = re.split(r"[^A-Za-z0-9]+", name or "Model")
    out = "".join(p[:1].upper() + p[1:] for p in parts if p)
    return out or "Model"


def _camel(name: str) -> str:
    p = _pascal(name)
    return p[:1].lower() + p[1:]


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def parse_schema(text: str) -> SchemaIR:
    """Parse the deterministic entity DSL. Raises ValueError on malformed input."""
    src = text or ""
    ir = SchemaIR()

    for m in _ENUM_RE.finditer(src):
        name = m.group(1)
        if not _IDENT.match(name):
            raise ValueError(f"bad enum name: {name!r}")
        values = [v for v in re.split(r"[,\s]+", m.group(2).strip()) if v]
        if not values:
            raise ValueError(f"enum {name} has no values")
        for v in values:
            if not _IDENT.match(v):
                raise ValueError(f"bad enum value {v!r} in {name}")
        ir.enums[name] = values

    names = {m.group(1) for m in _ENTITY_RE.finditer(src)}
    for m in _ENTITY_RE.finditer(src):
        name = m.group(1)
        if not _IDENT.match(name):
            raise ValueError(f"bad entity name: {name!r}")
        if name in ir.enums:
            raise ValueError(f"name collision: {name} is both entity and enum")
        model = Model(name=name)
        for lineno, raw in enumerate(m.group(2).splitlines(), 1):
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            toks = line.split()
            if len(toks) < 2:
                raise ValueError(f"{name}:{lineno} field needs name + type: {line!r}")
            fname, ftype = toks[0], toks[1]
            if not _IDENT.match(fname):
                raise ValueError(f"{name}:{lineno} bad field name {fname!r}")
            if ftype not in _KNOWN_TYPES and ftype not in ir.enums and ftype not in names:
                raise ValueError(f"{name}:{lineno} unknown type {ftype!r} "
                                 f"(known: {sorted(_KNOWN_TYPES)} + declared enums/entities)")
            fld = Field(name=fname, type=ftype)
            for mod in toks[2:]:
                if mod not in _MODIFIERS:
                    raise ValueError(f"{name}:{lineno} unknown modifier {mod!r}")
                setattr(fld, mod, True)
            if fld.pk and ftype not in ("string", "int", "uuid"):
                raise ValueError(f"{name}:{lineno} pk must be string/int/uuid")
            if fld.list and fld.pk:
                raise ValueError(f"{name}:{lineno} pk cannot be a list")
            model.fields.append(fld)
        if not model.fields:
            raise ValueError(f"entity {name} has no fields")
        ir.models.append(model)

    if not ir.models:
        raise ValueError("no entities declared (use: entity Name { field type ... })")
    return ir


# ---------------------------------------------------------------------------
# Value + TS/Py type helpers
# ---------------------------------------------------------------------------

def _ts_type(fld: Field, enums: Dict[str, List[str]]) -> str:
    if fld.type in enums:
        base = " | ".join(json.dumps(v) for v in enums[fld.type])
    elif fld.type == "bool":
        base = "boolean"
    elif fld.type in ("int", "float"):
        base = "number"
    elif fld.type in ("string", "datetime", "uuid"):
        base = "string"
    else:
        base = "string"  # relation: referenced pk
    if fld.list:
        base = f"{base}[]"
    if fld.optional and not fld.list:
        base += " | undefined"
    return base


def _py_type(fld: Field, enums: Dict[str, List[str]]) -> str:
    if fld.type in enums:
        base = fld.type
    elif fld.type == "bool":
        base = "bool"
    elif fld.type == "int":
        base = "int"
    elif fld.type == "float":
        base = "float"
    elif fld.type == "datetime":
        base = "datetime"
    elif fld.type == "uuid":
        base = "str"
    else:
        base = "str"  # relation: referenced pk
    if fld.list:
        base = f"list[{base}]"
    return base


def _zod_expr(fld: Field, enums: Dict[str, List[str]]) -> str:
    if fld.type in enums:
        base = f"z.enum({json.dumps(enums[fld.type])})"
    elif fld.type == "int":
        base = "z.number().int()"
    elif fld.type == "float":
        base = "z.number()"
    elif fld.type == "bool":
        base = "z.boolean()"
    elif fld.type == "datetime":
        base = "z.string().datetime()"
    elif fld.type == "uuid":
        base = "z.string().uuid()"
    else:
        base = "z.string().min(1)"
    if fld.list:
        base = f"z.array({base})"
    if fld.optional and not fld.list:
        base += ".optional()"
    return base


def _seed_value(fld: Field, var: str, enums: Dict[str, List[str]], lang: str) -> str:
    """Deterministic seed literal for a field. ``var`` is the loop variable name
    (``i`` for both TS and Python); it is inserted *literally* into the emitted
    source so generation stays index-independent."""
    t = fld.type
    if t == "int":
        return var
    if t == "float":
        return f"{var} + 0.5"
    if t == "bool":
        return f"{var} % 2 === 0" if lang == "ts" else f"{var} % 2 == 0"
    if t == "datetime":
        return '"2026-01-01T00:00:00.000Z"' if lang == "ts" else "'2026-01-01T00:00:00.000Z'"
    if t == "uuid":
        return '"00000000-0000-4000-8000-000000000001"' if lang == "ts" else "'00000000-0000-4000-8000-000000000001'"
    if t in enums:
        q = '"' if lang == "ts" else "'"
        return f"{q}{enums[t][0]}{q}"
    if lang == "ts":
        return f'"{fld.name}-" + {var}'
    return f"'{fld.name}-{var}'"


def _sample_value(fld: Field, enums: Dict[str, List[str]], lang: str) -> str:
    """A valid literal for a required non-pk field, used by the generated tests
    so the CRUD POST actually passes zod validation."""
    t = fld.type
    if t == "int":
        return "0"
    if t == "float":
        return "0.5"
    if t == "bool":
        return "true" if lang == "ts" else "True"
    if t == "datetime":
        return '"2026-01-01T00:00:00.000Z"' if lang == "ts" else "'2026-01-01T00:00:00.000Z'"
    if t == "uuid":
        return '"00000000-0000-4000-8000-000000000001"' if lang == "ts" else "'00000000-0000-4000-8000-000000000001'"
    if t in enums:
        q = '"' if lang == "ts" else "'"
        return f"{q}{enums[t][0]}{q}"
    q = '"' if lang == "ts" else "'"
    return f"{q}test-0{q}"


def _sample_payload(model: Model, enums: Dict[str, List[str]], lang: str) -> List[str]:
    """List of `key: value` lines for every required non-pk field."""
    out: List[str] = []
    for f in model.fields:
        if f.pk or f.optional or f.list:
            continue
        q = '"' if lang == "ts" else "'"
        out.append(f"{q}{f.name}{q}: {_sample_value(f, enums, lang)}")
    return out


# ---------------------------------------------------------------------------
# Express emitters
# ---------------------------------------------------------------------------

_GITIGNORE = "node_modules/\ndist/\ncoverage/\n*.log\n__pycache__/\n.venv/\n"

_TSCONFIG_CRUD = """{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "outDir": "dist",
    "rootDir": "src"
  },
  "include": ["src"]
}
"""

_VITEST_CFG = """import { defineConfig } from "vitest/config";

export default defineConfig({ test: { environment: "node" } });
"""


def _prisma_schema(ir: SchemaIR) -> str:
    lines = [
        "// Generated by Overlay Cheetah schema engine (deterministic; zero tokens).",
        'datasource db {',
        '  provider = "postgresql"',
        '  url      = env("DATABASE_URL")',
        "}",
        "",
        "generator client {",
        '  provider = "prisma-client-js"',
        "}",
        "",
    ]
    for ename, values in ir.enums.items():
        lines.append(f"enum {ename} {{")
        for v in values:
            lines.append(f"  {v}")
        lines.append("}")
        lines.append("")
    for model in ir.models:
        lines.append(f"model {model.name} {{")
        for f in model.fields:
            ann = _prisma_type(f, ir)
            mods = []
            if f.pk:
                mods.append("@id")
                if f.type in ("string", "uuid"):
                    mods.append("@default(uuid())")
                else:
                    mods.append("@default(autoincrement())")
            if f.unique:
                mods.append("@unique")
            line = f"  {f.name:<16} {ann}"
            if mods:
                line += "  " + " ".join(mods)
            lines.append(line.rstrip())
        lines.append("}")
        lines.append("")
    return "\n".join(lines)


def _prisma_type(fld: Field, ir: SchemaIR) -> str:
    if fld.type == "int":
        base = "Int"
    elif fld.type == "float":
        base = "Float"
    elif fld.type == "bool":
        base = "Boolean"
    elif fld.type == "datetime":
        base = "DateTime"
    elif fld.type in ("string", "uuid"):
        base = "String"
    elif fld.type in ir.enums:
        base = fld.type
    else:
        base = fld.type  # relation to another model
    if fld.list:
        base = f"{base}[]"
    if fld.optional and not fld.list:
        base += "?"
    return base


def _models_ts(ir: SchemaIR) -> str:
    lines = ["// Generated by Overlay Cheetah schema engine (deterministic; zero tokens)."]
    for ename, values in ir.enums.items():
        lines.append(f"export type {ename} = {' | '.join(json.dumps(v) for v in values)};")
    if ir.enums:
        lines.append("")
    for model in ir.models:
        lines.append(f"export interface {model.name} {{")
        for f in model.fields:
            lines.append(f"  {f.name}: {_ts_type(f, ir.enums)};")
        lines.append("}")
        lines.append("")
    return "\n".join(lines)


def _zod_ts(ir: SchemaIR) -> str:
    lines = [
        "// Generated by Overlay Cheetah schema engine (deterministic; zero tokens).",
        'import { z } from "zod";',
        "",
    ]
    for ename, values in ir.enums.items():
        lines.append(f"export const {ename}Schema = z.enum({json.dumps(values)});")
    if ir.enums:
        lines.append("")
    for model in ir.models:
        c = _pascal(model.name)
        fields = [f for f in model.fields if not f.pk]
        entries = [f"  {f.name}: {_zod_expr(f, ir.enums)}," for f in fields]
        lines.append(f"export const {c}CreateSchema = z.object({{")
        lines += entries
        lines.append("});")
        lines.append(f"export const {c}UpdateSchema = {c}CreateSchema.partial();")
        lines.append(f"export const {c}Schema = {c}CreateSchema.extend({{ id: z.string() }});")
        lines.append(f"export type {c} = z.infer<typeof {c}Schema>;")
        lines.append(f"export type {c}Create = z.infer<typeof {c}CreateSchema>;")
        lines.append(f"export type {c}Update = z.infer<typeof {c}UpdateSchema>;")
        lines.append("")
    return "\n".join(lines)


def _store_ts(ir: SchemaIR) -> str:
    lines = [
        "// Generated by Overlay Cheetah schema engine (deterministic in-memory store; zero tokens).",
        "type Row = Record<string, unknown> & { id: string };",
        "",
        "const _tables = new Map<string, Map<string, Row>>();",
        "const _counters = new Map<string, number>();",
        "",
        "function _table(name: string): Map<string, Row> {",
        "  let t = _tables.get(name);",
        "  if (!t) { t = new Map(); _tables.set(name, t); }",
        "  return t;",
        "}",
        "",
        "function _nextId(name: string): string {",
        "  const n = (_counters.get(name) ?? 0) + 1;",
        "  _counters.set(name, n);",
        "  return `${name}_${n}`;",
        "}",
        "",
        "export function list(name: string): Row[] {",
        "  return Array.from(_table(name).values());",
        "}",
        "",
        "export function get(name: string, id: string): Row | undefined {",
        "  return _table(name).get(id);",
        "}",
        "",
        "export function create(name: string, input: Record<string, unknown>): Row {",
        "  const row: Row = { id: _nextId(name), ...input } as Row;",
        "  _table(name).set(row.id, row);",
        "  return row;",
        "}",
        "",
        "export function update(name: string, id: string, patch: Record<string, unknown>): Row | undefined {",
        "  const row = _table(name).get(id);",
        "  if (!row) return undefined;",
        "  const next: Row = { ...row, ...patch, id } as Row;",
        "  _table(name).set(id, next);",
        "  return next;",
        "}",
        "",
        "export function remove(name: string, id: string): boolean {",
        "  return _table(name).delete(id);",
        "}",
        "",
        "export function seed(): void {",
        "  for (const t of _tables.values()) t.clear();",
    ]
    for model in ir.models:
        lname = _camel(model.name)
        lines.append("  for (let i = 1; i <= 2; i++) {")
        fields = [f"      {f.name}: {_seed_value(f, 'i', ir.enums, 'ts')}"
                  for f in model.fields if not f.pk]
        body = ",\n".join(fields)
        lines.append(f"    _table({json.dumps(lname)}).set(`{lname}_${{i}}`, {{ id: `{lname}_${{i}}`,")
        lines.append(body)
        lines.append("    });")
        lines.append("  }")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def _routes_ts(ir: SchemaIR) -> str:
    lines = [
        "// Generated by Overlay Cheetah schema engine (deterministic CRUD; zero tokens).",
        'import type { Express, Request, Response } from "express";',
        'import { list, get, create, update, remove } from "./store";',
    ]
    for model in ir.models:
        c = _pascal(model.name)
        lines.append(f'import {{ {c}CreateSchema, {c}UpdateSchema }} from "./zod";')
    lines.append("")
    lines.append("export function registerRoutes(app: Express): void {")
    lines.append('  app.get("/health", (_req: Request, res: Response) => { res.json({ status: "ok" }); });')
    for model in ir.models:
        c = _pascal(model.name)
        lname = _camel(model.name)
        path = f"/{_plural(lname)}"
        lines.append(f"  app.get({json.dumps(path)}, (_req: Request, res: Response) => {{")
        lines.append(f'    res.json(list({json.dumps(lname)}));')
        lines.append("  });")
        lines.append(f"  app.post({json.dumps(path)}, (req: Request, res: Response) => {{")
        lines.append(f"    const parsed = {c}CreateSchema.safeParse(req.body);")
        lines.append('    if (!parsed.success) { res.status(400).json({ error: parsed.error.flatten() }); return; }')
        lines.append(f'    res.status(201).json(create({json.dumps(lname)}, parsed.data));')
        lines.append("  });")
        lines.append(f"  app.get({json.dumps(path + '/:id')}, (req: Request, res: Response) => {{")
        lines.append(f'    const row = get({json.dumps(lname)}, req.params.id);')
        lines.append('    if (!row) { res.status(404).json({ error: "not found" }); return; }')
        lines.append("    res.json(row);")
        lines.append("  });")
        lines.append(f"  app.put({json.dumps(path + '/:id')}, (req: Request, res: Response) => {{")
        lines.append(f"    const parsed = {c}UpdateSchema.safeParse(req.body);")
        lines.append('    if (!parsed.success) { res.status(400).json({ error: parsed.error.flatten() }); return; }')
        lines.append(f'    const row = update({json.dumps(lname)}, req.params.id, parsed.data);')
        lines.append('    if (!row) { res.status(404).json({ error: "not found" }); return; }')
        lines.append("    res.json(row);")
        lines.append("  });")
        lines.append(f"  app.delete({json.dumps(path + '/:id')}, (req: Request, res: Response) => {{")
        lines.append(f'    if (!remove({json.dumps(lname)}, req.params.id)) {{ res.status(404).json({{ error: "not found" }}); return; }}')
        lines.append("    res.status(204).end();")
        lines.append("  });")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def _app_ts() -> str:
    return (
        'import express from "express";\n'
        'import type { Express } from "express";\n'
        'import { registerRoutes } from "./routes";\n\n'
        "export function createApp(): Express {\n"
        "  const app = express();\n"
        "  app.use(express.json());\n"
        "  registerRoutes(app);\n"
        "  return app;\n"
        "}\n"
    )


def _server_ts() -> str:
    return (
        'import { createApp } from "./app";\n'
        'import type { Express } from "express";\n\n'
        "const app = createApp() as Express;\n"
        "const port = Number(process.env.PORT) || 3000;\n"
        "app.listen(port, () => {\n"
        '  console.log(`api listening on :${port}`);\n'
        "});\n"
    )


def _client_ts(ir: SchemaIR) -> str:
    lines = [
        "// Generated by Overlay Cheetah schema engine (typed fetch client; zero tokens).",
        "type Json = Record<string, unknown>;",
        "",
        "async function _json<T>(res: Response): Promise<T> {",
        "  if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);",
        "  return (res.status === 204 ? undefined : await res.json()) as T;",
        "}",
        "",
        "function _crud<T, C, U>(base: string, path: string) {",
        "  const url = `${base}${path}`;",
        "  return {",
        "    list: async () => _json<T[]>(await fetch(url)),",
        "    get: async (id: string) => _json<T>(await fetch(`${url}/${id}`)),",
        "    create: async (input: C) => _json<T>(await fetch(url, { method: \"POST\",",
        "      headers: { \"Content-Type\": \"application/json\" }, body: JSON.stringify(input) })),",
        "    update: async (id: string, patch: U) => _json<T>(await fetch(`${url}/${id}`, { method: \"PUT\",",
        "      headers: { \"Content-Type\": \"application/json\" }, body: JSON.stringify(patch) })),",
        "    remove: async (id: string) => fetch(`${url}/${id}`, { method: \"DELETE\" }),",
        "  };",
        "}",
        "",
    ]
    for model in ir.models:
        c = _pascal(model.name)
        lines.append(f"import type {{ {c}, {c}Create, {c}Update }} from \"./zod\";")
    lines.append("")
    lines.append("export interface CheetahClient {")
    for model in ir.models:
        c = _pascal(model.name)
        lname = _camel(model.name)
        lines.append(f"  {_plural(lname)}: ReturnType<typeof _crud<{c}, {c}Create, {c}Update>>;")
    lines.append("}")
    lines.append("")
    lines.append("export function createClient(baseUrl: string): CheetahClient {")
    lines.append("  return {")
    for model in ir.models:
        c = _pascal(model.name)
        lname = _camel(model.name)
        lines.append(f"    {_plural(lname)}: _crud<{c}, {c}Create, {c}Update>(baseUrl, {json.dumps('/' + _plural(lname))}),")
    lines.append("  };")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def _openapi_yaml(ir: SchemaIR) -> str:
    lines = [
        "openapi: 3.1.0",
        "info:",
        "  title: Cheetah CRUD API",
        "  version: 0.1.0",
        "paths:",
    ]
    if not ir.models:
        lines.append("  {}:")
        return "\n".join(lines)
    for model in ir.models:
        c = _pascal(model.name)
        lname = _camel(model.name)
        path = f"/{_plural(lname)}"
        lines.append(f"  {path}:")
        lines.append("    get:")
        lines.append(f"      summary: List {_plural(lname)}")
        lines.append("      responses:")
        lines.append("        '200':")
        lines.append("          description: ok")
        lines.append("          content:")
        lines.append("            application/json:")
        lines.append("              schema:")
        lines.append(f"                type: array")
        lines.append(f"                items: {{ $ref: '#/components/schemas/{c}' }}")
        lines.append("    post:")
        lines.append(f"      summary: Create {lname}")
        lines.append("      requestBody:")
        lines.append("        required: true")
        lines.append("        content:")
        lines.append("          application/json:")
        lines.append("            schema:")
        lines.append(f"              $ref: '#/components/schemas/{c}Create'")
        lines.append("      responses:")
        lines.append("        '201':")
        lines.append("          description: created")
        lines.append(f"  {path}/{{id}}:")
        lines.append("    get:")
        lines.append(f"      summary: Get {lname}")
        lines.append("      parameters:")
        lines.append("        - name: id")
        lines.append("          in: path")
        lines.append("          required: true")
        lines.append("          schema: { type: string }")
        lines.append("      responses:")
        lines.append("        '200': { description: ok }")
        lines.append("        '404': { description: not found }")
        lines.append("    put:")
        lines.append(f"      summary: Update {lname}")
        lines.append("      parameters:")
        lines.append("        - name: id")
        lines.append("          in: path")
        lines.append("          required: true")
        lines.append("          schema: { type: string }")
        lines.append("      requestBody:")
        lines.append("        required: true")
        lines.append("        content:")
        lines.append("          application/json:")
        lines.append("            schema:")
        lines.append(f"              $ref: '#/components/schemas/{c}Update'")
        lines.append("      responses:")
        lines.append("        '200': { description: ok }")
        lines.append("        '404': { description: not found }")
        lines.append("    delete:")
        lines.append(f"      summary: Delete {lname}")
        lines.append("      parameters:")
        lines.append("        - name: id")
        lines.append("          in: path")
        lines.append("          required: true")
        lines.append("          schema: { type: string }")
        lines.append("      responses:")
        lines.append("        '204': { description: deleted }")
        lines.append("        '404': { description: not found }")
    lines.append("components:")
    lines.append("  schemas:")
    for model in ir.models:
        c = _pascal(model.name)
        lines.append(f"    {c}:")
        lines.append("      type: object")
        lines.append("      required: [id]")
        lines.append("      properties:")
        for f in model.fields:
            lines.append(f"        {f.name}: {{ type: {_openapi_type(f, ir.enums)} }}")
        lines.append(f"    {c}Create:")
        lines.append("      type: object")
        lines.append("      properties:")
        for f in model.fields:
            if f.pk:
                continue
            lines.append(f"        {f.name}: {{ type: {_openapi_type(f, ir.enums)} }}")
    return "\n".join(lines)


def _openapi_type(fld: Field, enums: Dict[str, List[str]]) -> str:
    if fld.type == "int":
        return "integer"
    if fld.type == "float":
        return "number"
    if fld.type == "bool":
        return "boolean"
    if fld.type == "datetime":
        return "string"
    if fld.type == "uuid":
        return "string"
    if fld.type in enums:
        return "string"
    return "string"


def _routes_test_ts(ir: SchemaIR) -> str:
    lines = [
        "// Generated by Overlay Cheetah schema engine (real integration tests; zero tokens).",
        'import { describe, it, expect, beforeAll, afterAll } from "vitest";',
        'import type { Server } from "node:http";',
        'import { createApp } from "./app";',
        'import { seed } from "./store";',
        "",
        "let server: Server;",
        'let base = "";',
        "",
        'beforeAll(async () => {',
        "  seed();",
        "  server = createApp().listen(0);",
        '  await new Promise((r) => server.once("listening", r));',
        '  const addr = server.address();',
        '  base = `http://127.0.0.1:${typeof addr === "object" && addr ? addr.port : 0}`;',
        "});",
        "",
        'afterAll(() => server?.close());',
        "",
        'describe("crud", () => {',
        '  it("health", async () => {',
        '    const res = await fetch(`${base}/health`);',
        '    expect(res.status).toBe(200);',
        '  });',
    ]
    for model in ir.models:
        c = _pascal(model.name)
        lname = _camel(model.name)
        path = f"/{_plural(lname)}"
        payload = "JSON.stringify({})" if not _sample_payload(model, ir.enums, "ts") \
            else "JSON.stringify({ " + ", ".join(_sample_payload(model, ir.enums, "ts")) + " })"
        lines.append(f'  it("{path} create + list + get + update + delete", async () => {{')
        lines.append(f"    const created = await fetch(`${{base}}{path}`, {{ method: \"POST\",")
        lines.append(f"      headers: {{ \"Content-Type\": \"application/json\" }}, body: {payload} }});")
        lines.append("    expect(created.status).toBe(201);")
        lines.append(f"    const row = (await created.json()) as {{ id: string }};")
        lines.append("    expect(row.id).toBeTruthy();")
        lines.append(f"    const listed = await fetch(`${{base}}{path}`);")
        lines.append("    expect(listed.status).toBe(200);")
        lines.append(f"    const one = await fetch(`${{base}}{path}/${{row.id}}`);")
        lines.append("    expect(one.status).toBe(200);")
        lines.append(f"    const bad = await fetch(`${{base}}{path}/nope`);")
        lines.append("    expect(bad.status).toBe(404);")
        lines.append(f"    const updated = await fetch(`${{base}}{path}/${{row.id}}`, {{ method: \"PUT\",")
        lines.append('      headers: { "Content-Type": "application/json" }, body: JSON.stringify({}) });')
        lines.append("    expect(updated.status).toBe(200);")
        lines.append(f"    const deleted = await fetch(`${{base}}{path}/${{row.id}}`, {{ method: \"DELETE\" }});")
        lines.append("    expect(deleted.status).toBe(204);")
        lines.append("  });")
    lines.append("});")
    lines.append("")
    return "\n".join(lines)


def _express_pkg(name: str, tests: bool) -> str:
    scripts: Dict[str, str] = {
        "dev": "tsx watch src/server.ts",
        "build": "tsc",
        "start": "node dist/server.js",
        "lint": "tsc --noEmit",
        "typecheck": "tsc --noEmit",
    }
    if tests:
        scripts["test"] = "vitest run"
    return json.dumps({
        "name": name,
        "version": "0.1.0",
        "private": True,
        "type": "module",
        "scripts": scripts,
        "dependencies": {"express": "^4.21.2", "zod": "^3.24.1"},
        "devDependencies": {
            "typescript": "~5.8.2",
            "vitest": "^4.1.11",
            "@types/express": "^4.17.21",
            "@types/node": "^22.0.0",
            "tsx": "^4.19.0",
        },
    }, indent=2) + "\n"


# ---------------------------------------------------------------------------
# FastAPI emitters
# ---------------------------------------------------------------------------

def _schemas_py(ir: SchemaIR) -> str:
    lines = [
        "from pydantic import BaseModel",
        "from datetime import datetime",
        "from enum import Enum",
        "",
    ]
    for ename, values in ir.enums.items():
        lines.append(f"class {ename}(str, Enum):")
        for v in values:
            lines.append(f"    {v} = {json.dumps(v)}")
        lines.append("")
    for model in ir.models:
        c = _pascal(model.name)
        lines.append(f"class {c}Create(BaseModel):")
        for f in model.fields:
            if f.pk:
                continue
            typ = _py_type(f, ir.enums)
            if f.optional and not f.list:
                lines.append(f"    {f.name}: {typ} | None = None")
            else:
                lines.append(f"    {f.name}: {typ}")
        lines.append("")
        lines.append(f"class {c}Update(BaseModel):")
        for f in model.fields:
            if f.pk:
                continue
            typ = _py_type(f, ir.enums)
            lines.append(f"    {f.name}: {typ} | None = None")
        lines.append("")
        lines.append(f"class {c}({c}Create):")
        lines.append("    id: str")
        lines.append("")
    return "\n".join(lines)


def _store_py(ir: SchemaIR) -> str:
    lines = [
        '"""Deterministic in-memory store with seeded rows. Zero tokens."""',
        "from __future__ import annotations",
        "from typing import Any",
        "",
        "_tables: dict[str, dict[str, dict[str, Any]]] = {}",
        "_counters: dict[str, int] = {}",
        "",
        "def _table(name: str) -> dict[str, dict[str, Any]]:",
        "    if name not in _tables:",
        "        _tables[name] = {}",
        "    return _tables[name]",
        "",
        "def _next_id(name: str) -> str:",
        "    _counters[name] = _counters.get(name, 0) + 1",
        "    return f'{name}_{_counters[name]}'",
        "",
        "def list_rows(name: str) -> list[dict[str, Any]]:",
        "    return list(_table(name).values())",
        "",
        "def get_row(name: str, row_id: str) -> dict[str, Any] | None:",
        "    return _table(name).get(row_id)",
        "",
        "def create_row(name: str, payload: dict[str, Any]) -> dict[str, Any]:",
        "    row: dict[str, Any] = {'id': _next_id(name), **payload}",
        "    _table(name)[row['id']] = row",
        "    return row",
        "",
        "def update_row(name: str, row_id: str, patch: dict[str, Any]) -> dict[str, Any] | None:",
        "    row = _table(name).get(row_id)",
        "    if row is None:",
        "        return None",
        "    merged = {**row, **patch, 'id': row_id}",
        "    _table(name)[row_id] = merged",
        "    return merged",
        "",
        "def delete_row(name: str, row_id: str) -> bool:",
        "    return _table(name).pop(row_id, None) is not None",
        "",
        "def seed() -> None:",
        "    for t in _tables.values():",
        "        t.clear()",
    ]
    for model in ir.models:
        lname = _camel(model.name)
        lines.append("    for i in (1, 2):")
        fields = [f"            '{f.name}': {_seed_value(f, 'i', ir.enums, 'py')}"
                  for f in model.fields if not f.pk]
        lines.append(f"        _table({json.dumps(lname)})[f'{lname}_{{i}}'] = {{'id': f'{lname}_{{i}}',")
        lines.append(",\n".join(fields))
        lines.append("        }")
    lines.append("")
    return "\n".join(lines)


def _routes_py(ir: SchemaIR) -> str:
    lines = [
        "from fastapi import APIRouter, HTTPException",
        "from . import schemas",
        "from .store import list_rows, get_row, create_row, update_row, delete_row, seed",
        "",
        "api = APIRouter()",
        "",
        "def _payload(row):",
        "    return {k: v for k, v in row.items()}",
        "",
    ]
    for model in ir.models:
        c = _pascal(model.name)
        lname = _camel(model.name)
        path = f"/{_plural(lname)}"
        mid = f"{lname}_id"
        dynamic = path + "/{" + mid + "}"
        lines.append(f"@api.get({json.dumps(path)})")
        lines.append(f"def list_{lname}() -> list[schemas.{c}]:")
        lines.append(f"    return [_payload(r) for r in list_rows({json.dumps(lname)})]")
        lines.append("")
        lines.append(f"@api.post({json.dumps(path)}, status_code=201)")
        lines.append(f"def create_{lname}(payload: schemas.{c}Create) -> schemas.{c}:")
        lines.append(f"    return create_row({json.dumps(lname)}, payload.model_dump())")
        lines.append("")
        lines.append(f"@api.get({json.dumps(dynamic)})")
        lines.append(f"def get_{lname}({mid}: str) -> schemas.{c}:")
        lines.append(f"    row = get_row({json.dumps(lname)}, {mid})")
        lines.append(f"    if row is None:")
        lines.append("        raise HTTPException(status_code=404, detail='not found')")
        lines.append("    return _payload(row)")
        lines.append("")
        lines.append(f"@api.put({json.dumps(dynamic)})")
        lines.append(f"def update_{lname}({mid}: str, payload: schemas.{c}Update) -> schemas.{c}:")
        lines.append(f"    row = update_row({json.dumps(lname)}, {mid}, payload.model_dump(exclude_none=True))")
        lines.append("    if row is None:")
        lines.append("        raise HTTPException(status_code=404, detail='not found')")
        lines.append("    return _payload(row)")
        lines.append("")
        lines.append(f"@api.delete({json.dumps(dynamic)}, status_code=204)")
        lines.append(f"def delete_{lname}({mid}: str) -> None:")
        lines.append(f"    if not delete_row({json.dumps(lname)}, {mid}):")
        lines.append("        raise HTTPException(status_code=404, detail='not found')")
        lines.append("")
    return "\n".join(lines)


def _main_py() -> str:
    return (
        "from fastapi import FastAPI\n"
        "from .routes import api\n\n"
        "app = FastAPI()\n"
        "app.include_router(api)\n\n\n"
        "@app.get('/health')\n"
        "def health():\n"
        "    return {'status': 'ok'}\n"
    )


def _test_api_py(ir: SchemaIR) -> str:
    lines = [
        "from fastapi.testclient import TestClient",
        "from app.main import app",
        "from app.store import seed",
        "",
        "client = TestClient(app)",
        "",
        "def setup_function():\n    seed()\n",
        "",
        "def test_health():\n    assert client.get('/health').status_code == 200\n",
    ]
    for model in ir.models:
        c = _pascal(model.name)
        lname = _camel(model.name)
        path = f"/{_plural(lname)}"
        payload = "{}" if not _sample_payload(model, ir.enums, "py") \
            else "{" + ", ".join(_sample_payload(model, ir.enums, "py")) + "}"
        lines.append(f"def test_{lname}_crud():")
        lines.append(f"    created = client.post({json.dumps(path)}, json={payload})")
        lines.append("    assert created.status_code == 201")
        lines.append("    row = created.json()")
        lines.append("    assert row['id']")
        lines.append(f"    assert client.get({json.dumps(path)}).status_code == 200")
        lines.append(f"    assert client.get({json.dumps(path + '/' + lname + '_1')}).status_code == 200")
        lines.append(f"    assert client.get({json.dumps(path + '/missing')}).status_code == 404")
        lines.append(f"    assert client.put({json.dumps(path + '/' + lname + '_1')}, json={{}}).status_code == 200")
        lines.append(f"    assert client.delete({json.dumps(path + '/' + lname + '_1')}).status_code == 204")
        lines.append("")
    return "\n".join(lines)


def _fastapi_requirements(tests: bool) -> str:
    reqs = "fastapi>=0.111\nuvicorn>=0.30\npydantic>=2.7\n"
    if tests:
        reqs += "pytest>=8\nhttpx>=0.27\n"
    return reqs


def _pyproject(tests: bool) -> str:
    if not tests:
        return ""
    return '[tool.pytest.ini_options]\npythonpath = ["."]\ntestpaths = ["tests"]\n'


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_crud_plan(goal: str, schema_text: str, framework: str = "express",
                    name: Optional[str] = None, tests: bool = True) -> Dict[str, Any]:
    """Generate a deterministic, runnable CRUD plan from the entity DSL."""
    if framework not in FRAMEWORKS:
        return {"ok": False, "shape": "crud-api", "error": f"framework must be one of {list(FRAMEWORKS)}"}
    try:
        ir = parse_schema(schema_text)
    except ValueError as exc:
        return {"ok": False, "shape": "crud-api", "error": f"schema parse failed: {exc}"}

    resolved_name = (name or (re.search(r"\b(?:called|named)\s+[\"']?([A-Za-z][A-Za-z0-9_-]{1,30})", goal or "", re.I)
                      .group(1) if re.search(r"\b(?:called|named)\s+[\"']?([A-Za-z][A-Za-z0-9_-]{1,30})", goal or "", re.I) else "crud-app"))
    resolved_name = str(resolved_name).replace(" ", "-").lower()[:40]

    files: List[Dict[str, str]] = []
    manifest: List[str] = []
    notes: List[str] = [
        f"{len(ir.models)} model(s), {len(ir.enums)} enum(s) parsed deterministically.",
        "Relations are stored as plain pk references (no join semantics invented).",
        "Seeds are deterministic (field name + counter) — never random.",
    ]

    def add(path: str, rendered: str) -> None:
        files.append({"output": path, "rendered": rendered})
        manifest.append(path)

    add("cheetah.schema", schema_text.strip() + "\n")
    add(".gitignore", _GITIGNORE)
    add("README.md",
        f"# {resolved_name}\n\nCRUD API generated by Overlay Cheetah schema engine "
        f"(deterministic; zero LLM tokens). Framework: {framework}.\n\n"
        f"Goal: {(goal or '').strip()[:300]}\n\nModels: {', '.join(m.name for m in ir.models)}\n")

    if framework == "express":
        add("package.json", _express_pkg(resolved_name, tests))
        add("tsconfig.json", _TSCONFIG_CRUD)
        add("vitest.config.ts", _VITEST_CFG)
        add("prisma/schema.prisma", _prisma_schema(ir))
        add("src/models.ts", _models_ts(ir))
        add("src/zod.ts", _zod_ts(ir))
        add("src/store.ts", _store_ts(ir))
        add("src/app.ts", _app_ts())
        add("src/server.ts", _server_ts())
        add("src/routes.ts", _routes_ts(ir))
        add("src/client.ts", _client_ts(ir))
        add("src/openapi.yaml", _openapi_yaml(ir))
        if tests:
            add("src/routes.test.ts", _routes_test_ts(ir))
        notes.append("Express: build → tsc, run → node dist/server.js, test → vitest run. "
                     "DB-ready: prisma/schema.prisma is the migration source of truth.")
    else:  # fastapi
        add("requirements.txt", _fastapi_requirements(tests))
        add("pyproject.toml", _pyproject(tests))
        add("app/__init__.py", "")
        add("app/schemas.py", _schemas_py(ir))
        add("app/store.py", _store_py(ir))
        add("app/routes.py", _routes_py(ir))
        add("app/main.py", _main_py())
        if tests:
            add("tests/test_api.py", _test_api_py(ir))
        notes.append("FastAPI: uvicorn app.main:app --reload, test → pytest. "
                     "In-memory store; swap store.py for a real DB when ready.")

    # The manifest is emitted last: it lists every generated path and is the
    # source of truth the `drift` verify gate diffs against. goal/name/framework
    # are recorded so a regeneration reproduces byte-identical files.
    manifest_rendered = json.dumps({
        "engine": VERSION,
        "framework": framework,
        "goal": (goal or "").strip()[:300],
        "name": resolved_name,
        "generated": manifest,
    }, indent=2) + "\n"
    files.append({"output": "cheetah.manifest.json", "rendered": manifest_rendered})

    return {
        "ok": True,
        "shape": "crud-api",
        "framework": framework,
        "name": resolved_name,
        "models": [m.name for m in ir.models],
        "enums": list(ir.enums.keys()),
        "files": files,
        "manifest": manifest,
        "notes": notes,
    }


def crud_plan_for_goal(goal: str, schema_text: str, framework: str = "express",
                       name: Optional[str] = None) -> Dict[str, Any]:
    return build_crud_plan(goal, schema_text, framework=framework, name=name)


def wants_crud(goal: str) -> bool:
    """Heuristic: does the goal describe a data-driven API? Used by detect_shape."""
    return bool(_CRUD_HINT.search(goal or ""))