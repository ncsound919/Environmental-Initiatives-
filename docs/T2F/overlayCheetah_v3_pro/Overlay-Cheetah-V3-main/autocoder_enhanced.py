#!/usr/bin/env python3
"""
Enhanced AutoCoder with smart template matching, parallel generation, and incremental builds
- Backwards compatible with original autocoder.py
- Adds new features: parallel generation, incremental builds, dry-run, better error handling
"""
from pathlib import Path
import argparse
import time
import json
import subprocess
import sys
from typing import Dict, Any, List, Optional
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

# Import new features if available
try:
    from autocoder.core.parallel_generator import ParallelGenerator, GenerationResult

    ENHANCED_FEATURES = True
except ImportError:
    ENHANCED_FEATURES = False

ROOT = Path(__file__).resolve().parent
TPL_DIR = ROOT / "templates"
TASK_DIR = ROOT / "tasks"
OUT_DIR = ROOT / "out"
REPORTS_DIR = ROOT / "reports"
CACHE_DIR = ROOT / ".cache"

# Create directories
REPORTS_DIR.mkdir(exist_ok=True)
OUT_DIR.mkdir(exist_ok=True)


def load_yaml(p: Path) -> Dict[str, Any]:
    """Load YAML file"""
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def render_file(env: Environment, tpl_name: str, context: Dict[str, Any]) -> str:
    """Render a Jinja2 template"""
    tpl = env.get_template(tpl_name)
    return tpl.render(**context)


