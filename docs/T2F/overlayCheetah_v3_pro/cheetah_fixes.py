"""Deterministic static fixes for a workspace — mechanical work with zero tokens.

Fixes are conservative and mechanical; a semantic change is never attempted:
  - source files missing a trailing newline
  - package.json: add `type: module` when ESM syntax is present, ensure
    `scripts.test`/`scripts.lint` and the matching devDependencies, format
  - tsconfig.json/.gitignore/README.md created when their absence would break
    the verify gate or waste an LLM round-trip
  - unused *single-line* import specifiers removed (only when the identifier
    appears nowhere else in the file)

`plan_fixes(root)` returns edits; it never writes. The caller (Axiom) applies
them through its guarded writer, or `apply=True` writes via the root-confined
Workspace for non-guarded targets.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from cheetah_agent import Workspace

SKIP_DIRS = {"node_modules", ".git", "dist", "build", "coverage", "__pycache__", ".venv", ".next", ".turbo"}
SRC_EXT = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py"}
ESM_RE = re.compile(r"^\s*(?:import\s|export\s)", re.M)
IMPORT_LINE_RE = re.compile(r'^(\s*)import\s+(.+?)\s+from\s+["\']([^"\']+)["\'];?\s*$')
NAMED_RE = re.compile(r"^\{(.*)\}$")
IDENT_RE = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*")


def _iter_files(root: Path, cap: int = 400) -> List[Path]:
    out: List[Path] = []
    for p in sorted(root.rglob("*")):
        if len(out) >= cap:
            break
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.is_file():
            out.append(p)
    return out


def _read(p: Path) -> Optional[str]:
    try:
        if p.stat().st_size > 400_000:
            return None
        return p.read_text(encoding="utf-8")
    except Exception:
        return None


def _strip_unused_imports(rel: str, text: str) -> Optional[tuple[str, str]]:
    """Remove single-line import specifiers never referenced elsewhere. Returns
    (new_text, reason) or None. Conservative: multi-line imports are skipped."""
    lines = text.split("\n")
    changed = False
    reasons: List[str] = []
    for i, line in enumerate(lines):
        m = IMPORT_LINE_RE.match(line)
        if not m:
            continue
        indent, spec, module = m.groups()
        rest = "\n".join(lines[:i] + lines[i + 1 :])
        kept: List[str] = []
        removed: List[str] = []
        named = NAMED_RE.match(spec.strip())
        if named:
            for raw in named.group(1).split(","):
                raw = raw.strip()
                if not raw:
                    continue
                local = raw.split(" as ")[-1].strip()
                if IDENT_RE.fullmatch(local) and not re.search(rf"\b{re.escape(local)}\b", rest):
                    removed.append(raw)
                else:
                    kept.append(raw)
            if not kept and removed:
                lines[i] = ""
                changed = True
                reasons.append(f"removed unused import from '{module}'")
                continue
            if removed:
                lines[i] = f"{indent}import {{ {', '.join(kept)} }} from \"{module}\";"
                changed = True
                reasons.append(f"pruned unused import(s) from '{module}'")
            continue
        local = spec.split(" as ")[-1].strip()
        if IDENT_RE.fullmatch(local) and not re.search(rf"\b{re.escape(local)}\b", rest):
            lines[i] = ""
            changed = True
            reasons.append(f"removed unused default import from '{module}'")
    if not changed:
        return None
    return "\n".join(lines), "; ".join(reasons)


def _ensure_pkg_json(root: Path, files: Dict[str, str], edits: List[Dict[str, str]], notes: List[str]) -> None:
    raw = files.get("package.json")
    if raw is None:
        return
    try:
        pkg = json.loads(raw)
    except Exception:
        notes.append("package.json is not valid JSON — left untouched (needs a human/LLM fix)")
        return
    if not isinstance(pkg, dict):
        return
    changed = False

    has_esm = any(ESM_RE.search(files[r]) for r in files if r != "package.json" and r.endswith((".ts", ".tsx", ".js", ".jsx", ".mjs")))
    if has_esm and pkg.get("type") != "module":
        pkg["type"] = "module"
        changed = True

    scripts = pkg.get("scripts") if isinstance(pkg.get("scripts"), dict) else {}
    tests = [r for r in files if re.search(r"\.(test|spec)\.(ts|tsx|js|jsx)$|(^|/)test_.*\.py$|_test\.py$", r)]
    if tests and not scripts.get("test"):
        scripts["test"] = "vitest run" if any(t.endswith((".ts", ".tsx", ".js", ".jsx")) for t in tests) else "pytest -q"
        changed = True
    if (root / "tsconfig.json").exists() and not scripts.get("lint"):
        scripts["lint"] = "tsc --noEmit"
        changed = True
    if scripts:
        pkg["scripts"] = scripts

    dev = pkg.get("devDependencies") if isinstance(pkg.get("devDependencies"), dict) else {}
    if tests and "vitest" not in dev and "vitest" not in (pkg.get("dependencies") or {}):
        dev["vitest"] = "^4.1.11"
        changed = True
    if (root / "tsconfig.json").exists() and "typescript" not in dev and "typescript" not in (pkg.get("dependencies") or {}):
        dev["typescript"] = "~5.8.2"
        changed = True
    if dev:
        pkg["devDependencies"] = dev

    if changed:
        edits.append({"path": "package.json", "content": json.dumps(pkg, indent=2) + "\n", "reason": "package.json alignment (type/scripts/devDeps)"})


_TSCONFIG_MIN = """{
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


def plan_fixes(root: str, cap: int = 400) -> Dict[str, Any]:
    base = Path(root).resolve()
    edits: List[Dict[str, str]] = []
    notes: List[str] = []
    skipped: List[str] = []
    if not base.is_dir():
        return {"edits": [], "notes": [f"not a directory: {root}"], "skipped": []}

    files: Dict[str, str] = {}
    for p in _iter_files(base, cap=cap):
        rel = p.resolve().relative_to(base).as_posix()
        txt = _read(p)
        if txt is None:
            skipped.append(rel)
            continue
        files[rel] = txt

    for rel, txt in files.items():
        ext = Path(rel).suffix.lower()
        if ext in SRC_EXT:
            pruned = _strip_unused_imports(rel, txt)
            if pruned:
                new_txt, reason = pruned
                files[rel] = new_txt
                edits.append({"path": rel, "content": new_txt, "reason": reason})
                txt = new_txt
        # JSON is left to the package.json pass: a malformed JSON file must not
        # be touched at all (we cannot guarantee the result stays parseable).
        if ext != ".json" and txt and not txt.endswith("\n"):
            new_txt = txt + "\n"
            files[rel] = new_txt
            edits.append({"path": rel, "content": new_txt, "reason": "ensure trailing newline"})

    _ensure_pkg_json(base, files, edits, notes)

    has_ts = any(r.endswith((".ts", ".tsx")) for r in files)
    if has_ts and "tsconfig.json" not in files:
        edits.append({"path": "tsconfig.json", "content": _TSCONFIG_MIN, "reason": "add tsconfig for TS sources"})
    if any(r.endswith((".ts", ".tsx", ".js", ".jsx")) for r in files) and ".gitignore" not in files:
        edits.append({"path": ".gitignore", "content": "node_modules/\ndist/\ncoverage/\n*.log\n", "reason": "add .gitignore"})
    if "README.md" not in files and files:
        edits.append({"path": "README.md", "content": "# Project\n\nScaffolded/verified by Overlay Cheetah (deterministic).\n", "reason": "add README"})

    # De-duplicate edits by path, keeping the last (later edits already incorporate earlier).
    dedup: Dict[str, Dict[str, str]] = {}
    for e in edits:
        dedup[e["path"]] = e
    return {"edits": list(dedup.values()), "notes": notes, "skipped": skipped}


def apply_fixes(root: str, cap: int = 400) -> Dict[str, Any]:
    """Apply the planned fixes server-side via the root-confined Workspace."""
    plan = plan_fixes(root, cap=cap)
    ws = Workspace(Path(root))
    written: List[str] = []
    for e in plan["edits"]:
        res = ws.write_new_file(e["path"], e["content"], overwrite=True)
        if isinstance(res, dict) and res.get("ok"):
            written.append(e["path"])
    return {**plan, "written": written}
