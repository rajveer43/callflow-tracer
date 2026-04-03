"""
Funnel Analysis Module for CallFlow Tracer

This module provides comprehensive funnel analysis capabilities for tracking
user journeys, performance bottlenecks, and conversion rates through
sequential steps in application flows.
"""

import json
import time
import uuid
import statistics
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
from contextlib import contextmanager
import threading
from collections import defaultdict
from ..tracer import CallGraph
from .models import FunnelStep, FunnelType, FunnelSession, StepStatus


class FunnelAnalyzer:
    """Main funnel analysis engine"""

    def __init__(self, name: str, funnel_type: FunnelType = FunnelType.PERFORMANCE):
        self.name = name
        self.funnel_type = funnel_type
        self.funnel_id = str(uuid.uuid4())

        # Core data structures
        self.steps: List[FunnelStep] = []
        self.sessions: Dict[str, FunnelSession] = {}
        self.active_sessions: Dict[str, FunnelSession] = {}

        # Configuration
        self.max_sessions = 10000
        self.session_timeout_minutes = 30
        self.enable_real_time = True
        self.auto_detect_steps = True

        # Thread safety
        self._lock = threading.RLock()

        # Callbacks and hooks
        self.step_callbacks: List[Callable] = []
        self.session_callbacks: List[Callable] = []

        # Analytics cache
        self._analytics_cache: Dict[str, Any] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl_minutes = 5

        # Start time
        self.created_at = datetime.now()
        self.last_updated = datetime.now()

    def add_step(
        self, name: str, description: str = "", order: Optional[int] = None
    ) -> FunnelStep:
        """Add a step to the funnel"""
        with self._lock:
            if order is None:
                order = len(self.steps)

            step = FunnelStep(name=name, description=description, order=order)

            self.steps.append(step)
            self.steps.sort(key=lambda s: s.order)

            # Invalidate cache
            self._invalidate_cache()

            return step

    def start_session(self, user_id: Optional[str] = None, **metadata) -> FunnelSession:
        """Start a new funnel session"""
        with self._lock:
            session = FunnelSession(user_id=user_id, **metadata)

            # Add to active sessions
            self.active_sessions[session.session_id] = session
            self.sessions[session.session_id] = session

            # Cleanup old sessions if needed
            self._cleanup_sessions()

            # Trigger callbacks
            for callback in self.session_callbacks:
                try:
                    callback("session_started", session)
                except Exception:
                    pass

            return session

    def track_step(
        self,
        session_id: str,
        step_name: str,
        status: StepStatus = StepStatus.SUCCESS,
        duration_ms: Optional[float] = None,
        error_message: Optional[str] = None,
        **metrics,
    ) -> bool:
        """Track a step completion for a session"""
        with self._lock:
            session = self.active_sessions.get(session_id)
            if not session:
                return False

            # Calculate duration if not provided
            if duration_ms is None:
                duration_ms = (
                    datetime.now() - session.start_time
                ).total_seconds() * 1000

            # Update session
            session.complete_step(step_name, status)
            session.add_step_timing(step_name, duration_ms)

            if status == StepStatus.FAILURE or status == StepStatus.ERROR:
                session.status = status
                session.exit_reason = error_message or "Step failed"
                self._complete_session(session_id)

            # Update step metrics
            step = self._get_step_by_name(step_name)
            if step:
                self._update_step_metrics(
                    step, session, duration_ms, status, error_message
                )

            # Trigger callbacks
            for callback in self.step_callbacks:
                try:
                    callback("step_completed", session, step, status, duration_ms)
                except Exception:
                    pass

            # Invalidate cache
            self._invalidate_cache()

            return True

    def complete_session(
        self,
        session_id: str,
        status: StepStatus = StepStatus.SUCCESS,
        conversion_value: float = 0.0,
        **metadata,
    ) -> bool:
        """Complete a funnel session"""
        with self._lock:
            session = self.active_sessions.get(session_id)
            if not session:
                return False

            session.status = status
            session.conversion_value = conversion_value
            session.end_time = datetime.now()

            # Update metadata
            for key, value in metadata.items():
                if hasattr(session, key):
                    setattr(session, key, value)

            return self._complete_session(session_id)

    def _complete_session(self, session_id: str) -> bool:
        """Internal method to complete a session"""
        session = self.active_sessions.pop(session_id, None)
        if session:
            session.end_time = datetime.now()

            # Trigger callbacks
            for callback in self.session_callbacks:
                try:
                    callback("session_completed", session)
                except Exception:
                    pass

            # Invalidate cache
            self._invalidate_cache()

            return True
        return False

    def _get_step_by_name(self, name: str) -> Optional[FunnelStep]:
        """Get step by name"""
        for step in self.steps:
            if step.name == name:
                return step
        return None

    def _update_step_metrics(
        self,
        step: FunnelStep,
        session: FunnelSession,
        duration_ms: float,
        status: StepStatus,
        error_message: Optional[str],
    ):
        """Update step metrics with new data"""
        step.total_users += 1

        if status == StepStatus.SUCCESS:
            step.successful_users += 1
        else:
            step.failed_users += 1
            step.error_count += 1
            if error_message:
                if error_message not in step.common_errors:
                    step.common_errors.append(error_message)

        # Update timing metrics
        # Note: In a real implementation, we'd store all durations and calculate percentiles
        step.avg_time_ms = (
            step.avg_time_ms * (step.total_users - 1) + duration_ms
        ) / step.total_users

        # Update conversion and dropoff rates
        self._recalculate_conversion_rates()

    def _recalculate_conversion_rates(self):
        """Recalculate conversion and dropoff rates for all steps"""
        if not self.steps:
            return

        total_users = self.steps[0].total_users if self.steps else 0

        for i, step in enumerate(self.steps):
            if total_users > 0:
                step.conversion_rate = (step.successful_users / total_users) * 100
                step.dropoff_rate = (
                    (total_users - step.successful_users) / total_users
                ) * 100

            # Calculate relative dropoff from previous step
            if i > 0 and self.steps[i - 1].successful_users > 0:
                prev_successful = self.steps[i - 1].successful_users
                if prev_successful > 0:
                    step.relative_dropoff = (
                        (prev_successful - step.successful_users) / prev_successful
                    ) * 100

    def get_analytics(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Get comprehensive funnel analytics"""
        with self._lock:
            # Check cache
            if not force_refresh and self._is_cache_valid():
                return self._analytics_cache.copy()

            analytics = {
                "funnel_info": {
                    "name": self.name,
                    "type": self.funnel_type.value,
                    "id": self.funnel_id,
                    "created_at": self.created_at.isoformat(),
                    "last_updated": self.last_updated.isoformat(),
                    "total_steps": len(self.steps),
                    "total_sessions": len(self.sessions),
                    "active_sessions": len(self.active_sessions),
                },
                "steps": [step.to_dict() for step in self.steps],
                "conversion_metrics": self._calculate_conversion_metrics(),
                "performance_metrics": self._calculate_performance_metrics(),
                "error_analysis": self._analyze_errors(),
                "user_segments": self._analyze_user_segments(),
                "time_analysis": self._analyze_time_patterns(),
                "recommendations": self._generate_recommendations(),
            }

            # Update cache
            self._analytics_cache = analytics
            self._cache_timestamp = datetime.now()

            return analytics

    def _calculate_conversion_metrics(self) -> Dict[str, Any]:
        """Calculate conversion metrics"""
        if not self.steps:
            return {}

        total_sessions = len(self.sessions)
        if total_sessions == 0:
            return {}

        completed_sessions = sum(1 for s in self.sessions.values() if s.is_completed)
        overall_conversion = (completed_sessions / total_sessions) * 100

        # Calculate step-by-step conversion
        step_conversions = []
        for i, step in enumerate(self.steps):
            step_conversions.append(
                {
                    "step_name": step.name,
                    "conversion_rate": step.conversion_rate,
                    "dropoff_rate": step.dropoff_rate,
                    "relative_dropoff": step.relative_dropoff,
                }
            )

        return {
            "overall_conversion_rate": overall_conversion,
            "completed_sessions": completed_sessions,
            "total_sessions": total_sessions,
            "step_conversions": step_conversions,
            "biggest_dropoff": self._find_biggest_dropoff(),
            "conversion_trend": self._calculate_conversion_trend(),
        }

    def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics"""
        if not self.steps:
            return {}

        # Calculate average times
        avg_times = [step.avg_time_ms for step in self.steps if step.avg_time_ms > 0]

        if not avg_times:
            return {}

        return {
            "average_step_time_ms": statistics.mean(avg_times),
            "median_step_time_ms": statistics.median(avg_times),
            "slowest_step": (
                max(self.steps, key=lambda s: s.avg_time_ms).name
                if self.steps
                else None
            ),
            "fastest_step": (
                min(self.steps, key=lambda s: s.avg_time_ms).name
                if self.steps
                else None
            ),
            "total_avg_time_ms": sum(avg_times),
            "performance_distribution": self._calculate_performance_distribution(),
        }

    def _analyze_errors(self) -> Dict[str, Any]:
        """Analyze error patterns"""
        if not self.steps:
            return {}

        total_errors = sum(step.error_count for step in self.steps)
        if total_errors == 0:
            return {"total_errors": 0}

        # Collect all errors
        all_errors = []
        for step in self.steps:
            for error in step.common_errors:
                all_errors.append(
                    {
                        "step": step.name,
                        "error": error,
                        "count": step.common_errors.count(error),
                    }
                )

        # Find most common errors
        error_counts = defaultdict(int)
        for error_info in all_errors:
            error_counts[error_info["error"]] += error_info["count"]

        most_common = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_errors": total_errors,
            "error_rate": (total_errors / sum(step.total_users for step in self.steps))
            * 100,
            "most_common_errors": most_common,
            "error_prone_steps": [
                {
                    "step": step.name,
                    "error_count": step.error_count,
                    "error_rate": step.error_rate,
                }
                for step in self.steps
                if step.error_count > 0
            ],
        }

    def _analyze_user_segments(self) -> Dict[str, Any]:
        """Analyze user segments"""
        # Group sessions by device type, location, etc.
        segments = defaultdict(
            lambda: {"total": 0, "completed": 0, "conversion_rate": 0}
        )

        for session in self.sessions.values():
            segment_key = session.device_type or "unknown"
            segments[segment_key]["total"] += 1
            if session.is_completed:
                segments[segment_key]["completed"] += 1

        # Calculate conversion rates
        for segment_data in segments.values():
            if segment_data["total"] > 0:
                segment_data["conversion_rate"] = (
                    segment_data["completed"] / segment_data["total"]
                ) * 100

        return dict(segments)

    def _analyze_time_patterns(self) -> Dict[str, Any]:
        """Analyze time-based patterns"""
        if not self.sessions:
            return {}

        # Analyze by hour of day
        hourly_stats = defaultdict(lambda: {"total": 0, "completed": 0})

        for session in self.sessions.values():
            hour = session.start_time.hour
            hourly_stats[hour]["total"] += 1
            if session.is_completed:
                hourly_stats[hour]["completed"] += 1

        # Calculate conversion rates by hour
        for hour, stats in hourly_stats.items():
            if stats["total"] > 0:
                stats["conversion_rate"] = (stats["completed"] / stats["total"]) * 100

        return {
            "hourly_patterns": dict(hourly_stats),
            "peak_hour": (
                max(hourly_stats.items(), key=lambda x: x[1]["total"])[0]
                if hourly_stats
                else None
            ),
            "best_conversion_hour": (
                max(hourly_stats.items(), key=lambda x: x[1]["conversion_rate"])[0]
                if hourly_stats
                else None
            ),
        }

    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""
        recommendations = []

        if not self.steps:
            return recommendations

        # Find biggest dropoff
        biggest_dropoff = self._find_biggest_dropoff()
        if biggest_dropoff and biggest_dropoff["relative_dropoff"] > 20:
            recommendations.append(
                {
                    "type": "high_dropoff",
                    "priority": "high",
                    "step": biggest_dropoff["step_name"],
                    "issue": f"High dropoff rate ({biggest_dropoff['relative_dropoff']:.1f}%)",
                    "recommendation": "Investigate user experience issues, simplify the process, or provide better guidance",
                }
            )

        # Find slowest step
        slowest_step = (
            max(self.steps, key=lambda s: s.avg_time_ms) if self.steps else None
        )
        if slowest_step and slowest_step.avg_time_ms > 5000:  # 5 seconds
            recommendations.append(
                {
                    "type": "performance",
                    "priority": "medium",
                    "step": slowest_step.name,
                    "issue": f"Slow step ({slowest_step.avg_time_ms:.1f}ms average)",
                    "recommendation": "Optimize code, add caching, or improve database queries",
                }
            )

        # Find error-prone steps
        error_prone = [step for step in self.steps if step.error_rate > 10]
        for step in error_prone:
            recommendations.append(
                {
                    "type": "error",
                    "priority": "high",
                    "step": step.name,
                    "issue": f"High error rate ({step.error_rate:.1f}%)",
                    "recommendation": "Add better error handling, input validation, or user feedback",
                }
            )

        return recommendations

    def _find_biggest_dropoff(self) -> Optional[Dict[str, Any]]:
        """Find the step with biggest relative dropoff"""
        if len(self.steps) < 2:
            return None

        biggest_dropoff = None
        max_dropoff = -1

        for i in range(1, len(self.steps)):
            step = self.steps[i]
            if step.relative_dropoff > max_dropoff:
                max_dropoff = step.relative_dropoff
                biggest_dropoff = {
                    "step_name": step.name,
                    "relative_dropoff": step.relative_dropoff,
                    "absolute_dropoff": step.dropoff_rate,
                }

        return biggest_dropoff

    def _calculate_conversion_trend(self) -> Dict[str, Any]:
        """Calculate conversion trend over time"""
        # Simple implementation - in reality, this would be more sophisticated
        recent_sessions = list(self.sessions.values())[-100:]  # Last 100 sessions
        older_sessions = (
            list(self.sessions.values())[-200:-100] if len(self.sessions) > 100 else []
        )

        recent_conversion = (
            sum(1 for s in recent_sessions if s.is_completed)
            / len(recent_sessions)
            * 100
            if recent_sessions
            else 0
        )
        older_conversion = (
            sum(1 for s in older_sessions if s.is_completed) / len(older_sessions) * 100
            if older_sessions
            else 0
        )

        trend = (
            "improving"
            if recent_conversion > older_conversion
            else "declining" if recent_conversion < older_conversion else "stable"
        )

        return {
            "recent_conversion_rate": recent_conversion,
            "previous_conversion_rate": older_conversion,
            "trend": trend,
            "change_percentage": recent_conversion - older_conversion,
        }

    def _calculate_performance_distribution(self) -> Dict[str, Any]:
        """Calculate performance distribution across steps"""
        if not self.steps:
            return {}

        times = [step.avg_time_ms for step in self.steps if step.avg_time_ms > 0]
        if not times:
            return {}

        return {
            "min": min(times),
            "max": max(times),
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
            "quartiles": [
                statistics.quantiles(times, n=4)[0],
                statistics.quantiles(times, n=4)[1],
                statistics.quantiles(times, n=4)[2],
            ],
        }

    def _cleanup_sessions(self):
        """Clean up old or expired sessions"""
        current_time = datetime.now()
        timeout_threshold = timedelta(minutes=self.session_timeout_minutes)

        # Remove expired active sessions
        expired_sessions = [
            sid
            for sid, session in self.active_sessions.items()
            if current_time - session.start_time > timeout_threshold
        ]

        for sid in expired_sessions:
            self._complete_session(sid)

        # Limit total sessions
        if len(self.sessions) > self.max_sessions:
            # Remove oldest sessions
            sorted_sessions = sorted(
                self.sessions.items(), key=lambda x: x[1].start_time
            )
            to_remove = sorted_sessions[: len(self.sessions) - self.max_sessions]

            for sid, _ in to_remove:
                self.sessions.pop(sid, None)
                self.active_sessions.pop(sid, None)

    def _invalidate_cache(self):
        """Invalidate analytics cache"""
        self._cache_timestamp = None
        self._analytics_cache.clear()
        self.last_updated = datetime.now()

    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        if not self._cache_timestamp:
            return False

        age = datetime.now() - self._cache_timestamp
        return age.total_seconds() < (self._cache_ttl_minutes * 60)

    def export_data(self, format_type: str = "json") -> str:
        """Export funnel data"""
        data = {
            "funnel_info": {
                "name": self.name,
                "type": self.funnel_type.value,
                "id": self.funnel_id,
                "exported_at": datetime.now().isoformat(),
            },
            "steps": [step.to_dict() for step in self.steps],
            "sessions": [session.to_dict() for session in self.sessions.values()],
            "analytics": self.get_analytics(),
        }

        if format_type.lower() == "json":
            return json.dumps(data, indent=2, default=str)
        elif format_type.lower() == "csv":
            # Simplified CSV export
            import csv
            import io

            output = io.StringIO()
            writer = csv.writer(output)

            # Write steps
            writer.writerow(
                [
                    "Step Name",
                    "Total Users",
                    "Successful",
                    "Failed",
                    "Conversion Rate",
                    "Avg Time (ms)",
                ]
            )
            for step in self.steps:
                writer.writerow(
                    [
                        step.name,
                        step.total_users,
                        step.successful_users,
                        step.failed_users,
                        step.conversion_rate,
                        step.avg_time_ms,
                    ]
                )

            return output.getvalue()
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def add_step_callback(self, callback: Callable):
        """Add callback for step events"""
        self.step_callbacks.append(callback)

    def add_session_callback(self, callback: Callable):
        """Add callback for session events"""
        self.session_callbacks.append(callback)


