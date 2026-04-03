"""
Advanced Funnel Analysis Algorithms for CallFlow Tracer

This module provides sophisticated algorithms for funnel analysis including
anomaly detection, predictive analytics, pattern recognition, and optimization
recommendations.
"""

import statistics
import math
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json

from .analysis import FunnelAnalyzer, FunnelStep, FunnelSession, StepStatus
from .models import AnomalyResult, PredictionResult, PatternResult


class FunnelAnomalyDetector:
    """Advanced anomaly detection for funnel analysis"""

    def __init__(self, analyzer: FunnelAnalyzer):
        self.analyzer = analyzer
        self.baseline_window_days = 30
        self.significance_threshold = 2.0  # Standard deviations
        self.min_sample_size = 100

    def detect_anomalies(self) -> List[AnomalyResult]:
        """Detect all types of anomalies in the funnel"""
        anomalies = []

        # Conversion rate anomalies
        conversion_anomalies = self._detect_conversion_anomalies()
        anomalies.extend(conversion_anomalies)

        # Performance anomalies
        performance_anomalies = self._detect_performance_anomalies()
        anomalies.extend(performance_anomalies)

        # Error rate anomalies
        error_anomalies = self._detect_error_anomalies()
        anomalies.extend(error_anomalies)

        # Time-based anomalies
        time_anomalies = self._detect_time_based_anomalies()
        anomalies.extend(time_anomalies)

        # User behavior anomalies
        behavior_anomalies = self._detect_behavior_anomalies()
        anomalies.extend(behavior_anomalies)

        # Sort by severity and confidence
        anomalies.sort(
            key=lambda x: (self._severity_score(x.severity), x.confidence), reverse=True
        )

        return anomalies

    def _detect_conversion_anomalies(self) -> List[AnomalyResult]:
        """Detect conversion rate anomalies"""
        anomalies = []
        analytics = self.analyzer.get_analytics()
        steps = analytics.get("steps", [])

        for step in steps:
            conversion_rate = step.get("conversion_rate", 0)
            step_name = step["name"]

            # Check for abnormally low conversion
            if conversion_rate < 20 and step["total_users"] > self.min_sample_size:
                severity = "critical" if conversion_rate < 10 else "high"
                anomalies.append(
                    AnomalyResult(
                        anomaly_type="low_conversion",
                        severity=severity,
                        confidence=0.8,
                        description=f"Step '{step_name}' has unusually low conversion rate: {conversion_rate:.1f}%",
                        affected_steps=[step_name],
                        metrics={
                            "conversion_rate": conversion_rate,
                            "total_users": step["total_users"],
                        },
                        timestamp=datetime.now(),
                        recommendations=[
                            "Investigate user experience issues",
                            "Simplify the step or provide better guidance",
                            "Check for technical errors or bugs",
                        ],
                    )
                )

            # Check for sudden drop in conversion
            relative_dropoff = step.get("relative_dropoff", 0)
            if relative_dropoff > 50:
                anomalies.append(
                    AnomalyResult(
                        anomaly_type="high_dropoff",
                        severity="high",
                        confidence=0.9,
                        description=f"Step '{step_name}' shows high relative dropoff: {relative_dropoff:.1f}%",
                        affected_steps=[step_name],
                        metrics={
                            "relative_dropoff": relative_dropoff,
                            "conversion_rate": conversion_rate,
                        },
                        timestamp=datetime.now(),
                        recommendations=[
                            "Analyze why users are abandoning at this step",
                            "Review step complexity and user friction",
                            "Consider splitting the step into smaller parts",
                        ],
                    )
                )

        return anomalies

    def _detect_performance_anomalies(self) -> List[AnomalyResult]:
        """Detect performance anomalies"""
        anomalies = []
        analytics = self.analyzer.get_analytics()
        steps = analytics.get("steps", [])

        # Calculate performance baseline
        avg_times = [
            step.get("avg_time_ms", 0)
            for step in steps
            if step.get("avg_time_ms", 0) > 0
        ]
        if len(avg_times) < 2:
            return anomalies

        baseline_mean = statistics.mean(avg_times)
        baseline_std = statistics.stdev(avg_times) if len(avg_times) > 1 else 0

        for step in steps:
            avg_time = step.get("avg_time_ms", 0)
            step_name = step["name"]

            if avg_time == 0:
                continue

            # Check for outlier performance
            if baseline_std > 0:
                z_score = abs(avg_time - baseline_mean) / baseline_std
                if z_score > self.significance_threshold:
                    severity = "critical" if avg_time > baseline_mean * 3 else "high"
                    anomalies.append(
                        AnomalyResult(
                            anomaly_type="performance_outlier",
                            severity=severity,
                            confidence=min(0.9, z_score / 3),
                            description=f"Step '{step_name}' has anomalous performance: {avg_time:.1f}ms (z-score: {z_score:.1f})",
                            affected_steps=[step_name],
                            metrics={
                                "avg_time_ms": avg_time,
                                "z_score": z_score,
                                "baseline_mean": baseline_mean,
                            },
                            timestamp=datetime.now(),
                            recommendations=[
                                "Profile the function for bottlenecks",
                                "Check for database query inefficiencies",
                                "Consider caching or optimization strategies",
                            ],
                        )
                    )

            # Check for extremely slow steps
            if avg_time > 10000:  # 10 seconds
                anomalies.append(
                    AnomalyResult(
                        anomaly_type="slow_performance",
                        severity="critical",
                        confidence=0.95,
                        description=f"Step '{step_name}' is extremely slow: {avg_time:.1f}ms",
                        affected_steps=[step_name],
                        metrics={"avg_time_ms": avg_time},
                        timestamp=datetime.now(),
                        recommendations=[
                            "Immediate optimization required",
                            "Check for infinite loops or blocking operations",
                            "Consider async processing or background jobs",
                        ],
                    )
                )

        return anomalies

    def _detect_error_anomalies(self) -> List[AnomalyResult]:
        """Detect error rate anomalies"""
        anomalies = []
        analytics = self.analyzer.get_analytics()
        steps = analytics.get("steps", [])

        for step in steps:
            error_rate = step.get("error_rate", 0)
            step_name = step["name"]

            # Check for high error rates
            if error_rate > 20:
                severity = "critical" if error_rate > 50 else "high"
                anomalies.append(
                    AnomalyResult(
                        anomaly_type="high_error_rate",
                        severity=severity,
                        confidence=0.9,
                        description=f"Step '{step_name}' has high error rate: {error_rate:.1f}%",
                        affected_steps=[step_name],
                        metrics={
                            "error_rate": error_rate,
                            "error_count": step.get("error_count", 0),
                        },
                        timestamp=datetime.now(),
                        recommendations=[
                            "Review error handling and validation",
                            "Check for external service failures",
                            "Implement better error logging and monitoring",
                        ],
                    )
                )

        return anomalies

    def _detect_time_based_anomalies(self) -> List[AnomalyResult]:
        """Detect time-based anomalies"""
        anomalies = []
        analytics = self.analyzer.get_analytics()
        time_analysis = analytics.get("time_analysis", {})

        hourly_patterns = time_analysis.get("hourly_patterns", {})
        if not hourly_patterns:
            return anomalies

        # Find conversion rates by hour
        conversion_rates = [
            (hour, data.get("conversion_rate", 0))
            for hour, data in hourly_patterns.items()
        ]

        if len(conversion_rates) < 3:
            return anomalies

        rates = [rate for _, rate in conversion_rates]
        mean_rate = statistics.mean(rates)
        std_rate = statistics.stdev(rates) if len(rates) > 1 else 0

        for hour, rate in conversion_rates:
            if std_rate > 0:
                z_score = abs(rate - mean_rate) / std_rate
                if z_score > self.significance_threshold:
                    anomalies.append(
                        AnomalyResult(
                            anomaly_type="time_based_anomaly",
                            severity="medium",
                            confidence=min(0.8, z_score / 3),
                            description=f"Hour {hour}:00 shows unusual conversion rate: {rate:.1f}%",
                            affected_steps=[],
                            metrics={
                                "hour": hour,
                                "conversion_rate": rate,
                                "z_score": z_score,
                            },
                            timestamp=datetime.now(),
                            recommendations=[
                                "Investigate time-specific issues (e.g., load, maintenance)",
                                "Check for geographical or timezone effects",
                                "Review scheduled tasks or batch processes",
                            ],
                        )
                    )

        return anomalies

    def _detect_behavior_anomalies(self) -> List[AnomalyResult]:
        """Detect user behavior anomalies"""
        anomalies = []
        sessions = list(self.analyzer.sessions.values())

        if len(sessions) < self.min_sample_size:
            return anomalies

        # Calculate session duration statistics
        durations = [session.total_duration_ms for session in sessions]
        mean_duration = statistics.mean(durations)
        std_duration = statistics.stdev(durations) if len(durations) > 1 else 0

        # Find unusually long or short sessions
        for session in sessions:
            if std_duration > 0:
                z_score = abs(session.total_duration_ms - mean_duration) / std_duration
                if z_score > self.significance_threshold:
                    behavior_type = (
                        "extremely_long"
                        if session.total_duration_ms > mean_duration
                        else "extremely_short"
                    )
                    anomalies.append(
                        AnomalyResult(
                            anomaly_type="behavior_anomaly",
                            severity="medium",
                            confidence=min(0.7, z_score / 3),
                            description=f"Session {session.session_id} shows {behavior_type} duration: {session.total_duration_ms:.1f}ms",
                            affected_steps=[],
                            metrics={
                                "duration_ms": session.total_duration_ms,
                                "z_score": z_score,
                            },
                            timestamp=datetime.now(),
                            recommendations=[
                                "Investigate user journey patterns",
                                "Check for technical issues or confusion",
                                "Analyze user segments for behavioral differences",
                            ],
                        )
                    )

        return anomalies

    def _severity_score(self, severity: str) -> int:
        """Convert severity to numeric score"""
        scores = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        return scores.get(severity, 0)


