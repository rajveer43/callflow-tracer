"""Concrete commands: quality, predict, churn."""

from __future__ import annotations

import json
import traceback as tb
from argparse import ArgumentParser
from typing import Dict

from .._utils import open_browser
from ..interfaces.command import BaseCommand, CommandContext, CommandResult


class QualityCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "quality"

    @property
    def help(self) -> str:
        return "Analyze code quality metrics"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("directory", nargs="?", default=".")
        parser.add_argument("-o", "--output", default="quality_report.html")
        parser.add_argument("--format", choices=["html", "json"], default="html")
        parser.add_argument("--track-trends", action="store_true")
        parser.add_argument("--no-browser", action="store_true")

    def execute(self, ctx: CommandContext) -> CommandResult:
        from ...analysis.code_quality import analyze_codebase, QualityTrendAnalyzer

        args = ctx.args
        try:
            results = analyze_codebase(args.directory)

            if args.track_trends:
                from ...analysis.code_quality import (
                    ComplexityMetrics, MaintainabilityMetrics, TechnicalDebtIndicator,
                )
                ta = QualityTrendAnalyzer()
                trend = ta.add_snapshot(
                    [ComplexityMetrics(**m) for m in results["complexity_metrics"]],
                    [MaintainabilityMetrics(**m) for m in results["maintainability_metrics"]],
                    [TechnicalDebtIndicator(**d) for d in results["debt_indicators"]],
                )
                results["trend"] = trend.to_dict()
                results["trend_analysis"] = ta.analyze_trends()

            if args.format == "json":
                with open(args.output, "w") as f:
                    json.dump(results, f, indent=2)
            else:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(_quality_html(results))
                if not args.no_browser:
                    open_browser(args.output)

            print(f"Quality report saved to: {args.output}")
            s = results["summary"]
            print(f"\n=== Quality Summary ===")
            print(f"  Functions: {s['total_functions']}, Avg complexity: {s['average_complexity']:.2f}")
            print(f"  Critical issues: {s['critical_issues']}, Debt score: {s['total_debt_score']:.2f}")

            return CommandResult.success(data={"summary": results["summary"]})
        except Exception as e:
            tb.print_exc()
            return CommandResult.failure(str(e))


class PredictCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "predict"

    @property
    def help(self) -> str:
        return "Predict performance issues from trace history"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("trace_history", help="JSON file with trace history")
        parser.add_argument("-o", "--output", default="predictions.html")
        parser.add_argument("--format", choices=["html", "json"], default="html")
        parser.add_argument("--no-browser", action="store_true")

    def execute(self, ctx: CommandContext) -> CommandResult:
        from ...analysis.predictive_analysis import generate_predictive_report

        args = ctx.args
        try:
            with open(args.trace_history, "r") as f:
                raw = json.load(f)
            history = [raw] if isinstance(raw, dict) else raw
            if len(history) < 2:
                return CommandResult.failure("Need at least 2 traces for prediction", exit_code=2)

            report = generate_predictive_report(history[:-1], history[-1])

            if args.format == "json":
                with open(args.output, "w") as f:
                    json.dump(report, f, indent=2)
            else:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(_predictions_html(report))
                if not args.no_browser:
                    open_browser(args.output)

            print(f"Predictions saved to: {args.output}")
            s = report["summary"]
            print(f"\n=== Predictions: critical={s['critical_risks']} high={s['high_risks']} "
                  f"confidence={s['average_confidence']:.0%} ===")

            return CommandResult.success(data={"summary": report["summary"]})
        except Exception as e:
            tb.print_exc()
            return CommandResult.failure(str(e))


class ChurnCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "churn"

    @property
    def help(self) -> str:
        return "Analyze code churn from git history"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("directory", nargs="?", default=".")
        parser.add_argument("-o", "--output", default="churn_report.html")
        parser.add_argument("--days", type=int, default=90)
        parser.add_argument("--format", choices=["html", "json"], default="html")
        parser.add_argument("--no-browser", action="store_true")

    def execute(self, ctx: CommandContext) -> CommandResult:
        from ...analysis.code_churn import generate_churn_report

        args = ctx.args
        try:
            report = generate_churn_report(args.directory, args.days)

            if args.format == "json":
                with open(args.output, "w") as f:
                    json.dump(report, f, indent=2)
            else:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(_churn_html(report))
                if not args.no_browser:
                    open_browser(args.output)

            print(f"Churn report saved to: {args.output}")
            s = report["summary"]
            print(f"\n=== Churn: files={s['total_files']} commits={s['total_commits']} "
                  f"high_risk={s['high_risk_files']} ===")

            return CommandResult.success(data={"summary": report["summary"]})
        except Exception as e:
            tb.print_exc()
            return CommandResult.failure(str(e))


# ── HTML generators (pure functions, no state) ─────────────────────────────────

