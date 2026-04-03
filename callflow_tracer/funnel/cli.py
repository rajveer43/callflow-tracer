"""
Funnel Analysis CLI Commands for CallFlow Tracer

This module provides comprehensive command-line interface for funnel analysis,
including tracking, monitoring, reporting, and visualization commands.
"""

import click
import json
import sys
from pathlib import Path
from typing import Optional, List
import time

from .analysis import FunnelType, StepStatus, create_funnel
from .visualizer import create_funnel_visualizer
from .algorithms import (
    analyze_funnel_anomalies,
    predict_funnel_performance,
    recognize_funnel_patterns,
    generate_optimization_plan,
)
from .monitor import create_funnel_monitor
from .reporting import generate_funnel_report, export_funnel_data


@click.group()
@click.version_option()
def funnel():
    """Funnel analysis commands for CallFlow Tracer"""
    pass


@funnel.command()
@click.option("--name", "-n", required=True, help="Funnel name")
@click.option(
    "--type",
    "-t",
    default="performance",
    type=click.Choice(
        ["performance", "conversion", "error_tracking", "user_journey", "api_flow"]
    ),
    help="Funnel type",
)
@click.option("--output", "-o", help="Output file for funnel configuration")
def create(name: str, type: str, output: Optional[str]):
    """Create a new funnel analyzer"""
    try:
        funnel_type = FunnelType(type)
        analyzer = create_funnel(name, funnel_type.value)

        config = {
            "funnel_id": analyzer.funnel_id,
            "name": analyzer.name,
            "type": analyzer.funnel_type.value,
            "created_at": analyzer.created_at.isoformat(),
            "steps": [],
        }

        if output:
            with open(output, "w") as f:
                json.dump(config, f, indent=2)
            click.echo(f"Funnel configuration saved to {output}")
        else:
            click.echo(json.dumps(config, indent=2))

    except Exception as e:
        click.echo(f"Error creating funnel: {e}", err=True)
        sys.exit(1)


@funnel.command()
@click.option("--config", "-c", required=True, help="Funnel configuration file")
@click.option(
    "--step", "-s", multiple=True, help='Add step (format: "name:description")'
)
@click.option("--session", help="Start a new session with user ID")
@click.option(
    "--track",
    help='Track step completion (format: "session_id:step_name:status:duration")',
)
@click.option("--complete", help='Complete session (format: "session_id:status")')
@click.option("--output", "-o", help="Output file for results")
def track(
    config: str,
    step: List[str],
    session: Optional[str],
    track: Optional[str],
    complete: Optional[str],
    output: Optional[str],
):
    """Track funnel steps and sessions"""
    try:
        # Load funnel configuration
        with open(config, "r") as f:
            config_data = json.load(f)

        # Create analyzer
        funnel_type = FunnelType(config_data["type"])
        analyzer = create_funnel(config_data["name"], funnel_type.value)

        # Add steps
        for step_def in step:
            if ":" in step_def:
                name, description = step_def.split(":", 1)
                analyzer.add_step(name.strip(), description.strip())
                click.echo(f"Added step: {name.strip()}")
            else:
                analyzer.add_step(step_def.strip())
                click.echo(f"Added step: {step_def.strip()}")

        # Start session
        if session:
            session_obj = analyzer.start_session(user_id=session)
            click.echo(f"Started session: {session_obj.session_id}")

        # Track step
        if track:
            parts = track.split(":")
            if len(parts) >= 3:
                session_id, step_name, status = parts[:3]
                duration = float(parts[3]) if len(parts) > 3 else None

                step_status = StepStatus.SUCCESS
                if status.lower() == "failure":
                    step_status = StepStatus.FAILURE
                elif status.lower() == "error":
                    step_status = StepStatus.ERROR

                success = analyzer.track_step(
                    session_id, step_name, step_status, duration
                )
                if success:
                    click.echo(f"Tracked step: {step_name} for session {session_id}")
                else:
                    click.echo(
                        f"Failed to track step - session not found: {session_id}",
                        err=True,
                    )

        # Complete session
        if complete:
            parts = complete.split(":")
            if len(parts) >= 2:
                session_id, status = parts[:2]

                session_status = StepStatus.SUCCESS
                if status.lower() == "failure":
                    session_status = StepStatus.FAILURE
                elif status.lower() == "error":
                    session_status = StepStatus.ERROR

                success = analyzer.complete_session(session_id, session_status)
                if success:
                    click.echo(f"Completed session: {session_id}")
                else:
                    click.echo(
                        f"Failed to complete session - session not found: {session_id}",
                        err=True,
                    )

        # Export results
        if output:
            results = analyzer.get_analytics()
            with open(output, "w") as f:
                json.dump(results, f, indent=2, default=str)
            click.echo(f"Results exported to {output}")

    except Exception as e:
        click.echo(f"Error in track command: {e}", err=True)
        sys.exit(1)


