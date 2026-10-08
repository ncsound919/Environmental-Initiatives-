"""Template-based CRUD/route/component generation keyed off the goal.

Deterministic, zero tokens. The emitted files are complete enough to be useful
immediately (a React component, an Express router skeleton, a FastAPI router),
and the stubs that are NOT complete raise IMPL_MARK so a verify gate can never
pass on them.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

IMPL_MARK = "NOT IMPLEMENTED"
KINDS = ("express-route", "react-component", "fastapi-endpoint")

_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def pascal(name: str) -> str:
    parts = re.split(r"[^A-Za-z0-9]+", name or "Widget")
    out = "".join(p[:1].upper() + p[1:] for p in parts if p)
    return out or "Widget"


def camel(name: str) -> str:
    p = pascal(name)
    return p[:1].lower() + p[1:]


def kinds_for_goal(goal: str) -> List[str]:
    text = (goal or "").lower()
    kinds: List[str] = []
    if re.search(r"\b(route|endpoint|crud|api|rest)\b", text):
        if re.search(r"\bfastapi\b", text):
            kinds.append("fastapi-endpoint")
        else:
            kinds.append("express-route")
    if re.search(r"\b(component|ui|react|page|button|form|dashboard)\b", text):
        kinds.append("react-component")
    return kinds


def generate_template(kind: str, name: str, opts: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    opts = opts or {}
    entity = str(opts.get("entity") or name or "item")
    Comp = pascal(entity)
    camel_name = camel(entity)

    if kind == "express-route":
        path = f"src/routes/{camel_name}.ts"
        content = (
            'import type { Express } from "express";\n\n'
            f"// TODO: implement the {camel_name} CRUD endpoints (validate input, persist, return typed responses).\n"
            f"export function register{Comp}Routes(app: Express): void {{\n"
            f'  throw new Error("{IMPL_MARK}");\n'
            "}\n"
        )
        return {"path": path, "content": content, "note": f"Express route skeleton for {camel_name}"}

    if kind == "react-component":
        path = f"src/components/{Comp}.tsx"
        content = (
            "import React from \"react\";\n\n"
            f"export interface {Comp}Props {{\n"
            f"  label?: string;\n"
            "}\n\n"
            f"export default function {Comp}({{ label = \"{Comp}\" }}: {Comp}Props) {{\n"
            f"  return <div className=\"{camel_name}\">{{label}}</div>;\n"
            "}\n"
        )
        return {"path": path, "content": content, "note": f"React component {Comp}"}

    if kind == "fastapi-endpoint":
        path = f"app/routes/{camel_name}.py"
        content = (
            "from fastapi import APIRouter\n\n"
            f"router = APIRouter(prefix=\"/{camel_name}\", tags=[\"{camel_name}\"])\n\n\n"
            f"@router.get(\"/\")\ndef list_{camel_name}():\n"
            f'    raise NotImplementedError("{IMPL_MARK}")\n'
        )
        return {"path": path, "content": content, "note": f"FastAPI router for {camel_name}"}

    return {"path": "", "content": "", "note": f"unknown template kind: {kind}"}


def generate_for_goal(goal: str, name: Optional[str] = None) -> List[Dict[str, Any]]:
    target = name or goal
    out: List[Dict[str, Any]] = []
    for kind in kinds_for_goal(goal):
        t = generate_template(kind, target)
        if t["path"]:
            t["kind"] = kind
            out.append(t)
    return out
