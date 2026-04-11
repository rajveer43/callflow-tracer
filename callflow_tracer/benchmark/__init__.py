"""Benchmark mode for CallFlow Tracer."""

from .models import BenchmarkReport, BenchmarkRunResult, BenchmarkSummary
from .html import export_benchmark_html
from .recommendations import recommend_sampling_rate, build_benchmark_recommendations
from .report import format_benchmark_report, benchmark_report_to_dict
from .runner import run_benchmark

__all__ = [
    "BenchmarkRunResult",
    "BenchmarkSummary",
    "BenchmarkReport",
    "run_benchmark",
    "benchmark_report_to_dict",
    "format_benchmark_report",
    "export_benchmark_html",
    "recommend_sampling_rate",
    "build_benchmark_recommendations",
]
