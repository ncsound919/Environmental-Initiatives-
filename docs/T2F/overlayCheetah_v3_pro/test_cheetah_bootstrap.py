"""Tests for the toolchain-backed bootstrap. Honest SKIP/ERROR paths only —
no live network is required."""

from pathlib import Path
from unittest import mock

from cheetah_scaffold import bootstrap_scaffold


def test_skip_when_no_tool_mapped(tmp_path: Path):
    result = bootstrap_scaffold(str(tmp_path), "crud-api")
    assert result["status"] == "SKIP"
    assert result["ok"] is True


def test_skip_when_command_missing(tmp_path: Path):
    with mock.patch("cheetah_scaffold.subprocess.run",
                    side_effect=FileNotFoundError("no such file")) as run:
        result = bootstrap_scaffold(str(tmp_path), "react-vite", name="demo")
    run.assert_called_once()
    assert result["status"] == "SKIP"
    assert "not available" in result["detail"]


def test_error_when_bootstrap_fails(tmp_path: Path):
    fake = mock.Mock(returncode=1, stdout="boom", stderr="")
    with mock.patch("cheetah_scaffold.subprocess.run", return_value=fake):
        result = bootstrap_scaffold(str(tmp_path), "react-vite", name="demo")
    assert result["status"] == "ERROR"
    assert result["ok"] is False
    assert "exit=1" in result["detail"]


def test_done_applies_fixes(tmp_path: Path):
    fake = mock.Mock(returncode=0, stdout="scaffolded ok", stderr="")
    with mock.patch("cheetah_scaffold.subprocess.run", return_value=fake):
        with mock.patch("cheetah_scaffold.apply_fixes", return_value={"written": ["README.md"]}) as fixes:
            result = bootstrap_scaffold(str(tmp_path), "react-vite", name="demo")
    fixes.assert_called_once_with(str(tmp_path.resolve()))
    assert result["status"] == "DONE"
    assert result["written"] == ["README.md"]
    assert result["notes"]


def test_command_uses_shape_template(tmp_path: Path):
    fake = mock.Mock(returncode=0, stdout="", stderr="")
    with mock.patch("cheetah_scaffold.subprocess.run", return_value=fake) as run:
        with mock.patch("cheetah_scaffold.apply_fixes", return_value={}):
            bootstrap_scaffold(str(tmp_path), "react-vite", name="myapp")
    args = run.call_args.args[0]
    assert args[:2] == ["npm", "create"]
    assert "myapp" in args