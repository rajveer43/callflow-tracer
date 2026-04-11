"""HTML generation for benchmark reports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Union

from .models import BenchmarkReport


def export_benchmark_html(
    report: BenchmarkReport, output_path: Union[str, Path]
) -> None:
    """Export a benchmark report to HTML."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    html = _generate_html(report)
    output_path.write_text(html, encoding="utf-8")


def _generate_html(report: BenchmarkReport) -> str:
    summary = report.summary
    recommendations = (
        "\n".join(f"<li>{item}</li>" for item in report.recommendations)
        or "<li>No recommendations available.</li>"
    )
    top_functions_rows = (
        "\n".join(
            f"<tr><td>{item['full_name']}</td><td>{item['call_count']}</td><td>{item['total_time']:.6f}s</td><td>{item['avg_time']:.6f}s</td></tr>"
            for item in report.top_functions[:10]
        )
        or "<tr><td colspan='4'>No hotspot data available.</td></tr>"
    )

    baseline_json = json.dumps(
        [run.to_dict() for run in report.baseline_runs], indent=2
    )
    traced_json = json.dumps([run.to_dict() for run in report.traced_runs], indent=2)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CallFlow Benchmark Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; background: #0f172a; color: #e2e8f0; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 32px; }}
        .card {{ background: #111827; border: 1px solid #1f2937; border-radius: 16px; padding: 20px; margin-bottom: 20px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }}
        .stat {{ background: linear-gradient(135deg, #1e293b, #111827); border-radius: 12px; padding: 18px; }}
        .label {{ color: #94a3b8; font-size: 12px; text-transform: uppercase; letter-spacing: .08em; }}
        .value {{ font-size: 28px; font-weight: 700; margin-top: 8px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; border-bottom: 1px solid #334155; text-align: left; }}
        th {{ color: #93c5fd; }}
        code, pre {{ background: #020617; color: #cbd5e1; border-radius: 12px; }}
        pre {{ overflow-x: auto; padding: 16px; }}
        h1, h2 {{ margin: 0 0 16px 0; }}
        ul {{ line-height: 1.7; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>CallFlow Benchmark Report</h1>
            <p>{report.script}</p>
        </div>

        <div class="grid">
            <div class="stat"><div class="label">Baseline Avg</div><div class="value">{summary.baseline_avg_time_s:.6f}s</div></div>
            <div class="stat"><div class="label">Traced Avg</div><div class="value">{summary.traced_avg_time_s:.6f}s</div></div>
            <div class="stat"><div class="label">Overhead</div><div class="value">{summary.overhead_pct:+.2f}%</div></div>
            <div class="stat"><div class="label">Memory Delta</div><div class="value">{summary.memory_delta_mb:+.2f} MB</div></div>
        </div>

        <div class="card">
            <h2>Recommendations</h2>
            <ul>{recommendations}</ul>
        </div>

        <div class="card">
            <h2>Top Functions</h2>
            <table>
                <thead><tr><th>Function</th><th>Calls</th><th>Total</th><th>Avg</th></tr></thead>
                <tbody>{top_functions_rows}</tbody>
            </table>
        </div>

        <div class="card">
            <h2>Raw Runs</h2>
            <h3>Baseline</h3>
            <pre>{baseline_json}</pre>
            <h3>Traced</h3>
            <pre>{traced_json}</pre>
        </div>
    </div>
</body>
</html>"""
