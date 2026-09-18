#!/usr/bin/env python3
"""
Cheetah Coding Agent — repo-aware editing layer for Overlay Cheetah V3 Pro.

Why this exists: the historical V3 Pro core (overlay_cheetah_v3_pro.py) is a
deterministic Jinja template renderer. It scaffolds, it does not *engineer*:
no workspace confinement, no diff preview, no test gates. This module adds
the missing engineering substrate without rewriting the GUI core:

- Workspace: root-confined read / list / search. Path traversal is rejected,
  symlinks that escape the root are rejected, binary files are refused.
- Edits are planned first (unified diff), applied second (with .bak backup),
  and logged with sha256 before/after hashes.
- Test gates: auto-detect pytest / npm test / vitest in the workspace and run
  the relevant one with a timeout. No test runner => honest SKIP, never a
  fabricated PASS.
- Zero third-party dependencies (stdlib only) so preflight stays green.

This module never calls an LLM and never pretends to. It is the deterministic
foundation that an LLM planner (LLMManager) or the Axiom cheetah.ts bridge can
drive through cheetah_server.py.
"""

from __future__ import annotations

import difflib
import hashlib
import json
import re
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

VERSION = "4.0.0-agent"

_TEXT_SUFFIXES = {
    ".py", ".pyi", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".json",
    ".yaml", ".yml", ".toml", ".ini", ".cfg", ".md", ".mdx", ".txt",
    ".html", ".css", ".scss", ".vue", ".svelte", ".sql", ".sh", ".ps1",
    ".java", ".go", ".rs", ".c", ".h", ".cpp", ".hpp", ".cs", ".rb",
    ".php", ".swift", ".kt", ".env.example", ".gitignore", ".dockerignore",
}

_SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", ".cache",
    ".next", "dist", "build", "out", "coverage", ".pytest_cache",
}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass
class OperationRecord:
    timestamp: str
    op: str
    path: str
    ok: bool
    detail: str = ""
    sha_before: str = ""
    sha_after: str = ""


