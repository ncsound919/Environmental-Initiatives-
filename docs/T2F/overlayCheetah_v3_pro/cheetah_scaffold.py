"""Deterministic project scaffolder for Overlay Cheetah V3 Pro+.

Purpose: produce real boilerplate so a coding harness (Axiom) can generate
`files[].rendered` for `/generate` and `/scaffold`, let the model fill only the
logic, and cut output tokens. Zero LLM calls.

Design rules:
  - Deterministic: the same goal always yields the same shape, name, exports,
    and file contents. No clock, no randomness.
  - Fail-closed stubs: every required export is emitted as a stub that raises
    "NOT IMPLEMENTED", and the scaffold's own test asserts the stub is gone.
    This makes it impossible for a verify gate to pass on un-implemented code.
  - Bounded: a fixed, small file set per shape.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from cheetah_fixes import apply_fixes

IMPL_MARK = "NOT IMPLEMENTED"

SHAPES = (
    "node-lib",
    "node-cli",
    "express-api",
    "react-vite",
    "python-pkg",
    "fastapi-service",
    "full-stack",
    "crud-api",
    "generic",
)

_SHAPE_HINTS = (
    ("full-stack", r"\b(full[ -]stack|frontend and backend|spa and api|web app with (an )?api|monorepo)\b"),
    ("crud-api", r"\b(crud( api)?|postgres|sqlite|database schema|data model|entities)\b|\b(storage|persist|repository)\b"),
    ("react-vite", r"\b(react|vite|frontend|front-end|ui\b|component|spa)\b"),
    ("express-api", r"\b(express|rest api|restful|http server|api server|endpoint|route[s]?)\b"),
    ("fastapi-service", r"\b(fastapi|uvicorn)\b"),
    ("node-cli", r"\b(cli|command[- ]line|argv|terminal tool)\b"),
    ("python-pkg", r"\b(python|pyproject|pip|package)\b"),
    ("node-lib", r"\b(lib|library|module|npm|node|typescript)\b"),
)

_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_PATH_NAME = re.compile(r"(?:[\w./-]*/)?([A-Za-z_][A-Za-z0-9_-]*)\.[A-Za-z]+")


def detect_shape(goal: str, requested: Optional[str] = None) -> str:
    if requested in SHAPES:
        return requested
    text = (goal or "").lower()
    for shape, pattern in _SHAPE_HINTS:
        if re.search(pattern, text):
            return shape
    return "node-lib"


def project_name(goal: str, fallback: str = "app") -> str:
    text = goal or ""
    # Prefer an explicit path in the goal: lib/math.js, src/strings.ts, cli.js
    for m in _PATH_NAME.finditer(text):
        cand = m.group(1)
        if cand.lower() in ("index", "main", "app", "lib", "src"):
            continue
        return cand.lower()
    # "called foo" / "named foo" / "a tool that ..." -> first significant word
    m = re.search(r"\b(?:called|named)\s+[\"']?([A-Za-z][A-Za-z0-9_-]{1,30})", text, re.I)
    if m:
        return m.group(1).lower()
    words = re.findall(r"[A-Za-z][A-Za-z0-9]{2,}", text)
    stop = {"create", "build", "make", "write", "tool", "with", "that", "using", "tests", "test", "pass", "all", "and", "the"}
    for w in words:
        if w.lower() not in stop:
            return w.lower()[:24]
    return fallback


def goal_exports(goal: str, limit: int = 8) -> List[str]:
    """Extract export names the goal names (e.g. 'exporting add, sub and mul')."""
    text = goal or ""
    found: List[str] = []
    _KW = {"if", "for", "while", "return", "test", "tests", "describe", "it", "and", "with"}

    def add(name: str) -> None:
        if _IDENT.match(name) and name.lower() not in _KW and name not in found:
            found.append(name)

    # Pass 1 — call-shaped names after an export keyword: `exporting add(a,b), sub(x)`
    for m in re.finditer(r"\b(?:export(?:ing|s)?|functions?|methods?)\s+([^.;]+)", text, re.I):
        for call in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", m.group(1)):
            add(call.group(1))

    # Pass 2 — bare identifier lists after an export keyword: `exporting add, sub and mul`
    if not found:
        for m in re.finditer(
            r"\bexport(?:ing|s)?\s+([A-Za-z_][A-Za-z0-9_]*(?:\s*(?:,|\band\b)\s*[A-Za-z_][A-Za-z0-9_]*)+)",
            text,
            re.I,
        ):
            for tok in re.split(r",|\band\b", m.group(1)):
                add(tok.strip())

    # Pass 3 — last resort: explicit `name(...)` call shapes anywhere in the goal
    if not found:
        for m in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\([^)]*\)", text):
            add(m.group(1))
    # Drop language keywords that are never exports
    found = [f for f in found if f not in ("if", "for", "while", "return", "test", "describe", "it")]
    return found[:limit]


def _pkg_json(name: str, shape: str, deps: Dict[str, str], scripts: Dict[str, str], extra: Optional[Dict[str, Any]] = None) -> str:
    import json

    body: Dict[str, Any] = {
        "name": name,
        "version": "0.1.0",
        "private": True,
        "type": "module",
        "scripts": scripts,
        **({"dependencies": deps} if shape in ("express-api",) else {}),
        "devDependencies": deps if shape not in ("express-api",) else {"vitest": "^4.1.11", "typescript": "~5.8.2"},
    }
    if extra:
        body.update(extra)
    return json.dumps(body, indent=2) + "\n"


_TS_TSCONFIG = """{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "skipLibCheck": true,
    "noEmit": true
  },
  "include": ["src"]
}
"""


def _tsconfig(strict: bool) -> str:
    return _TS_TSCONFIG.replace('"strict": true', f'"strict": {str(strict).lower()}')


def _tsconfig_emit(strict: bool) -> str:
    """Emit-capable tsconfig for an API service (builds to dist/)."""
    return f"""{{
  "compilerOptions": {{
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": {str(strict).lower()},
    "outDir": "dist",
    "rootDir": "src",
    "skipLibCheck": true
  }},
  "include": ["src"]
}}
"""


def _server_entry() -> str:
    """Thin deterministic Express entry that wires the scaffolded stubs. The
    stubs throw NOT IMPLEMENTED until the model fills them, so a verify gate
    can never pass on an un-implemented app; until then `node dist/server.js`
    fails closed exactly like the module stubs."""
    return (
        'import { createApp } from "./app";\n'
        'import { registerRoutes } from "./routes";\n'
        'import type { Express } from "express";\n\n'
        "const app = createApp() as Express;\n"
        "registerRoutes(app);\n\n"
        "const port = Number(process.env.PORT) || 3000;\n"
        "app.listen(port, () => {\n"
        '  console.log(`api listening on :${port}`);\n'
        "});\n"
    )

_VITEST_CFG = """import { defineConfig } from "vitest/config";

