"""Benchmark report formatting helpers."""

from __future__ import annotations

from typing import Any, Dict

from .models import BenchmarkReport


def benchmark_report_to_dict(report: BenchmarkReport) -> Dict[str, Any]:
    """Convert a benchmark report to a JSON-friendly dictionary."""
    return report.to_dict()


def format_benchmark_report(report: BenchmarkReport) -> str:
    """Format a benchmark report for terminal output."""
    summary = report.summary
    lines = [
        "=== Benchmark Report ===",
        f"Script: {report.script}",
        f"Runs: {summary.runs}",
        "",
        "Timing:",
        f"  Baseline avg: {summary.baseline_avg_time_s:.6f}s",
        f"  Traced avg:   {summary.traced_avg_time_s:.6f}s",
        f"  Overhead:     {summary.overhead_s:+.6f}s ({summary.overhead_pct:+.2f}%)",
        "",
        "Memory:",
        f"  Baseline avg: {summary.baseline_avg_memory_mb:.2f} MB",
        f"  Traced avg:   {summary.traced_avg_memory_mb:.2f} MB",
        f"  Delta:        {summary.memory_delta_mb:+.2f} MB",
        "",
        "Trace:",
        f"  Total calls:   {summary.total_traced_calls}",
        f"  Total nodes:   {summary.total_traced_nodes}",
        f"  Total edges:   {summary.total_traced_edges}",
        f"  Recommended sampling rate: {summary.recommended_sampling_rate:.2f}",
    ]

    if report.top_functions:
        lines.append("")
        lines.append("Top functions:")
        for index, item in enumerate(report.top_functions[:5], 1):
            lines.append(
                f"  {index}. {item['full_name']} - {item['total_time']:.6f}s total, {item['avg_time']:.6f}s avg"
            )

    if report.recommendations:
        lines.append("")
        lines.append("Recommendations:")
        for item in report.recommendations:
            lines.append(f"  - {item}")

    return "\n".join(lines)