class FunnelPredictor:
    """Predictive analytics for funnel performance"""

    def __init__(self, analyzer: FunnelAnalyzer):
        self.analyzer = analyzer
        self.prediction_horizons = {
            "next_hour": 1,
            "next_day": 24,
            "next_week": 168,
            "next_month": 720,
        }

    def predict_conversion_rate(self, horizon: str = "next_day") -> PredictionResult:
        """Predict future conversion rates"""
        analytics = self.analyzer.get_analytics()
        conversion_metrics = analytics.get("conversion_metrics", {})

        current_rate = conversion_metrics.get("overall_conversion_rate", 0)
        trend = conversion_metrics.get("conversion_trend", {})

        # Simple linear prediction based on trend
        trend_direction = trend.get("trend", "stable")
        trend_change = trend.get("change_percentage", 0)

        predicted_change = 0
        if trend_direction == "improving":
            predicted_change = abs(trend_change) * 0.5  # Conservative estimate
        elif trend_direction == "declining":
            predicted_change = -abs(trend_change) * 0.5

        predicted_rate = current_rate + predicted_change
        confidence = 0.7 if trend_direction != "stable" else 0.5

        return PredictionResult(
            prediction_type="conversion_rate",
            confidence=confidence,
            predicted_value=predicted_rate,
            time_horizon=horizon,
            factors=["historical_trend", "current_performance", "seasonal_patterns"],
            accuracy_estimate=confidence * 0.8,
            recommendations=self._generate_conversion_recommendations(
                predicted_rate, current_rate
            ),
        )

    def predict_performance(self, horizon: str = "next_day") -> PredictionResult:
        """Predict future performance metrics"""
        analytics = self.analyzer.get_analytics()
        performance_metrics = analytics.get("performance_metrics", {})

        current_avg_time = performance_metrics.get("average_step_time_ms", 0)

        # Simple prediction based on recent trends
        # In reality, this would use more sophisticated time series analysis
        predicted_time = current_avg_time * 1.02  # Assume 2% degradation
        confidence = 0.6

        return PredictionResult(
            prediction_type="performance",
            confidence=confidence,
            predicted_value=predicted_time,
            time_horizon=horizon,
            factors=["historical_performance", "load_patterns", "resource_usage"],
            accuracy_estimate=confidence * 0.7,
            recommendations=self._generate_performance_recommendations(
                predicted_time, current_avg_time
            ),
        )

    def predict_volume(self, horizon: str = "next_day") -> PredictionResult:
        """Predict future session volume"""
        sessions = list(self.analyzer.sessions.values())

        if not sessions:
            return PredictionResult(
                prediction_type="volume",
                confidence=0.0,
                predicted_value=0,
                time_horizon=horizon,
                factors=[],
                accuracy_estimate=0.0,
                recommendations=["Insufficient data for volume prediction"],
            )

        # Calculate recent session rate
        recent_sessions = [
            s
            for s in sessions
            if (datetime.now() - s.start_time).total_seconds() < 3600
        ]
        hourly_rate = len(recent_sessions)

        # Predict based on hourly rate and time horizon
        hours_factor = self.prediction_horizons.get(horizon, 24)
        predicted_volume = hourly_rate * hours_factor

        confidence = 0.8 if len(recent_sessions) > 10 else 0.5

        return PredictionResult(
            prediction_type="volume",
            confidence=confidence,
            predicted_value=predicted_volume,
            time_horizon=horizon,
            factors=["recent_activity", "historical_patterns", "seasonal_trends"],
            accuracy_estimate=confidence * 0.75,
            recommendations=self._generate_volume_recommendations(predicted_volume),
        )

    def _generate_conversion_recommendations(
        self, predicted: float, current: float
    ) -> List[str]:
        """Generate conversion optimization recommendations"""
        recommendations = []

        if predicted < current:
            recommendations.extend(
                [
                    "Implement conversion optimization strategies",
                    "Analyze and address conversion bottlenecks",
                    "Consider A/B testing different approaches",
                ]
            )
        elif predicted > current:
            recommendations.extend(
                [
                    "Monitor for conversion improvements",
                    "Document successful optimization strategies",
                    "Scale successful approaches to other funnels",
                ]
            )
        else:
            recommendations.extend(
                [
                    "Maintain current conversion strategies",
                    "Look for incremental improvement opportunities",
                    "Monitor for external factors affecting conversion",
                ]
            )

        return recommendations

    def _generate_performance_recommendations(
        self, predicted: float, current: float
    ) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []

        if predicted > current * 1.1:  # 10% degradation expected
            recommendations.extend(
                [
                    "Proactive performance optimization required",
                    "Review and optimize slow database queries",
                    "Consider implementing caching strategies",
                ]
            )
        elif predicted < current * 0.9:  # 10% improvement expected
            recommendations.extend(
                [
                    "Monitor performance improvements",
                    "Document successful optimizations",
                    "Apply similar optimizations to other areas",
                ]
            )
        else:
            recommendations.extend(
                [
                    "Maintain current performance levels",
                    "Continue monitoring for performance issues",
                    "Plan for capacity scaling as needed",
                ]
            )

        return recommendations

    def _generate_volume_recommendations(self, predicted_volume: float) -> List[str]:
        """Generate volume handling recommendations"""
        recommendations = []

        if predicted_volume > 1000:
            recommendations.extend(
                [
                    "Prepare for high traffic volume",
                    "Ensure infrastructure can handle load",
                    "Implement load balancing and scaling strategies",
                ]
            )
        elif predicted_volume < 100:
            recommendations.extend(
                [
                    "Low volume expected - optimize for efficiency",
                    "Consider resource consolidation",
                    "Focus on conversion optimization rather than scale",
                ]
            )
        else:
            recommendations.extend(
                [
                    "Normal volume expected - maintain current capacity",
                    "Monitor for unexpected spikes or drops",
                    "Prepare contingency plans for volume changes",
                ]
            )

        return recommendations