@funnel.command()
@click.option("--config", "-c", required=True, help="Funnel configuration file")
@click.option("--data", "-d", help="Funnel data file (JSON)")
@click.option(
    "--format",
    "-f",
    default="table",
    type=click.Choice(["table", "json", "csv"]),
    help="Output format",
)
@click.option("--output", "-o", help="Output file")
def analyze(config: str, data: Optional[str], format: str, output: Optional[str]):
    """Analyze funnel data"""
    try:
        # Load funnel configuration
        with open(config, "r") as f:
            config_data = json.load(f)

        # Create analyzer
        funnel_type = FunnelType(config_data["type"])
        analyzer = create_funnel(config_data["name"], funnel_type.value)

        # Load data if provided
        if data and Path(data).exists():
            with open(data, "r") as f:
                data_json = json.load(f)

            # Load sessions and steps from data
            # This is a simplified implementation
            if "sessions" in data_json:
                for session_data in data_json["sessions"]:
                    # Recreate session data
                    pass

        # Get analytics
        analytics = analyzer.get_analytics()

        # Output results
        if format == "json":
            results = json.dumps(analytics, indent=2, default=str)
        elif format == "csv":
            # Simple CSV export
            import csv
            import io

            output_buffer = io.StringIO()
            writer = csv.writer(output_buffer)

            # Write conversion metrics
            conversion_metrics = analytics.get("conversion_metrics", {})
            writer.writerow(["Metric", "Value"])
            for key, value in conversion_metrics.items():
                writer.writerow([key, value])

            results = output_buffer.getvalue()
        else:  # table format
            results = _format_analytics_table(analytics)

        if output:
            with open(output, "w") as f:
                f.write(results)
            click.echo(f"Analysis results saved to {output}")
        else:
            click.echo(results)

    except Exception as e:
        click.echo(f"Error in analyze command: {e}", err=True)
        sys.exit(1)


@funnel.command()
@click.option("--config", "-c", required=True, help="Funnel configuration file")
@click.option("--data", "-d", help="Funnel data file (JSON)")
@click.option(
    "--chart-type",
    default="standard",
    type=click.Choice(["standard", "stacked", "3d", "comparison"]),
    help="Chart type",
)
@click.option(
    "--theme",
    default="default",
    type=click.Choice(["default", "dark", "vibrant"]),
    help="Color theme",
)
@click.option("--output", "-o", required=True, help="Output HTML file")
def visualize(
    config: str, data: Optional[str], chart_type: str, theme: str, output: str
):
    """Generate funnel visualizations"""
    try:
        # Load funnel configuration
        with open(config, "r") as f:
            config_data = json.load(f)

        # Create analyzer
        funnel_type = FunnelType(config_data["type"])
        analyzer = create_funnel(config_data["name"], funnel_type.value)

        # Load data if provided
        if data and Path(data).exists():
            with open(data, "r") as f:
                data_json = json.load(f)
            # Load data into analyzer (simplified)

        # Create visualizer
        visualizer = create_funnel_visualizer(analyzer)

        # Generate chart
        chart_data = visualizer.generate_funnel_chart(chart_type, theme, True)

        # Generate HTML visualization
        html_content = _generate_funnel_html(chart_data, config_data["name"])

        # Save to file
        with open(output, "w") as f:
            f.write(html_content)

        click.echo(f"Visualization saved to {output}")

    except Exception as e:
        click.echo(f"Error generating visualization: {e}", err=True)
        sys.exit(1)


