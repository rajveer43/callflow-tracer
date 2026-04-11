"""Tests for the regression explainer flagship feature."""

from __future__ import annotations

import json
from pathlib import Path

from callflow_tracer.analysis.regression_explainer import (
    explain_regression,
    format_regression_report,
)
from callflow_tracer.command_line.main import CallflowCLI
from callflow_tracer.core.tracer import CallGraph, TraceOptions


def _build_graph(pairs):
    graph = CallGraph(TraceOptions())
    for caller, callee, duration in pairs:
        graph.record_call(caller, callee, duration)
    return graph


def test_regression_explainer_identifies_primary_driver():
    before = _build_graph(
        [
            ("app.main", "pkg.worker", 0.2),
            ("app.main", "pkg.worker", 0.1),
        ]
    )
    after = _build_graph(
        [
            ("app.main", "pkg.worker", 0.2),
            ("app.main", "pkg.db", 0.6),
        ]
    )

    report = explain_regression(before, after, top_n=3)
    text = format_regression_report(report, top_n=3)

    assert report["summary"]["regressions"] >= 1
    assert report["regression_driver"]["name"] == "pkg.db"
    # pkg.db is a new function so label is "Primary new hotspot"
    assert ("Primary regression driver" in text or "Primary new hotspot" in text)
    assert "Next steps" in text
    assert "pkg.db" in text


def test_explain_command_outputs_report(tmp_path: Path):
    before = _build_graph(
        [
            ("app.main", "pkg.worker", 0.1),
            ("app.main", "pkg.worker", 0.1),
        ]
    )
    after = _build_graph(
        [
            ("app.main", "pkg.worker", 0.1),
            ("app.main", "pkg.db", 0.5),
        ]
    )

    before_file = tmp_path / "before.json"
    after_file = tmp_path / "after.json"
    output_file = tmp_path / "report.txt"
    before_file.write_text(json.dumps(before.to_dict(), indent=2))
    after_file.write_text(json.dumps(after.to_dict(), indent=2))

    cli = CallflowCLI()
    exit_code = cli.run(
        [
            "explain",
            str(before_file),
            str(after_file),
            "--top",
            "3",
            "--output",
            str(output_file),
        ]
    )

    assert exit_code == 0
    content = output_file.read_text()
    assert "Regression Explanation" in content
    assert "pkg.db" in content