class FunnelPatternRecognizer:
    """Pattern recognition for funnel analysis"""

    def __init__(self, analyzer: FunnelAnalyzer):
        self.analyzer = analyzer
        self.min_pattern_frequency = 3
        self.pattern_confidence_threshold = 0.6

    def recognize_patterns(self) -> List[PatternResult]:
        """Recognize all types of patterns in funnel data"""
        patterns = []

        # Conversion patterns
        conversion_patterns = self._recognize_conversion_patterns()
        patterns.extend(conversion_patterns)

        # Performance patterns
        performance_patterns = self._recognize_performance_patterns()
        patterns.extend(performance_patterns)

        # Error patterns
        error_patterns = self._recognize_error_patterns()
        patterns.extend(error_patterns)

        # User journey patterns
        journey_patterns = self._recognize_journey_patterns()
        patterns.extend(journey_patterns)

        # Time-based patterns
        time_patterns = self._recognize_time_patterns()
        patterns.extend(time_patterns)

        # Sort by impact and confidence
        patterns.sort(key=lambda x: x.impact_score * x.confidence, reverse=True)

        return patterns

    def _recognize_conversion_patterns(self) -> List[PatternResult]:
        """Recognize conversion-related patterns"""
        patterns = []
        analytics = self.analyzer.get_analytics()
        steps = analytics.get("steps", [])

        # Pattern: Step-wise conversion degradation
        conversion_rates = [
            (step["name"], step.get("conversion_rate", 0)) for step in steps
        ]

        # Check for consistent degradation pattern
        degradation_count = 0
        for i in range(1, len(conversion_rates)):
            if conversion_rates[i][1] < conversion_rates[i - 1][1]:
                degradation_count += 1

        if degradation_count >= len(steps) * 0.7:  # 70% of steps show degradation
            patterns.append(
                PatternResult(
                    pattern_type="conversion_degradation",
                    description="Consistent step-by-step conversion degradation",
                    frequency=degradation_count,
                    confidence=0.8,
                    impact_score=0.7,
                    examples=[
                        {"step": name, "rate": rate} for name, rate in conversion_rates
                    ],
                    actionable_insights=[
                        "Review funnel design for complexity",
                        "Consider simplifying multi-step processes",
                        "Implement progress indicators and user guidance",
                    ],
                )
            )

        # Pattern: Conversion cliff (sudden large drop)
        for i in range(1, len(steps)):
            prev_rate = steps[i - 1].get("conversion_rate", 0)
            curr_rate = steps[i].get("conversion_rate", 0)

            if prev_rate > 0 and (prev_rate - curr_rate) / prev_rate > 0.5:  # 50%+ drop
                patterns.append(
                    PatternResult(
                        pattern_type="conversion_cliff",
                        description=f"Sudden conversion drop at step '{steps[i]['name']}'",
                        frequency=1,
                        confidence=0.9,
                        impact_score=0.9,
                        examples=[
                            {
                                "step": steps[i]["name"],
                                "previous_rate": prev_rate,
                                "current_rate": curr_rate,
                                "drop_percentage": ((prev_rate - curr_rate) / prev_rate)
                                * 100,
                            }
                        ],
                        actionable_insights=[
                            f"Investigate step '{steps[i]['name']}' for UX issues",
                            "Check for technical errors or bugs",
                            "Consider breaking down complex steps",
                        ],
                    )
                )

        return patterns

    def _recognize_performance_patterns(self) -> List[PatternResult]:
        """Recognize performance-related patterns"""
        patterns = []
        analytics = self.analyzer.get_analytics()
        steps = analytics.get("steps", [])

        # Pattern: Performance increases through funnel
        times = [
            (step["name"], step.get("avg_time_ms", 0))
            for step in steps
            if step.get("avg_time_ms", 0) > 0
        ]

        if len(times) >= 3:
            increasing_count = 0
            for i in range(1, len(times)):
                if times[i][1] > times[i - 1][1]:
                    increasing_count += 1

            if increasing_count >= len(times) * 0.7:
                patterns.append(
                    PatternResult(
                        pattern_type="performance_degradation",
                        description="Performance degrades through funnel steps",
                        frequency=increasing_count,
                        confidence=0.7,
                        impact_score=0.6,
                        examples=[{"step": name, "time": time} for name, time in times],
                        actionable_insights=[
                            "Optimize later steps which may accumulate complexity",
                            "Check for resource leaks or memory issues",
                            "Consider async processing for long-running steps",
                        ],
                    )
                )

        # Pattern: Performance outliers
        if len(times) >= 2:
            time_values = [time for _, time in times]
            mean_time = statistics.mean(time_values)
            std_time = statistics.stdev(time_values) if len(time_values) > 1 else 0

            if std_time > 0:
                outliers = [
                    (name, time)
                    for name, time in times
                    if abs(time - mean_time) / std_time > 2
                ]

                if outliers:
                    patterns.append(
                        PatternResult(
                            pattern_type="performance_outliers",
                            description="Steps with anomalous performance",
                            frequency=len(outliers),
                            confidence=0.8,
                            impact_score=0.8,
                            examples=[
                                {
                                    "step": name,
                                    "time": time,
                                    "z_score": abs(time - mean_time) / std_time,
                                }
                                for name, time in outliers
                            ],
                            actionable_insights=[
                                "Profile outlier steps for bottlenecks",
                                "Check for database query inefficiencies",
                                "Review algorithmic complexity",
                            ],
                        )
                    )

        return patterns

    def _recognize_error_patterns(self) -> List[PatternResult]:
        """Recognize error-related patterns"""
        patterns = []
        analytics = self.analyzer.get_analytics()
        error_analysis = analytics.get("error_analysis", {})

        # Pattern: Common error types
        most_common = error_analysis.get("most_common_errors", [])
        if most_common:
            patterns.append(
                PatternResult(
                    pattern_type="recurring_errors",
                    description="Recurring error types across funnel",
                    frequency=len(most_common),
                    confidence=0.9,
                    impact_score=0.7,
                    examples=[
                        {"error": error, "count": count}
                        for error, count in most_common[:5]
                    ],
                    actionable_insights=[
                        "Fix root causes of common errors",
                        "Implement better error handling and validation",
                        "Add user-friendly error messages and recovery options",
                    ],
                )
            )

        # Pattern: Error-prone steps
        error_prone = error_analysis.get("error_prone_steps", [])
        if error_prone:
            patterns.append(
                PatternResult(
                    pattern_type="error_hotspots",
                    description="Steps with consistently high error rates",
                    frequency=len(error_prone),
                    confidence=0.8,
                    impact_score=0.8,
                    examples=error_prone,
                    actionable_insights=[
                        "Prioritize fixes for error-prone steps",
                        "Implement additional validation and error prevention",
                        "Monitor these steps closely after fixes",
                    ],
                )
            )

        return patterns

    def _recognize_journey_patterns(self) -> List[PatternResult]:
        """Recognize user journey patterns"""
        patterns = []
        sessions = list(self.analyzer.sessions.values())

        if len(sessions) < 10:
            return patterns

        # Pattern: Common exit points
        exit_steps = defaultdict(int)
        for session in sessions:
            if session.failed_steps:
                last_failed = session.failed_steps[-1]
                exit_steps[last_failed] += 1

        if exit_steps:
            common_exits = sorted(exit_steps.items(), key=lambda x: x[1], reverse=True)[
                :3
            ]
            patterns.append(
                PatternResult(
                    pattern_type="common_exit_points",
                    description="Steps where users commonly abandon the funnel",
                    frequency=len(common_exits),
                    confidence=0.7,
                    impact_score=0.8,
                    examples=[
                        {"step": step, "exit_count": count}
                        for step, count in common_exits
                    ],
                    actionable_insights=[
                        "Investigate why users abandon at these steps",
                        "Simplify or improve problematic steps",
                        "Add user guidance and support at critical points",
                    ],
                )
            )

        # Pattern: Fast completions vs slow completions
        durations = [
            session.total_duration_ms for session in sessions if session.is_completed
        ]
        if len(durations) >= 5:
            quartiles = statistics.quantiles(durations, n=4)
            fast_threshold = quartiles[0]  # 25th percentile
            slow_threshold = quartiles[2]  # 75th percentile

            fast_sessions = [
                s
                for s in sessions
                if s.is_completed and s.total_duration_ms <= fast_threshold
            ]
            slow_sessions = [
                s
                for s in sessions
                if s.is_completed and s.total_duration_ms >= slow_threshold
            ]

            if fast_sessions and slow_sessions:
                patterns.append(
                    PatternResult(
                        pattern_type="duration_variance",
                        description="Significant variance in completion times",
                        frequency=len(fast_sessions) + len(slow_sessions),
                        confidence=0.6,
                        impact_score=0.5,
                        examples=[
                            {
                                "type": "fast_completions",
                                "count": len(fast_sessions),
                                "avg_time": fast_threshold,
                            },
                            {
                                "type": "slow_completions",
                                "count": len(slow_sessions),
                                "avg_time": slow_threshold,
                            },
                        ],
                        actionable_insights=[
                            "Analyze differences between fast and slow journeys",
                            "Identify and eliminate bottlenecks causing delays",
                            "Optimize user paths for faster completion",
                        ],
                    )
                )

        return patterns

    def _recognize_time_patterns(self) -> List[PatternResult]:
        """Recognize time-based patterns"""
        patterns = []
        analytics = self.analyzer.get_analytics()
        time_analysis = analytics.get("time_analysis", {})

        hourly_patterns = time_analysis.get("hourly_patterns", {})
        if not hourly_patterns:
            return patterns

        # Pattern: Peak hours
        hourly_data = [
            (hour, data.get("total", 0)) for hour, data in hourly_patterns.items()
        ]
        if hourly_data:
            max_hour, max_count = max(hourly_data, key=lambda x: x[1])
            avg_count = statistics.mean([count for _, count in hourly_data])

            if max_count > avg_count * 1.5:  # 50% above average
                patterns.append(
                    PatternResult(
                        pattern_type="peak_activity_hours",
                        description=f"Peak activity at hour {max_hour}:00",
                        frequency=1,
                        confidence=0.8,
                        impact_score=0.6,
                        examples=[
                            {"hour": max_hour, "count": max_count, "average": avg_count}
                        ],
                        actionable_insights=[
                            f"Ensure system can handle peak load at {max_hour}:00",
                            "Schedule maintenance during low-activity periods",
                            "Optimize user experience during peak hours",
                        ],
                    )
                )

        # Pattern: Low conversion hours
        conversion_data = [
            (hour, data.get("conversion_rate", 0))
            for hour, data in hourly_patterns.items()
        ]
        if conversion_data:
            min_hour, min_rate = min(conversion_data, key=lambda x: x[1])
            avg_rate = statistics.mean([rate for _, rate in conversion_data])

            if min_rate < avg_rate * 0.7:  # 30% below average
                patterns.append(
                    PatternResult(
                        pattern_type="low_conversion_hours",
                        description=f"Low conversion at hour {min_hour}:00",
                        frequency=1,
                        confidence=0.7,
                        impact_score=0.5,
                        examples=[
                            {"hour": min_hour, "rate": min_rate, "average": avg_rate}
                        ],
                        actionable_insights=[
                            f"Investigate conversion issues at {min_hour}:00",
                            "Check for technical issues during these hours",
                            "Consider time-specific user experience improvements",
                        ],
                    )
                )

        return patterns


