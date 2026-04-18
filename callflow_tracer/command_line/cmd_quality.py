"""CLI subcommands: quality, predict, churn."""

import json
import sys
import traceback
from typing import Dict

from ._utils import open_browser
from ..analysis.code_quality import (
    analyze_codebase,
    QualityTrendAnalyzer,
)
from ..analysis.predictive_analysis import generate_predictive_report
from ..analysis.code_churn import generate_churn_report


# ── Parser registration ────────────────────────────────────────────────────────

def add_quality_parser(subparsers) -> None:
    p = subparsers.add_parser("quality", help="Analyze code quality metrics")
    p.add_argument("directory", nargs="?", default=".", help="Directory to analyze")
    p.add_argument("-o", "--output", default="quality_report.html", help="Output file")
    p.add_argument("--format", choices=["html", "json"], default="html")
    p.add_argument("--track-trends", action="store_true",
                   help="Track quality trends over time")
    p.add_argument("--no-browser", action="store_true", help="Do not open browser")


def add_predict_parser(subparsers) -> None:
    p = subparsers.add_parser("predict", help="Predict performance issues")
    p.add_argument("trace_history", help="JSON file with trace history")
    p.add_argument("-o", "--output", default="predictions.html", help="Output file")
    p.add_argument("--format", choices=["html", "json"], default="html")
    p.add_argument("--no-browser", action="store_true", help="Do not open browser")


def add_churn_parser(subparsers) -> None:
    p = subparsers.add_parser("churn", help="Analyze code churn")
    p.add_argument("directory", nargs="?", default=".", help="Repository directory")
    p.add_argument("-o", "--output", default="churn_report.html", help="Output file")
    p.add_argument("--days", type=int, default=90, help="Days of history to analyze")
    p.add_argument("--format", choices=["html", "json"], default="html")
    p.add_argument("--no-browser", action="store_true", help="Do not open browser")


# ── Handlers ──────────────────────────────────────────────────────────────────

