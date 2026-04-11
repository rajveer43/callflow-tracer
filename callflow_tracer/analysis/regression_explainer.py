"""Trace regression explanation helpers."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable, List, Optional

from ..core.tracer import CallGraph
from ..visualization.comparison import compare_graphs


def explain_regression(
    before_graph: CallGraph,
    after_graph: CallGraph,
    label1: str = "Before",
    label2: str = "After",
    top_n: int = 5,
) -> Dict[str, Any]:
    """Compare two traces and return an actionable regression explanation."""
    comparison = compare_graphs(before_graph, after_graph, label1, label2)

    before_data = before_graph.to_dict()
    after_data = after_graph.to_dict()

    before_nodes = before_data.get("nodes", [])
    after_nodes = after_data.get("nodes", [])

    before_total = _total_time(before_nodes)
    after_total = _total_time(after_nodes)

    module_deltas = _module_deltas(before_nodes, after_nodes)
    top_regressions = [
        item
        for item in comparison["node_comparisons"]
        if item["status"] == "modified" and item["time_diff"] > 0
    ]
    top_regressions.sort(key=lambda item: item["time_diff"], reverse=True)

    top_improvements = [
        item
        for item in comparison["node_comparisons"]
        if item["status"] == "modified" and item["time_diff"] < 0
    ]
    top_improvements.sort(key=lambda item: item["time_diff"])

    added_nodes = [
        item for item in comparison["node_comparisons"] if item["status"] == "added"
    ]
    removed_nodes = [
        item for item in comparison["node_comparisons"] if item["status"] == "removed"
    ]

    regression_driver = (
        top_regressions[0]
        if top_regressions
        else (added_nodes[0] if added_nodes else None)
    )
    structural_driver = _largest_module(module_deltas)
    next_steps = _build_next_steps(
        regression_driver,
        structural_driver,
        len(added_nodes),
        len(removed_nodes),
        comparison["summary"].get("regressions", 0),
    )

    summary = {
        "before_total_time": round(before_total, 6),
        "after_total_time": round(after_total, 6),
        "time_change": round(after_total - before_total, 6),
        "time_change_pct": (
            round(((after_total - before_total) / before_total) * 100, 2)
            if before_total > 0
            else 0.0
        ),
        "nodes_before": len(before_nodes),
        "nodes_after": len(after_nodes),
        "nodes_added": len(added_nodes),
        "nodes_removed": len(removed_nodes),
        "nodes_modified": comparison["summary"].get("nodes_modified", 0),
        "regressions": comparison["summary"].get("regressions", 0),
        "improvements": comparison["summary"].get("improvements", 0),
    }

    return {
        "labels": {"before": label1, "after": label2},
        "summary": summary,
        "comparison": comparison,
        "module_deltas": module_deltas[:top_n],
        "top_regressions": top_regressions[:top_n],
        "top_improvements": top_improvements[:top_n],
        "regression_driver": regression_driver,
        "structural_driver": structural_driver,
        "next_steps": next_steps,
    }


def format_regression_report(report: Dict[str, Any], top_n: int = 5) -> str:
    """Format a regression explanation report for terminal output."""
    summary = report["summary"]
    lines = [
        "=== Regression Explanation ===",
        f"Before: {report['labels']['before']}",
        f"After: {report['labels']['after']}",
        f"Total time before: {summary['before_total_time']:.6f}s",
        f"Total time after: {summary['after_total_time']:.6f}s",
        f"Change: {summary['time_change']:+.6f}s ({summary['time_change_pct']:+.2f}%)",
        f"Nodes before: {summary['nodes_before']}",
        f"Nodes after: {summary['nodes_after']}",
        f"Nodes added: {summary['nodes_added']}",
        f"Nodes removed: {summary['nodes_removed']}",
        f"Modified nodes: {summary['nodes_modified']}",
        f"Regressions: {summary['regressions']}",
        f"Improvements: {summary['improvements']}",
    ]

    if report.get("regression_driver"):
        driver = report["regression_driver"]
        driver_label = (
            "Primary new hotspot"
            if driver.get("status") == "added"
            else "Primary regression driver"
        )
        lines.extend(
            [
                "",
                f"{driver_label}:",
                f"  {driver['name']} ({driver['time_diff']:+.6f}s, {driver['time_diff_pct']:+.1f}%)",
            ]
        )

    if report.get("structural_driver"):
        module = report["structural_driver"]
        lines.extend(
            [
                "",
                "Largest module delta:",
                f"  {module['module']} ({module['time_diff']:+.6f}s, {module['time_diff_pct']:+.1f}%)",
            ]
        )

    if report.get("top_regressions"):
        lines.append("")
        lines.append(f"Top {min(top_n, len(report['top_regressions']))} regressions:")
        for index, item in enumerate(report["top_regressions"][:top_n], 1):
            lines.append(
                f"  {index}. {item['name']} - {item['time_diff']:+.6f}s ({item['time_diff_pct']:+.1f}%)"
            )

    if report.get("top_improvements"):
        lines.append("")
        lines.append(f"Top {min(top_n, len(report['top_improvements']))} improvements:")
        for index, item in enumerate(report["top_improvements"][:top_n], 1):
            lines.append(
                f"  {index}. {item['name']} - {item['time_diff']:+.6f}s ({item['time_diff_pct']:+.1f}%)"
            )

    if report.get("module_deltas"):
        lines.append("")
        lines.append(f"Top {min(top_n, len(report['module_deltas']))} module deltas:")
        for index, module in enumerate(report["module_deltas"][:top_n], 1):
            lines.append(
                f"  {index}. {module['module']} - {module['time_diff']:+.6f}s ({module['time_diff_pct']:+.1f}%)"
            )

    if report.get("next_steps"):
        lines.append("")
        lines.append("Next steps:")
        for step in report["next_steps"]:
            lines.append(f"  - {step}")

    return "\n".join(lines)


def _total_time(nodes: Iterable[Dict[str, Any]]) -> float:
    return sum(float(node.get("total_time", 0.0)) for node in nodes)


def _module_deltas(
    before_nodes: Iterable[Dict[str, Any]], after_nodes: Iterable[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Aggregate timing deltas by module."""
    before = defaultdict(lambda: {"total_time": 0.0, "call_count": 0})
    after = defaultdict(lambda: {"total_time": 0.0, "call_count": 0})

    for node in before_nodes:
        module = node.get("module") or "__main__"
        before[module]["total_time"] += float(node.get("total_time", 0.0))
        before[module]["call_count"] += int(node.get("call_count", 0))

    for node in after_nodes:
        module = node.get("module") or "__main__"
        after[module]["total_time"] += float(node.get("total_time", 0.0))
        after[module]["call_count"] += int(node.get("call_count", 0))

    modules = set(before.keys()) | set(after.keys())
    deltas = []
    for module in modules:
        before_time = before[module]["total_time"]
        after_time = after[module]["total_time"]
        time_diff = after_time - before_time
        time_diff_pct = (time_diff / before_time * 100) if before_time > 0 else 0.0
        deltas.append(
            {
                "module": module,
                "time_before": round(before_time, 6),
                "time_after": round(after_time, 6),
                "time_diff": round(time_diff, 6),
                "time_diff_pct": round(time_diff_pct, 2),
                "calls_before": before[module]["call_count"],
                "calls_after": after[module]["call_count"],
            }
        )

    deltas.sort(key=lambda item: abs(item["time_diff"]), reverse=True)
    return deltas


