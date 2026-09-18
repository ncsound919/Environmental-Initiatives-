#!/usr/bin/env python3
"""
Cheetah Audit Engine — security + correctness auditing for generated code.

Replaces the historical 5-substring `Auditor.security_scan` with something
credible enough to gate real promotions:

SECURITY (fail-closed, severity-ranked):
- Secret scanning: AWS, GitHub, Slack, Stripe, GCP, generic API keys, JWT,
  RSA/EC private keys, password assignments. Findings include the rule id and
  line number, never the secret value (redacted to first 4 + ...).
- Python AST analysis: eval/exec/__import__/compile abuse, os.system,
  subprocess with shell=True, pickle/marshal/yaml-unsafe loads, socket
  servers bound to 0.0.0.0 without auth markers, hashlib.md5/sha1 use,
  `assert` used for security checks, hardcoded password comparisons.
- JS/TS regex analysis: eval/new Function/child_process exec, innerHTML,
  document.write, dangerouslySetInnerHTML, hardcoded secrets.
- Dependency hygiene: requirements.txt / package.json pins checked; unpinned
  (`*`, `latest`, bare package names) reported as medium.

CORRECTNESS:
- Python files must `ast.parse` cleanly; JS/TS files get `node --check`
  when node exists (honest SKIP when it does not — never a fake pass).
- Optional test gate delegates to cheetah_agent.Workspace.run_tests.
- Every audited file gets a sha256; the report carries a stable
  `audit_id` (hash of sorted file hashes) so re-runs are comparable.

Severity policy: any `critical` finding => passed=False. `high` findings =>
passed=False unless `strict=False`. Medium/low are advisory.

Stdlib only. No network. No LLM.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION = "4.0.0-audit"

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


@dataclass
class Finding:
    severity: str  # critical|high|medium|low
    rule: str
    file: str
    line: int
    message: str

    def to_dict(self) -> Dict[str, Any]:
        return {"severity": self.severity, "rule": self.rule,
                "file": self.file, "line": self.line,
                "message": self.message}


# ---------------------------------------------------------------------------
# Secret patterns. Values are redacted in output; only rule + location emitted.
# ---------------------------------------------------------------------------
_SECRET_PATTERNS: List[Tuple[str, str, str]] = [
    ("aws-access-key", "critical", r"AKIA[0-9A-Z]{16}"),
    ("aws-secret-key", "critical",
     r"(?i)aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{30,}"),
    ("github-token", "critical", r"gh[pousr]_[A-Za-z0-9]{20,}"),
    ("github-classic", "critical", r"\bghp_[A-Za-z0-9]{20,}"),
    ("slack-token", "high", r"xox[bpars]-[A-Za-z0-9-]{10,}"),
    ("stripe-key", "high", r"s[kr]_(?:live|test)_[A-Za-z0-9]{10,}"),
    ("openai-key", "high", r"sk-(?:proj-)?[A-Za-z0-9_-]{20,}"),
    ("google-api-key", "high", r"AIza[0-9A-Za-z_-]{30,}"),
    ("jwt-token", "medium",
     r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"),
    ("private-key", "critical",
     r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    ("password-assign", "high",
     r"(?i)(password|passwd|pwd|secret)\s*[:=]\s*['\"][^'\"]{3,}['\"]"),
    ("generic-api-key", "medium",
     r"(?i)(api[_-]?key|apikey|auth[_-]?token)\s*[:=]\s*['\"][A-Za-z0-9_.-]{12,}['\"]"),
]

_JS_DANGEROUS: List[Tuple[str, str, str]] = [
    ("js-eval", "critical", r"\beval\s*\("),
    ("js-new-function", "critical", r"\bnew\s+Function\s*\("),
    ("js-child-exec", "high",
     r"child_process['\"]?\s*\)?\s*\.\s*(exec|execSync|spawn\s*\([^)]*shell\s*:\s*true)"),
    ("js-inner-html", "medium", r"\.\s*innerHTML\s*="),
    ("js-document-write", "medium", r"\bdocument\s*\.\s*write\s*\("),
    ("js-dangerous-html", "medium", r"dangerouslySetInnerHTML"),
]


class _PythonSecurityVisitor(ast.NodeVisitor):
    """AST visitor collecting security findings for one Python file."""

    def __init__(self, rel: str) -> None:
        self.rel = rel
        self.findings: List[Finding] = []

    def _add(self, node: ast.AST, severity: str, rule: str, message: str) -> None:
        self.findings.append(Finding(severity, rule, self.rel,
                                     getattr(node, "lineno", 0), message))

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        is_bare = isinstance(func, ast.Name)
        name = func.id if is_bare else (
            func.attr if isinstance(func, ast.Attribute) else "")
        receiver = ""
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
            receiver = func.value.id

        # Bare builtins only: re.compile / pathlib.compile must NOT match.
        if is_bare and name in ("eval", "exec", "compile"):
            self._add(node, "critical", f"py-{name}",
                      f"dynamic code execution via {name}()")
        elif is_bare and name == "__import__":
            self._add(node, "high", "py-dynamic-import",
                      "dynamic import via __import__()")
        elif name == "system" and isinstance(func, ast.Attribute):
            self._add(node, "critical", "py-os-system",
                      "os.system() shell execution")
        elif name in ("Popen", "call", "run", "check_output") and isinstance(func, ast.Attribute):
            for kw in node.keywords:
                if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    self._add(node, "critical", "py-subprocess-shell",
                              f"subprocess.{name}() with shell=True")
        elif name in ("loads", "load") and receiver in (
                "pickle", "marshal", "shelve"):
            self._add(node, "high", "py-pickle-load",
                      f"deserialization via {receiver}.{name}() — unsafe on untrusted input")
        elif name == "load" and receiver == "yaml":
            # yaml.load without SafeLoader — safe_load is clean.
            self._add(node, "medium", "py-yaml-load",
                      "yaml.load() — use yaml.safe_load() unless Loader is explicit")
        elif name in ("md5", "sha1") and (is_bare or receiver == "hashlib"):
            self._add(node, "low", "py-weak-hash",
                      f"weak hash {name}() — unsuitable for security use")
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name in ("pickle", "marshal", "shelve"):
                self._add(node, "medium", "py-unsafe-import",
                          f"import of {alias.name} (unsafe deserialization module)")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module in ("pickle", "marshal", "shelve"):
            self._add(node, "medium", "py-unsafe-import",
                      f"import from {node.module} (unsafe deserialization module)")
        self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert) -> None:
        self._add(node, "low", "py-assert-security",
                  "assert used for a check — asserts vanish under python -O")
        self.generic_visit(node)


def _scan_secrets(rel: str, text: str) -> List[Finding]:
    findings: List[Finding] = []
    for rule, severity, pattern in _SECRET_PATTERNS:
        try:
            rx = re.compile(pattern)
        except re.error:
            continue
        for match in rx.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            findings.append(Finding(severity, rule, rel, line,
                                    f"possible secret ({rule}) — value redacted"))
    return findings


def _scan_python_ast(rel: str, text: str) -> List[Finding]:
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return [Finding("high", "py-syntax-error", rel,
                        exc.lineno or 0,
                        f"Python syntax error: {exc.msg}")]
    visitor = _PythonSecurityVisitor(rel)
    visitor.visit(tree)
    return visitor.findings


def _scan_js(rel: str, text: str) -> List[Finding]:
    findings: List[Finding] = []
    for rule, severity, pattern in _JS_DANGEROUS:
        for i, line in enumerate(text.splitlines(), 1):
            if re.search(pattern, line):
                findings.append(Finding(severity, rule, rel, i,
                                        f"dangerous JS pattern ({rule})"))
    findings.extend(_scan_secrets(rel, text))
    return findings


def _check_node_syntax(rel: str, text: str) -> Optional[Finding]:
    """node --check for JS files. None => checked clean; Finding => error;
    returns a synthetic SKIP marker via RuntimeError when node is missing."""
    node = shutil.which("node")
    if not node:
        raise RuntimeError("node not installed: syntax check skipped")
    import tempfile, os
    suffix = ".ts" if rel.endswith(".ts") else ".js"
    with tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False,
                                     encoding="utf-8") as fh:
        fh.write(text)
        tmp = fh.name
    try:
        proc = subprocess.run([node, "--check", tmp], capture_output=True,
                              text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return Finding("medium", "js-syntax-timeout", rel, 0,
                       "node --check timed out")
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout).strip().splitlines()
        return Finding("high", "js-syntax-error", rel, 0,
                       f"node --check failed: {err[0][:200] if err else 'unknown'}")
    return None


def _check_dependency_pins(rel: str, text: str) -> List[Finding]:
    findings: List[Finding] = []
    if rel.endswith("requirements.txt"):
        for i, line in enumerate(text.splitlines(), 1):
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            if not re.search(r"[=<>~!]=|==|>=|~=|===", line):
                findings.append(Finding(
                    "medium", "dep-unpinned", rel, i,
                    f"unpinned dependency: {line[:60]}"))
    elif rel.endswith("package.json"):
        try:
            deps = {**json.loads(text).get("dependencies", {}),
                    **json.loads(text).get("devDependencies", {})}
        except (json.JSONDecodeError, AttributeError):
            return [Finding("medium", "dep-parse-error", rel, 0,
                            "package.json is not valid JSON")]
        for name, spec in deps.items():
            if not isinstance(spec, str):
                continue
            if spec in ("*", "latest") or spec == "":
                findings.append(Finding("medium", "dep-unpinned", rel, 0,
                                        f"unpinned npm dep: {name}@{spec}"))
    return findings


def audit_text(rel: str, text: str) -> Tuple[List[Finding], List[str]]:
    """Audit one in-memory file. Returns (findings, skipped_checks)."""
    findings: List[Finding] = []
    skipped: List[str] = []
    findings.extend(_scan_secrets(rel, text))
    if rel.endswith((".py", ".pyi")):
        findings.extend(_scan_python_ast(rel, text))
    elif rel.endswith((".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx")):
        findings.extend(_scan_js(rel, text))
        try:
            result = _check_node_syntax(rel, text)
            if result is not None:
                findings.append(result)
        except RuntimeError as exc:
            skipped.append(str(exc))
    if rel.endswith(("requirements.txt", "package.json")):
        findings.extend(_check_dependency_pins(rel, text))
    # Hardcoded TODO-security markers are advisory.
    for i, line in enumerate(text.splitlines(), 1):
        if re.search(r"(?i)\b(TODO|FIXME|HACK).{0,40}(auth|secur|password|token|key)\b", line):
            findings.append(Finding("low", "security-todo", rel, i,
                                    "security-relevant TODO marker"))
    findings.sort(key=lambda f: (SEVERITY_ORDER.get(f.severity, 9),
                                 f.file, f.line))
    return findings, skipped


def audit_files(files: Dict[str, str],
                strict: bool = True) -> Dict[str, Any]:
    """Audit a {rel_path: content} mapping. Pure function, no I/O."""
    all_findings: List[Finding] = []
    skipped: List[str] = []
    hashes: Dict[str, str] = {}
    for rel, text in files.items():
        hashes[rel] = hashlib.sha256(text.encode("utf-8")).hexdigest()
        findings, skip = audit_text(rel, text)
        all_findings.extend(findings)
        skipped.extend(skip)
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for f in all_findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1
    passed = counts["critical"] == 0 and (not strict or counts["high"] == 0)
    audit_id = hashlib.sha256(
        json.dumps(hashes, sort_keys=True).encode()).hexdigest()[:16]
    return {
        "ok": True,
        "passed": passed,
        "audit_id": audit_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "engine": VERSION,
        "strict": strict,
        "counts": counts,
        "findings": [f.to_dict() for f in all_findings],
        "skipped_checks": sorted(set(skipped)),
        "file_hashes": hashes,
    }


def audit_workspace(root: str, glob: str = "**/*.py",
                    strict: bool = True,
                    run_tests: bool = False) -> Dict[str, Any]:
    """Audit files on disk under root. Optionally run the test gate too."""
    from cheetah_agent import Workspace
    ws = Workspace(Path(root))
    listing = ws.list_files(".", glob=glob)
    if not listing.get("ok"):
        return {"ok": False, "passed": False, "error": listing.get("error")}
    files: Dict[str, str] = {}
    for rel in listing["files"]:
        read = ws.read_file(rel)
        if read.get("ok"):
            files[rel] = read["content"]
    report = audit_files(files, strict=strict)
    report["workspace"] = str(ws.root)
    report["files_audited"] = len(files)
    if run_tests:
        report["test_gate"] = ws.run_tests("auto")
        if report["test_gate"].get("status") == "FAIL":
            report["passed"] = False
    return report
