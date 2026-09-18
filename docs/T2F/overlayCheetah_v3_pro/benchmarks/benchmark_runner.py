#!/usr/bin/env python3
"""
Benchmark Runner for Overlay Cheetah Version Comparison
======================================================
Comprehensive benchmarking tool to compare V1 (Autocoder), V2, and V3 PRO performance.

Usage:
    python benchmark_runner.py --all --cold     # Run all versions with cold start
    python benchmark_runner.py --all --warm     # Run all versions with warm start
    python benchmark_runner.py --v3 --cold      # Run only V3 with cold start
    python benchmark_runner.py --compare        # Compare previous results
"""

import argparse
import json
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configuration
VERSIONS = {
    "v1": {
        "name": "Autocoder V1",
        "script": "autocoder.py",
        "description": "Original autocoder implementation",
    },
    "v2": {
        "name": "Overlay Cheetah V2",
        "script": "improved_perfected_overlay_cheetah_v2.py",
        "description": "Improved V2 with optimizations",
    },
    "v3": {
        "name": "Overlay Cheetah V3 PRO",
        "script": "Overlay-Cheetah-V3-main/overlay_cheetah_v3_pro.py",
        "description": "Latest V3 PRO with advanced features",
    },
}

RESULTS_DIR = Path("benchmark_results")
REPORTS_DIR = Path("reports")


