"""Tests for the decision-gated scaffold (cheetah_jev).

No live network: the JEV transport is patched; env-controlled fallback paths
are exercised with CHEETAH_JEV_ENABLED=0 / a dead port.
"""

import json
import os
from unittest import mock

from cheetah_jev import decide_scaffold


def _files(plan):
    return {f["output"]: f["rendered"] for f in plan["files"]}


def test_pinned_is_deterministic_no_http(monkeypatch):
    monkeypatch.delenv("CHEETAH_JEV_ENABLED", raising=False)
    monkeypatch.setenv("CHEETAH_JEV_URL", "http://127.0.0.1:9")
    plan = decide_scaffold("build anything", shape="node-lib", strict=True, tests=True)
    assert plan["source"] == "offline"
    assert plan["error"] is None
    assert {d["source"] for d in plan["decisions"]} == {"pinned"}
    assert plan["shape"] == "node-lib"
    assert "src/index.test.ts" in _files(plan)


def test_disabled_offline_fallback(monkeypatch):
    monkeypatch.setenv("CHEETAH_JEV_ENABLED", "0")
    plan = decide_scaffold("Build a React app with a dashboard component")
    assert plan["source"] == "offline"
    assert plan["error"] == "JEV disabled (CHEETAH_JEV_ENABLED=0)"
    assert [d["source"] for d in plan["decisions"]] == ["offline", "offline", "offline"]
    # fallback classifier still resolves the shape
    assert plan["shape"] == "react-vite"
    assert all(d["decision"] is True for d in plan["decisions"] if d["id"] in ("strict", "tests"))
    assert "src/App.test.ts" in _files(plan)


def test_unreachable_offline_fallback(monkeypatch):
    monkeypatch.delenv("CHEETAH_JEV_ENABLED", raising=False)
    monkeypatch.setenv("CHEETAH_JEV_URL", "http://127.0.0.1:9")
    monkeypatch.setenv("CHEETAH_JEV_TIMEOUT", "0.5")
    plan = decide_scaffold("Create an Express REST API with /users routes")
    assert plan["source"] == "offline"
    assert plan["error"], "must report the real transport error"
    assert plan["shape"] == "express-api"
    # defaults preserved: strict True, tests True
    assert "src/routes.test.ts" in _files(plan)


def test_maps_localjev_answers(monkeypatch):
    monkeypatch.delenv("CHEETAH_JEV_ENABLED", raising=False)
    body = {
        "model": "localjev-test",
        "answers": {
            "shape": {
                "type": "choice",
                "choice": "python-pkg",
                "probabilities": {"python-pkg": 0.82, "node-lib": 0.1},
                "confidence": 0.81,
            },
            "strict": {"type": "noul", "noul": 0.9},
            "tests": {"type": "noul", "noul": 0.1},
        },
        "usage": {"input_tokens": 1, "output_tokens": 1},
    }
    with mock.patch("cheetah_jev._post_systemone", return_value=(200, body)) as post:
        plan = decide_scaffold("Create a python package exporting normalize and clamp")
    post.assert_called_once()
    assert plan["source"] == "localjev"
    assert plan["model"] == "localjev-test"
    assert plan["shape"] == "python-pkg"
    decisions = {d["id"]: d for d in plan["decisions"]}
    assert decisions["shape"]["choice"] == "python-pkg"
    assert decisions["shape"]["probability"] == 0.82
    assert decisions["shape"]["confidence"] == 0.81
    assert decisions["strict"]["decision"] is True
    assert decisions["strict"]["value"] == 0.9
    assert decisions["tests"]["decision"] is False
    files = _files(plan)
    assert not any(f.startswith("tests/") for f in files)  # tests decided off


def test_malformed_shape_falls_back(monkeypatch):
    monkeypatch.delenv("CHEETAH_JEV_ENABLED", raising=False)
    body = {
        "model": "localjev-test",
        "answers": {
            "shape": {"type": "choice", "choice": "not-a-shape",
                      "probabilities": {"not-a-shape": 0.9}, "confidence": 0.5},
            "strict": {"type": "noul", "noul": 0.9},
            "tests": {"type": "noul", "noul": 0.9},
        },
    }
    with mock.patch("cheetah_jev._post_systemone", return_value=(200, body)):
        plan = decide_scaffold("Create lib/math.js exporting add with vitest tests")
    shape = next(d for d in plan["decisions"] if d["id"] == "shape")
    assert shape["source"] == "offline"
    assert shape["error"]
    # fell back to the regex classifier
    assert plan["shape"] == "node-lib"


def test_transient_status_retries_then_falls_back(monkeypatch):
    monkeypatch.delenv("CHEETAH_JEV_ENABLED", raising=False)
    with mock.patch("cheetah_jev._post_systemone",
                    side_effect=[(529, {"detail": "overloaded"}), (529, {"detail": "overloaded"}), (529, {"detail": "overloaded"})]) as post:
        plan = decide_scaffold("Build a CLI that reads two args")
    assert post.call_count == 3
    assert plan["source"] == "offline"
    assert "529" in plan["error"]
    assert plan["shape"] == "node-cli"


def test_strict_false_and_no_tests_knobs(monkeypatch):
    monkeypatch.setenv("CHEETAH_JEV_ENABLED", "0")
    plan = decide_scaffold("Create lib/math.js exporting add with vitest tests",
                           strict=False, tests=False)
    files = _files(plan)
    assert '"strict": false' in files["tsconfig.json"]
    assert "src/index.test.ts" not in files
    pkg = json.loads(files["package.json"])
    assert "test" not in pkg["scripts"]


def test_python_no_tests_omits_pytest_config(monkeypatch):
    monkeypatch.setenv("CHEETAH_JEV_ENABLED", "0")
    plan = decide_scaffold("Create a python package exporting clamp", tests=False)
    files = _files(plan)
    assert not any(f.startswith("tests/") for f in files)
    assert "pytest" not in files["pyproject.toml"]


def test_full_ledger_present_for_offline(monkeypatch):
    monkeypatch.setenv("CHEETAH_JEV_ENABLED", "0")
    plan = decide_scaffold("A FastAPI service exposing /health")
    ids = [d["id"] for d in plan["decisions"]]
    assert ids == ["shape", "strict", "tests"]
    assert plan["shape"] == "fastapi-service"