def _largest_module(module_deltas: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Return the module with the largest absolute delta."""
    return module_deltas[0] if module_deltas else None


def _build_next_steps(
    regression_driver: Optional[Dict[str, Any]],
    structural_driver: Optional[Dict[str, Any]],
    added_nodes: int,
    removed_nodes: int,
    regression_count: int,
) -> List[str]:
    """Generate actionable next steps for the user."""
    steps: List[str] = []

    if regression_driver:
        steps.append(
            f"Inspect {regression_driver['name']} first. It regressed by {regression_driver['time_diff']:+.6f}s."
        )

    if structural_driver and structural_driver["time_diff"] > 0:
        steps.append(
            f"Review module {structural_driver['module']} next. It added {structural_driver['time_diff']:+.6f}s overall."
        )

    if added_nodes > 0:
        steps.append(
            f"Review {added_nodes} newly introduced functions. New paths often explain regressions."
        )

    if removed_nodes > 0:
        steps.append(
            f"Check {removed_nodes} removed functions to see whether the behavior change was intentional."
        )

    if regression_count >= 3:
        steps.append(
            "Use the summary output with the trace compare view to isolate whether this is a single hotspot or a broader slowdown."
        )

    if not steps:
        steps.append(
            "No clear regression detected. The change looks neutral or improved."
        )

    return steps
