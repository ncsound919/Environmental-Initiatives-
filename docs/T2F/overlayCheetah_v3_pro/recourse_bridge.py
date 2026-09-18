#!/usr/bin/env python3
"""
Recourse Bridge — deep integration between Cheetah V3 Pro and the Recourse
self-developing OS (Draymond-Orchestrator/agents/recourse).

Design contract (mirrors Recourse's own honesty rules):
- Every remote call is fail-soft: {ok, online, data|error}. Offline never
  fabricates a PASS; it reports online=False and the caller decides.
- Promotion requires a real test suite + a passing audit. The local ledger
  (`cheetah_tool_registry.json` next to this file) stores every promoted
  version WITH its test suite and sha256, so any version can be re-verified.
- Provenance: each promotion appends a hash-chained event
  (prev_hash -> event_hash), giving a tamper-evident trail without a server.

Recourse endpoints used (server.ts):
- POST /api/recourse/verify   {domain, sourceCode, testSuiteCode}
- POST /api/recourse/execute  {sourceCode, functionName, args}
- POST /api/recourse/repair/single {toolName, brokenCode, faultHint}
- GET  /api/recourse/registry
- GET  /api/recourse/templates / POST /api/recourse/templates/build

Stdlib only (urllib) — no new dependencies.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

VERSION = "4.0.0-recourse"

DEFAULT_RECOURSE_URL = os.environ.get("RECOURSE_URL", "http://127.0.0.1:3050")
LEDGER_NAME = "cheetah_tool_registry.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class RecourseClient:
    """Thin fail-soft HTTP client for the Recourse server."""

    def __init__(self, base_url: str = DEFAULT_RECOURSE_URL,
                 timeout_sec: int = 15) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_sec = timeout_sec

    # -- transport ------------------------------------------------------
    def _call(self, method: str, path: str,
              payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = self.base_url + path
        data = json.dumps(payload or {}).encode("utf-8") if method != "GET" else None
        req = urllib.request.Request(
            url, data=data, method=method,
            headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_sec) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                try:
                    return {"ok": True, "online": True,
                            "status": resp.status, "data": json.loads(body)}
                except json.JSONDecodeError:
                    return {"ok": True, "online": True,
                            "status": resp.status, "data": {"raw": body}}
        except urllib.error.HTTPError as exc:
            try:
                detail = exc.read().decode("utf-8", errors="replace")[:2000]
            except Exception:
                detail = str(exc)
            return {"ok": False, "online": True, "status": exc.code,
                    "error": f"HTTP {exc.code}: {detail}"}
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            return {"ok": False, "online": False,
                    "error": f"recourse offline at {self.base_url}: {exc}"}

    def reachable(self) -> Dict[str, Any]:
        res = self._call("GET", "/api/recourse/registry")
        return {"online": res.get("online", False), "ok": res.get("ok", False),
                "base_url": self.base_url}

    # -- verifier ---------------------------------------------------------
    def verify(self, source_code: str, test_suite_code: str = "",
               domain: str = "coding") -> Dict[str, Any]:
        """Remote sandbox verification. Never fabricates: offline => online False."""
        return self._call("POST", "/api/recourse/verify", {
            "domain": domain, "sourceCode": source_code,
            "testSuiteCode": test_suite_code})

    def verify_coding(self, source_code: str,
                      test_suite_code: str = "") -> Dict[str, Any]:
        return self.verify(source_code, test_suite_code, domain="coding")

    def verify_security(self, source_code: str,
                        test_suite_code: str = "") -> Dict[str, Any]:
        return self.verify(source_code, test_suite_code,
                           domain="cyber_defense")

    def execute(self, source_code: str, function_name: str = "",
                args: Optional[List[Any]] = None) -> Dict[str, Any]:
        return self._call("POST", "/api/recourse/execute", {
            "sourceCode": source_code, "functionName": function_name,
            "args": args or []})

    # -- self-heal ----------------------------------------------------------
    def heal(self, tool_name: str, broken_code: str,
             fault_hint: str = "") -> Dict[str, Any]:
        return self._call("POST", "/api/recourse/repair/single", {
            "toolName": tool_name, "brokenCode": broken_code,
            "faultHint": fault_hint})

    # -- templates -----------------------------------------------------------
    def list_templates(self) -> Dict[str, Any]:
        return self._call("GET", "/api/recourse/templates")

    def build_from_template(self, template_id: str, component_name: str,
                            params: Optional[Dict[str, Any]] = None,
                            domain: str = "coding") -> Dict[str, Any]:
        return self._call("POST", "/api/recourse/templates/build", {
            "templateId": template_id, "componentName": component_name,
            "params": params or {}, "withSelfHealing": True,
            "domain": domain})

    def registry(self) -> Dict[str, Any]:
        return self._call("GET", "/api/recourse/registry")


# ---------------------------------------------------------------------------
# Local promotion ledger — the offline-capable half of "deep integration".
# A promotion is only recorded when: test suite non-empty AND audit passed.
# ---------------------------------------------------------------------------
class PromotionLedger:
    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or (Path(__file__).resolve().parent / LEDGER_NAME)

    def _load(self) -> Dict[str, Any]:
        if not self.path.is_file():
            return {"tools": {}, "events": []}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {"tools": {}, "events": []}

    def _save(self, state: Dict[str, Any]) -> None:
        self.path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    def promote(self, tool_name: str, source_code: str,
                test_suite_code: str, audit_report: Dict[str, Any],
                origin: str = "cheetah",
                remote_verdict: Optional[Dict[str, Any]] = None
                ) -> Dict[str, Any]:
        """Record a promoted tool version. Fail-closed on weak evidence."""
        if not test_suite_code or not test_suite_code.strip():
            return {"ok": False, "error": (
                "promotion refused: every promoted version requires "
                "a real test suite (none provided)")}
        if not audit_report.get("passed", False):
            return {"ok": False, "error": (
                "promotion refused: audit did not pass "
                f"(counts={audit_report.get('counts')})")}
        state = self._load()
        tools = state.setdefault("tools", {})
        entry = tools.setdefault(tool_name, {"versions": []})
        version_no = len(entry["versions"]) + 1
        code_hash = sha256_text(source_code)
        event = {
            "timestamp": _now(),
            "tool": tool_name,
            "version": f"1.0.{version_no}-cheetah",
            "hash": code_hash[:16],
            "full_hash": code_hash,
            "audit_id": audit_report.get("audit_id", ""),
            "origin": origin,
            "remote_verdict": bool(remote_verdict and remote_verdict.get("ok")),
        }
        prev = state["events"][-1]["event_hash"] if state.get("events") else "GENESIS"
        event["prev_hash"] = prev
        event["event_hash"] = sha256_text(prev + json.dumps(event, sort_keys=True))[:16]
        version = {
            "version": event["version"],
            "hash": event["hash"],
            "created_at": event["timestamp"],
            "source_code": source_code,
            "test_suite_code": test_suite_code,
            "audit_id": event["audit_id"],
            "promoted": True,
        }
        entry["versions"].append(version)
        entry["currentVersion"] = version["version"]
        state["events"].append(event)
        self._save(state)
        return {"ok": True, "tool": tool_name, "version": version["version"],
                "hash": event["hash"], "event_hash": event["event_hash"]}

    def get_tool(self, tool_name: str) -> Dict[str, Any]:
        state = self._load()
        tool = state.get("tools", {}).get(tool_name)
        if not tool:
            return {"ok": False, "error": f"tool not found: {tool_name}"}
        return {"ok": True, "tool": tool}

    def verify_local(self, tool_name: str) -> Dict[str, Any]:
        """Re-verify the live version: re-run audit + require stored suite."""
        from cheetah_audit import audit_files
        got = self.get_tool(tool_name)
        if not got.get("ok"):
            return got
        tool = got["tool"]
        live = tool["versions"][-1]
        report = audit_files({f"{tool_name}.js": live["source_code"]})
        suite_ok = bool(live.get("test_suite_code", "").strip())
        passed = report["passed"] and suite_ok
        return {"ok": True, "passed": passed, "audit": report,
                "suite_present": suite_ok, "version": live["version"]}


def full_promotion_pipeline(tool_name: str, source_code: str,
                            test_suite_code: str,
                            audit_report: Dict[str, Any],
                            base_url: str = DEFAULT_RECOURSE_URL,
                            ledger_path: Optional[Path] = None
                            ) -> Dict[str, Any]:
    """Deep-integration pipeline: local audit -> remote verify -> ledger.

    Steps:
    1. Local audit must already pass (checked, not re-run here — caller owns it).
    2. Remote Recourse verify attempted (coding + cyber_defense). Offline is
       reported honestly; pipeline continues locally but marks remote as skipped.
    3. Ledger promotion (fail-closed on missing suite / failed audit).
    Returns a single structured verdict — never raises.
    """
    started = time.time()
    client = RecourseClient(base_url)
    remote: Dict[str, Any] = {"attempted": True, "online": False,
                              "coding": None, "security": None}
    reach = client.reachable()
    if reach.get("online"):
        remote["online"] = True
        remote["coding"] = client.verify_coding(source_code, test_suite_code)
        remote["security"] = client.verify_security(source_code, test_suite_code)
    ledger = PromotionLedger(ledger_path)
    promotion = ledger.promote(tool_name, source_code, test_suite_code,
                               audit_report, origin="cheetah-pipeline",
                               remote_verdict=remote.get("coding"))
    return {"ok": promotion.get("ok", False),
            "tool": tool_name,
            "promotion": promotion,
            "remote": remote,
            "duration_sec": round(time.time() - started, 2)}
