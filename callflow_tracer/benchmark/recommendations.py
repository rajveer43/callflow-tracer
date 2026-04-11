"""Recommendation helpers for benchmark mode."""

from __future__ import annotations

from typing import List


def recommend_sampling_rate(overhead_pct: float, total_nodes: int) -> float:
    """Recommend a sampling rate based on measured overhead and graph size."""
    if overhead_pct >= 30 or total_nodes >= 300:
        return 0.1
    if overhead_pct >= 15 or total_nodes >= 150:
        return 0.25
    if overhead_pct >= 5 or total_nodes >= 50:
        return 0.5
    return 1.0


def build_benchmark_recommendations(
    overhead_pct: float,
    memory_delta_mb: float,
    total_nodes: int,
    trace_summary: dict | None = None,
) -> List[str]:
    """Convert benchmark metrics into actionable advice."""
    recommendations: List[str] = []

    if overhead_pct >= 30:
        recommendations.append(
            "Tracing overhead is high. Use sampling and module filters for production debugging."
        )
    elif overhead_pct >= 15:
        recommendations.append(
            "Tracing overhead is moderate. Start with sampling and narrow the trace scope."
        )
    else:
        recommendations.append(
            "Tracing overhead is low. Full tracing is reasonable for this workload."
        )

    if memory_delta_mb >= 20:
        recommendations.append(
            "Memory growth is noticeable. Run shorter traces or reduce trace retention."
        )
    elif memory_delta_mb >= 5:
        recommendations.append(
            "Memory impact is measurable. Consider sampling or a narrower module filter."
        )

    if total_nodes >= 200:
        recommendations.append(
            "The trace graph is large. Use module filtering or compare mode to focus on hotspots."
        )

    if trace_summary:
        top_function = trace_summary.get("suspect_function")
        if top_function:
            recommendations.append(
                f"Primary hotspot: {top_function['full_name']}. Inspect this function first."
            )

    return recommendations