@funnel.command()
@click.option("--config", "-c", required=True, help="Funnel configuration file")
@click.option("--data", "-d", help="Funnel data file (JSON)")
@click.option(
    "--mode",
    default="passive",
    type=click.Choice(["passive", "active", "predictive"]),
    help="Monitoring mode",
)
@click.option("--interval", default=5.0, help="Monitoring interval in seconds")
@click.option("--duration", help="Monitoring duration in seconds (optional)")
@click.option("--output", "-o", help="Output file for monitoring results")
def monitor(
    config: str,
    data: Optional[str],
    mode: str,
    interval: float,
    duration: Optional[int],
    output: Optional[str],
):
    """Monitor funnel in real-time"""
    try:
        # Load funnel configuration
        with open(config, "r") as f:
            config_data = json.load(f)

        # Create analyzer
        funnel_type = FunnelType(config_data["type"])
        analyzer = create_funnel(config_data["name"], funnel_type.value)

        # Load data if provided
        if data and Path(data).exists():
            with open(data, "r") as f:
                data_json = json.load(f)
            # Load data into analyzer (simplified)

        # Create monitor
        monitor = create_funnel_monitor(analyzer, mode)

        # Start monitoring
        click.echo(f"Starting funnel monitoring in {mode} mode...")
        click.echo(f"Monitoring interval: {interval}s")
        if duration:
            click.echo(f"Duration: {duration}s")

        monitor.start_monitoring(interval)

        try:
            # Monitor for specified duration or until interrupt
            start_time = time.time()

            while True:
                if duration and (time.time() - start_time) > duration:
                    break

                # Get monitoring status
                status = monitor.get_monitoring_status()
                active_alerts = monitor.get_active_alerts()

                # Display status
                click.echo(f"\n--- Monitoring Status ---")
                click.echo(f"Active alerts: {len(active_alerts)}")
                click.echo(
                    f"Total alerts generated: {status['total_alerts_generated']}"
                )
                click.echo(f"Uptime: {status['uptime_seconds']:.1f}s")

                # Display recent alerts
                if active_alerts:
                    click.echo("\nRecent Alerts:")
                    for alert in active_alerts[:3]:
                        click.echo(f"  [{alert.severity.value.upper()}] {alert.title}")

                time.sleep(interval)

        except KeyboardInterrupt:
            click.echo("\nMonitoring stopped by user")

        finally:
            monitor.stop_monitoring()

            # Export monitoring results
            if output:
                monitoring_data = monitor.export_monitoring_data()
                with open(output, "w") as f:
                    f.write(monitoring_data)
                click.echo(f"Monitoring results saved to {output}")

    except Exception as e:
        click.echo(f"Error in monitor command: {e}", err=True)
        sys.exit(1)


@funnel.command()
@click.option("--config", "-c", required=True, help="Funnel configuration file")
@click.option("--data", "-d", help="Funnel data file (JSON)")
@click.option(
    "--report-type",
    default="standard",
    type=click.Choice(["standard", "executive", "technical", "comparison"]),
    help="Report type",
)
@click.option(
    "--format",
    default="html",
    type=click.Choice(["html", "pdf", "json"]),
    help="Report format",
)
@click.option("--output", "-o", required=True, help="Output file")
def report(
    config: str, data: Optional[str], report_type: str, format: str, output: str
):
    """Generate funnel analysis report"""
    try:
        # Load funnel configuration
        with open(config, "r") as f:
            config_data = json.load(f)

        # Create analyzer
        funnel_type = FunnelType(config_data["type"])
        analyzer = create_funnel(config_data["name"], funnel_type.value)

        # Load data if provided
        if data and Path(data).exists():
            with open(data, "r") as f:
                data_json = json.load(f)
            # Load data into analyzer (simplified)

        # Generate report
        report_path = generate_funnel_report(analyzer, report_type, output)

        click.echo(f"Report generated: {report_path}")

        # Display report summary
        if format == "html":
            click.echo(f"Open {output} in a web browser to view the report")

    except Exception as e:
        click.echo(f"Error generating report: {e}", err=True)
        sys.exit(1)


