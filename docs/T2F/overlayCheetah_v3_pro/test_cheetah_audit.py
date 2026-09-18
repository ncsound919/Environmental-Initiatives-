"""Tests for cheetah_audit — security findings, syntax, policy."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cheetah_audit import audit_files


def test_clean_code_passes():
    report = audit_files({"ok.py": "def add(a, b):\n    return a + b\n"})
    assert report["ok"] and report["passed"] is True
    assert report["counts"]["critical"] == 0


def test_eval_is_critical():
    report = audit_files({"bad.py": "result = eval(user_input)\n"})
    assert report["passed"] is False
    assert report["counts"]["critical"] >= 1
    assert any(f["rule"] == "py-eval" for f in report["findings"])


def test_subprocess_shell_is_critical():
    code = "import subprocess\nsubprocess.run(cmd, shell=True)\n"
    report = audit_files({"bad.py": code})
    assert report["passed"] is False
    assert any(f["rule"] == "py-subprocess-shell"
               for f in report["findings"])


def test_secret_redacted_not_leaked():
    code = 'AWS_KEY = "AKIAIOSFODNN7EXAMPLE"\n'
    report = audit_files({"bad.py": code})
    assert report["counts"]["critical"] >= 1
    blob = str(report["findings"])
    assert "AKIAIOSFODNN7EXAMPLE" not in blob


def test_broken_python_fails():
    report = audit_files({"bad.py": "def broken(:\n"})
    assert report["passed"] is False
    assert any(f["rule"] == "py-syntax-error" for f in report["findings"])


def test_js_eval_flagged():
    report = audit_files({"bad.js": "function p(d){ return eval(d); }\n"})
    assert any(f["rule"] == "js-eval" for f in report["findings"])


def test_unpinned_requirement_advisory():
    report = audit_files({"requirements.txt": "requests\nflask==2.0\n"},
                         strict=False)
    assert any(f["rule"] == "dep-unpinned" for f in report["findings"])


def test_safe_stdlib_calls_are_clean():
    code = ("import json, re, hashlib\n"
            "data = json.loads(payload)\n"
            "rx = re.compile(r'x+')\n"
            "h = hashlib.sha256(b'x').hexdigest()\n")
    report = audit_files({"ok.py": code})
    assert report["counts"]["critical"] == 0
    assert report["counts"]["high"] == 0


def test_pickle_loads_flagged():
    code = "import pickle\nobj = pickle.loads(blob)\n"
    report = audit_files({"bad.py": code})
    assert any(f["rule"] == "py-pickle-load" for f in report["findings"])


def test_yaml_load_flagged_safe_load_clean():
    bad = audit_files({"b.py": "import yaml\nd = yaml.load(text)\n"})
    assert any(f["rule"] == "py-yaml-load" for f in bad["findings"])
    good = audit_files({"g.py": "import yaml\nd = yaml.safe_load(text)\n"})
    assert not any(f["rule"] == "py-yaml-load" for f in good["findings"])