def write_text(path: Path, text: str):
    """Write text to file, creating parent directories"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(text)


def run(cmd: List[str], cwd: Optional[Path] = None) -> int:
    """Run a command and return exit code"""
    try:
        return subprocess.run(cmd, check=False, cwd=cwd, capture_output=True).returncode
    except FileNotFoundError:
        return 127


def validate_template(env: Environment, tpl_name: str) -> Optional[str]:
    """Validate template syntax

    Args:
        env: Jinja2 environment
        tpl_name: Template name

    Returns:
        Error message if invalid, None if valid
    """
    try:
        env.get_template(tpl_name)
        return None
    except Exception as e:
        return str(e)


def handle_task_legacy(
    task_path: Path,
    format_code: bool = True,
    run_tests: bool = False,
    dry_run: bool = False,
) -> dict:
    """Legacy task handler (original implementation)"""
    env = Environment(
        loader=FileSystemLoader(str(TPL_DIR)),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    spec = load_yaml(task_path)
    task_id = spec.get("task_id", task_path.stem)
    files = spec.get("files", [])
    results = {"task_id": task_id, "generated": [], "errors": [], "warnings": []}

    for f in files:
        tpl = f["template"]
        out_rel = f["output"]
        ctx = f.get("context", {})

        # Validate template
        error = validate_template(env, tpl)
        if error:
            results["errors"].append(
                {
                    "file": out_rel,
                    "template": tpl,
                    "error": f"Template validation failed: {error}",
                }
            )
            continue

        try:
            rendered = render_file(env, tpl, ctx)

            if not dry_run:
                out_path = OUT_DIR / out_rel
                write_text(out_path, rendered)
                results["generated"].append(str(out_rel))
            else:
                results["generated"].append(f"{out_rel} (dry-run)")

        except Exception as e:
            results["errors"].append(
                {"file": out_rel, "template": tpl, "error": str(e)}
            )

    # Format with black if available
    if format_code and not dry_run:
        ret = run([sys.executable, "-m", "black", str(OUT_DIR)])
        if ret != 0:
            results["warnings"].append("Code formatting failed or black not installed")

    # Optional pytest run
    if run_tests and not dry_run:
        ret = run([sys.executable, "-m", "pytest", str(OUT_DIR)])
        if ret != 0:
            results["warnings"].append("Tests failed or pytest not available")

    # Write a report
    report_path = REPORTS_DIR / f"{task_id}.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    return results


def handle_task_enhanced(
    task_path: Path,
    format_code: bool = True,
    run_tests: bool = False,
    dry_run: bool = False,
    parallel: bool = True,
    incremental: bool = True,
) -> dict:
    """Enhanced task handler with new features"""
    spec = load_yaml(task_path)
    task_id = spec.get("task_id", task_path.stem)
    files = spec.get("files", [])

    # Use parallel generator
    generator = ParallelGenerator(
        templates_dir=TPL_DIR, output_dir=OUT_DIR, cache_dir=CACHE_DIR, max_workers=4
    )

    # Prepare tasks for generation
    tasks = []
    for f in files:
        tasks.append(
            {
                "task_id": f'{task_id}_{f["output"]}',
                "template": f["template"],
                "output": f["output"],
                "context": f.get("context", {}),
            }
        )

    # Progress callback
    def on_progress(result: GenerationResult):
        status = "✓" if result.success else "✗"
        msg = f"{status} {result.output_path}"
        if result.skipped:
            msg += f" (skipped: {result.reason})"
        elif result.error:
            msg += f" - Error: {result.error}"
        print(f"  {msg}")

    # Generate files
    if parallel:
        generation_results = generator.generate_parallel(
            tasks,
            incremental=incremental,
            dry_run=dry_run,
            progress_callback=on_progress,
        )
    else:
        generation_results = generator.generate_sequential(
            tasks,
            incremental=incremental,
            dry_run=dry_run,
            progress_callback=on_progress,
        )

    # Compile results
    results = {
        "task_id": task_id,
        "generated": [],
        "errors": [],
        "warnings": [],
        "skipped": [],
    }

    for res in generation_results:
        if res.success:
            if res.skipped:
                results["skipped"].append(
                    {"file": res.output_path, "reason": res.reason}
                )
            else:
                results["generated"].append(res.output_path)
        else:
            results["errors"].append({"file": res.output_path, "error": res.error})

    # Format with black if available
    if format_code and not dry_run and results["generated"]:
        ret = run([sys.executable, "-m", "black", str(OUT_DIR)])
        if ret != 0:
            results["warnings"].append("Code formatting failed or black not installed")

    # Optional pytest run
    if run_tests and not dry_run:
        ret = run([sys.executable, "-m", "pytest", str(OUT_DIR)])
        if ret != 0:
            results["warnings"].append("Tests failed or pytest not available")

    # Write report
    report_path = REPORTS_DIR / f"{task_id}.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    return results


def scan_once(
    format_code: bool,
    run_tests: bool,
    dry_run: bool = False,
    parallel: bool = True,
    incremental: bool = True,
    use_enhanced: bool = True,
):
    """Scan and process all pending tasks"""
    if not TASK_DIR.exists():
        print(f"[AutoCoder] Task directory {TASK_DIR} does not exist. Creating it...")
        TASK_DIR.mkdir(parents=True, exist_ok=True)
        print(f"[AutoCoder] Place .yaml task files in {TASK_DIR} to process them.")
        return

    tasks = list(TASK_DIR.glob("*.yaml"))
    if not tasks:
        print(f"[AutoCoder] No task files found in {TASK_DIR}")
        return

    for p in tasks:
        done_flag = p.with_suffix(".done")
        if done_flag.exists():
            continue

        print(f"\n[AutoCoder] Processing task: {p.name}")

        # Choose handler
        if use_enhanced and ENHANCED_FEATURES:
            res = handle_task_enhanced(
                p,
                format_code=format_code,
                run_tests=run_tests,
                dry_run=dry_run,
                parallel=parallel,
                incremental=incremental,
            )
        else:
            res = handle_task_legacy(
                p, format_code=format_code, run_tests=run_tests, dry_run=dry_run
            )

        # Mark as done
        if not dry_run:
            done_flag.write_text("ok")

        # Print summary
        print(f"\n[AutoCoder] Task {p.name} completed:")
        print(f"  Generated: {len(res['generated'])} files")
        if res.get("skipped"):
            print(f"  Skipped: {len(res['skipped'])} files (unchanged)")
        print(f"  Errors: {len(res['errors'])}")
        if res.get("warnings"):
            print(f"  Warnings: {len(res['warnings'])}")

        # Show errors
        for err in res["errors"]:
            print(
                f"  ✗ Error in {err.get('file', 'unknown')}: {err.get('error', 'unknown error')}"
            )


def watch_loop(
    interval: float,
    format_code: bool,
    run_tests: bool,
    dry_run: bool,
    parallel: bool,
    incremental: bool,
    use_enhanced: bool,
):
    """Watch task directory and process new tasks"""
    print(f"[AutoCoder] Watching {TASK_DIR} every {interval}s. Ctrl+C to stop.")
    if use_enhanced and ENHANCED_FEATURES:
        print(
            "[AutoCoder] Enhanced features enabled (parallel, incremental, smart matching)"
        )

    while True:
        scan_once(
            format_code=format_code,
            run_tests=run_tests,
            dry_run=dry_run,
            parallel=parallel,
            incremental=incremental,
            use_enhanced=use_enhanced,
        )
        time.sleep(interval)


def main():
    """Main entry point"""
    ap = argparse.ArgumentParser(
        description="Enhanced AutoCoder - Template-based code generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process tasks once
  %(prog)s --once
  
  # Watch mode with parallel generation
  %(prog)s --parallel
  
  # Dry run to preview changes
  %(prog)s --once --dry-run
  
  # Disable incremental builds
  %(prog)s --no-incremental
        """,
    )

    ap.add_argument(
        "--once", action="store_true", help="Process pending tasks once and exit"
    )
    ap.add_argument(
        "--interval",
        type=float,
        default=3.0,
        help="Watch interval in seconds (default: 3.0)",
    )
    ap.add_argument(
        "--no-format", action="store_true", help="Skip code formatting with black"
    )
    ap.add_argument("--test", action="store_true", help="Run pytest after generation")
    ap.add_argument(
        "--dry-run", action="store_true", help="Simulate without writing files"
    )
    ap.add_argument(
        "--no-parallel",
        action="store_true",
        help="Disable parallel generation (enabled by default)",
    )
    ap.add_argument(
        "--no-incremental",
        action="store_true",
        help="Disable incremental builds (enabled by default)",
    )
    ap.add_argument(
        "--legacy",
        action="store_true",
        help="Use legacy handler (disable enhanced features)",
    )
    ap.add_argument(
        "--clear-cache", action="store_true", help="Clear build cache and exit"
    )

    args = ap.parse_args()

    # Handle cache clearing
    if args.clear_cache:
        if CACHE_DIR.exists():
            for f in CACHE_DIR.glob("*.hash"):
                f.unlink()
            print(f"[AutoCoder] Cache cleared: {CACHE_DIR}")
        else:
            print(f"[AutoCoder] No cache to clear")
        sys.exit(0)

    # Determine settings (defaults are enabled, only --no-* flags disable)
    parallel = not args.no_parallel
    incremental = not args.no_incremental
    use_enhanced = not args.legacy and ENHANCED_FEATURES

    if args.legacy or not ENHANCED_FEATURES:
        if not ENHANCED_FEATURES:
            print("[AutoCoder] Enhanced features not available. Using legacy mode.")
        else:
            print("[AutoCoder] Using legacy mode (enhanced features disabled).")

    # Run
    if args.once:
        scan_once(
            format_code=not args.no_format,
            run_tests=args.test,
            dry_run=args.dry_run,
            parallel=parallel,
            incremental=incremental,
            use_enhanced=use_enhanced,
        )
    else:
        try:
            watch_loop(
                interval=args.interval,
                format_code=not args.no_format,
                run_tests=args.test,
                dry_run=args.dry_run,
                parallel=parallel,
                incremental=incremental,
                use_enhanced=use_enhanced,
            )
        except KeyboardInterrupt:
            print("\n[AutoCoder] Stopped by user")
            sys.exit(0)


if __name__ == "__main__":
    main()