@funnel.command()
@click.option("--config", "-c", required=True, help="Funnel configuration file")
@click.option("--data", "-d", help="Funnel data file (JSON)")
@click.option(
    "--format",
    default="json",
    type=click.Choice(["json", "csv", "excel", "html"]),
    help="Export format",
)
@click.option("--sections", help="Sections to include (comma-separated)")
@click.option("--output", "-o", required=True, help="Output file")
def export(
    config: str, data: Optional[str], format: str, sections: Optional[str], output: str
):
    """Export funnel data"""
    try:
        # Load funnel configuration
        with open(config, "r") as f:
            config_data = json.load(f)

        # Create analyzer
        funnel_type = FunnelType(config_data["type"])
        analyzer = create_funnel(config_data["name"], funnel_type.value)

        # Load data if provided
        if data and Path(data).exists():
            with open(data, "r") as f:
                data_json = json.load(f)
            # Load data into analyzer (simplified)

        # Parse sections
        include_sections = None
        if sections:
            include_sections = [s.strip() for s in sections.split(",")]

        # Export data
        export_path = export_funnel_data(analyzer, format, output)

        click.echo(f"Data exported to {output}")

        # Display export info
        file_size = Path(output).stat().st_size if Path(output).exists() else 0
        click.echo(f"File size: {file_size:,} bytes")

    except Exception as e:
        click.echo(f"Error exporting data: {e}", err=True)
        sys.exit(1)


@funnel.command()
@click.option("--config", "-c", required=True, help="Funnel configuration file")
@click.option("--data", "-d", help="Funnel data file (JSON)")
def anomalies(config: str, data: Optional[str]):
    """Detect and display funnel anomalies"""
    try:
        # Load funnel configuration
        with open(config, "r") as f:
            config_data = json.load(f)

        # Create analyzer
        funnel_type = FunnelType(config_data["type"])
        analyzer = create_funnel(config_data["name"], funnel_type.value)

        # Load data if provided
        if data and Path(data).exists():
            with open(data, "r") as f:
                data_json = json.load(f)
            # Load data into analyzer (simplified)

        # Detect anomalies
        anomaly_results = analyze_funnel_anomalies(analyzer)

        if not anomaly_results:
            click.echo("No anomalies detected.")
            return

        click.echo(f"Found {len(anomaly_results)} anomalies:\n")

        for i, anomaly in enumerate(anomaly_results, 1):
            click.echo(f"{i}. [{anomaly.severity.upper()}] {anomaly.anomaly_type}")
            click.echo(f"   Description: {anomaly.description}")
            click.echo(f"   Confidence: {anomaly.confidence:.2f}")
            click.echo(f"   Affected steps: {', '.join(anomaly.affected_steps)}")
            if anomaly.recommendations:
                click.echo(f"   Recommendations:")
                for rec in anomaly.recommendations[:2]:  # Show top 2
                    click.echo(f"     - {rec}")
            click.echo()

    except Exception as e:
        click.echo(f"Error detecting anomalies: {e}", err=True)
        sys.exit(1)


@funnel.command()
@click.option("--config", "-c", required=True, help="Funnel configuration file")
@click.option("--data", "-d", help="Funnel data file (JSON)")
@click.option(
    "--horizon",
    default="next_day",
    type=click.Choice(["next_hour", "next_day", "next_week", "next_month"]),
    help="Prediction horizon",
)
def predict(config: str, data: Optional[str], horizon: str):
    """Generate funnel performance predictions"""
    try:
        # Load funnel configuration
        with open(config, "r") as f:
            config_data = json.load(f)

        # Create analyzer
        funnel_type = FunnelType(config_data["type"])
        analyzer = create_funnel(config_data["name"], funnel_type.value)

        # Load data if provided
        if data and Path(data).exists():
            with open(data, "r") as f:
                data_json = json.load(f)
            # Load data into analyzer (simplified)

        # Generate predictions
        predictions = predict_funnel_performance(analyzer, horizon)

        click.echo(f"Funnel Performance Predictions ({horizon}):\n")

        for prediction in predictions:
            click.echo(f"Prediction: {prediction.prediction_type}")
            click.echo(f"  Predicted Value: {prediction.predicted_value:.2f}")
            click.echo(f"  Confidence: {prediction.confidence:.2f}")
            click.echo(f"  Time Horizon: {prediction.time_horizon}")
            click.echo(f"  Accuracy Estimate: {prediction.accuracy_estimate:.2f}")
            if prediction.recommendations:
                click.echo("  Recommendations:")
                for rec in prediction.recommendations[:2]:
                    click.echo(f"    - {rec}")
            click.echo()

    except Exception as e:
        click.echo(f"Error generating predictions: {e}", err=True)
        sys.exit(1)


