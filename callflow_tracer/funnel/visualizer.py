"""
Funnel Visualization Module for CallFlow Tracer

This module provides comprehensive visualization capabilities for funnel analysis,
including interactive charts, heat maps, and detailed performance visualizations.
"""

import json
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import asdict
import statistics

from .analysis import FunnelAnalyzer, FunnelStep, FunnelSession, FunnelType


class FunnelVisualizer:
    """Main visualization engine for funnel analysis"""

    def __init__(self, analyzer: FunnelAnalyzer):
        self.analyzer = analyzer
        self.color_schemes = {
            "default": {
                "primary": "#3b82f6",
                "success": "#10b981",
                "warning": "#f59e0b",
                "error": "#ef4444",
                "neutral": "#6b7280",
                "background": "#f9fafb",
                "text": "#111827",
            },
            "dark": {
                "primary": "#60a5fa",
                "success": "#34d399",
                "warning": "#fbbf24",
                "error": "#f87171",
                "neutral": "#9ca3af",
                "background": "#1f2937",
                "text": "#f9fafb",
            },
            "vibrant": {
                "primary": "#8b5cf6",
                "success": "#06b6d4",
                "warning": "#f97316",
                "error": "#ec4899",
                "neutral": "#64748b",
                "background": "#fafafa",
                "text": "#0f172a",
            },
        }

    def generate_funnel_chart(
        self,
        chart_type: str = "standard",
        color_scheme: str = "default",
        include_metrics: bool = True,
    ) -> Dict[str, Any]:
        """Generate funnel chart visualization data"""
        analytics = self.analyzer.get_analytics()
        steps = analytics.get("steps", [])

        if not steps:
            return {"error": "No steps data available"}

        colors = self.color_schemes.get(color_scheme, self.color_schemes["default"])

        if chart_type == "standard":
            return self._generate_standard_funnel(steps, colors, include_metrics)
        elif chart_type == "stacked":
            return self._generate_stacked_funnel(steps, colors, include_metrics)
        elif chart_type == "3d":
            return self._generate_3d_funnel(steps, colors, include_metrics)
        elif chart_type == "comparison":
            return self._generate_comparison_funnel(steps, colors, include_metrics)
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")

    def _generate_standard_funnel(
        self, steps: List[Dict], colors: Dict, include_metrics: bool
    ) -> Dict[str, Any]:
        """Generate standard funnel chart"""
        max_users = max(step["total_users"] for step in steps) if steps else 1

        chart_data = {
            "type": "funnel",
            "style": "standard",
            "colors": colors,
            "config": {
                "animated": True,
                "show_labels": True,
                "show_percentages": True,
                "show_metrics": include_metrics,
            },
            "steps": [],
        }

        for i, step in enumerate(steps):
            width_percentage = (step["total_users"] / max_users) * 100
            conversion_rate = step.get("conversion_rate", 0)
            dropoff_rate = step.get("dropoff_rate", 0)

            step_data = {
                "name": step["name"],
                "order": i,
                "users": step["total_users"],
                "successful_users": step.get("successful_users", 0),
                "failed_users": step.get("failed_users", 0),
                "width_percentage": width_percentage,
                "conversion_rate": conversion_rate,
                "dropoff_rate": dropoff_rate,
                "color": self._get_step_color(conversion_rate, colors),
                "metrics": (
                    {
                        "avg_time_ms": step.get("avg_time_ms", 0),
                        "error_rate": step.get("error_rate", 0),
                        "median_time_ms": step.get("median_time_ms", 0),
                    }
                    if include_metrics
                    else {}
                ),
            }

            chart_data["steps"].append(step_data)

        return chart_data

    def _generate_stacked_funnel(
        self, steps: List[Dict], colors: Dict, include_metrics: bool
    ) -> Dict[str, Any]:
        """Generate stacked funnel chart showing success/failure breakdown"""
        chart_data = {
            "type": "funnel",
            "style": "stacked",
            "colors": colors,
            "config": {
                "animated": True,
                "show_labels": True,
                "show_percentages": True,
                "show_metrics": include_metrics,
                "stack_colors": {
                    "success": colors["success"],
                    "failure": colors["error"],
                    "pending": colors["warning"],
                },
            },
            "steps": [],
        }

        max_users = max(step["total_users"] for step in steps) if steps else 1

        for i, step in enumerate(steps):
            successful = step.get("successful_users", 0)
            failed = step.get("failed_users", 0)
            total = step["total_users"]

            width_percentage = (total / max_users) * 100
            success_percentage = (successful / total) * 100 if total > 0 else 0
            failure_percentage = (failed / total) * 100 if total > 0 else 0

            step_data = {
                "name": step["name"],
                "order": i,
                "total_users": total,
                "width_percentage": width_percentage,
                "stacks": [
                    {
                        "type": "success",
                        "count": successful,
                        "percentage": success_percentage,
                        "color": colors["success"],
                    },
                    {
                        "type": "failure",
                        "count": failed,
                        "percentage": failure_percentage,
                        "color": colors["error"],
                    },
                ],
                "metrics": (
                    {
                        "avg_time_ms": step.get("avg_time_ms", 0),
                        "error_rate": step.get("error_rate", 0),
                    }
                    if include_metrics
                    else {}
                ),
            }

            chart_data["steps"].append(step_data)

        return chart_data

    def _generate_3d_funnel(
        self, steps: List[Dict], colors: Dict, include_metrics: bool
    ) -> Dict[str, Any]:
        """Generate 3D perspective funnel chart"""
        chart_data = {
            "type": "funnel",
            "style": "3d",
            "colors": colors,
            "config": {
                "perspective": "isometric",
                "depth": 50,
                "show_labels": True,
                "show_percentages": True,
                "show_metrics": include_metrics,
                "lighting": {"ambient": 0.4, "directional": 0.6, "angle": 45},
            },
            "steps": [],
        }

        max_users = max(step["total_users"] for step in steps) if steps else 1

        for i, step in enumerate(steps):
            width = (step["total_users"] / max_users) * 100
            height = 80  # Fixed height for 3D effect

            # Calculate 3D coordinates
            x_center = 50
            y_position = i * (height + 10)

            step_data = {
                "name": step["name"],
                "order": i,
                "position": {
                    "x": x_center - (width / 2),
                    "y": y_position,
                    "z": i * 10,
                    "width": width,
                    "height": height,
                    "depth": 50,
                },
                "users": step["total_users"],
                "conversion_rate": step.get("conversion_rate", 0),
                "color": self._get_step_color(step.get("conversion_rate", 0), colors),
                "shading": self._calculate_3d_shading(width, colors),
                "metrics": (
                    {
                        "avg_time_ms": step.get("avg_time_ms", 0),
                        "error_rate": step.get("error_rate", 0),
                    }
                    if include_metrics
                    else {}
                ),
            }

            chart_data["steps"].append(step_data)

        return chart_data

    def _generate_comparison_funnel(
        self, steps: List[Dict], colors: Dict, include_metrics: bool
    ) -> Dict[str, Any]:
        """Generate comparison funnel for A/B testing"""
        chart_data = {
            "type": "funnel",
            "style": "comparison",
            "colors": colors,
            "config": {
                "show_labels": True,
                "show_percentages": True,
                "show_metrics": include_metrics,
                "comparison_mode": "side_by_side",
            },
            "variants": [],
        }

        # For demonstration, create A/B variants
        # In reality, this would use actual comparison data
        variant_a = {"name": "Variant A", "color": colors["primary"], "steps": []}

        variant_b = {"name": "Variant B", "color": colors["success"], "steps": []}

        max_users = max(step["total_users"] for step in steps) if steps else 1

        for i, step in enumerate(steps):
            # Simulate A/B test data
            base_users = step["total_users"]
            variant_a_users = int(base_users * 0.9)  # 10% worse
            variant_b_users = int(base_users * 1.1)  # 10% better

            # Variant A
            variant_a_step = {
                "name": step["name"],
                "order": i,
                "users": variant_a_users,
                "width_percentage": (variant_a_users / max_users) * 100,
                "conversion_rate": step.get("conversion_rate", 0) * 0.9,
                "metrics": (
                    {
                        "avg_time_ms": step.get("avg_time_ms", 0) * 1.1,
                        "error_rate": step.get("error_rate", 0) * 1.2,
                    }
                    if include_metrics
                    else {}
                ),
            }
            variant_a["steps"].append(variant_a_step)

            # Variant B
            variant_b_step = {
                "name": step["name"],
                "order": i,
                "users": variant_b_users,
                "width_percentage": (variant_b_users / max_users) * 100,
                "conversion_rate": step.get("conversion_rate", 0) * 1.1,
                "metrics": (
                    {
                        "avg_time_ms": step.get("avg_time_ms", 0) * 0.9,
                        "error_rate": step.get("error_rate", 0) * 0.8,
                    }
                    if include_metrics
                    else {}
                ),
            }
            variant_b["steps"].append(variant_b_step)

        chart_data["variants"] = [variant_a, variant_b]

        return chart_data

    def _get_step_color(self, conversion_rate: float, colors: Dict) -> str:
        """Get color based on conversion rate"""
        if conversion_rate >= 80:
            return colors["success"]
        elif conversion_rate >= 60:
            return colors["primary"]
        elif conversion_rate >= 40:
            return colors["warning"]
        else:
            return colors["error"]

    def _calculate_3d_shading(self, width: float, colors: Dict) -> Dict[str, str]:
        """Calculate 3D shading colors"""
        base_color = colors["primary"]
        # Simplified shading - in reality would use color manipulation
        return {
            "top": base_color,
            "front": self._darken_color(base_color, 0.8),
            "side": self._darken_color(base_color, 0.6),
        }

    def _darken_color(self, color: str, factor: float) -> str:
        """Simplified color darkening"""
        # This is a placeholder - real implementation would parse hex colors
        return color

    def generate_performance_chart(
        self, chart_type: str = "timeline"
    ) -> Dict[str, Any]:
        """Generate performance visualization charts"""
        analytics = self.analyzer.get_analytics()
        steps = analytics.get("steps", [])

        if chart_type == "timeline":
            return self._generate_timeline_chart(steps)
        elif chart_type == "heatmap":
            return self._generate_performance_heatmap(steps)
        elif chart_type == "scatter":
            return self._generate_performance_scatter(steps)
        elif chart_type == "distribution":
            return self._generate_performance_distribution(steps)
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")

    def _generate_timeline_chart(self, steps: List[Dict]) -> Dict[str, Any]:
        """Generate timeline performance chart"""
        chart_data = {
            "type": "timeline",
            "config": {
                "show_grid": True,
                "show_labels": True,
                "time_format": "ms",
                "y_axis": "performance_time",
            },
            "series": [],
        }

        # Average time series
        avg_times = {"name": "Average Time", "data": [], "color": "#3b82f6"}

        # Median time series
        median_times = {"name": "Median Time", "data": [], "color": "#10b981"}

        # P95 time series
        p95_times = {"name": "P95 Time", "data": [], "color": "#f59e0b"}

        for i, step in enumerate(steps):
            step_name = step["name"]

            avg_times["data"].append(
                {"x": i, "y": step.get("avg_time_ms", 0), "label": step_name}
            )

            median_times["data"].append(
                {"x": i, "y": step.get("median_time_ms", 0), "label": step_name}
            )

            p95_times["data"].append(
                {"x": i, "y": step.get("p95_time_ms", 0), "label": step_name}
            )

        chart_data["series"] = [avg_times, median_times, p95_times]

        return chart_data

    def _generate_performance_heatmap(self, steps: List[Dict]) -> Dict[str, Any]:
        """Generate performance heatmap"""
        chart_data = {
            "type": "heatmap",
            "config": {
                "color_scale": "viridis",
                "show_values": True,
                "cell_size": "auto",
            },
            "data": [],
        }

        # Create matrix of performance metrics
        metrics = [
            "avg_time_ms",
            "median_time_ms",
            "p95_time_ms",
            "p99_time_ms",
            "error_rate",
        ]

        for i, step in enumerate(steps):
            row = []
            for metric in metrics:
                value = step.get(metric, 0)
                row.append(
                    {
                        "x": i,
                        "y": metrics.index(metric),
                        "value": value,
                        "label": f"{step['name']} - {metric}: {value}",
                    }
                )
            chart_data["data"].extend(row)

        # Add axis labels
        chart_data["x_labels"] = [step["name"] for step in steps]
        chart_data["y_labels"] = metrics

        return chart_data

    def _generate_performance_scatter(self, steps: List[Dict]) -> Dict[str, Any]:
        """Generate scatter plot of performance vs conversion"""
        chart_data = {
            "type": "scatter",
            "config": {
                "x_axis": "conversion_rate",
                "y_axis": "avg_time_ms",
                "show_trendline": True,
                "bubble_size": "total_users",
            },
            "data": [],
        }

        for step in steps:
            chart_data["data"].append(
                {
                    "x": step.get("conversion_rate", 0),
                    "y": step.get("avg_time_ms", 0),
                    "size": step.get("total_users", 1),
                    "label": step["name"],
                    "color": self._get_step_color(
                        step.get("conversion_rate", 0), self.color_schemes["default"]
                    ),
                }
            )

        return chart_data

    def _generate_performance_distribution(self, steps: List[Dict]) -> Dict[str, Any]:
        """Generate performance distribution chart"""
        chart_data = {
            "type": "distribution",
            "config": {
                "chart_type": "box_plot",
                "show_outliers": True,
                "show_mean": True,
            },
            "data": [],
        }

        for step in steps:
            # Simplified - in reality would use actual distribution data
            avg_time = step.get("avg_time_ms", 0)
            median_time = step.get("median_time_ms", 0)
            p95_time = step.get("p95_time_ms", 0)

            chart_data["data"].append(
                {
                    "name": step["name"],
                    "min": avg_time * 0.5,  # Estimated
                    "q1": median_time * 0.8,  # Estimated
                    "median": median_time,
                    "q3": p95_time * 0.7,  # Estimated
                    "max": p95_time * 1.2,  # Estimated
                    "outliers": [],  # Would need actual data
                }
            )

        return chart_data

    def generate_error_analysis_chart(self) -> Dict[str, Any]:
        """Generate error analysis visualization"""
        analytics = self.analyzer.get_analytics()
        error_analysis = analytics.get("error_analysis", {})
        steps = analytics.get("steps", [])

        chart_data = {
            "type": "error_analysis",
            "config": {
                "show_error_types": True,
                "show_error_rates": True,
                "show_trends": True,
            },
            "charts": {},
        }

        # Error rate by step
        error_rates = {"type": "bar", "title": "Error Rate by Step", "data": []}

        for step in steps:
            error_rate = step.get("error_rate", 0)
            error_rates["data"].append(
                {
                    "x": step["name"],
                    "y": error_rate,
                    "color": (
                        "#ef4444"
                        if error_rate > 10
                        else "#f59e0b" if error_rate > 5 else "#10b981"
                    ),
                }
            )

        chart_data["charts"]["error_rates"] = error_rates

        # Common errors
        most_common = error_analysis.get("most_common_errors", [])
        if most_common:
            common_errors = {
                "type": "horizontal_bar",
                "title": "Most Common Errors",
                "data": [
                    {"x": count, "y": error, "color": "#ef4444"}
                    for error, count in most_common[:10]
                ],
            }
            chart_data["charts"]["common_errors"] = common_errors

        # Error-prone steps
        error_prone = error_analysis.get("error_prone_steps", [])
        if error_prone:
            error_prone_chart = {
                "type": "bubble",
                "title": "Error-Prone Steps",
                "data": [
                    {
                        "x": step["error_count"],
                        "y": step["error_rate"],
                        "size": step["error_count"],
                        "label": step["step"],
                    }
                    for step in error_prone
                ],
            }
            chart_data["charts"]["error_prone"] = error_prone_chart

        return chart_data

    def generate_user_segment_chart(self) -> Dict[str, Any]:
        """Generate user segment analysis chart"""
        analytics = self.analyzer.get_analytics()
        segments = analytics.get("user_segments", {})

        if not segments:
            return {"error": "No segment data available"}

        chart_data = {
            "type": "segment_analysis",
            "config": {
                "chart_type": "grouped_bar",
                "show_conversion_rates": True,
                "show_user_counts": True,
            },
            "data": [],
        }

        for segment_name, segment_data in segments.items():
            chart_data["data"].append(
                {
                    "segment": segment_name,
                    "total_users": segment_data.get("total", 0),
                    "completed_users": segment_data.get("completed", 0),
                    "conversion_rate": segment_data.get("conversion_rate", 0),
                }
            )

        return chart_data

    def generate_time_analysis_chart(self) -> Dict[str, Any]:
        """Generate time-based analysis chart"""
        analytics = self.analyzer.get_analytics()
        time_analysis = analytics.get("time_analysis", {})

        if not time_analysis:
            return {"error": "No time analysis data available"}

        chart_data = {
            "type": "time_analysis",
            "config": {
                "show_hourly_patterns": True,
                "show_trends": True,
                "time_format": "hour",
            },
            "charts": {},
        }

        # Hourly patterns
        hourly_patterns = time_analysis.get("hourly_patterns", {})
        if hourly_patterns:
            hourly_chart = {
                "type": "line",
                "title": "Hourly Conversion Patterns",
                "data": [
                    {"x": hour, "y": data["conversion_rate"], "users": data["total"]}
                    for hour, data in sorted(hourly_patterns.items())
                ],
            }
            chart_data["charts"]["hourly_patterns"] = hourly_chart

        return chart_data

    def generate_dashboard(self, theme: str = "light") -> Dict[str, Any]:
        """Generate complete dashboard with all visualizations"""
        analytics = self.analyzer.get_analytics()

        dashboard = {
            "type": "dashboard",
            "theme": theme,
            "config": {
                "auto_refresh": True,
                "refresh_interval": 30,  # seconds
                "layout": "grid",
                "responsive": True,
            },
            "widgets": [],
        }

        # Funnel chart widget
        funnel_widget = {
            "id": "funnel_chart",
            "type": "funnel",
            "title": f"Funnel Analysis: {self.analyzer.name}",
            "size": {"width": 12, "height": 6},
            "data": self.generate_funnel_chart("standard", "default", True),
        }
        dashboard["widgets"].append(funnel_widget)

        # Performance timeline widget
        performance_widget = {
            "id": "performance_timeline",
            "type": "timeline",
            "title": "Performance Timeline",
            "size": {"width": 8, "height": 4},
            "data": self.generate_performance_chart("timeline"),
        }
        dashboard["widgets"].append(performance_widget)

        # Error analysis widget
        error_widget = {
            "id": "error_analysis",
            "type": "error_analysis",
            "title": "Error Analysis",
            "size": {"width": 4, "height": 4},
            "data": self.generate_error_analysis_chart(),
        }
        dashboard["widgets"].append(error_widget)

        # Key metrics widget
        metrics_widget = {
            "id": "key_metrics",
            "type": "metrics",
            "title": "Key Metrics",
            "size": {"width": 12, "height": 2},
            "data": self._generate_key_metrics_widget(analytics),
        }
        dashboard["widgets"].append(metrics_widget)

        # Recommendations widget
        recommendations = analytics.get("recommendations", [])
        if recommendations:
            rec_widget = {
                "id": "recommendations",
                "type": "recommendations",
                "title": "Optimization Recommendations",
                "size": {"width": 12, "height": 3},
                "data": recommendations,
            }
            dashboard["widgets"].append(rec_widget)

        return dashboard

    def _generate_key_metrics_widget(self, analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate key metrics summary"""
        conversion_metrics = analytics.get("conversion_metrics", {})
        performance_metrics = analytics.get("performance_metrics", {})
        error_analysis = analytics.get("error_analysis", {})

        return {
            "overall_conversion_rate": conversion_metrics.get(
                "overall_conversion_rate", 0
            ),
            "total_sessions": conversion_metrics.get("total_sessions", 0),
            "completed_sessions": conversion_metrics.get("completed_sessions", 0),
            "average_step_time": performance_metrics.get("average_step_time_ms", 0),
            "total_errors": error_analysis.get("total_errors", 0),
            "error_rate": error_analysis.get("error_rate", 0),
        }

    def export_visualization(self, chart_type: str, format_type: str = "json") -> str:
        """Export visualization data"""
        if chart_type == "funnel":
            data = self.generate_funnel_chart()
        elif chart_type == "performance":
            data = self.generate_performance_chart()
        elif chart_type == "error":
            data = self.generate_error_analysis_chart()
        elif chart_type == "dashboard":
            data = self.generate_dashboard()
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")

        if format_type == "json":
            return json.dumps(data, indent=2, default=str)
        elif format_type == "html":
            return self._generate_html_visualization(data)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def _generate_html_visualization(self, data: Dict[str, Any]) -> str:
        """Generate HTML visualization"""
        # Build a simple, self-contained HTML rendering of the funnel
        name = self.analyzer.name
        analytics = self.analyzer.get_analytics()
        conv_metrics = (
            analytics.get("conversion_metrics", {})
            if isinstance(analytics, dict)
            else {}
        )
        perf_metrics = (
            analytics.get("performance_metrics", {})
            if isinstance(analytics, dict)
            else {}
        )
        err_metrics = (
            analytics.get("error_analysis", {}) if isinstance(analytics, dict) else {}
        )
        steps = []
        if data.get("steps"):
            steps = data["steps"]
        elif data.get("variants"):
            # Fallback: take first variant steps if comparison data
            steps = (data["variants"][0].get("steps") or []) if data["variants"] else []
        colors = data.get("colors", self.color_schemes.get("default", {}))
        primary = colors.get("primary", "#3b82f6")
        text = colors.get("text", "#111827")
        bg = colors.get("background", "#f9fafb")

        # Compute max width for normalization if missing
        max_users = (
            max((s.get("users", s.get("total_users", 0)) for s in steps), default=1)
            or 1
        )

        # Determine step with biggest relative dropoff for highlighting
        biggest_dropoff_value = None
        biggest_dropoff_name = None
        for _step in steps:
            rel = _step.get("relative_dropoff", _step.get("dropoff_rate", 0))
            if biggest_dropoff_value is None or rel > biggest_dropoff_value:
                biggest_dropoff_value = rel
                biggest_dropoff_name = _step.get("name")

        # Render rows
        rows = []
        rows_stacked = []
        for s in steps:
            users = s.get("users", s.get("total_users", 0))
            width_pct = s.get("width_percentage")
            if width_pct is None:
                width_pct = (users / max_users) * 100 if max_users else 0
            width_pct = max(5, min(100, round(width_pct, 2)))
            conv = s.get("conversion_rate", 0)
            avg_time = s.get("metrics", {}).get("avg_time_ms", s.get("avg_time_ms", 0))
            err = s.get("metrics", {}).get("error_rate", s.get("error_rate", 0))
            drop = s.get("dropoff_rate", 0)
            label = s.get("name", "")
            # Severity badges
            drop_severity = "normal"
            if drop >= 60:
                drop_severity = "critical"
            elif drop >= 30:
                drop_severity = "warning"
            err_severity = "normal"
            if err >= 10:
                err_severity = "critical"
            elif err >= 5:
                err_severity = "warning"

            error_badge = (
                f'<span class="badge badge-{err_severity}">error</span>'
                if err > 0
                else ""
            )
            drop_badge = (
                f'<span class="badge badge-{drop_severity}">drop</span>'
                if drop > 0
                else ""
            )

            highlight_class = (
                " step-highlight"
                if label == biggest_dropoff_name and (biggest_dropoff_value or 0) > 0
                else ""
            )
            highlight_badge = (
                ' <span class="badge badge-critical">Biggest drop-off</span>'
                if highlight_class
                else ""
            )

            rows.append(
                f"""
                <div class=\"row{highlight_class}\">\n                  <div class=\"label\">{label}</div>\n                  <div class=\"bar\" style=\"width:{width_pct}%\">{users} users • {conv:.1f}% conv</div>\n                </div>\n                <div class=\"metrics\">avg: {avg_time:.0f}ms • err: {err:.1f}% {error_badge} • drop: {drop:.1f}% {drop_badge}{highlight_badge}</div>\n                """
            )

            # Build stacked variant (success vs failure)
            succ = s.get("successful_users", 0)
            fail = s.get("failed_users", 0)
            total_sf = succ + fail if (succ + fail) > 0 else users
            spct = (succ / total_sf * 100) if total_sf else 0
            fpct = (fail / total_sf * 100) if total_sf else 0
            bar_total_width = width_pct
            succ_w = (
                max(2, round(bar_total_width * (spct / 100.0), 2))
                if bar_total_width > 0
                else 0
            )
            fail_w = (
                max(0, round(bar_total_width - succ_w, 2)) if bar_total_width > 0 else 0
            )

            rows_stacked.append(
                f"""
                <div class=\"row{highlight_class}\">\n                  <div class=\"label\">{label}</div>\n                  <div class=\"bar bar-stack\">\n                    <div class=\"bar-succ\" style=\"width:{succ_w}%\">{succ} ✓</div>\n                    <div class=\"bar-fail\" style=\"width:{fail_w}%\">{fail} ✕</div>\n                  </div>\n                </div>\n                <div class=\"metrics\">success: {spct:.1f}% • failure: {fpct:.1f}% • avg: {avg_time:.0f}ms</div>\n                """
            )

        html = f"""
<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Funnel Analysis: {name}</title>
  <style>
    :root {{ --primary: {primary}; --text: {text}; --bg: {bg}; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', 'Apple Color Emoji', 'Segoe UI Emoji'; margin: 0; color: var(--text); background: var(--bg); }}
    .page {{ padding: 32px 24px 40px; }}
    h1 {{ margin: 0 0 8px 0; font-size: 28px; }}
    .subtitle {{ color: #6b7280; margin-bottom: 20px; }}
    .container {{ max-width: 1100px; margin: 0 auto; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin: 16px 0 24px; }}
    .card {{ background: #ffffff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }}
    .card .label {{ font-size: 12px; color: #6b7280; }}
    .card .value {{ font-size: 22px; font-weight: 700; color: #111827; margin-top: 2px; }}
    .funnel {{ background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }}
    .row {{ display: flex; align-items: center; gap: 12px; margin: 12px 0 6px; }}
    .label {{ width: 220px; font-weight: 600; color: #111827; }}
    .bar {{ height: 36px; background: linear-gradient(90deg, var(--primary), #60a5fa); border-radius: 8px; display: flex; align-items: center; padding: 0 12px; color: #fff; font-weight: 600; white-space: nowrap; overflow: hidden; box-shadow: inset 0 -1px 0 rgba(255,255,255,0.25); }}
    .chip {{ display: inline-block; background: #eef2ff; color: #3730a3; border: 1px solid #c7d2fe; border-radius: 9999px; padding: 2px 8px; font-size: 12px; font-weight: 600; margin-left: 8px; }}
    .metrics {{ margin: 2px 0 8px 232px; font-size: 12px; color: #374151; }}
    .legend {{ margin-top: 14px; font-size: 12px; color: #4b5563; }}
    .footer {{ margin-top: 24px; color: #6b7280; font-size: 12px; }}
    .topbar {{ position: sticky; top: 0; z-index: 20; background: #111827; color: #e5e7eb; display: flex; align-items: center; justify-content: space-between; padding: 8px 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.3); }}
    .topbar-title {{ font-weight: 600; letter-spacing: .02em; font-size: 14px; }}
    .topbar-actions {{ display: flex; gap: 8px; align-items: center; }}
    .toolbar-button {{ background: #374151; color: #e5e7eb; border: 1px solid #4b5563; padding: 6px 10px; border-radius: 9999px; font-size: 12px; cursor: pointer; }}
    .toolbar-button:hover {{ background: #4b5563; }}
    .toolbar-button:focus-visible {{ outline: 2px solid #3b82f6; outline-offset: 2px; }}
    .bar-stack {{ width: 100%; padding: 0; overflow: hidden; display: flex; border-radius: 8px; }}
    .bar-succ {{ background: linear-gradient(90deg, #10b981, #34d399); height: 36px; display: flex; align-items: center; justify-content: flex-end; padding: 0 8px; color: #022c22; font-weight: 700; }}
    .bar-fail {{ background: linear-gradient(90deg, #f97373, #ef4444); height: 36px; display: flex; align-items: center; justify-content: flex-start; padding: 0 8px; color: #fff; font-weight: 700; }}
    .badge {{ display: inline-block; margin-left: 4px; padding: 1px 6px; border-radius: 9999px; font-size: 11px; border: 1px solid transparent; }}
    .badge-normal {{ background: #f3f4f6; color: #374151; border-color: #e5e7eb; }}
    .badge-warning {{ background: #fffbeb; color: #92400e; border-color: #fed7aa; }}
    .badge-critical {{ background: #fef2f2; color: #991b1b; border-color: #fecaca; }}
    .step-highlight {{ background: #fffbeb; }}
    .hidden {{ display: none; }}
    body.dark-theme {{ background: #020617; color: #e5e7eb; }}
    body.dark-theme .page {{ background: #020617; }}
    body.dark-theme .card, body.dark-theme .funnel {{ background: #020617; border-color: #374151; }}
    body.dark-theme .footer {{ color: #9ca3af; }}
    body.dark-theme .step-highlight {{ background: #020617; box-shadow: none; }}
    body.dark-theme .label {{ color: #e5e7eb; }}
    body.dark-theme .metrics {{ color: #d1d5db; }}
    body.dark-theme .legend {{ color: #9ca3af; }}
    body.dark-theme .subtitle {{ color: #9ca3af; }}
    body.dark-theme .card .label {{ color: #9ca3af; }}
    body.dark-theme .card .value {{ color: #f9fafb; }}
  </style>
  <script>/* Data for debugging if needed */
    window.__FUNNEL_DATA__ = {json.dumps(data)};
    console.log('Chart data:', window.__FUNNEL_DATA__);
    function toggleTheme() {{
      const body = document.body;
      body.classList.toggle('dark-theme');
    }}
    function toggleView(mode) {{
      const standard = document.getElementById('standard-view');
      const stacked = document.getElementById('stacked-view');
      if (!standard || !stacked) return;
      if (mode === 'stacked') {{
        standard.classList.add('hidden');
        stacked.classList.remove('hidden');
      }} else {{
        stacked.classList.add('hidden');
        standard.classList.remove('hidden');
      }}
    }}
  </script>
  </head>
<body>
  <div class="topbar" role="toolbar" aria-label="Funnel controls">
    <div class="topbar-title">CallFlow Tracer • Funnel</div>
    <div class="topbar-actions">
      <button type="button" class="toolbar-button" onclick="toggleView('standard')" aria-label="Show standard funnel view">Standard</button>
      <button type="button" class="toolbar-button" onclick="toggleView('stacked')" aria-label="Show stacked success and failure view">Stacked</button>
      <button type="button" class="toolbar-button" onclick="toggleTheme()" aria-label="Toggle light or dark theme">Toggle theme</button>
    </div>
  </div>
  <div class="page">
    <div class=\"container\">
      <h1>Funnel Analysis: {name}</h1>
      <div class=\"subtitle\">Interactive summary of conversion and performance</div>
      <div class="cards">
        <div class="card"><div class="label">Overall Conversion</div><div class="value">{conv_metrics.get('overall_conversion_rate', 0):.1f}%</div></div>
        <div class="card"><div class="label">Total Sessions</div><div class="value">{conv_metrics.get('total_sessions', 0)}</div></div>
        <div class="card"><div class="label">Completed Sessions</div><div class="value">{conv_metrics.get('completed_sessions', 0)}</div></div>
        <div class="card"><div class="label">Avg Step Time</div><div class="value">{perf_metrics.get('average_step_time_ms', 0):.0f} ms</div></div>
        <div class="card"><div class="label">Error Rate</div><div class="value">{err_metrics.get('error_rate', 0):.1f}%</div></div>
      </div>
      <div id="standard-view" class="funnel">
        {''.join(rows) if rows else '<p>No funnel steps to display.</p>'}
      </div>
      <div id="stacked-view" class="funnel hidden">
        {''.join(rows_stacked) if rows_stacked else '<p>No funnel steps to display.</p>'}
      </div>
      <div class="legend"><strong>Legend:</strong> Blue bars show total users per step. In stacked view, green represents successful users, red represents failed users. Badges: grey = normal, orange = warning, red = critical. "Biggest drop-off" marks the step with the highest relative drop-off.</div>
      <div class="footer">Rendered by CallFlow Tracer • Metrics are computed from the current funnel sessions and steps.</div>
    </div>
  </div>
</body>
</html>
"""
        return html


# Convenience functions
def create_funnel_visualizer(analyzer: FunnelAnalyzer) -> FunnelVisualizer:
    """Create a funnel visualizer"""
    return FunnelVisualizer(analyzer)


def generate_funnel_dashboard(
    analyzer: FunnelAnalyzer, theme: str = "light"
) -> Dict[str, Any]:
    """Generate complete funnel dashboard"""
    visualizer = FunnelVisualizer(analyzer)
    return visualizer.generate_dashboard(theme)
