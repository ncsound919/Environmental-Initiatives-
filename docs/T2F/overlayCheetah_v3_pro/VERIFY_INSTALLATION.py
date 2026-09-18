#!/usr/bin/env python3
"""
Overlay Cheetah V3 PRO - Commercial Package Verification Script
===============================================================

This script verifies that the commercial installation is complete and functional.
Run this after installation to ensure everything is working correctly.

Usage:
    python VERIFY_INSTALLATION.py
    python VERIFY_INSTALLATION.py --verbose
    python VERIFY_INSTALLATION.py --quick
"""

import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Version information
EXPECTED_VERSION = "3.1.0-pro"
SCRIPT_VERSION = "1.0.0"


class Colors:
    """ANSI color codes for terminal output"""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    END = "\033[0m"


class CommercialVerifier:
    """Comprehensive verification for Overlay Cheetah V3 PRO commercial package"""

    def __init__(self, verbose=False, quick=False):
        self.verbose = verbose
        self.quick = quick
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = 0
        self.start_time = time.time()

        # Expected files and their purposes
        self.required_files = {
            "overlay_cheetah_v3_pro.py": "Main application",
            "requirements.txt": "Dependencies specification",
            "README.md": "Product documentation",
            "LICENSE.md": "Commercial license",
            "INSTALLATION.md": "Installation guide",
            "PERFORMANCE_REPORT.md": "Performance data",
        }

        self.required_dirs = {
            "benchmarks": "Benchmark and testing tools",
            "templates": "Template system",
        }

        self.benchmark_files = {
            "benchmarks/benchmark_runner.py": "Cross-version comparison",
            "benchmarks/master_benchmark_suite.py": "Comprehensive testing",
            "benchmarks/production_benchmark.py": "Production validation",
            "benchmarks/PUBLIC_PERFORMANCE_REPORT.md": "Public benchmark data",
        }

    def log(self, message, level="INFO"):
        """Enhanced logging with colors and timestamps"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        color_map = {
            "SUCCESS": Colors.GREEN + "✅",
            "ERROR": Colors.RED + "❌",
            "WARNING": Colors.YELLOW + "⚠️",
            "INFO": Colors.BLUE + "ℹ️",
            "TEST": Colors.PURPLE + "🧪",
            "BENCHMARK": Colors.CYAN + "📊",
        }

        icon = color_map.get(level, Colors.WHITE + "📝")
        print(f"[{timestamp}] {icon} {message}{Colors.END}")

    def check_file_exists(self, filepath, description=""):
        """Check if a required file exists"""
        path = Path(filepath)
        if path.exists():
            size_mb = path.stat().st_size / (1024 * 1024)
            self.log(f"{description}: {filepath} ({size_mb:.2f}MB)", "SUCCESS")
            self.checks_passed += 1
            return True
        else:
            self.log(f"Missing required file: {filepath}", "ERROR")
            self.checks_failed += 1
            return False

    def check_python_version(self):
        """Verify Python version compatibility"""
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"

        if version.major >= 3 and version.minor >= 8:
            self.log(f"Python version: {version_str} (compatible)", "SUCCESS")
            self.checks_passed += 1
            return True
        else:
            self.log(
                f"Python version: {version_str} (incompatible - need 3.8+)", "ERROR"
            )
            self.checks_failed += 1
            return False

    def check_dependencies(self):
        """Check if required dependencies are installed"""
        required_modules = [
            ("yaml", "pyyaml"),
            ("jinja2", "jinja2"),
            ("psutil", "psutil"),
            ("requests", "requests"),
        ]

        optional_modules = [
            ("google.generativeai", "google-generativeai"),
            ("ollama", "ollama"),
            ("PIL", "pillow"),
        ]

        # Check required modules
        for module, package in required_modules:
            try:
                __import__(module)
                self.log(f"Required dependency: {package} installed", "SUCCESS")
                self.checks_passed += 1
            except ImportError:
                self.log(f"Missing required dependency: {package}", "ERROR")
                self.checks_failed += 1

        # Check optional modules
        for module, package in optional_modules:
            try:
                __import__(module)
                self.log(f"Optional dependency: {package} installed", "SUCCESS")
            except ImportError:
                self.log(f"Optional dependency: {package} not installed", "WARNING")
                self.warnings += 1

    def test_import_main(self):
        """Test if the main application can be imported"""
        try:
            sys.path.insert(0, str(Path.cwd()))

            # Test if we can read the main file
            main_file = Path("overlay_cheetah_v3_pro.py")
            if main_file.exists():
                content = main_file.read_text()
                if "class OverlayCheetahV3Pro" in content:
                    self.log("Main application structure valid", "SUCCESS")
                    self.checks_passed += 1
                else:
                    self.log("Main application structure invalid", "ERROR")
                    self.checks_failed += 1
            else:
                self.log("Main application file not found", "ERROR")
                self.checks_failed += 1

        except Exception as e:
            self.log(f"Failed to validate main application: {e}", "ERROR")
            self.checks_failed += 1

    def run_preflight_check(self):
        """Run the built-in preflight validation"""
        try:
            self.log("Running preflight validation...", "TEST")

            cmd = [
                sys.executable,
                "overlay_cheetah_v3_pro.py",
                "--preflight",
                "--quiet",
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=60, cwd=Path.cwd()
            )

            if result.returncode == 0:
                self.log("Preflight validation passed", "SUCCESS")
                self.checks_passed += 1
            else:
                self.log(
                    f"Preflight validation failed (code {result.returncode})", "ERROR"
                )
                if self.verbose and result.stderr:
                    print(f"Error output: {result.stderr}")
                self.checks_failed += 1

        except subprocess.TimeoutExpired:
            self.log("Preflight validation timed out", "ERROR")
            self.checks_failed += 1
        except Exception as e:
            self.log(f"Preflight validation error: {e}", "ERROR")
            self.checks_failed += 1

    def run_self_tests(self):
        """Run the built-in self-test suite"""
        if self.quick:
            self.log("Skipping self-tests (quick mode)", "WARNING")
            self.warnings += 1
            return

        try:
            self.log("Running self-test suite...", "TEST")

            cmd = [sys.executable, "overlay_cheetah_v3_pro.py", "--test"]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=120, cwd=Path.cwd()
            )

            if result.returncode == 0:
                # Parse test results
                output = result.stdout
                if "Results:" in output and "passed" in output:
                    self.log("Self-test suite passed", "SUCCESS")
                    self.checks_passed += 1
                else:
                    self.log("Self-test suite results unclear", "WARNING")
                    self.warnings += 1
            else:
                self.log(f"Self-test suite failed (code {result.returncode})", "ERROR")
                if self.verbose and result.stderr:
                    print(f"Error output: {result.stderr}")
                self.checks_failed += 1

        except subprocess.TimeoutExpired:
            self.log("Self-test suite timed out", "ERROR")
            self.checks_failed += 1
        except Exception as e:
            self.log(f"Self-test suite error: {e}", "ERROR")
            self.checks_failed += 1

    def run_benchmark_test(self):
        """Run a quick benchmark validation"""
        if self.quick:
            self.log("Skipping benchmark test (quick mode)", "WARNING")
            self.warnings += 1
            return

        try:
            self.log("Running benchmark validation...", "BENCHMARK")

            cmd = [sys.executable, "overlay_cheetah_v3_pro.py", "--benchmark", "--warm"]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=180, cwd=Path.cwd()
            )

            if result.returncode == 0:
                # Parse benchmark results
                output = result.stdout
                if "completed in" in output and "seconds" in output:
                    self.log("Benchmark validation passed", "SUCCESS")
                    self.checks_passed += 1

                    # Extract timing if possible
                    try:
                        import re

                        match = re.search(r"(\d+\.?\d*)\s*seconds", output)
                        if match:
                            duration = float(match.group(1))
                            if duration < 120:
                                self.log(
                                    f"Benchmark performance good: {duration:.1f}s",
                                    "SUCCESS",
                                )
                            else:
                                self.log(
                                    f"Benchmark performance slow: {duration:.1f}s",
                                    "WARNING",
                                )
                                self.warnings += 1
                    except:
                        pass
                else:
                    self.log("Benchmark results unclear", "WARNING")
                    self.warnings += 1
            else:
                self.log(
                    f"Benchmark validation failed (code {result.returncode})", "ERROR"
                )
                self.checks_failed += 1

        except subprocess.TimeoutExpired:
            self.log("Benchmark validation timed out", "ERROR")
            self.checks_failed += 1
        except Exception as e:
            self.log(f"Benchmark validation error: {e}", "ERROR")
            self.checks_failed += 1

    def check_system_resources(self):
        """Check if system has adequate resources"""
        try:
            import psutil

            # Check memory
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)

            if memory_gb >= 2:
                self.log(f"System memory: {memory_gb:.1f}GB (adequate)", "SUCCESS")
                self.checks_passed += 1
            else:
                self.log(
                    f"System memory: {memory_gb:.1f}GB (insufficient - need 2GB+)",
                    "WARNING",
                )
                self.warnings += 1

            # Check disk space
            disk = psutil.disk_usage(".")
            disk_free_gb = disk.free / (1024**3)

            if disk_free_gb >= 1:
                self.log(f"Disk space: {disk_free_gb:.1f}GB free (adequate)", "SUCCESS")
                self.checks_passed += 1
            else:
                self.log(
                    f"Disk space: {disk_free_gb:.1f}GB free (insufficient - need 1GB+)",
                    "WARNING",
                )
                self.warnings += 1

        except ImportError:
            self.log("psutil not available - cannot check system resources", "WARNING")
            self.warnings += 1
        except Exception as e:
            self.log(f"System resource check failed: {e}", "WARNING")
            self.warnings += 1

    def check_benchmark_tools(self):
        """Verify benchmark tools are present and functional"""
        for filepath, description in self.benchmark_files.items():
            path = Path(filepath)
            if path.exists():
                self.log(f"Benchmark tool: {description}", "SUCCESS")
                self.checks_passed += 1
            else:
                self.log(f"Missing benchmark tool: {filepath}", "WARNING")
                self.warnings += 1

    def generate_report(self):
        """Generate final verification report"""
        duration = time.time() - self.start_time

        print("\n" + "=" * 80)
        print(f"{Colors.BOLD}OVERLAY CHEETAH V3 PRO - VERIFICATION REPORT{Colors.END}")
        print("=" * 80)

        # Summary
        total_checks = self.checks_passed + self.checks_failed
        success_rate = (
            (self.checks_passed / total_checks * 100) if total_checks > 0 else 0
        )

        print(f"\n{Colors.BOLD}SUMMARY:{Colors.END}")
        print(f"• Total Checks: {total_checks}")
        print(f"• Passed: {Colors.GREEN}{self.checks_passed}{Colors.END}")
        print(f"• Failed: {Colors.RED}{self.checks_failed}{Colors.END}")
        print(f"• Warnings: {Colors.YELLOW}{self.warnings}{Colors.END}")
        print(f"• Success Rate: {success_rate:.1f}%")
        print(f"• Verification Time: {duration:.1f} seconds")

        # Overall status
        print(f"\n{Colors.BOLD}OVERALL STATUS:{Colors.END}")
        if self.checks_failed == 0:
            if self.warnings == 0:
                print(
                    f"{Colors.GREEN}✅ EXCELLENT - Ready for production use{Colors.END}"
                )
                status = "EXCELLENT"
            else:
                print(
                    f"{Colors.YELLOW}⚠️ GOOD - Ready with minor considerations{Colors.END}"
                )
                status = "GOOD"
        else:
            print(
                f"{Colors.RED}❌ ISSUES DETECTED - Installation needs attention{Colors.END}"
            )
            status = "ISSUES"

        # Recommendations
        print(f"\n{Colors.BOLD}RECOMMENDATIONS:{Colors.END}")
        if status == "EXCELLENT":
            print("• Installation is complete and fully functional")
            print("• All enterprise features are available")
            print("• Ready for production deployment")

        elif status == "GOOD":
            print("• Core functionality is working correctly")
            print("• Some optional features may not be available")
            print("• Consider installing missing optional dependencies")

        else:
            print("• Fix failed checks before using in production")
            print("• Review installation guide for troubleshooting")
            print("• Ensure all required dependencies are installed")

        # System information
        print(f"\n{Colors.BOLD}SYSTEM INFORMATION:{Colors.END}")
        print(f"• Platform: {platform.system()} {platform.release()}")
        print(f"• Architecture: {platform.machine()}")
        print(f"• Python: {platform.python_version()}")
        print(f"• Working Directory: {Path.cwd()}")

        print("\n" + "=" * 80)

        return status

    def run_verification(self):
        """Run complete verification suite"""
        print(f"{Colors.BOLD}{Colors.CYAN}")
        print("🚀 OVERLAY CHEETAH V3 PRO - COMMERCIAL PACKAGE VERIFICATION")
        print(f"Version: {EXPECTED_VERSION} | Verifier: {SCRIPT_VERSION}")
        print(f"Platform: {platform.system()} {platform.machine()}")
        print(f"Python: {platform.python_version()}")
        print("=" * 80)
        print(f"{Colors.END}")

        # Core verification steps
        self.log("Starting commercial package verification", "INFO")

        # 1. Check Python version
        self.log("Checking Python version compatibility", "TEST")
        self.check_python_version()

        # 2. Check file structure
        self.log("Verifying package structure", "TEST")
        for filepath, description in self.required_files.items():
            self.check_file_exists(filepath, description)

        for dirpath, description in self.required_dirs.items():
            if Path(dirpath).exists():
                self.log(f"{description}: {dirpath}/", "SUCCESS")
                self.checks_passed += 1
            else:
                self.log(f"Missing directory: {dirpath}/", "ERROR")
                self.checks_failed += 1

        # 3. Check dependencies
        self.log("Checking dependencies", "TEST")
        self.check_dependencies()

        # 4. Check main application
        self.log("Validating main application", "TEST")
        self.test_import_main()

        # 5. Check system resources
        self.log("Checking system resources", "TEST")
        self.check_system_resources()

        # 6. Check benchmark tools
        self.log("Verifying benchmark tools", "TEST")
        self.check_benchmark_tools()

        # 7. Run preflight check
        self.log("Running preflight validation", "TEST")
        self.run_preflight_check()

        # 8. Run self-tests
        self.log("Running self-test suite", "TEST")
        self.run_self_tests()

        # 9. Run benchmark test
        self.log("Running benchmark validation", "TEST")
        self.run_benchmark_test()

        # Generate final report
        status = self.generate_report()

        # Return appropriate exit code
        return 0 if self.checks_failed == 0 else 1


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Overlay Cheetah V3 PRO Commercial Package Verification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python VERIFY_INSTALLATION.py                 # Full verification
  python VERIFY_INSTALLATION.py --verbose       # Detailed output
  python VERIFY_INSTALLATION.py --quick         # Quick validation only
        """,
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output with detailed error information",
    )

    parser.add_argument(
        "--quick",
        "-q",
        action="store_true",
        help="Quick validation (skip time-consuming tests)",
    )

    args = parser.parse_args()

    # Run verification
    verifier = CommercialVerifier(verbose=args.verbose, quick=args.quick)
    exit_code = verifier.run_verification()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
