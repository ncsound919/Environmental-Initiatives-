"""Deterministic test-skeleton synthesis — zero tokens.

Beyond the exports-only smoke net, this derives a per-function skeleton from the
*actual signatures* in the entry file and lists boundary inputs for each
parameter. It is intentionally honest: the emitted file asserts the implementation
guard and the callable shape, and carries a commented boundary table for the
model to turn into real assertions. It never invents expected values.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

IMPL_MARK = "NOT IMPLEMENTED"

_TS_SIG = re.compile(r"export\s+(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(([^)]*)\)")
_TS_ARROW = re.compile(r"export\s+const\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*=>")
_PY_SIG = re.compile(r"^def\s+([A-Za-z_][\w]*)\s*\(([^)]*)\)", re.M)

_BOUNDARY = (
    (r"num|count|size|len|index|idx|n\b|amount|qty|total", "0, 1, -1"),
    (r"text|str|s\b|name|word|label|message|id\b", '"", "a", "ab"'),
    (r"arr|array|nums|list|items|values|xs", "[] , [1]"),
    (r"flag|bool|enabled|is[A-Z]", "true, false"),
)


def parse_signatures(source: str, lang: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen = set()
    patterns = [_TS_SIG, _TS_ARROW] if lang == "ts" else [_PY_SIG]
    for pat in patterns:
        for m in pat.finditer(source or ""):
            name, raw_params = m.group(1), m.group(2)
            if name in seen:
                continue
            seen.add(name)
            params = [p.strip().split(":")[0].split("=")[0].strip() for p in raw_params.split(",") if p.strip()]
            out.append({"name": name, "params": [p for p in params if p and p not in ("self", "args", "kwargs")]})
    return out


def _boundary_for(param: str) -> str:
    for pat, vals in _BOUNDARY:
        if re.search(pat, param, re.I):
            return vals
    return "undefined (or a representative value)"


def synth_tests(source: str, entry_rel: str) -> Dict[str, Any]:
    lang = "py" if entry_rel.endswith(".py") else "ts"
    sigs = parse_signatures(source, lang)
    names = [s["name"] for s in sigs]
    base = Path(entry_rel).name
    if lang == "py":
        rel = f"tests/test_{base}"
        lines = [
            "# Scaffolded test skeleton (Overlay Cheetah, deterministic; zero tokens).",
            "# Asserts the implementation guard + callable shape. Replace with real assertions.",
            "import inspect",
            f"from {base[:-3]} import {', '.join(names) or 'ready'}",
            "",
        ]
        for s in sigs:
            args = ", ".join(_boundary_for(p) for p in s["params"]) or ""
            lines += [
                f"def test_{s['name']}_implemented():",
                f"    assert \"{IMPL_MARK}\" not in inspect.getsource({s['name']})",
                "",
                f"# boundary({s['name']}): {args or 'n/a'}",
                "",
            ]
        return {"path": rel, "content": "\n".join(lines), "exports": names, "note": f"{len(names)} signature(s) → skeleton"}
    rel = Path(entry_rel).with_suffix("").as_posix() + ".test.ts"
    imp = "./" + Path(entry_rel).name.rsplit(".", 1)[0]
    lines = [
        "// Scaffolded test skeleton (Overlay Cheetah, deterministic; zero tokens).",
        "// Asserts the implementation guard + callable shape. Replace with real assertions.",
        'import { describe, it, expect } from "vitest";',
        f'import {{ {", ".join(names) or "ready"} }} from "{imp}";' if names else f'import "{imp}";',
        "",
        'describe("implementation", () => {',
    ]
    for s in sigs:
        lines.append(f'  it("implements {s["name"]}", () => {{ expect(String({s["name"]})).not.toContain("{IMPL_MARK}"); }});')
        args = ", ".join(_boundary_for(p) for p in s["params"]) or ""
        lines.append(f'  // boundary({s["name"]}): {args or "n/a"}')
    if not sigs:
        lines.append('  it("loads", () => { expect(true).toBe(true); });')
    lines += ["});", ""]
    return {"path": rel, "content": "\n".join(lines), "exports": names, "note": f"{len(names)} signature(s) → skeleton"}


def synthesize_tests_for_file(root: str, entry_rel: str) -> Dict[str, Any]:
    p = (Path(root).resolve() / entry_rel.lstrip("/\\")).resolve()
    try:
        p.relative_to(Path(root).resolve())
    except ValueError:
        return {"path": "", "content": "", "exports": [], "note": "entry escapes root"}
    if not p.is_file():
        return {"path": "", "content": "", "exports": [], "note": f"entry not found: {entry_rel}"}
    src = p.read_text(encoding="utf-8", errors="replace")
    return {"entry": entry_rel, **synth_tests(src, entry_rel)}
