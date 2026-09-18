"""Tests for recourse_bridge — offline honesty + ledger fail-closed rules."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cheetah_audit import audit_files
from recourse_bridge import PromotionLedger, RecourseClient


def test_offline_client_never_fabricates():
    client = RecourseClient("http://127.0.0.1:59999", timeout_sec=2)
    reach = client.reachable()
    assert reach["online"] is False
    verify = client.verify_coding("export function f(){}")
    assert verify["online"] is False and verify["ok"] is False


def test_promote_refuses_missing_suite(tmp_path):
    ledger = PromotionLedger(tmp_path / "registry.json")
    audit = audit_files({"t.js": "export function add(a,b){return a+b;}"})
    res = ledger.promote("adder", "export function add(a,b){return a+b;}",
                         "", audit)
    assert res["ok"] is False and "test suite" in res["error"]


def test_promote_refuses_failed_audit(tmp_path):
    ledger = PromotionLedger(tmp_path / "registry.json")
    bad = "result = eval(user_input)\n"
    audit = audit_files({"bad.py": bad})
    assert audit["passed"] is False
    res = ledger.promote("evil", bad, "assert True", audit)
    assert res["ok"] is False and "audit" in res["error"]


def test_promote_and_reverify(tmp_path):
    ledger = PromotionLedger(tmp_path / "registry.json")
    code = "export function add(a, b) { return a + b; }\n"
    audit = audit_files({"adder.js": code})
    assert audit["passed"] is True
    res = ledger.promote("adder", code, "assert add(1,2) === 3", audit)
    assert res["ok"] is True
    check = ledger.verify_local("adder")
    assert check["ok"] is True and check["suite_present"] is True
