"""Tests for benchmark mode."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

from callflow_tracer.benchmark import format_benchmark_report, run_benchmark
from callflow_tracer.command_line.main import CallflowCLI


def _write_script(path: Path) -> None:
    path.write_text(
        textwrap.dedent(
            """
            import time


            def inner(value):
                return sum(range(value))


            def main():
                total = 0
                for _ in range(20):
                    total += inner(5000)
                time.sleep(0.01)
                print(total)


            if __name__ == "__main__":
                main()
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )


def test_run_benchmark_generates_report(tmp_path: Path):
    script = tmp_path / "sample_app.py"
    _write_script(script)

    report = run_benchmark(str(script), runs=2, sampling_rate=1.0)
    text = format_benchmark_report(report)

    assert report.summary.runs == 2
    assert report.summary.baseline_avg_time_s >= 0
    assert report.summary.traced_avg_time_s >= 0
    assert report.recommendations
    assert report.traced_runs[0].trace_summary is not None
    assert report.traced_runs[0].trace_summary["summary"]["total_nodes"] >= 1
    assert report.top_functions
    assert "Benchmark Report" in text


def test_benchmark_cli_json_output(tmp_path: Path):
    script = tmp_path / "sample_app.py"
    _write_script(script)

    output_file = tmp_path / "benchmark.json"
    cli = CallflowCLI()
    exit_code = cli.run(
        [
            "benchmark",
            str(script),
            "--runs",
            "1",
            "--format",
            "json",
            "--output",
            str(output_file),
        ]
    )

    assert exit_code == 0
    payload = json.loads(output_file.read_text())
    assert payload["summary"]["runs"] == 1
    assert payload["recommendations"]