def _quality_html(results: Dict) -> str:
    s = results["summary"]
    rows = "".join(
        f"<tr><td>{d['function_name']}</td><td>{d['module']}</td>"
        f"<td>{d['debt_score']:.1f}</td>"
        f"<td class='{d['severity'].lower()}'>{d['severity']}</td>"
        f"<td>{', '.join(d['issues'][:2])}</td></tr>"
        for d in results["debt_indicators"][:20]
    )
    return f"""<!DOCTYPE html><html><head><title>Code Quality Report</title>
<style>body{{font-family:Arial,sans-serif;margin:20px;background:#f5f5f5}}
.container{{max-width:1200px;margin:0 auto;background:white;padding:30px;border-radius:8px}}
h1{{color:#333;border-bottom:3px solid #4CAF50;padding-bottom:10px}}
.summary{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin:20px 0}}
.stat-card{{background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:20px;border-radius:8px;text-align:center}}
.stat-value{{font-size:2em;font-weight:bold}}
table{{width:100%;border-collapse:collapse;margin:20px 0}}
th,td{{padding:12px;text-align:left;border-bottom:1px solid #ddd}}
th{{background:#4CAF50;color:white}}
.critical{{color:#f44336;font-weight:bold}}.high{{color:#ff9800;font-weight:bold}}
.medium{{color:#ffc107}}.low{{color:#4CAF50}}</style></head>
<body><div class="container"><h1>Code Quality Report</h1>
<div class="summary">
<div class="stat-card"><div class="stat-value">{s['total_functions']}</div><div>Functions</div></div>
<div class="stat-card"><div class="stat-value">{s['average_complexity']:.1f}</div><div>Avg Complexity</div></div>
<div class="stat-card"><div class="stat-value">{s['average_maintainability']:.1f}</div><div>Maintainability</div></div>
<div class="stat-card"><div class="stat-value">{s['critical_issues']}</div><div>Critical Issues</div></div>
</div>
<h2>Technical Debt Indicators</h2>
<table><tr><th>Function</th><th>Module</th><th>Debt Score</th><th>Severity</th><th>Issues</th></tr>
{rows}</table></div></body></html>"""


def _predictions_html(report: Dict) -> str:
    s = report["summary"]
    cards = "".join(
        f"<div class='prediction {p['risk_level'].lower()}'>"
        f"<h3>{p['function_name']}</h3>"
        f"<p>Risk: <strong>{p['risk_level']}</strong> | "
        f"Current: {p['current_avg_time']:.4f}s | "
        f"Predicted: {p['predicted_time']:.4f}s | "
        f"Confidence: {p['confidence']:.0%}</p>"
        f"<ul>{''.join(f'<li>{r}</li>' for r in p['recommendations'])}</ul></div>"
        for p in report["performance_predictions"][:10]
    )
    return f"""<!DOCTYPE html><html><head><title>Performance Predictions</title>
<style>body{{font-family:Arial,sans-serif;margin:20px;background:#f5f5f5}}
.container{{max-width:1200px;margin:0 auto;background:white;padding:30px;border-radius:8px}}
.prediction{{border-left:4px solid #2196F3;padding:15px;margin:10px 0;background:#f9f9f9}}
.critical{{border-color:#f44336}}.high{{border-color:#ff9800}}
.medium{{border-color:#ffc107}}.low{{border-color:#4CAF50}}</style></head>
<body><div class="container"><h1>Performance Predictions</h1>
<p>Total: {s['total_predictions']} | Critical: {s['critical_risks']} | Confidence: {s['average_confidence']:.0%}</p>
{cards}</div></body></html>"""


def _churn_html(report: Dict) -> str:
    s = report["summary"]
    rows = "".join(
        f"<tr><td>{h['file_path']}</td><td>{h['hotspot_score']:.1f}</td>"
        f"<td>{h['total_commits']}</td><td>{h['lines_modified']}</td>"
        f"<td>{h['churn_rate']:.2f}/day</td></tr>"
        for h in report["hotspots"]
    )
    return f"""<!DOCTYPE html><html><head><title>Code Churn Report</title>
<style>body{{font-family:Arial,sans-serif;margin:20px;background:#f5f5f5}}
.container{{max-width:1200px;margin:0 auto;background:white;padding:30px;border-radius:8px}}
table{{width:100%;border-collapse:collapse;margin:20px 0}}
th,td{{padding:12px;text-align:left;border-bottom:1px solid #ddd}}
th{{background:#FF5722;color:white}}</style></head>
<body><div class="container"><h1>Code Churn Report</h1>
<p>Period: {s['analysis_period_days']} days | Files: {s['total_files']} | Commits: {s['total_commits']}</p>
<table><tr><th>File</th><th>Score</th><th>Commits</th><th>Changes</th><th>Rate</th></tr>
{rows}</table></div></body></html>"""
