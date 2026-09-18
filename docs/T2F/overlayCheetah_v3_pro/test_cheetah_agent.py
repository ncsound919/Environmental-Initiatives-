"""Tests for cheetah_agent.Workspace — root confinement, diff/apply, test gates."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cheetah_agent import Workspace, run_coding_task


def _ws(tmp_path):
    root = tmp_path / "ws"
    root.mkdir()
    return Workspace(root)


def test_read_and_list(tmp_path):
    ws = _ws(tmp_path)
    (ws.root / "a.py").write_text("print('hi')\n", encoding="utf-8")
    read = ws.read_file("a.py")
    assert read["ok"] and "print" in read["content"]
    listing = ws.list_files(".", glob="**/*.py")
    assert listing["ok"] and "a.py" in listing["files"]


def test_path_traversal_blocked(tmp_path):
    ws = _ws(tmp_path)
    (ws.root / "a.py").write_text("x=1\n", encoding="utf-8")
    assert ws.read_file("../escape.py")["ok"] is False
    assert ws.write_new_file("../escape.py", "evil")["ok"] is False
    assert ws.apply_edit("../escape.py", "a", "b")["ok"] is False


def test_apply_edit_exact_match_only(tmp_path):
    ws = _ws(tmp_path)
    (ws.root / "a.py").write_text("x = 1\n", encoding="utf-8")
    sha = ws.read_file("a.py")["sha256"]
    # Wrong oldString => no changes.
    assert ws.apply_edit("a.py", "missing", "y")["ok"] is False
    # Stale sha => refused.
    assert ws.apply_edit("a.py", "x = 1", "x = 2",
                         expected_sha="0" * 64)["ok"] is False
    # Correct edit applies with diff + backup.
    res = ws.apply_edit("a.py", "x = 1", "x = 2", expected_sha=sha)
    assert res["ok"] and (ws.root / "a.py").read_text() == "x = 2\n"
    assert "diff" in res and res["sha_before"] != res["sha_after"]


def test_search(tmp_path):
    ws = _ws(tmp_path)
    (ws.root / "a.py").write_text("import os\nos.system('x')\n", encoding="utf-8")
    res = ws.search(r"os\.system", glob="**/*.py")
    assert res["ok"] and res["count"] == 1
    assert res["hits"][0]["file"] == "a.py"


def test_run_tests_skip_when_no_runner(tmp_path):
    ws = _ws(tmp_path)
    res = ws.run_tests("auto")
    assert res["status"] == "SKIP" and res["ok"] is True


def test_run_coding_task_plan(tmp_path):
    root = tmp_path / "proj"
    root.mkdir()
    (root / "a.py").write_text("x = 1\n", encoding="utf-8")
    out = run_coding_task(str(root), [
        {"op": "read", "path": "a.py"},
        {"op": "edit", "path": "a.py", "old": "x = 1", "new": "x = 2"},
        {"op": "test", "allow_fail": True},
    ])
    assert out["ok"] is True
    assert (root / "a.py").read_text() == "x = 2\n"