@dataclass
class Workspace:
    """A root-confined working directory for all agent file operations."""

    root: Path
    log: List[OperationRecord] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.root = self.root.resolve()

    # -- confinement ----------------------------------------------------
    def _checked_resolve(self, rel: str) -> Path:
        candidate = (self.root / Path(rel)).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError:
            raise ValueError(f"path escapes workspace root: {rel!r}")
        if candidate.is_symlink():
            target = candidate.resolve()
            try:
                target.relative_to(self.root)
            except ValueError:
                raise ValueError(f"symlink escapes workspace root: {rel!r}")
        return candidate

    # -- read -----------------------------------------------------------
    def read_file(self, rel: str, max_bytes: int = 1_000_000) -> Dict[str, Any]:
        try:
            path = self._checked_resolve(rel)
        except ValueError as exc:
            return {"ok": False, "error": str(exc)}
        if not path.is_file():
            return {"ok": False, "error": f"not a file: {rel}"}
        if path.stat().st_size > max_bytes:
            return {"ok": False, "error": f"file too large: {rel}"}
        if path.suffix not in _TEXT_SUFFIXES and path.name not in _TEXT_SUFFIXES:
            # Peek for null bytes rather than trusting the suffix alone.
            with open(path, "rb") as fh:
                if b"\x00" in fh.read(8192):
                    return {"ok": False, "error": f"binary file refused: {rel}"}
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return {"ok": False, "error": f"non-utf8 file refused: {rel}"}
        self.log.append(OperationRecord(
            timestamp=datetime.now(timezone.utc).isoformat(),
            op="read", path=rel, ok=True,
            detail=f"{len(text)} chars", sha_after=sha256_text(text),
        ))
        return {"ok": True, "path": rel, "content": text,
                "sha256": sha256_text(text)}

    def list_files(self, rel: str = ".", glob: str = "**/*",
                   limit: int = 500) -> Dict[str, Any]:
        try:
            base = self._checked_resolve(rel)
        except ValueError as exc:
            return {"ok": False, "error": str(exc)}
        if not base.is_dir():
            return {"ok": False, "error": f"not a directory: {rel}"}
        out: List[str] = []
        for path in sorted(base.glob(glob)):
            if len(out) >= limit:
                break
            if any(part in _SKIP_DIRS for part in path.parts):
                continue
            try:
                display = path.resolve().relative_to(self.root).as_posix()
            except ValueError:
                continue
            if path.is_file():
                out.append(display)
        return {"ok": True, "root": self.root.as_posix(),
                "count": len(out), "files": out, "truncated": len(out) >= limit}

    def search(self, pattern: str, glob: str = "**/*.py",
               limit: int = 100) -> Dict[str, Any]:
        try:
            rx = re.compile(pattern)
        except re.error as exc:
            return {"ok": False, "error": f"bad regex: {exc}"}
        hits: List[Dict[str, Any]] = []
        listing = self.list_files(".", glob=glob, limit=2000)
        if not listing.get("ok"):
            return listing
        for rel in listing["files"]:
            read = self.read_file(rel)
            if not read.get("ok"):
                continue
            for lineno, line in enumerate(read["content"].splitlines(), 1):
                if rx.search(line):
                    hits.append({"file": rel, "line": lineno,
                                 "text": line.strip()[:300]})
                    if len(hits) >= limit:
                        return {"ok": True, "count": len(hits),
                                "hits": hits, "truncated": True}
        return {"ok": True, "count": len(hits), "hits": hits,
                "truncated": False}

    # -- edits: plan first, apply second --------------------------------
    def build_diff(self, rel: str, old: str, new: str) -> Dict[str, Any]:
        """Compute a unified diff without touching disk."""
        if old == new:
            return {"ok": True, "path": rel, "empty": True, "diff": ""}
        diff = "".join(difflib.unified_diff(
            old.splitlines(keepends=True), new.splitlines(keepends=True),
            fromfile=f"a/{rel}", tofile=f"b/{rel}",
        ))
        return {"ok": True, "path": rel, "empty": False, "diff": diff}

    def apply_edit(self, rel: str, old: str, new: str,
                   expected_sha: str = "") -> Dict[str, Any]:
        """Apply an exact-match replacement. Fail-closed on mismatch."""
        try:
            path = self._checked_resolve(rel)
        except ValueError as exc:
            return {"ok": False, "error": str(exc)}
        if not path.is_file():
            return {"ok": False, "error": f"not a file: {rel}"}
        current = path.read_text(encoding="utf-8")
        if expected_sha and sha256_text(current) != expected_sha:
            return {"ok": False,
                    "error": "expected_sha mismatch: file changed since read"}
        if old not in current:
            return {"ok": False,
                    "error": "oldString not found: no changes applied"}
        if current.count(old) > 1:
            return {"ok": False, "error": (
                "oldString matches multiple locations: "
                "provide more context or use apply_edit_all")}
        before = sha256_text(current)
        backup = path.with_suffix(path.suffix + ".cheetah-bak")
        backup.write_text(current, encoding="utf-8")
        updated = current.replace(old, new, 1)
        path.write_text(updated, encoding="utf-8")
        after = sha256_text(updated)
        diff = self.build_diff(rel, current, updated)["diff"]
        self.log.append(OperationRecord(
            timestamp=datetime.now(timezone.utc).isoformat(),
            op="edit", path=rel, ok=True,
            detail=f"backup={backup.name}", sha_before=before, sha_after=after,
        ))
        return {"ok": True, "path": rel, "sha_before": before,
                "sha_after": after, "backup": backup.name, "diff": diff}

    def apply_edit_all(self, rel: str, old: str, new: str) -> Dict[str, Any]:
        try:
            path = self._checked_resolve(rel)
        except ValueError as exc:
            return {"ok": False, "error": str(exc)}
        if not path.is_file():
            return {"ok": False, "error": f"not a file: {rel}"}
        current = path.read_text(encoding="utf-8")
        if old not in current:
            return {"ok": False,
                    "error": "oldString not found: no changes applied"}
        before = sha256_text(current)
        backup = path.with_suffix(path.suffix + ".cheetah-bak")
        backup.write_text(current, encoding="utf-8")
        updated = current.replace(old, new)
        path.write_text(updated, encoding="utf-8")
        after = sha256_text(updated)
        self.log.append(OperationRecord(
            timestamp=datetime.now(timezone.utc).isoformat(),
            op="edit_all", path=rel, ok=True,
            detail=f"replacements={current.count(old)}",
            sha_before=before, sha_after=after,
        ))
        return {"ok": True, "path": rel, "sha_before": before,
                "sha_after": after, "backup": backup.name,
                "diff": self.build_diff(rel, current, updated)["diff"]}

    def write_new_file(self, rel: str, content: str,
                       overwrite: bool = False) -> Dict[str, Any]:
        try:
            path = self._checked_resolve(rel)
        except ValueError as exc:
            return {"ok": False, "error": str(exc)}
        if path.exists() and not overwrite:
            return {"ok": False,
                    "error": f"file exists (pass overwrite=True): {rel}"}
        path.parent.mkdir(parents=True, exist_ok=True)
        before = sha256_text(path.read_text(encoding="utf-8")) if path.exists() else ""
        path.write_text(content, encoding="utf-8")
        after = sha256_text(content)
        self.log.append(OperationRecord(
            timestamp=datetime.now(timezone.utc).isoformat(),
            op="write", path=rel, ok=True,
            detail=f"{len(content)} chars", sha_before=before, sha_after=after,
        ))
        return {"ok": True, "path": rel, "sha_after": after}

    # -- test gates ------------------------------------------------------
    def detect_test_runners(self) -> List[str]:
        runners: List[str] = []
        root = self.root
        if list(root.glob("test_*.py")) or list(root.glob("*_test.py")) or (root / "tests").is_dir():
            runners.append("pytest")
        pkg = root / "package.json"
        if pkg.is_file():
            try:
                scripts = json.loads(pkg.read_text(encoding="utf-8")).get("scripts", {})
            except (json.JSONDecodeError, UnicodeDecodeError):
                scripts = {}
            if "test" in scripts:
                runners.append("npm test")
            if (root / "vitest.config.ts").exists() or (root / "vitest.config.js").exists():
                runners.append("vitest")
        return runners

    def run_tests(self, runner: str = "auto",
                  timeout_sec: int = 300) -> Dict[str, Any]:
        available = self.detect_test_runners()
        if runner == "auto":
            runner = available[0] if available else ""
        if not runner:
            return {"ok": True, "status": "SKIP",
                    "detail": "no test runner detected (pytest/tests/, npm test, vitest)"}
        if runner not in available and runner != "pytest":
            return {"ok": False, "status": "ERROR",
                    "detail": f"runner {runner!r} not detected here"}
        cmd: List[str]
        if runner == "pytest":
            cmd = ["python", "-m", "pytest", "-q"]
        elif runner == "vitest":
            cmd = ["npx", "vitest", "run"]
        else:
            cmd = ["npm", "test", "--silent"]
        started = time.time()
        try:
            proc = subprocess.run(
                cmd, cwd=str(self.root), capture_output=True, text=True,
                timeout=timeout_sec,
            )
        except FileNotFoundError:
            return {"ok": False, "status": "ERROR",
                    "detail": f"runner binary missing for {runner!r}"}
        except subprocess.TimeoutExpired:
            return {"ok": False, "status": "TIMEOUT",
                    "detail": f"exceeded {timeout_sec}s"}
        elapsed = time.time() - started
        passed = proc.returncode == 0
        tail = (proc.stdout + "\n" + proc.stderr)[-4000:]
        self.log.append(OperationRecord(
            timestamp=datetime.now(timezone.utc).isoformat(),
            op="test", path=".", ok=passed,
            detail=f"{runner} exit={proc.returncode} {elapsed:.1f}s",
        ))
        return {"ok": passed, "status": "PASS" if passed else "FAIL",
                "runner": runner, "exit_code": proc.returncode,
                "duration_sec": round(elapsed, 2), "output_tail": tail}

    def operation_log(self) -> List[Dict[str, Any]]:
        return [{"timestamp": r.timestamp, "op": r.op, "path": r.path,
                 "ok": r.ok, "detail": r.detail,
                 "sha_before": r.sha_before, "sha_after": r.sha_after}
                for r in self.log]