class BenchmarkRunner:
    """Manages benchmarking of different Overlay Cheetah versions"""

    def __init__(self):
        self.results: Dict[str, Any] = {}
        self.ensure_directories()

    def ensure_directories(self):
        """Create necessary directories"""
        RESULTS_DIR.mkdir(exist_ok=True)
        REPORTS_DIR.mkdir(exist_ok=True)

    def clear_caches(self, aggressive: bool = True):
        """Clear all possible caches for cold start"""
        print("🧹 Clearing caches for cold start...")

        # Clear V3 cache
        cache_dirs = [
            Path("cache"),
            Path(".cache"),
            Path("Overlay-Cheetah-V3-main/cache"),
            Path("out"),
            Path("templates/.cache"),
        ]

        for cache_dir in cache_dirs:
            if cache_dir.exists():
                try:
                    shutil.rmtree(cache_dir)
                    print(f"  ✓ Cleared {cache_dir}")
                except Exception as e:
                    print(f"  ⚠ Failed to clear {cache_dir}: {e}")

        if aggressive:
            # Clear npm cache
            try:
                subprocess.run(
                    ["npm", "cache", "clean", "--force"],
                    capture_output=True,
                    timeout=30,
                )
                print("  ✓ Cleared npm cache")
            except Exception as e:
                print(f"  ⚠ Failed to clear npm cache: {e}")

            # Clear pip cache
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "cache", "purge"],
                    capture_output=True,
                    timeout=30,
                )
                print("  ✓ Cleared pip cache")
            except Exception as e:
                print(f"  ⚠ Failed to clear pip cache: {e}")

    def run_version_benchmark(self, version: str, cache_policy: str) -> Dict[str, Any]:
        """Run benchmark for a specific version"""
        version_info = VERSIONS[version]
        script_path = Path(version_info["script"])

        if not script_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")

        print(f"\n🚀 Running {version_info['name']} benchmark...")
        print(f"   Script: {script_path}")
        print(f"   Cache policy: {cache_policy}")

        start_time = time.time()

        try:
            # Special handling for V3 PRO with built-in benchmark
            if version == "v3":
                cmd = [sys.executable, str(script_path), "--benchmark"]
                if cache_policy == "cold":
                    cmd.append("--cold")
                elif cache_policy == "warm":
                    cmd.append("--warm")

                # Save V3 results to temp file
                temp_result_file = RESULTS_DIR / f"temp_v3_{cache_policy}.json"
                cmd.extend(["--output-benchmark", str(temp_result_file)])

                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=300
                )

                duration = time.time() - start_time

                if result.returncode == 0 and temp_result_file.exists():
                    # Load detailed V3 results
                    v3_data = json.loads(temp_result_file.read_text())
                    temp_result_file.unlink()  # Clean up

                    return {
                        "version": version,
                        "name": version_info["name"],
                        "success": True,
                        "duration_sec": duration,
                        "cache_policy": cache_policy,
                        "timestamp": datetime.now().isoformat(),
                        "detailed_results": v3_data,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "platform": {
                            "system": platform.system(),
                            "machine": platform.machine(),
                            "python_version": platform.python_version(),
                        },
                    }
                else:
                    return {
                        "version": version,
                        "name": version_info["name"],
                        "success": False,
                        "duration_sec": duration,
                        "cache_policy": cache_policy,
                        "timestamp": datetime.now().isoformat(),
                        "error": f"Process failed with code {result.returncode}",
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "platform": {
                            "system": platform.system(),
                            "machine": platform.machine(),
                            "python_version": platform.python_version(),
                        },
                    }

            else:
                # For V1 and V2, run basic execution test
                cmd = [sys.executable, str(script_path)]

                # Add version-specific parameters if needed
                if version == "v2":
                    # V2 might have special flags
                    pass

                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=300, input="test\n"
                )

                duration = time.time() - start_time

                return {
                    "version": version,
                    "name": version_info["name"],
                    "success": result.returncode == 0,
                    "duration_sec": duration,
                    "cache_policy": cache_policy,
                    "timestamp": datetime.now().isoformat(),
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "platform": {
                        "system": platform.system(),
                        "machine": platform.machine(),
                        "python_version": platform.python_version(),
                    },
                }

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return {
                "version": version,
                "name": version_info["name"],
                "success": False,
                "duration_sec": duration,
                "cache_policy": cache_policy,
                "timestamp": datetime.now().isoformat(),
                "error": "Process timed out after 300 seconds",
                "platform": {
                    "system": platform.system(),
                    "machine": platform.machine(),
                    "python_version": platform.python_version(),
                },
            }
        except Exception as e:
            duration = time.time() - start_time
            return {
                "version": version,
                "name": version_info["name"],
                "success": False,
                "duration_sec": duration,
                "cache_policy": cache_policy,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "platform": {
                    "system": platform.system(),
                    "machine": platform.machine(),
                    "python_version": platform.python_version(),
                },
            }

    def run_comparison_suite(
        self, versions: List[str], cache_policy: str
    ) -> Dict[str, Any]:
        """Run full comparison suite"""
        print(f"\n{'=' * 60}")
        print(f"OVERLAY CHEETAH BENCHMARK SUITE")
        print(f"Cache Policy: {cache_policy.upper()}")
        print(f"Versions: {', '.join([VERSIONS[v]['name'] for v in versions])}")
        print(f"{'=' * 60}")

        if cache_policy == "cold":
            self.clear_caches()

        results = {
            "suite_info": {
                "timestamp": datetime.now().isoformat(),
                "cache_policy": cache_policy,
                "versions_tested": versions,
                "platform": {
                    "system": platform.system(),
                    "machine": platform.machine(),
                    "python_version": platform.python_version(),
                },
            },
            "results": {},
        }

        for version in versions:
            try:
                if cache_policy == "cold":
                    # Clear caches before each version for truly isolated cold start
                    self.clear_caches()

                result = self.run_version_benchmark(version, cache_policy)
                results["results"][version] = result

                # Print immediate feedback
                status = "✓" if result["success"] else "✗"
                duration = result["duration_sec"]
                print(f"  {status} {result['name']}: {duration:.2f}s")

                if not result["success"]:
                    print(f"    Error: {result.get('error', 'Unknown error')}")

            except Exception as e:
                print(f"  ✗ {VERSIONS[version]['name']}: Failed to run ({e})")
                results["results"][version] = {
                    "version": version,
                    "name": VERSIONS[version]["name"],
                    "success": False,
                    "error": str(e),
                    "cache_policy": cache_policy,
                    "timestamp": datetime.now().isoformat(),
                }

        return results

    def save_results(
        self, results: Dict[str, Any], filename: Optional[str] = None
    ) -> Path:
        """Save benchmark results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cache_policy = results["suite_info"]["cache_policy"]
            filename = f"benchmark_{cache_policy}_{timestamp}.json"

        result_file = RESULTS_DIR / filename
        result_file.write_text(json.dumps(results, indent=2))
        print(f"\n📊 Results saved to: {result_file}")
        return result_file

    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate human-readable report"""
        report_lines = []
        suite_info = results["suite_info"]

        report_lines.append("# Overlay Cheetah Benchmark Report")
        report_lines.append("")
        report_lines.append(f"**Generated:** {suite_info['timestamp']}")
        report_lines.append(f"**Cache Policy:** {suite_info['cache_policy'].upper()}")
        report_lines.append(
            f"**Platform:** {suite_info['platform']['system']} {suite_info['platform']['machine']}"
        )
        report_lines.append(f"**Python:** {suite_info['platform']['python_version']}")
        report_lines.append("")

        # Summary table
        report_lines.append("## Performance Summary")
        report_lines.append("")
        report_lines.append("| Version | Status | Duration | Notes |")
        report_lines.append("|---------|---------|----------|-------|")

        for version, result in results["results"].items():
            status = "PASS" if result["success"] else "FAIL"
            duration = (
                f"{result['duration_sec']:.2f}s" if "duration_sec" in result else "N/A"
            )
            notes = ""

            if not result["success"]:
                notes = result.get("error", "Unknown error")[:50]
                if len(notes) == 50:
                    notes += "..."

            report_lines.append(
                f"| {result['name']} | {status} | {duration} | {notes} |"
            )

        report_lines.append("")

        # Detailed results
        report_lines.append("## Detailed Results")
        report_lines.append("")

        for version, result in results["results"].items():
            report_lines.append(f"### {result['name']}")
            report_lines.append("")

            if result["success"]:
                report_lines.append(
                    f"- **Duration:** {result['duration_sec']:.2f} seconds"
                )

                # Add V3-specific detailed metrics
                if "detailed_results" in result:
                    detailed = result["detailed_results"]
                    if "steps" in detailed:
                        report_lines.append("- **Step Performance:**")
                        for step in detailed["steps"]:
                            step_status = (
                                "PASS" if step.get("success", False) else "FAIL"
                            )
                            report_lines.append(
                                f"  - {step['name']}: {step_status} {step.get('duration_sec', 0):.3f}s"
                            )

                    if "resource_monitoring" in detailed and detailed[
                        "resource_monitoring"
                    ]["summary"].get("available"):
                        rm = detailed["resource_monitoring"]["summary"]
                        report_lines.append("- **Resource Usage:**")
                        report_lines.append(f"  - CPU Peak: {rm['cpu']['max']:.1f}%")
                        report_lines.append(
                            f"  - Memory Peak: {rm['memory']['max_percent']:.1f}%"
                        )
                        report_lines.append(f"  - Duration: {rm['duration_sec']:.1f}s")

            else:
                report_lines.append(f"- **Status:** Failed")
                report_lines.append(f"- **Error:** {result.get('error', 'Unknown')}")
                if result.get("stderr"):
                    report_lines.append(f"- **Stderr:** ```{result['stderr'][:200]}```")

            report_lines.append("")

        return "\n".join(report_lines)

    def save_report(
        self, results: Dict[str, Any], filename: Optional[str] = None
    ) -> Path:
        """Save markdown report"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cache_policy = results["suite_info"]["cache_policy"]
            filename = f"benchmark_report_{cache_policy}_{timestamp}.md"

        report_content = self.generate_report(results)
        report_file = REPORTS_DIR / filename
        report_file.write_text(report_content, encoding="utf-8")
        print(f"📄 Report saved to: {report_file}")
        return report_file

    def compare_previous_results(self):
        """Compare previous benchmark results"""
        result_files = list(RESULTS_DIR.glob("benchmark_*.json"))

        if len(result_files) < 2:
            print("❌ Not enough previous results to compare")
            return

        print(f"📊 Found {len(result_files)} previous benchmark results")

        # Group by cache policy
        cold_results = []
        warm_results = []

        for file in result_files:
            try:
                data = json.loads(file.read_text())
                policy = data["suite_info"]["cache_policy"]
                if policy == "cold":
                    cold_results.append((file, data))
                elif policy == "warm":
                    warm_results.append((file, data))
            except Exception as e:
                print(f"⚠ Failed to load {file}: {e}")

        # Show comparison
        for policy, results in [("Cold", cold_results), ("Warm", warm_results)]:
            if not results:
                continue

            print(f"\n## {policy} Start Results")
            print("| Date | V1 Duration | V2 Duration | V3 Duration |")
            print("|------|-------------|-------------|-------------|")

            for file, data in sorted(
                results, key=lambda x: x[1]["suite_info"]["timestamp"]
            ):
                timestamp = datetime.fromisoformat(
                    data["suite_info"]["timestamp"]
                ).strftime("%m/%d %H:%M")

                durations = {}
                for version, result in data["results"].items():
                    if result["success"]:
                        durations[version] = f"{result['duration_sec']:.1f}s"
                    else:
                        durations[version] = "FAIL"

                v1_dur = durations.get("v1", "N/A")
                v2_dur = durations.get("v2", "N/A")
                v3_dur = durations.get("v3", "N/A")

                print(f"| {timestamp} | {v1_dur} | {v2_dur} | {v3_dur} |")


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark runner for Overlay Cheetah versions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--all", action="store_true", help="Run all versions (V1, V2, V3)"
    )
    parser.add_argument("--v1", action="store_true", help="Run Autocoder V1 only")
    parser.add_argument("--v2", action="store_true", help="Run Overlay Cheetah V2 only")
    parser.add_argument(
        "--v3", action="store_true", help="Run Overlay Cheetah V3 PRO only"
    )

    parser.add_argument(
        "--cold", action="store_true", help="Force cold start (clear all caches)"
    )
    parser.add_argument(
        "--warm", action="store_true", help="Force warm start (preserve caches)"
    )

    parser.add_argument(
        "--compare", action="store_true", help="Compare previous benchmark results"
    )
    parser.add_argument("--output", type=str, help="Custom output filename")

    args = parser.parse_args()

    if args.compare:
        runner = BenchmarkRunner()
        runner.compare_previous_results()
        return

    # Determine versions to test
    versions_to_test = []
    if args.all:
        versions_to_test = ["v1", "v2", "v3"]
    else:
        if args.v1:
            versions_to_test.append("v1")
        if args.v2:
            versions_to_test.append("v2")
        if args.v3:
            versions_to_test.append("v3")

    if not versions_to_test:
        print("No versions specified. Use --all or specific version flags.")
        parser.print_help()
        return

    # Determine cache policy
    if args.cold and args.warm:
        print("Cannot specify both --cold and --warm")
        return
    elif args.cold:
        cache_policy = "cold"
    elif args.warm:
        cache_policy = "warm"
    else:
        cache_policy = "auto"

    # Run benchmarks
    runner = BenchmarkRunner()
    results = runner.run_comparison_suite(versions_to_test, cache_policy)

    # Save results
    runner.save_results(results, args.output)
    runner.save_report(results)

    print("\nBenchmark suite completed!")


if __name__ == "__main__":
    main()
