"""Actionable debug summaries for trace data."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from ..core.tracer import CallGraph


def summarize_graph(graph: CallGraph, top_n: int = 5) -> Dict[str, Any]:
    """Generate an actionable debugging summary from a call graph."""
    return summarize_trace_data(graph.to_dict(), top_n=top_n)


def summarize_trace_data(trace_data: Dict[str, Any], top_n: int = 5) -> Dict[str, Any]:
    """Generate an actionable debugging summary from raw trace JSON data."""
    nodes = trace_data.get("nodes", [])
    edges = trace_data.get("edges", [])
    metadata = trace_data.get("metadata", {})
    trace_stats = metadata.get("trace_stats", {})
    trace_options = metadata.get("trace_options", {})

    total_time = sum(node.get("total_time", 0.0) for node in nodes)
    total_calls = sum(node.get("call_count", 0) for node in nodes)
    total_nodes = len(nodes)
    total_edges = len(edges)

    slow_functions = _build_slow_functions(nodes, total_time, top_n)
    hot_modules = _build_hot_modules(nodes, total_time, top_n)
    next_steps = _build_next_steps(
        slow_functions, hot_modules, total_nodes, trace_stats
    )

    suspect_function = slow_functions[0] if slow_functions else None
    suspect_module = hot_modules[0] if hot_modules else None

    summary = {
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "total_calls": total_calls,
        "total_time": round(total_time, 6),
        "average_time_per_call": round(total_time / max(total_calls, 1), 6),
        "recorded_calls": trace_stats.get("recorded_calls", total_calls),
        "skipped_sampling": trace_stats.get("skipped_sampling", 0),
        "skipped_filtering": trace_stats.get("skipped_filtering", 0),
        "skipped_duration": trace_stats.get("skipped_duration", 0),
        "trace_options": trace_options,
    }

    return {
        "summary": summary,
        "suspect_function": suspect_function,
        "suspect_module": suspect_module,
        "slow_functions": slow_functions,
        "hot_modules": hot_modules,
        "next_steps": next_steps,
    }


def format_debug_summary(report: Dict[str, Any], top_n: int = 5) -> str:
    """Format a debug summary as readable terminal text."""
    summary = report.get("summary", {})
    slow_functions = report.get("slow_functions", [])
    hot_modules = report.get("hot_modules", [])
    next_steps = report.get("next_steps", [])

    lines = []
    lines.append("=== Debug Summary ===")
    lines.append(f"Total nodes: {summary.get('total_nodes', 0)}")
    lines.append(f"Total edges: {summary.get('total_edges', 0)}")
    lines.append(f"Total calls: {summary.get('total_calls', 0)}")
    lines.append(f"Total time: {summary.get('total_time', 0.0):.6f}s")
    lines.append(
        f"Average time per call: {summary.get('average_time_per_call', 0.0):.6f}s"
    )

    if summary.get("trace_options"):
        options = summary["trace_options"]
        lines.append(
            "Trace options: "
            f"sampling={options.get('sampling_rate', 1.0)}, "
            f"min_duration_ms={options.get('min_duration_ms', 0.0)}, "
            f"include_modules={options.get('include_modules')}, "
            f"exclude_modules={options.get('exclude_modules')}"
        )

    if report.get("suspect_function"):
        suspect = report["suspect_function"]
        lines.append(
            "Primary suspect function: "
            f"{suspect['full_name']} ({suspect['total_time']:.6f}s total, "
            f"{suspect['avg_time']:.6f}s avg)"
        )

    if report.get("suspect_module"):
        module = report["suspect_module"]
        lines.append(
            "Primary suspect module: "
            f"{module['module']} ({module['total_time']:.6f}s total)"
        )

    if slow_functions:
        lines.append("")
        lines.append(f"Top {min(top_n, len(slow_functions))} slow functions:")
        for index, func in enumerate(slow_functions[:top_n], 1):
            lines.append(
                f"  {index}. {func['full_name']} - {func['total_time']:.6f}s total, "
                f"{func['avg_time']:.6f}s avg, {func['call_count']} calls"
            )

    if hot_modules:
        lines.append("")
        lines.append(f"Top {min(top_n, len(hot_modules))} hot modules:")
        for index, module in enumerate(hot_modules[:top_n], 1):
            lines.append(
                f"  {index}. {module['module']} - {module['total_time']:.6f}s total, "
                f"{module['call_count']} calls"
            )

    if next_steps:
        lines.append("")
        lines.append("Next steps:")
        for step in next_steps:
            lines.append(f"  - {step}")

    return "\n".join(lines)


def _build_slow_functions(
    nodes: Iterable[Dict[str, Any]], total_time: float, top_n: int
) -> List[Dict[str, Any]]:
    """Return the slowest functions sorted by total execution time."""
    entries = []
    for node in nodes:
        node_total = float(node.get("total_time", 0.0))
        node_calls = int(node.get("call_count", 0))
        if node_total <= 0:
            continue
        entries.append(
            {
                "name": node.get("name", ""),
                "module": node.get("module", ""),
                "full_name": node.get("full_name", node.get("name", "")),
                "call_count": node_calls,
                "total_time": node_total,
                "avg_time": round(node_total / max(node_calls, 1), 6),
                "share_pct": (
                    round((node_total / total_time) * 100, 2) if total_time else 0.0
                ),
            }
        )

    entries.sort(key=lambda item: item["total_time"], reverse=True)
    return entries[:top_n]


def _build_hot_modules(
    nodes: Iterable[Dict[str, Any]], total_time: float, top_n: int
) -> List[Dict[str, Any]]:
    """Aggregate node time by module."""
    modules: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {"module": "", "call_count": 0, "total_time": 0.0, "functions": 0}
    )

    for node in nodes:
        module_name = node.get("module") or "__main__"
        module_total = float(node.get("total_time", 0.0))
        if module_total <= 0:
            continue
        module_entry = modules[module_name]
        module_entry["module"] = module_name
        module_entry["call_count"] += int(node.get("call_count", 0))
        module_entry["total_time"] += module_total
        module_entry["functions"] += 1

    results = []
    for module in modules.values():
        results.append(
            {
                "module": module["module"],
                "call_count": module["call_count"],
                "total_time": round(module["total_time"], 6),
                "functions": module["functions"],
                "share_pct": (
                    round((module["total_time"] / total_time) * 100, 2)
                    if total_time
                    else 0.0
                ),
            }
        )

    results.sort(key=lambda item: item["total_time"], reverse=True)
    return results[:top_n]


def _build_next_steps(
    slow_functions: List[Dict[str, Any]],
    hot_modules: List[Dict[str, Any]],
    total_nodes: int,
    trace_stats: Dict[str, Any],
) -> List[str]:
    """Create actionable next steps from the trace summary."""
    steps: List[str] = []

    if slow_functions:
        top = slow_functions[0]
        steps.append(
            f"Inspect {top['full_name']} first. It accounts for {top['share_pct']:.1f}% of total traced time."
        )

    if hot_modules:
        module = hot_modules[0]
        if module["share_pct"] >= 40:
            steps.append(
                f"Focus on module {module['module']} next. It dominates {module['share_pct']:.1f}% of traced time."
            )

    if trace_stats.get("skipped_sampling", 0) > 0:
        steps.append(
            "Lower the sampling rate only if you need more detail; the current profile is already sampling some calls."
        )

    if trace_stats.get("skipped_filtering", 0) > 0:
        steps.append(
            "Review your include/exclude module filters. Some calls were filtered out before recording."
        )

    if total_nodes > 25:
        steps.append(
            "Use compare mode against a baseline trace to identify regressions instead of inspecting this graph manually."
        )

    if not steps:
        steps.append(
            "No clear bottleneck found. Run a longer trace or lower the sampling threshold."
        )

    return steps