def run_coding_task(root: str, plan: List[Dict[str, Any]],
                    on_step: Optional[Callable[[Dict[str, Any]], None]] = None
                    ) -> Dict[str, Any]:
    """Execute a deterministic multi-step file plan with per-step results.

    Each step: {"op": "read"|"diff"|"edit"|"write"|"test", ...}. Stops at the
    first failed edit/write/test unless the step sets "allow_fail": true.
    Pure planner output — no LLM calls happen here.
    """
    ws = Workspace(Path(root))
    results: List[Dict[str, Any]] = []
    for i, step in enumerate(plan):
        op = step.get("op", "")
        if op == "read":
            res = ws.read_file(step.get("path", ""))
        elif op == "diff":
            cur = ws.read_file(step.get("path", ""))
            res = {"ok": False, "error": cur.get("error", "")} if not cur.get("ok") \
                else ws.build_diff(step["path"], cur["content"],
                                   step.get("new_content", ""))
        elif op == "edit":
            res = ws.apply_edit(step.get("path", ""), step.get("old", ""),
                                step.get("new", ""),
                                step.get("expected_sha", ""))
        elif op == "write":
            res = ws.write_new_file(step.get("path", ""),
                                    step.get("content", ""),
                                    step.get("overwrite", False))
        elif op == "test":
            res = ws.run_tests(step.get("runner", "auto"),
                               step.get("timeout_sec", 300))
        else:
            res = {"ok": False, "error": f"unknown op: {op!r}"}
        results.append({"step": i, "op": op, "result": res})
        if on_step:
            on_step({"step": i, "op": op, "result": res})
        if not res.get("ok") and not step.get("allow_fail", False):
            if op in ("edit", "write", "test"):
                break
    ok = all(r["result"].get("ok") for r in results)
    return {"ok": ok, "steps": results, "operation_log": ws.operation_log()}
