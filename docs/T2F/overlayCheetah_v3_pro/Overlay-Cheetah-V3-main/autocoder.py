#!/usr/bin/env python3
"""
AutoCoder (LLM-free release)
- Lightweight runtime: reads YAML tasks and renders Jinja2 templates into /out
- No LLM dependencies included
"""
from pathlib import Path
import argparse, time, json, subprocess
from typing import Dict, Any
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = Path(__file__).resolve().parent
TPL_DIR = ROOT / "templates"
TASK_DIR = ROOT / "tasks"
OUT_DIR = ROOT / "out"
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


def load_yaml(p: Path) -> Dict[str, Any]:
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def render_file(env: Environment, tpl_name: str, context: Dict[str, Any]) -> str:
    tpl = env.get_template(tpl_name)
    return tpl.render(**context)


def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(text)


def run(cmd: list[str]) -> int:
    try:
        return subprocess.run(cmd, check=False).returncode
    except FileNotFoundError:
        return 127


def handle_task(
    task_path: Path, format_code: bool = True, run_tests: bool = False
) -> dict:
    env = Environment(
        loader=FileSystemLoader(TPL_DIR),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    spec = load_yaml(task_path)
    task_id = spec.get("task_id", task_path.stem)
    files = spec.get("files", [])
    results = {"task_id": task_id, "generated": [], "errors": []}

    for f in files:
        tpl = f["template"]
        out_rel = f["output"]
        ctx = f.get("context", {})
        try:
            rendered = render_file(env, tpl, ctx)
            out_path = OUT_DIR / out_rel
            write_text(out_path, rendered)
            results["generated"].append(str(out_rel))
        except Exception as e:
            results["errors"].append({"file": out_rel, "error": str(e)})

    # format with black if available
    if format_code:
        run(["python", "-m", "black", str(OUT_DIR)])

    # optional pytest run
    if run_tests:
        run(["python", "-m", "pytest", str(OUT_DIR)])

    # write a report
    report_path = REPORTS_DIR / f"{task_id}.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    return results


def scan_once(format_code: bool, run_tests: bool):
    for p in TASK_DIR.glob("*.yaml"):
        done_flag = p.with_suffix(".done")
        if done_flag.exists():
            continue
        res = handle_task(p, format_code, run_tests)
        done_flag.write_text("ok")
        print(
            f"[AutoCoder] Task {p.name} -> {len(res['generated'])} files, {len(res['errors'])} errors."
        )


def watch_loop(interval: float, format_code: bool, run_tests: bool):
    print(f"[AutoCoder] Watching {TASK_DIR} every {interval}s. Ctrl+C to stop.")
    while True:
        scan_once(format_code, run_tests)
        time.sleep(interval)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--once", action="store_true", help="Process pending tasks once and exit"
    )
    ap.add_argument(
        "--interval", type=float, default=3.0, help="Watch interval seconds"
    )
    ap.add_argument("--no-format", action="store_true", help="Skip code formatting")
    ap.add_argument("--test", action="store_true", help="Run pytest after generation")
    args = ap.parse_args()
    if args.once:
        scan_once(format_code=not args.no_format, run_tests=args.test)
    else:
        watch_loop(args.interval, format_code=not args.no_format, run_tests=args.test)


if __name__ == "__main__":
    main()