def handle_quality(args) -> int:
    print(f"Analyzing code quality in: {args.directory}")
    try:
        results = analyze_codebase(args.directory)

        if args.track_trends:
            from ..analysis.code_quality import (
                ComplexityMetrics,
                MaintainabilityMetrics,
                TechnicalDebtIndicator,
            )
            trend_analyzer = QualityTrendAnalyzer()
            complexity = [ComplexityMetrics(**m) for m in results["complexity_metrics"]]
            maintainability = [MaintainabilityMetrics(**m) for m in results["maintainability_metrics"]]
            debt = [TechnicalDebtIndicator(**d) for d in results["debt_indicators"]]
            trend = trend_analyzer.add_snapshot(complexity, maintainability, debt)
            results["trend"] = trend.to_dict()
            results["trend_analysis"] = trend_analyzer.analyze_trends()

        if args.format == "json":
            with open(args.output, "w") as f:
                json.dump(results, f, indent=2)
            print(f"Quality report saved to: {args.output}")
        else:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(_generate_quality_html(results))
            print(f"Quality report saved to: {args.output}")
            if not args.no_browser:
                open_browser(args.output)

        summary = results["summary"]
        print(f"\n=== Quality Summary ===")
        print(f"Total functions: {summary['total_functions']}")
        print(f"Average complexity: {summary['average_complexity']:.2f}")
        print(f"Average maintainability: {summary['average_maintainability']:.2f}")
        print(f"Total debt score: {summary['total_debt_score']:.2f}")
        print(f"Critical issues: {summary['critical_issues']}")
        print(f"High issues: {summary['high_issues']}")
        return 0

    except Exception as e:
        print(f"Error analyzing quality: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1


def handle_predict(args) -> int:
    print(f"Analyzing trace history: {args.trace_history}")
    try:
        with open(args.trace_history, "r") as f:
            history_data = json.load(f)

        history = [history_data] if isinstance(history_data, dict) else history_data

        if len(history) < 2:
            print("Warning: Need at least 2 traces for prediction", file=sys.stderr)
            return 1

        report = generate_predictive_report(history[:-1], history[-1])

        if args.format == "json":
            with open(args.output, "w") as f:
                json.dump(report, f, indent=2)
            print(f"Predictions saved to: {args.output}")
        else:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(_generate_predictions_html(report))
            print(f"Predictions saved to: {args.output}")
            if not args.no_browser:
                open_browser(args.output)

        summary = report["summary"]
        print(f"\n=== Prediction Summary ===")
        print(f"Total predictions: {summary['total_predictions']}")
        print(f"Critical risks: {summary['critical_risks']}")
        print(f"High risks: {summary['high_risks']}")
        print(f"Average confidence: {summary['average_confidence']:.2%}")

        if report["recommendations"]:
            print(f"\n=== Recommendations ===")
            for rec in report["recommendations"]:
                print(f"  • {rec}")
        return 0

    except Exception as e:
        print(f"Error generating predictions: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1


def handle_churn(args) -> int:
    print(f"Analyzing code churn in: {args.directory}")
    try:
        report = generate_churn_report(args.directory, args.days)

        if args.format == "json":
            with open(args.output, "w") as f:
                json.dump(report, f, indent=2)
            print(f"Churn report saved to: {args.output}")
        else:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(_generate_churn_html(report))
            print(f"Churn report saved to: {args.output}")
            if not args.no_browser:
                open_browser(args.output)

        summary = report["summary"]
        print(f"\n=== Churn Summary ===")
        print(f"Total files analyzed: {summary['total_files']}")
        print(f"Total commits: {summary['total_commits']}")
        print(f"Total changes: {summary['total_changes']}")
        print(f"Average churn rate: {summary['average_churn_rate']:.2f} changes/day")
        print(f"High risk files: {summary['high_risk_files']}")

        if report["hotspots"]:
            print(f"\n=== Top 5 Hotspots ===")
            for i, hotspot in enumerate(report["hotspots"][:5], 1):
                print(f"{i}. {hotspot['file_path']}")
                print(f"   Score: {hotspot['hotspot_score']:.1f}, Commits: {hotspot['total_commits']}")
        return 0

    except Exception as e:
        print(f"Error analyzing churn: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1


# ── HTML generators ────────────────────────────────────────────────────────────

def _generate_quality_html(results: Dict) -> str:
    summary = results["summary"]
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Code Quality Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-value {{ font-size: 2em; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #4CAF50; color: white; }}
        .critical {{ color: #f44336; font-weight: bold; }}
        .high {{ color: #ff9800; font-weight: bold; }}
        .medium {{ color: #ffc107; }}
        .low {{ color: #4CAF50; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Code Quality Report</h1>
        <div class="summary">
            <div class="stat-card">
                <div class="stat-value">{summary['total_functions']}</div>
                <div>Total Functions</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{summary['average_complexity']:.1f}</div>
                <div>Avg Complexity</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{summary['average_maintainability']:.1f}</div>
                <div>Avg Maintainability</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{summary['critical_issues']}</div>
                <div>Critical Issues</div>
            </div>
        </div>
        <h2>Technical Debt Indicators</h2>
        <table>
            <tr>
                <th>Function</th><th>Module</th><th>Debt Score</th>
                <th>Severity</th><th>Issues</th>
            </tr>
"""
    for debt in results["debt_indicators"][:20]:
        severity_class = debt["severity"].lower()
        html += f"""
            <tr>
                <td>{debt['function_name']}</td>
                <td>{debt['module']}</td>
                <td>{debt['debt_score']:.1f}</td>
                <td class="{severity_class}">{debt['severity']}</td>
                <td>{', '.join(debt['issues'][:2])}</td>
            </tr>
"""
    html += "        </table>\n    </div>\n</body>\n</html>\n"
    return html


def _generate_predictions_html(report: Dict) -> str:
    summary = report["summary"]
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Performance Predictions</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
        h1 {{ color: #333; }}
        .prediction {{ border-left: 4px solid #2196F3; padding: 15px; margin: 10px 0; background: #f9f9f9; }}
        .critical {{ border-color: #f44336; }}
        .high {{ border-color: #ff9800; }}
        .medium {{ border-color: #ffc107; }}
        .low {{ border-color: #4CAF50; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Performance Predictions</h1>
        <p>Total Predictions: {summary['total_predictions']}</p>
        <p>Critical Risks: {summary['critical_risks']}</p>
"""
    for pred in report["performance_predictions"][:10]:
        risk_class = pred["risk_level"].lower()
        recs = "".join(f"<li>{r}</li>" for r in pred["recommendations"])
        html += f"""
        <div class="prediction {risk_class}">
            <h3>{pred['function_name']}</h3>
            <p><strong>Risk Level:</strong> {pred['risk_level']}</p>
            <p><strong>Current Time:</strong> {pred['current_avg_time']:.6f}s</p>
            <p><strong>Predicted Time:</strong> {pred['predicted_time']:.6f}s</p>
            <p><strong>Confidence:</strong> {pred['confidence']:.1%}</p>
            <p><strong>Recommendations:</strong></p>
            <ul>{recs}</ul>
        </div>
"""
    html += "    </div>\n</body>\n</html>\n"
    return html


def _generate_churn_html(report: Dict) -> str:
    summary = report["summary"]
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Code Churn Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
        h1 {{ color: #333; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #FF5722; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Code Churn Report</h1>
        <p>Analysis Period: {summary['analysis_period_days']} days</p>
        <p>Total Files: {summary['total_files']}</p>
        <p>Total Commits: {summary['total_commits']}</p>
        <h2>Top Hotspots</h2>
        <table>
            <tr>
                <th>File</th><th>Hotspot Score</th><th>Commits</th>
                <th>Changes</th><th>Churn Rate</th>
            </tr>
"""
    for hotspot in report["hotspots"]:
        html += f"""
            <tr>
                <td>{hotspot['file_path']}</td>
                <td>{hotspot['hotspot_score']:.1f}</td>
                <td>{hotspot['total_commits']}</td>
                <td>{hotspot['lines_modified']}</td>
                <td>{hotspot['churn_rate']:.2f}/day</td>
            </tr>
"""
    html += "        </table>\n    </div>\n</body>\n</html>\n"
    return html