class FunnelOptimizer:
    """Optimization recommendations and strategies"""

    def __init__(self, analyzer: FunnelAnalyzer):
        self.analyzer = analyzer
        self.optimization_strategies = {
            "conversion": self._optimize_conversion,
            "performance": self._optimize_performance,
            "errors": self._optimize_errors,
            "user_experience": self._optimize_user_experience,
        }

    def generate_optimization_plan(self) -> Dict[str, Any]:
        """Generate comprehensive optimization plan"""
        anomaly_detector = FunnelAnomalyDetector(self.analyzer)
        pattern_recognizer = FunnelPatternRecognizer(self.analyzer)

        # Get analysis results
        anomalies = anomaly_detector.detect_anomalies()
        patterns = pattern_recognizer.recognize_patterns()
        analytics = self.analyzer.get_analytics()

        # Generate optimization strategies
        plan = {
            "summary": self._generate_optimization_summary(
                anomalies, patterns, analytics
            ),
            "priorities": self._calculate_optimization_priorities(anomalies, patterns),
            "strategies": {},
            "implementation_plan": self._create_implementation_plan(
                anomalies, patterns
            ),
            "expected_impact": self._estimate_expected_impact(
                anomalies, patterns, analytics
            ),
            "success_metrics": self._define_success_metrics(),
        }

        # Generate specific strategies
        for strategy_type, strategy_func in self.optimization_strategies.items():
            plan["strategies"][strategy_type] = strategy_func(
                anomalies, patterns, analytics
            )

        return plan

    def _generate_optimization_summary(
        self,
        anomalies: List[AnomalyResult],
        patterns: List[PatternResult],
        analytics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate optimization summary"""
        conversion_metrics = analytics.get("conversion_metrics", {})
        overall_rate = conversion_metrics.get("overall_conversion_rate", 0)

        critical_anomalies = [a for a in anomalies if a.severity == "critical"]
        high_impact_patterns = [p for p in patterns if p.impact_score > 0.7]

        return {
            "current_performance": {
                "conversion_rate": overall_rate,
                "total_sessions": conversion_metrics.get("total_sessions", 0),
                "completed_sessions": conversion_metrics.get("completed_sessions", 0),
            },
            "issues_identified": {
                "critical_anomalies": len(critical_anomalies),
                "high_impact_patterns": len(high_impact_patterns),
                "total_anomalies": len(anomalies),
                "total_patterns": len(patterns),
            },
            "optimization_potential": {
                "conversion_improvement": min(
                    50, (100 - overall_rate) * 0.6
                ),  # Up to 60% of remaining gap
                "performance_improvement": 25,  # 25% performance improvement target
                "error_reduction": 50,  # 50% error reduction target
            },
        }

    def _calculate_optimization_priorities(
        self, anomalies: List[AnomalyResult], patterns: List[PatternResult]
    ) -> List[Dict[str, Any]]:
        """Calculate optimization priorities"""
        priorities = []

        # Prioritize anomalies
        for anomaly in anomalies[:5]:  # Top 5 anomalies
            priorities.append(
                {
                    "type": "anomaly",
                    "title": anomaly.description,
                    "priority": self._priority_score(
                        anomaly.severity, anomaly.confidence
                    ),
                    "impact": (
                        "high" if anomaly.severity in ["critical", "high"] else "medium"
                    ),
                    "effort": self._estimate_effort(anomaly),
                    "actions": anomaly.recommendations,
                }
            )

        # Prioritize patterns
        for pattern in patterns[:5]:  # Top 5 patterns
            priorities.append(
                {
                    "type": "pattern",
                    "title": pattern.description,
                    "priority": pattern.impact_score * pattern.confidence,
                    "impact": "high" if pattern.impact_score > 0.7 else "medium",
                    "effort": self._estimate_pattern_effort(pattern),
                    "actions": pattern.actionable_insights,
                }
            )

        # Sort by priority
        priorities.sort(key=lambda x: x["priority"], reverse=True)

        return priorities

    def _priority_score(self, severity: str, confidence: float) -> float:
        """Calculate priority score"""
        severity_scores = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        return severity_scores.get(severity, 0) * confidence

    def _estimate_effort(self, anomaly: AnomalyResult) -> str:
        """Estimate implementation effort"""
        if anomaly.severity == "critical":
            return "high"
        elif anomaly.severity == "high":
            return "medium"
        else:
            return "low"

    def _estimate_pattern_effort(self, pattern: PatternResult) -> str:
        """Estimate pattern fix effort"""
        if pattern.impact_score > 0.8:
            return "high"
        elif pattern.impact_score > 0.6:
            return "medium"
        else:
            return "low"

    def _create_implementation_plan(
        self, anomalies: List[AnomalyResult], patterns: List[PatternResult]
    ) -> Dict[str, Any]:
        """Create implementation timeline"""
        return {
            "phase_1": {
                "duration": "1-2 weeks",
                "focus": "Critical issues and quick wins",
                "items": [
                    "Fix critical anomalies",
                    "Address high-impact patterns",
                    "Implement basic optimizations",
                ],
            },
            "phase_2": {
                "duration": "3-4 weeks",
                "focus": "Systematic improvements",
                "items": [
                    "Performance optimizations",
                    "User experience enhancements",
                    "Error handling improvements",
                ],
            },
            "phase_3": {
                "duration": "5-8 weeks",
                "focus": "Advanced optimizations",
                "items": [
                    "A/B testing implementations",
                    "Advanced analytics setup",
                    "Continuous optimization processes",
                ],
            },
        }

    def _estimate_expected_impact(
        self,
        anomalies: List[AnomalyResult],
        patterns: List[PatternResult],
        analytics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Estimate expected impact of optimizations"""
        current_rate = analytics.get("conversion_metrics", {}).get(
            "overall_conversion_rate", 0
        )

        # Conservative impact estimates
        conversion_improvement = min(30, len(anomalies) * 2 + len(patterns) * 1.5)
        performance_improvement = min(
            25, len([a for a in anomalies if "performance" in a.anomaly_type]) * 5
        )
        error_reduction = min(
            40, len([a for a in anomalies if "error" in a.anomaly_type]) * 8
        )

        return {
            "conversion_rate": {
                "current": current_rate,
                "target": min(95, current_rate + conversion_improvement),
                "improvement": conversion_improvement,
            },
            "performance": {
                "improvement_percentage": performance_improvement,
                "areas": ["response_time", "throughput", "resource_usage"],
            },
            "reliability": {
                "error_reduction_percentage": error_reduction,
                "areas": ["error_handling", "validation", "recovery"],
            },
            "business_impact": {
                "estimated_roi": "200-300%",
                "payback_period": "2-3 months",
                "user_satisfaction": "+25%",
            },
        }

    def _define_success_metrics(self) -> Dict[str, Any]:
        """Define success metrics for optimization"""
        return {
            "primary_metrics": [
                {
                    "name": "conversion_rate",
                    "target": "+20%",
                    "measurement": "percentage",
                },
                {
                    "name": "average_step_time",
                    "target": "-25%",
                    "measurement": "milliseconds",
                },
                {"name": "error_rate", "target": "-50%", "measurement": "percentage"},
            ],
            "secondary_metrics": [
                {"name": "user_satisfaction", "target": "+30%", "measurement": "score"},
                {
                    "name": "session_completion_rate",
                    "target": "+15%",
                    "measurement": "percentage",
                },
                {"name": "support_tickets", "target": "-40%", "measurement": "count"},
            ],
            "monitoring": {
                "frequency": "daily",
                "alert_thresholds": {
                    "conversion_drop": ">10%",
                    "performance_degradation": ">20%",
                    "error_spike": ">5%",
                },
            },
        }

    def _optimize_conversion(
        self,
        anomalies: List[AnomalyResult],
        patterns: List[PatternResult],
        analytics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate conversion optimization strategies"""
        conversion_anomalies = [a for a in anomalies if "conversion" in a.anomaly_type]
        conversion_patterns = [p for p in patterns if "conversion" in p.pattern_type]

        return {
            "strategies": [
                {
                    "name": "Simplify Complex Steps",
                    "description": "Break down complex steps into smaller, manageable parts",
                    "expected_impact": "+15% conversion",
                    "implementation_effort": "medium",
                    "actions": [
                        "Analyze step complexity metrics",
                        "Create step breakdown plans",
                        "Implement progressive disclosure",
                    ],
                },
                {
                    "name": "Improve User Guidance",
                    "description": "Add better instructions, progress indicators, and help content",
                    "expected_impact": "+10% conversion",
                    "implementation_effort": "low",
                    "actions": [
                        "Add progress bars and step indicators",
                        "Create contextual help content",
                        "Implement tooltips and guidance",
                    ],
                },
                {
                    "name": "A/B Testing Framework",
                    "description": "Implement systematic A/B testing for optimization",
                    "expected_impact": "+20% conversion",
                    "implementation_effort": "high",
                    "actions": [
                        "Set up A/B testing infrastructure",
                        "Create hypothesis-driven tests",
                        "Implement statistical analysis",
                    ],
                },
            ],
            "priority_actions": [
                a.recommendations[0]
                for a in conversion_anomalies[:3]
                if a.recommendations
            ],
        }

    def _optimize_performance(
        self,
        anomalies: List[AnomalyResult],
        patterns: List[PatternResult],
        analytics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate performance optimization strategies"""
        performance_anomalies = [
            a for a in anomalies if "performance" in a.anomaly_type
        ]
        performance_patterns = [p for p in patterns if "performance" in p.pattern_type]

        return {
            "strategies": [
                {
                    "name": "Database Optimization",
                    "description": "Optimize database queries and implement caching",
                    "expected_impact": "-30% response time",
                    "implementation_effort": "medium",
                    "actions": [
                        "Profile and optimize slow queries",
                        "Implement Redis/Memcached caching",
                        "Add database indexing",
                    ],
                },
                {
                    "name": "Code Optimization",
                    "description": "Optimize algorithms and reduce computational complexity",
                    "expected_impact": "-25% processing time",
                    "implementation_effort": "high",
                    "actions": [
                        "Profile code for bottlenecks",
                        "Optimize algorithmic complexity",
                        "Implement lazy loading",
                    ],
                },
                {
                    "name": "Infrastructure Scaling",
                    "description": "Scale infrastructure and improve resource allocation",
                    "expected_impact": "-20% latency",
                    "implementation_effort": "medium",
                    "actions": [
                        "Implement auto-scaling",
                        "Optimize load balancing",
                        "Upgrade hardware resources",
                    ],
                },
            ],
            "priority_actions": [
                a.recommendations[0]
                for a in performance_anomalies[:3]
                if a.recommendations
            ],
        }

    def _optimize_errors(
        self,
        anomalies: List[AnomalyResult],
        patterns: List[PatternResult],
        analytics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate error optimization strategies"""
        error_anomalies = [a for a in anomalies if "error" in a.anomaly_type]
        error_patterns = [p for p in patterns if "error" in p.pattern_type]

        return {
            "strategies": [
                {
                    "name": "Enhanced Error Handling",
                    "description": "Implement comprehensive error handling and recovery",
                    "expected_impact": "-60% errors",
                    "implementation_effort": "medium",
                    "actions": [
                        "Add try-catch blocks for critical operations",
                        "Implement graceful degradation",
                        "Create error recovery mechanisms",
                    ],
                },
                {
                    "name": "Input Validation",
                    "description": "Strengthen input validation and sanitization",
                    "expected_impact": "-40% validation errors",
                    "implementation_effort": "low",
                    "actions": [
                        "Implement client-side validation",
                        "Add server-side validation",
                        "Create validation error messages",
                    ],
                },
                {
                    "name": "Monitoring and Alerting",
                    "description": "Implement comprehensive error monitoring",
                    "expected_impact": "-50% undetected errors",
                    "implementation_effort": "medium",
                    "actions": [
                        "Set up error tracking systems",
                        "Implement real-time alerts",
                        "Create error dashboards",
                    ],
                },
            ],
            "priority_actions": [
                a.recommendations[0] for a in error_anomalies[:3] if a.recommendations
            ],
        }

    def _optimize_user_experience(
        self,
        anomalies: List[AnomalyResult],
        patterns: List[PatternResult],
        analytics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate user experience optimization strategies"""
        return {
            "strategies": [
                {
                    "name": "Responsive Design",
                    "description": "Optimize for mobile and different screen sizes",
                    "expected_impact": "+15% mobile conversion",
                    "implementation_effort": "medium",
                    "actions": [
                        "Implement responsive layouts",
                        "Optimize touch interactions",
                        "Test on various devices",
                    ],
                },
                {
                    "name": "Loading Optimization",
                    "description": "Improve loading times and perceived performance",
                    "expected_impact": "+20% user satisfaction",
                    "implementation_effort": "low",
                    "actions": [
                        "Implement lazy loading",
                        "Optimize image sizes",
                        "Add loading indicators",
                    ],
                },
                {
                    "name": "Accessibility Improvements",
                    "description": "Improve accessibility for all users",
                    "expected_impact": "+10% inclusive conversion",
                    "implementation_effort": "medium",
                    "actions": [
                        "Add ARIA labels",
                        "Implement keyboard navigation",
                        "Test with screen readers",
                    ],
                },
            ]
        }


# Convenience functions
def analyze_funnel_anomalies(analyzer: FunnelAnalyzer) -> List[AnomalyResult]:
    """Analyze funnel for anomalies"""
    detector = FunnelAnomalyDetector(analyzer)
    return detector.detect_anomalies()


def predict_funnel_performance(
    analyzer: FunnelAnalyzer, horizon: str = "next_day"
) -> List[PredictionResult]:
    """Predict funnel performance"""
    predictor = FunnelPredictor(analyzer)
    return [
        predictor.predict_conversion_rate(horizon),
        predictor.predict_performance(horizon),
        predictor.predict_volume(horizon),
    ]


def recognize_funnel_patterns(analyzer: FunnelAnalyzer) -> List[PatternResult]:
    """Recognize funnel patterns"""
    recognizer = FunnelPatternRecognizer(analyzer)
    return recognizer.recognize_patterns()


def generate_optimization_plan(analyzer: FunnelAnalyzer) -> Dict[str, Any]:
    """Generate comprehensive optimization plan"""
    optimizer = FunnelOptimizer(analyzer)
    return optimizer.generate_optimization_plan()