export default defineConfig({ test: { environment: "node" } });
"""

_GITIGNORE = "node_modules/\ndist/\ncoverage/\n*.log\n__pycache__/\n.venv/\n"


def _ts_stubs(exports: List[str]) -> str:
    if not exports:
        return 'export const ready = true;\n'
    lines = []
    for name in exports:
        lines.append(f"export function {name}(...args: unknown[]): unknown {{")
        lines.append(f'  throw new Error("{IMPL_MARK}");')
        lines.append("}")
    return "\n".join(lines) + "\n"


def _ts_impl_tests(exports: List[str], rel: str) -> str:
    if not exports:
        return 'import { describe, it, expect } from "vitest";\n\ndescribe("smoke", () => {\n  it("loads", () => { expect(true).toBe(true); });\n});\n'
    entry = "./" + rel.split("/")[-1].replace(".ts", "")
    names = ", ".join(exports)
    cases = "\n".join(
        f'  it("implements {n}", () => {{ expect(String({n})).not.toContain("{IMPL_MARK}"); }});'
        for n in exports
    )
    return (
        "// Scaffolded implementation guard: fails while the stub is un-implemented.\n"
        f'import {{ describe, it, expect }} from "vitest";\nimport {{ {names} }} from "{entry}";\n\n'
        f'describe("implementation", () => {{\n{cases}\n}});\n'
    )


def _react_impl_test() -> str:
    return (
        "// Scaffolded implementation guard: fails while the App stub is un-implemented.\n"
        'import { describe, it, expect } from "vitest";\n'
        'import App from "./App";\n\n'
        'describe("App", () => {\n'
        f'  it("implements App", () => {{ expect(String(App)).not.toContain("{IMPL_MARK}"); }});\n'
        "});\n"
    )


def _py_stub_module(exports: List[str]) -> str:
    if not exports:
        return 'def ready() -> bool:\n    return True\n'
    lines = []
    for name in exports:
        lines.append(f"def {name}(*args, **kwargs):")
        lines.append(f'    raise NotImplementedError("{IMPL_MARK}")')
        lines.append("")
    return "\n".join(lines)


def _py_impl_tests(pkg: str, exports: List[str]) -> str:
    names = ", ".join(exports) if exports else "ready"
    cases = "\n".join(
        f'def test_{n}_implemented():\n    assert "{IMPL_MARK}" not in inspect.getsource({n})\n'
        for n in (exports or ["ready"])
    )
    return f"import inspect\nfrom {pkg} import {names}\n\n\n{cases}"


def build_scaffold(goal: str, name: Optional[str] = None, shape: Optional[str] = None,
                   strict: bool = True, tests: bool = True,
                   schema: Optional[str] = None) -> Dict[str, Any]:
    """Build a deterministic scaffold plan. Returns {shape, name, exports, files, notes}.

    ``strict`` pins strict TypeScript in tsconfig (TS shapes only).
    ``tests`` emits the implementation-guard test files + test scripts.
    ``schema`` (entity DSL) upgrades the ``crud-api`` shape into a runnable
    CRUD API via cheetah_schema (real routes + zod + store + seeds + tests).
    Defaults preserve the historical output exactly.
    """
    resolved_shape = detect_shape(goal, shape)
    resolved_name = (name or project_name(goal)).replace(" ", "-").lower()
    exports = goal_exports(goal)
    files: List[Dict[str, str]] = []
    notes: List[str] = []

    def add(path: str, rendered: str) -> None:
        files.append({"output": path, "rendered": rendered})

    add(".gitignore", _GITIGNORE)
    add("README.md", f"# {resolved_name}\n\nScaffolded by Overlay Cheetah V3 Pro+ (deterministic; zero LLM tokens).\n\nGoal: {goal.strip()[:300]}\n")

    if resolved_shape == "node-lib":
        scripts = {"lint": "tsc --noEmit"}
        if tests:
            scripts["test"] = "vitest run"
        add("package.json", _pkg_json(resolved_name, resolved_shape, {"vitest": "^4.1.11", "typescript": "~5.8.2"}, scripts))
        add("tsconfig.json", _tsconfig(strict))
        add("vitest.config.ts", _VITEST_CFG)
        add("src/index.ts", _ts_stubs(exports))
        if tests:
            add("src/index.test.ts", _ts_impl_tests(exports, "src/index.ts"))
    elif resolved_shape == "node-cli":
        cli_exports = list(exports)
        if "main" not in cli_exports:
            cli_exports.append("main")
        scripts = {"lint": "tsc --noEmit"}
        if tests:
            scripts["test"] = "vitest run"
        add("package.json", _pkg_json(resolved_name, resolved_shape, {"vitest": "^4.1.11", "typescript": "~5.8.2"}, scripts, {"bin": {resolved_name: "src/cli.ts"}}))
        add("tsconfig.json", _tsconfig(strict))
        add("vitest.config.ts", _VITEST_CFG)
        add("src/cli.ts", _ts_stubs(cli_exports))
        if tests:
            add("src/cli.test.ts", _ts_impl_tests(cli_exports, "src/cli.ts"))
    elif resolved_shape == "express-api":
        route_exports = exports or ["registerRoutes"]
        scripts = {"lint": "tsc --noEmit", "build": "tsc", "start": "node dist/server.js"}
        if tests:
            scripts["test"] = "vitest run"
        add("package.json", _pkg_json(resolved_name, resolved_shape, {"express": "^4.21.2"}, scripts,
                                       {"devDependencies": {"vitest": "^4.1.11", "typescript": "~5.8.2",
                                                            "@types/express": "^4.17.21", "@types/node": "^22.0.0"}}))
        add("tsconfig.json", _tsconfig_emit(strict))
        add("vitest.config.ts", _VITEST_CFG)
        add("src/routes.ts", _ts_stubs(route_exports))
        if tests:
            add("src/routes.test.ts", _ts_impl_tests(route_exports, "src/routes.ts"))
        add("src/app.ts", _ts_stubs(["createApp"]))
        add("src/server.ts", _server_entry())
        if tests:
            add("src/app.test.ts", _ts_impl_tests(["createApp"], "src/app.ts"))
        notes.append("Express scaffold: createApp() must return an express app; registerRoutes(app) wires endpoints; server.ts is the entry (build: tsc → dist).")
    elif resolved_shape == "react-vite":
        scripts = {"lint": "tsc --noEmit", "dev": "vite"}
        if tests:
            scripts["test"] = "vitest run"
        add("package.json", _pkg_json(resolved_name, resolved_shape, {"vitest": "^4.1.11", "typescript": "~5.8.2"}, scripts, {"dependencies": {"react": "^19.0.1", "react-dom": "^19.0.1"}}))
        add("tsconfig.json", _tsconfig(strict).replace('"include": ["src"]', '"include": ["src"], "jsx": "react-jsx"'))
        add("vite.config.ts", 'import { defineConfig } from "vite";\nimport react from "@vitejs/plugin-react";\n\nexport default defineConfig({ plugins: [react()] });\n')
        add("index.html", f'<!doctype html>\n<html lang="en">\n  <head><meta charset="utf-8" /><title>{resolved_name}</title></head>\n  <body><div id="root"></div><script type="module" src="/src/main.tsx"></script></body>\n</html>\n')
        add("src/App.tsx", f'export default function App() {{\n  throw new Error("{IMPL_MARK}");\n}}\n')
        add("src/main.tsx", "import React from \"react\";\nimport { createRoot } from \"react-dom/client\";\nimport App from \"./App\";\n\ncreateRoot(document.getElementById(\"root\")!).render(<App />);\n")
        if tests:
            add("src/App.test.ts", _react_impl_test())
    elif resolved_shape == "full-stack":
        route_exports = exports or ["registerRoutes"]
        import json as _json

        add("package.json", _json.dumps({
            "name": resolved_name,
            "version": "0.1.0",
            "private": True,
            "type": "module",
            "workspaces": ["web", "api"],
            "scripts": {
                "dev": "npm run dev --workspace=web",
                "build": "npm run build --workspaces --if-present",
                "test": "npm run test --workspaces --if-present",
                "lint": "npm run lint --workspaces --if-present",
                "typecheck": "npm run typecheck --workspaces --if-present",
            },
        }, indent=2) + "\n")
        add("README.md", f"# {resolved_name}\n\nFull-stack monorepo scaffolded by Overlay Cheetah V3 Pro+ (deterministic; zero LLM tokens).\n\n- `web/` React 19 + Vite frontend\n- `api/` Express backend\n\nGoal: {goal.strip()[:300]}\n")
        add(".gitignore", _GITIGNORE)
        web_scripts = {"dev": "vite", "build": "tsc --noEmit && vite build",
                       "lint": "tsc --noEmit", "typecheck": "tsc --noEmit"}
        if tests:
            web_scripts["test"] = "vitest run"
        add("web/package.json", _json.dumps({
            "name": f"{resolved_name}-web",
            "version": "0.1.0",
            "private": True,
            "type": "module",
            "scripts": web_scripts,
            "dependencies": {"react": "^19.0.1", "react-dom": "^19.0.1"},
            "devDependencies": {"@vitejs/plugin-react": "^4.3.1", "typescript": "~5.8.2",
                                "vite": "^6.0.0", "vitest": "^4.1.11"},
        }, indent=2) + "\n")
        add("web/tsconfig.json", _tsconfig(strict).replace('"include": ["src"]', '"include": ["src"], "jsx": "react-jsx"'))
        add("web/vite.config.ts", 'import { defineConfig } from "vite";\nimport react from "@vitejs/plugin-react";\n\nexport default defineConfig({ plugins: [react()] });\n')
        add("web/index.html", f'<!doctype html>\n<html lang="en">\n  <head><meta charset="utf-8" /><title>{resolved_name}</title></head>\n  <body><div id="root"></div><script type="module" src="/src/main.tsx"></script></body>\n</html>\n')
        add("web/src/main.tsx", "import React from \"react\";\nimport { createRoot } from \"react-dom/client\";\nimport App from \"./App\";\n\ncreateRoot(document.getElementById(\"root\")!).render(<App />);\n")
        add("web/src/App.tsx", f'export default function App() {{\n  throw new Error("{IMPL_MARK}");\n}}\n')
        if tests:
            add("web/src/App.test.ts", _react_impl_test())
        api_scripts = {"dev": "node dist/server.js", "build": "tsc",
                       "lint": "tsc --noEmit", "typecheck": "tsc --noEmit",
                       "start": "node dist/server.js"}
        if tests:
            api_scripts["test"] = "vitest run"
        add("api/package.json", _json.dumps({
            "name": f"{resolved_name}-api",
            "version": "0.1.0",
            "private": True,
            "type": "module",
            "scripts": api_scripts,
            "dependencies": {"express": "^4.21.2"},
            "devDependencies": {"@types/express": "^4.17.21", "@types/node": "^22.0.0",
                                "typescript": "~5.8.2", "vitest": "^4.1.11"},
        }, indent=2) + "\n")
        add("api/tsconfig.json", _tsconfig_emit(strict))
        add("api/vitest.config.ts", _VITEST_CFG)
        add("api/src/app.ts", _ts_stubs(["createApp"]))
        add("api/src/routes.ts", _ts_stubs(route_exports))
        add("api/src/server.ts", _server_entry())
        if tests:
            add("api/src/app.test.ts", _ts_impl_tests(["createApp"], "api/src/app.ts"))
            add("api/src/routes.test.ts", _ts_impl_tests(route_exports, "api/src/routes.ts"))
        notes.append("Full-stack scaffold: web/ (React+Vite) and api/ (Express) workspaces; App.tsx/createApp()/registerRoutes() must be implemented.")
    elif resolved_shape == "crud-api":
        from cheetah_schema import build_crud_plan
        if schema:
            sub = build_crud_plan(goal, schema, framework="express",
                                  name=resolved_name, tests=tests)
            if sub.get("ok"):
                files = sub["files"]
                exports = sub["models"]
                notes.extend(sub["notes"])
            else:
                add("NOTES.md", f"# {resolved_name}\n\ncrud-api could not be generated:\n\n{sub.get('error')}\n\nSchema:\n\n{schema.strip()[:500]}\n")
                notes.append(f"crud-api schema rejected: {sub.get('error')}")
        else:
            add("NOTES.md", f"# {resolved_name}\n\ncrud-api requires an entity DSL schema.\n\nPass schema text to build_scaffold (or POST /schema with `schema`), e.g.:\n\n    entity User {{\n      id string pk\n      email string unique\n    }}\n\nGoal: {goal.strip()[:300]}\n")
            notes.append("crud-api needs a schema: no runnable API was generated (honest — nothing inferred).")
    elif resolved_shape == "fastapi-service":
        requirements = "fastapi>=0.111\nuvicorn>=0.30" + ("\npytest>=8\n" if tests else "\n")
        add("requirements.txt", requirements)
        if tests:
            add("pyproject.toml", '[tool.pytest.ini_options]\npythonpath = ["."]\ntestpaths = ["tests"]\n')
        add("app/main.py", f'from fastapi import FastAPI\n\napp = FastAPI()\n\n\n@app.get("/health")\ndef health():\n    return {{"status": "ok"}}\n\n\ndef handle(*args, **kwargs):\n    raise NotImplementedError("{IMPL_MARK}")\n')
        if tests:
            add("tests/test_main.py", "import inspect\nfrom app.main import handle\n\n\ndef test_handle_implemented():\n    assert \"NOT IMPLEMENTED\" not in inspect.getsource(handle)\n")
        notes.append("FastAPI scaffold: app/main.py exposes /health and a handle() stub.")
    elif resolved_shape == "python-pkg":
        safe_pkg = re.sub(r"[^a-z0-9_]", "_", resolved_name) or "pkg"
        proj = f'[project]\nname = "{resolved_name}"\nversion = "0.1.0"\nrequires-python = ">=3.10"\n'
        if tests:
            proj += '\n[tool.pytest.ini_options]\npythonpath = ["src"]\ntestpaths = ["tests"]\n'
        add("pyproject.toml", proj)
        add(f"src/{safe_pkg}/__init__.py", _py_stub_module(exports))
        if tests:
            add(f"tests/test_{safe_pkg}.py", _py_impl_tests(safe_pkg, exports))
        notes.append(f"Python package: `from {safe_pkg} import ...` (src layout).")
    else:  # generic
        add("NOTES.md", f"# {resolved_name}\n\nNo shape-specific scaffold was detected. Goal:\n\n{goal.strip()[:500]}\n")
        notes.append("Generic scaffold: no runnable envelope was inferred from the goal.")

    return {"shape": resolved_shape, "name": resolved_name, "exports": exports, "files": files, "notes": notes}


def scaffold_plan_for_goal(goal: str, name: Optional[str] = None, shape: Optional[str] = None,
                           schema: Optional[str] = None) -> Dict[str, Any]:
    return build_scaffold(goal, name=name, shape=shape, schema=schema)


# ---------------------------------------------------------------------------
# Toolchain-backed bootstrap (Module 4)
#
# When the network + real CLI tooling exist, the richest deterministic output
# comes from the ecosystem's own scaffolds (create-vite, shadcn init, ...).
# Cheetah wraps those non-interactive runs, then aligns the result with
# plan_fixes so the verify gates still pass. When the tool is not available the
# status is an honest SKIP — Cheetah never pretends it scaffolded something.
# ---------------------------------------------------------------------------

_BOOTSTRAP_COMMANDS: Dict[str, List[str]] = {
    "react-vite": ["npm", "create", "vite@latest", "{name}", "--", "--template", "react-ts"],
    "full-stack": ["npm", "create", "vite@latest", "web", "--", "--template", "react-ts"],
    "node-cli": ["npm", "init", "-y"],
    "node-lib": ["npm", "init", "-y"],
}


def _bootstrap_notes(shape: str) -> List[str]:
    notes = {
        "react-vite": "Bootstrap: create-vite react-ts, then Cheetah fixes aligned scripts/devDeps.",
        "full-stack": "Bootstrap: create-vite web/ only; api/ still uses the deterministic scaffold.",
        "node-cli": "Bootstrap: npm init -y baseline only.",
        "node-lib": "Bootstrap: npm init -y baseline only.",
    }
    return [notes[shape]] if shape in notes else []


def bootstrap_scaffold(root: str, shape: str, name: str = "app",
                       timeout_sec: float = 120.0) -> Dict[str, Any]:
    """Shell out to a real scaffolder (non-interactive) when available.

    Honest statuses: DONE (tool ran, fixes applied), SKIP (no tool / offline),
    ERROR (tool present but failed). Never fakes a scaffold.
    """
    base = Path(root).resolve()
    base.mkdir(parents=True, exist_ok=True)
    cmd = _BOOTSTRAP_COMMANDS.get(shape)
    if cmd is None:
        return {"ok": True, "status": "SKIP",
                "detail": f"no bootstrap tool mapped for shape {shape!r} (deterministic scaffold used instead)",
                "notes": []}
    command = [c.replace("{name}", name) for c in cmd]
    try:
        proc = subprocess.run(command, cwd=str(base), capture_output=True,
                              text=True, timeout=timeout_sec)
    except FileNotFoundError:
        return {"ok": True, "status": "SKIP",
                "detail": f"bootstrap command not available on this host: {command[0]} (offline/honest)",
                "notes": []}
    except subprocess.TimeoutExpired:
        return {"ok": False, "status": "ERROR",
                "detail": f"bootstrap exceeded {int(timeout_sec)}s", "notes": []}
    tail = (proc.stdout + "\n" + proc.stderr)[-2000:]
    if proc.returncode != 0:
        return {"ok": False, "status": "ERROR",
                "detail": f"bootstrap failed (exit={proc.returncode})", "output_tail": tail,
                "notes": []}
    fixes = apply_fixes(str(base))
    return {"ok": True, "status": "DONE", "detail": f"scaffolded via {' '.join(command)}",
            "output_tail": tail, "written": fixes.get("written", []),
            "notes": _bootstrap_notes(shape)}
