from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import subprocess
import json
import os
from pathlib import Path

app = FastAPI(title="Cheetah Benchmark Runner")

# Assuming the benchmark script is in the same directory
BENCHMARK_SCRIPT = "website_build_benchmark.py"
REPORT_FILE = "website_build_benchmark_report.json"


@app.get("/", response_class=HTMLResponse)
async def home():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cheetah Benchmark Runner</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            button { padding: 10px 20px; font-size: 16px; }
            pre { background: #f4f4f4; padding: 10px; border: 1px solid #ddd; }
        </style>
    </head>
    <body>
        <h1>Overlay365 Ecosystem - Cheetah Benchmark</h1>
        <p>Run the competitive benchmark to measure Cheetah's performance in building websites.</p>
        <button onclick="runBenchmark()">Run Benchmark</button>
        <div id="results"></div>
        <script>
            async function runBenchmark() {
                document.getElementById('results').innerHTML = '<p>Running benchmark...</p>';
                try {
                    const response = await fetch('/run-benchmark');
                    const data = await response.json();
                    document.getElementById('results').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                } catch (error) {
                    document.getElementById('results').innerHTML = '<p>Error: ' + error.message + '</p>';
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/run-benchmark")
async def run_benchmark():
    try:
        # Run the benchmark script
        result = subprocess.run(
            ["python", BENCHMARK_SCRIPT],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )
        if result.returncode != 0:
            return {"error": result.stderr}

        # Read the report
        report_path = Path(__file__).parent / REPORT_FILE
        if report_path.exists():
            with open(report_path, "r") as f:
                report = json.load(f)
            return report
        else:
            return {"error": "Report file not found"}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