@funnel.command()
@click.option("--config", "-c", required=True, help="Funnel configuration file")
@click.option("--data", "-d", help="Funnel data file (JSON)")
def optimize(config: str, data: Optional[str]):
    """Generate funnel optimization plan"""
    try:
        # Load funnel configuration
        with open(config, "r") as f:
            config_data = json.load(f)

        # Create analyzer
        funnel_type = FunnelType(config_data["type"])
        analyzer = create_funnel(config_data["name"], funnel_type.value)

        # Load data if provided
        if data and Path(data).exists():
            with open(data, "r") as f:
                data_json = json.load(f)
            # Load data into analyzer (simplified)

        # Generate optimization plan
        plan = generate_optimization_plan(analyzer)

        click.echo("Funnel Optimization Plan\n")
        click.echo("=" * 50)

        # Summary
        summary = plan.get("summary", {})
        click.echo(f"Current Performance:")
        click.echo(
            f"  Conversion Rate: {summary.get('current_performance', {}).get('conversion_rate', 0):.1f}%"
        )
        click.echo(
            f"  Total Sessions: {summary.get('current_performance', {}).get('total_sessions', 0):,}"
        )

        click.echo(f"\nOptimization Potential:")
        optimization = summary.get("optimization_potential", {})
        click.echo(
            f"  Conversion Improvement: +{optimization.get('conversion_improvement', 0):.1f}%"
        )
        click.echo(
            f"  Performance Improvement: +{optimization.get('performance_improvement', 0):.1f}%"
        )
        click.echo(f"  Error Reduction: -{optimization.get('error_reduction', 0):.1f}%")

        # Top priorities
        priorities = plan.get("priorities", [])
        if priorities:
            click.echo(f"\nTop Optimization Priorities:")
            for i, priority in enumerate(priorities[:5], 1):
                click.echo(f"{i}. [{priority['impact'].upper()}] {priority['title']}")
                click.echo(f"   Priority Score: {priority['priority']:.2f}")
                click.echo(f"   Effort: {priority['effort']}")
                if priority["actions"]:
                    click.echo(f"   Action: {priority['actions'][0]}")
                click.echo()

        # Expected impact
        expected_impact = plan.get("expected_impact", {})
        if expected_impact:
            click.echo(f"Expected Business Impact:")
            conversion = expected_impact.get("conversion_rate", {})
            click.echo(
                f"  Conversion Rate: {conversion.get('current', 0):.1f}% → {conversion.get('target', 0):.1f}%"
            )

            business = expected_impact.get("business_impact", {})
            click.echo(f"  Estimated ROI: {business.get('estimated_roi', 'N/A')}")
            click.echo(f"  Payback Period: {business.get('payback_period', 'N/A')}")
            click.echo(
                f"  User Satisfaction: {business.get('user_satisfaction', 'N/A')}"
            )

    except Exception as e:
        click.echo(f"Error generating optimization plan: {e}", err=True)
        sys.exit(1)


@funnel.command()
@click.option("--config", "-c", required=True, help="Funnel configuration file")
@click.option("--data", "-d", help="Funnel data file (JSON)")
def patterns(config: str, data: Optional[str]):
    """Recognize and display funnel patterns"""
    try:
        # Load funnel configuration
        with open(config, "r") as f:
            config_data = json.load(f)

        # Create analyzer
        funnel_type = FunnelType(config_data["type"])
        analyzer = create_funnel(config_data["name"], funnel_type.value)

        # Load data if provided
        if data and Path(data).exists():
            with open(data, "r") as f:
                data_json = json.load(f)
            # Load data into analyzer (simplified)

        # Recognize patterns
        pattern_results = recognize_funnel_patterns(analyzer)

        if not pattern_results:
            click.echo("No significant patterns detected.")
            return

        click.echo(f"Found {len(pattern_results)} patterns:\n")

        for i, pattern in enumerate(pattern_results, 1):
            click.echo(f"{i}. [{pattern.pattern_type.replace('_', ' ').title()}]")
            click.echo(f"   Description: {pattern.description}")
            click.echo(f"   Frequency: {pattern.frequency}")
            click.echo(f"   Confidence: {pattern.confidence:.2f}")
            click.echo(f"   Impact Score: {pattern.impact_score:.2f}")
            if pattern.actionable_insights:
                click.echo(f"   Actionable Insights:")
                for insight in pattern.actionable_insights[:2]:
                    click.echo(f"     - {insight}")
            click.echo()

    except Exception as e:
        click.echo(f"Error recognizing patterns: {e}", err=True)
        sys.exit(1)