# Context manager for easy funnel tracking
@contextmanager
def funnel_scope(name: str, funnel_type: FunnelType = FunnelType.PERFORMANCE):
    """Context manager for funnel analysis"""
    analyzer = FunnelAnalyzer(name, funnel_type)
    try:
        yield analyzer
    finally:
        # Cleanup if needed
        pass


# Decorator for automatic funnel tracking
def track_funnel_step(step_name: str, analyzer: FunnelAnalyzer):
    """Decorator to automatically track function calls as funnel steps"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()

            # Start session if needed
            if not analyzer.active_sessions:
                session = analyzer.start_session()
                session_id = session.session_id
            else:
                session_id = next(iter(analyzer.active_sessions.keys()))

            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                analyzer.track_step(
                    session_id, step_name, StepStatus.SUCCESS, duration_ms
                )
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                analyzer.track_step(
                    session_id, step_name, StepStatus.ERROR, duration_ms, str(e)
                )
                raise

        return wrapper

    return decorator


# Integration with existing CallGraph
class CallGraphFunnelAdapter:
    """Adapter to convert CallGraph data into funnel analysis"""

    def __init__(self, call_graph: CallGraph, funnel_name: str = "call_graph_funnel"):
        self.call_graph = call_graph
        self.funnel = FunnelAnalyzer(funnel_name, FunnelType.PERFORMANCE)
        self._convert_graph_to_funnel()

    def _convert_graph_to_funnel(self):
        """Convert CallGraph nodes to funnel steps"""
        # Group nodes by function name and calculate metrics
        function_stats = defaultdict(
            lambda: {"calls": 0, "total_time": 0, "errors": 0, "times": []}
        )

        for node in self.call_graph.nodes:
            func_name = node.name
            function_stats[func_name]["calls"] += 1
            function_stats[func_name]["total_time"] += node.duration_ms
            function_stats[func_name]["times"].append(node.duration_ms)

            # Check for errors (this would need to be implemented in CallGraph)
            if hasattr(node, "error") and node.error:
                function_stats[func_name]["errors"] += 1

        # Create funnel steps
        for i, (func_name, stats) in enumerate(function_stats.items()):
            step = self.funnel.add_step(
                name=func_name, description=f"Function call: {func_name}", order=i
            )

            step.total_users = stats["calls"]
            step.successful_users = stats["calls"] - stats["errors"]
            step.failed_users = stats["errors"]
            step.avg_time_ms = (
                stats["total_time"] / stats["calls"] if stats["calls"] > 0 else 0
            )

            if stats["times"]:
                step.median_time_ms = statistics.median(stats["times"])
                step.p95_time_ms = statistics.quantile(stats["times"], 0.95)
                step.p99_time_ms = statistics.quantile(stats["times"], 0.99)

    def get_funnel_analytics(self) -> Dict[str, Any]:
        """Get funnel analytics from call graph"""
        return self.funnel.get_analytics()


# Convenience functions
def create_funnel(name: str, funnel_type: str = "performance") -> FunnelAnalyzer:
    """Create a new funnel analyzer"""
    type_enum = FunnelType(funnel_type)
    return FunnelAnalyzer(name, type_enum)


def analyze_call_graph_funnel(
    call_graph: CallGraph, name: str = "call_graph_analysis"
) -> Dict[str, Any]:
    """Analyze a CallGraph as a funnel"""
    adapter = CallGraphFunnelAdapter(call_graph, name)
    return adapter.get_funnel_analytics()
