"""Compact repo-context gathering — deterministic, zero tokens.

Axiom injects repository context into codegen prompts. When a harness would
otherwise spend an LLM retrieval call, this builds a bounded context block from
the real files on disk: goal-relevant files, the symbols they export, and the
test runner they declare. It never invents content — only what is read.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

from cheetah_agent import Workspace

SKIP_DIRS = {"node_modules", ".git", "dist", "build", "coverage", "__pycache__", ".venv", ".next", ".turbo"}
CODE_EXT = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py"}
STOP = {"the", "and", "for", "with", "that", "this", "from", "add", "use", "using", "create", "build", "write", "make", "test", "tests", "file", "files", "code", "all", "must", "should"}

_EXPORT_TS = re.compile(r"export\s+(?:async\s+)?(?:function|class|const|let|var|interface|type)\s+([A-Za-z_$][\w$]*)")
_EXPORT_PY = re.compile(r"^(?:def|class)\s+([A-Za-z_][\w]*)", re.M)


def _tokens(text: str) -> List[str]:
    return [t for t in re.findall(r"[a-z0-9_]{3,}", (text or "").lower()) if t not in STOP]


def build_context(root: str, goal: str, max_files: int = 8, max_chars: int = 6000) -> Dict[str, Any]:
    ws = Workspace(Path(root))
    listing = ws.list_files(".", "**/*", 500)
    names: List[str] = [str(f) for f in listing.get("files", [])] if isinstance(listing, dict) else []
    goal_tokens = set(_tokens(goal))

    scored: List[tuple[int, str]] = []
    for rel in names:
        if any(part in SKIP_DIRS for part in Path(rel).parts):
            continue
        if Path(rel).suffix.lower() not in CODE_EXT:
            continue
        score = sum(1 for t in goal_tokens if t in rel.lower())
        scored.append((score, rel))
    scored.sort(key=lambda x: (-x[0], x[1]))

    picked: List[Dict[str, Any]] = []
    lines: List[str] = ["[REPO CONTEXT — read from disk by Cheetah; zero tokens]"]
    total = 0
    for score, rel in scored:
        if len(picked) >= max_files or total >= max_chars:
            break
        r = ws.read_file(rel)
        if not isinstance(r, dict) or not r.get("ok"):
            continue
        content = str(r.get("content", ""))
        exts = (_EXPORT_PY if rel.endswith(".py") else _EXPORT_TS).findall(content)
        head = [ln.strip() for ln in content.splitlines() if ln.strip() and not ln.strip().startswith("//")][:2]
        entry = {"file": rel, "exports": exts[:8], "score": score}
        picked.append(entry)
        exported = ", ".join(exts[:8])
        block = f"- {rel}" + (f" exports: {exported}" if exts else "")
        if head:
            block += f" | {head[0][:120]}"
        lines.append(block)
        total += len(block)

    markers = [r for r in names if re.search(r"\.(test|spec)\.|(^/)test_|_test\.py$", r)]
    if markers:
        lines.append("tests: " + ", ".join(markers[:6]))
    pkg = ws.read_file("package.json")
    if isinstance(pkg, dict) and pkg.get("ok"):
        m = re.search(r'"test"\s*:\s*"([^"]+)"', str(pkg.get("content", "")))
        if m:
            lines.append(f"test script: {m.group(1)}")

    return {"context": "\n".join(lines).strip(), "files": picked, "count": len(picked)}