def _format_analytics_table(analytics: dict) -> str:
    """Format analytics data as a table"""
    output = []

    # Conversion metrics
    conversion_metrics = analytics.get("conversion_metrics", {})
    if conversion_metrics:
        output.append("Conversion Metrics:")
        output.append("-" * 40)
        for key, value in conversion_metrics.items():
            output.append(f"{key.replace('_', ' ').title()}: {value}")
        output.append("")

    # Performance metrics
    performance_metrics = analytics.get("performance_metrics", {})
    if performance_metrics:
        output.append("Performance Metrics:")
        output.append("-" * 40)
        for key, value in performance_metrics.items():
            output.append(f"{key.replace('_', ' ').title()}: {value}")
        output.append("")

    # Error analysis
    error_analysis = analytics.get("error_analysis", {})
    if error_analysis:
        output.append("Error Analysis:")
        output.append("-" * 40)
        for key, value in error_analysis.items():
            if key != "most_common_errors" and key != "error_prone_steps":
                output.append(f"{key.replace('_', ' ').title()}: {value}")
        output.append("")

    # Steps summary
    steps = analytics.get("steps", [])
    if steps:
        output.append("Steps Summary:")
        output.append("-" * 40)
        for step in steps:
            output.append(f"Step: {step['name']}")
            output.append(f"  Users: {step['total_users']}")
            output.append(f"  Conversion: {step.get('conversion_rate', 0):.1f}%")
            output.append(f"  Avg Time: {step.get('avg_time_ms', 0):.0f}ms")
            output.append("")

    return "\n".join(output)


def _generate_funnel_html(chart_data: dict, funnel_name: str) -> str:
    """Generate HTML for funnel visualization"""
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Funnel Visualization - {funnel_name}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .chart-container {{ margin: 30px 0; }}
        .funnel-bar {{ background: linear-gradient(to right, #3b82f6, #60a5fa); height: 50px; margin: 10px 0; border-radius: 4px; display: flex; align-items: center; padding: 0 20px; color: white; font-weight: bold; position: relative; }}
        .funnel-label {{ position: absolute; left: 20px; }}
        .funnel-metrics {{ position: absolute; right: 20px; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Funnel Analysis</h1>
            <h2>{funnel_name}</h2>
        </div>
        
        <div class="chart-container">
            <h3>Funnel Visualization</h3>
            <div id="funnel-chart">
                {funnel_bars}
            </div>
        </div>
        
        <div class="chart-container">
            <canvas id="conversion-chart"></canvas>
        </div>
    </div>
    
    <script>
        // Chart.js implementation
        const ctx = document.getElementById('conversion-chart').getContext('2d');
        const conversionChart = new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: {step_labels},
                datasets: [{{
                    label: 'Conversion Rate (%)',
                    data: {conversion_data},
                    backgroundColor: '#3b82f6',
                    borderColor: '#2563eb',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
    """

    # Generate funnel bars
    steps = chart_data.get("steps", [])
    funnel_bars = []
    step_labels = []
    conversion_data = []

    for step in steps:
        width = step.get("width_percentage", 0)
        name = step.get("name", "")
        users = step.get("users", 0)
        conversion_rate = step.get("conversion_rate", 0)

        funnel_bars.append(f"""
        <div class="funnel-bar" style="width: {width}%">
            <span class="funnel-label">{name}</span>
            <span class="funnel-metrics">{users} users ({conversion_rate:.1f}% conv)</span>
        </div>
        """)

        step_labels.append(name)
        conversion_data.append(conversion_rate)

    return html_template.format(
        funnel_name=funnel_name,
        funnel_bars="\n".join(funnel_bars),
        step_labels=json.dumps(step_labels),
        conversion_data=json.dumps(conversion_data),
    )


# Add CLI group to main CLI
def add_funnel_cli(cli_group):
    """Add funnel CLI commands to main CLI group"""
    cli_group.add_command(funnel, name="funnel")
