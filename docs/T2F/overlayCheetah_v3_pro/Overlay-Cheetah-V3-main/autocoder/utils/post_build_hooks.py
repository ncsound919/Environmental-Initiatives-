"""
Post-build hooks for linting, formatting, and testing
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass


# Use the current Python executable
PYTHON_EXE = sys.executable

# Timeouts for various operations (in seconds)
TOOL_DETECTION_TIMEOUT = 2  # Fast timeout for --version checks
LINTING_TIMEOUT = 180  # 3 minutes for linting/type checking large codebases
FORMATTING_TIMEOUT = 120  # 2 minutes for formatting
TESTING_TIMEOUT = 300  # 5 minutes for running tests


@dataclass
class LintResult:
    """Result from a linting/formatting operation"""

    tool: str
    success: bool
    output: str
    files_checked: int = 0
    issues_found: int = 0


class PostBuildHooks:
    """Execute post-build operations like linting and testing"""

    def __init__(self, output_dir: Path):
        """Initialize post-build hooks

        Args:
            output_dir: Directory containing generated files
        """
        self.output_dir = output_dir
        self.available_tools = self._detect_available_tools()

    def _detect_available_tools(self) -> Dict[str, bool]:
        """Detect which linting/formatting tools are available

        Returns:
            Dictionary of tool name to availability
        """
        tools = {}

        # Python tools
        for tool in ["black", "isort", "pylint", "flake8", "mypy", "ruff"]:
            try:
                result = subprocess.run(
                    [PYTHON_EXE, "-m", tool, "--version"],
                    capture_output=True,
                    timeout=TOOL_DETECTION_TIMEOUT,
                )
                tools[tool] = result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError):
                tools[tool] = False

        # JavaScript/TypeScript tools
        for tool in ["eslint", "prettier", "tsc"]:
            try:
                result = subprocess.run(
                    [tool, "--version"],
                    capture_output=True,
                    timeout=TOOL_DETECTION_TIMEOUT,
                )
                tools[tool] = result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError):
                tools[tool] = False

        return tools

    def format_python(self, files: Optional[List[Path]] = None) -> LintResult:
        """Format Python files with black

        Args:
            files: Specific files to format, or None for all

        Returns:
            LintResult
        """
        if not self.available_tools.get("black", False):
            return LintResult("black", False, "black not available")

        target = str(self.output_dir) if files is None else [str(f) for f in files]

        try:
            result = subprocess.run(
                [PYTHON_EXE, "-m", "black"]
                + ([target] if isinstance(target, str) else target),
                capture_output=True,
                timeout=FORMATTING_TIMEOUT,
                text=True,
            )

            return LintResult(
                tool="black",
                success=result.returncode == 0,
                output=result.stdout + result.stderr,
                files_checked=result.stdout.count("reformatted")
                + result.stdout.count("left unchanged"),
            )
        except Exception as e:
            return LintResult("black", False, str(e))

    def sort_imports(self, files: Optional[List[Path]] = None) -> LintResult:
        """Sort Python imports with isort

        Args:
            files: Specific files to process, or None for all

        Returns:
            LintResult
        """
        if not self.available_tools.get("isort", False):
            return LintResult("isort", False, "isort not available")

        target = str(self.output_dir) if files is None else [str(f) for f in files]

        try:
            result = subprocess.run(
                [PYTHON_EXE, "-m", "isort"]
                + ([target] if isinstance(target, str) else target),
                capture_output=True,
                timeout=FORMATTING_TIMEOUT,
                text=True,
            )

            return LintResult(
                tool="isort",
                success=result.returncode == 0,
                output=result.stdout + result.stderr,
            )
        except Exception as e:
            return LintResult("isort", False, str(e))

    def lint_python(self, files: Optional[List[Path]] = None) -> LintResult:
        """Lint Python files with ruff (or fallback to flake8)

        Args:
            files: Specific files to lint, or None for all

        Returns:
            LintResult
        """
        # Prefer ruff (faster)
        tool = (
            "ruff"
            if self.available_tools.get("ruff", False)
            else "flake8" if self.available_tools.get("flake8", False) else None
        )

        if not tool:
            return LintResult("ruff/flake8", False, "No Python linter available")

        target = str(self.output_dir) if files is None else [str(f) for f in files]

        try:
            result = subprocess.run(
                [PYTHON_EXE, "-m", tool]
                + ([target] if isinstance(target, str) else target),
                capture_output=True,
                timeout=LINTING_TIMEOUT,
                text=True,
            )

            issues = len(result.stdout.splitlines()) if result.returncode != 0 else 0

            return LintResult(
                tool=tool,
                success=result.returncode == 0,
                output=result.stdout + result.stderr,
                issues_found=issues,
            )
        except Exception as e:
            return LintResult(tool, False, str(e))

    def type_check_python(self, files: Optional[List[Path]] = None) -> LintResult:
        """Type check Python files with mypy

        Args:
            files: Specific files to check, or None for all

        Returns:
            LintResult
        """
        if not self.available_tools.get("mypy", False):
            return LintResult("mypy", False, "mypy not available")

        target = str(self.output_dir) if files is None else [str(f) for f in files]

        try:
            result = subprocess.run(
                [PYTHON_EXE, "-m", "mypy"]
                + ([target] if isinstance(target, str) else target),
                capture_output=True,
                timeout=LINTING_TIMEOUT,
                text=True,
            )

            issues = len([l for l in result.stdout.splitlines() if "error:" in l])

            return LintResult(
                tool="mypy",
                success=result.returncode == 0,
                output=result.stdout + result.stderr,
                issues_found=issues,
            )
        except Exception as e:
            return LintResult("mypy", False, str(e))

    def lint_javascript(self, files: Optional[List[Path]] = None) -> LintResult:
        """Lint JavaScript/TypeScript files with eslint

        Args:
            files: Specific files to lint, or None for all

        Returns:
            LintResult
        """
        if not self.available_tools.get("eslint", False):
            return LintResult("eslint", False, "eslint not available")

        target = str(self.output_dir) if files is None else [str(f) for f in files]

        try:
            result = subprocess.run(
                ["eslint"] + ([target] if isinstance(target, str) else target),
                capture_output=True,
                timeout=LINTING_TIMEOUT,
                text=True,
            )

            return LintResult(
                tool="eslint",
                success=result.returncode == 0,
                output=result.stdout + result.stderr,
            )
        except Exception as e:
            return LintResult("eslint", False, str(e))

    def format_javascript(self, files: Optional[List[Path]] = None) -> LintResult:
        """Format JavaScript/TypeScript files with prettier

        Args:
            files: Specific files to format, or None for all

        Returns:
            LintResult
        """
        if not self.available_tools.get("prettier", False):
            return LintResult("prettier", False, "prettier not available")

        target = str(self.output_dir) if files is None else [str(f) for f in files]

        try:
            result = subprocess.run(
                ["prettier", "--write"]
                + ([target] if isinstance(target, str) else target),
                capture_output=True,
                timeout=FORMATTING_TIMEOUT,
                text=True,
            )

            return LintResult(
                tool="prettier",
                success=result.returncode == 0,
                output=result.stdout + result.stderr,
            )
        except Exception as e:
            return LintResult("prettier", False, str(e))

    def run_tests(self, test_dir: Optional[Path] = None) -> LintResult:
        """Run pytest tests

        Args:
            test_dir: Directory containing tests, or None for default

        Returns:
            LintResult
        """
        target = str(test_dir) if test_dir else str(self.output_dir)

        try:
            result = subprocess.run(
                [PYTHON_EXE, "-m", "pytest", target, "-v"],
                capture_output=True,
                timeout=TESTING_TIMEOUT,
                text=True,
            )

            return LintResult(
                tool="pytest",
                success=result.returncode == 0,
                output=result.stdout + result.stderr,
            )
        except Exception as e:
            return LintResult("pytest", False, str(e))

    def get_available_tools(self) -> List[str]:
        """Get list of available tools

        Returns:
            List of tool names
        """
        return [tool for tool, available in self.available_tools.items() if available]
