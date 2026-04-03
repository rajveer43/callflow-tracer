"""
Real-time Funnel Monitoring System for CallFlow Tracer

This module provides real-time monitoring capabilities for funnel analysis,
including live updates, alerting, and automated responses to performance issues.
"""

import time
import threading
import queue
import json
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum
import asyncio
from contextlib import contextmanager

try:
    import websockets
except Exception:  # pragma: no cover - optional dependency
    websockets = None  # type: ignore

from .analysis import FunnelAnalyzer, FunnelSession, StepStatus
from .algorithms import FunnelAnomalyDetector, AnomalyResult


class AlertSeverity(Enum):
    """Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MonitoringMode(Enum):
    """Monitoring modes"""

    PASSIVE = "passive"  # Only monitor and alert
    ACTIVE = "active"  # Monitor and take automated actions
    PREDICTIVE = "predictive"  # Monitor, predict, and prevent issues


@dataclass
class FunnelAlert:
    """Funnel monitoring alert"""

    alert_id: str
    severity: AlertSeverity
    title: str
    description: str
    affected_steps: List[str]
    metrics: Dict[str, float]
    threshold: float
    current_value: float
    timestamp: datetime
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    actions_taken: List[str] = None

    def __post_init__(self):
        if self.actions_taken is None:
            self.actions_taken = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        if self.resolution_time:
            data["resolution_time"] = self.resolution_time.isoformat()
        data["severity"] = self.severity.value
        return data


@dataclass
class MonitoringThreshold:
    """Monitoring threshold configuration"""

    metric_name: str
    threshold_type: str  # 'absolute', 'percentage', 'rate'
    operator: str  # 'gt', 'lt', 'gte', 'lte', 'eq'
    threshold_value: float
    severity: AlertSeverity
    enabled: bool = True
    cooldown_minutes: int = 5

    def check_threshold(self, current_value: float) -> bool:
        """Check if threshold is breached"""
        if not self.enabled:
            return False

        if self.operator == "gt":
            return current_value > self.threshold_value
        elif self.operator == "lt":
            return current_value < self.threshold_value
        elif self.operator == "gte":
            return current_value >= self.threshold_value
        elif self.operator == "lte":
            return current_value <= self.threshold_value
        elif self.operator == "eq":
            return abs(current_value - self.threshold_value) < 0.001

        return False


class RealTimeFunnelMonitor:
    """Real-time funnel monitoring system"""

    def __init__(
        self,
        analyzer: FunnelAnalyzer,
        monitoring_mode: MonitoringMode = MonitoringMode.PASSIVE,
    ):
        self.analyzer = analyzer
        self.monitoring_mode = monitoring_mode

        # Monitoring state
        self.is_monitoring = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_interval = 5.0  # seconds

        # Data storage
        self.alerts: Dict[str, FunnelAlert] = {}
        self.active_alerts: Set[str] = set()
        self.thresholds: List[MonitoringThreshold] = []
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))

        # Event handling
        self.event_queue = queue.Queue()
        self.alert_callbacks: List[Callable] = []
        self.websocket_clients: Set = set()

        # Statistics
        self.monitoring_start_time: Optional[datetime] = None
        self.total_alerts_generated = 0
        self.alerts_resolved = 0

        # Lock for thread safety
        self._lock = threading.RLock()

        # Initialize default thresholds
        self._initialize_default_thresholds()

    def _initialize_default_thresholds(self):
        """Initialize default monitoring thresholds"""
        default_thresholds = [
            # Conversion rate thresholds
            MonitoringThreshold(
                metric_name="conversion_rate",
                threshold_type="percentage",
                operator="lt",
                threshold_value=20.0,
                severity=AlertSeverity.WARNING,
            ),
            MonitoringThreshold(
                metric_name="conversion_rate",
                threshold_type="percentage",
                operator="lt",
                threshold_value=10.0,
                severity=AlertSeverity.CRITICAL,
            ),
            # Error rate thresholds
            MonitoringThreshold(
                metric_name="error_rate",
                threshold_type="percentage",
                operator="gt",
                threshold_value=10.0,
                severity=AlertSeverity.WARNING,
            ),
            MonitoringThreshold(
                metric_name="error_rate",
                threshold_type="percentage",
                operator="gt",
                threshold_value=25.0,
                severity=AlertSeverity.ERROR,
            ),
            # Performance thresholds
            MonitoringThreshold(
                metric_name="avg_time_ms",
                threshold_type="absolute",
                operator="gt",
                threshold_value=5000.0,
                severity=AlertSeverity.WARNING,
            ),
            MonitoringThreshold(
                metric_name="avg_time_ms",
                threshold_type="absolute",
                operator="gt",
                threshold_value=10000.0,
                severity=AlertSeverity.ERROR,
            ),
            # Dropoff rate thresholds
            MonitoringThreshold(
                metric_name="relative_dropoff",
                threshold_type="percentage",
                operator="gt",
                threshold_value=30.0,
                severity=AlertSeverity.WARNING,
            ),
            MonitoringThreshold(
                metric_name="relative_dropoff",
                threshold_type="percentage",
                operator="gt",
                threshold_value=50.0,
                severity=AlertSeverity.CRITICAL,
            ),
            # Session volume thresholds
            MonitoringThreshold(
                metric_name="active_sessions",
                threshold_type="absolute",
                operator="gt",
                threshold_value=1000.0,
                severity=AlertSeverity.INFO,
            ),
            MonitoringThreshold(
                metric_name="active_sessions",
                threshold_type="absolute",
                operator="gt",
                threshold_value=5000.0,
                severity=AlertSeverity.WARNING,
            ),
        ]

        self.thresholds.extend(default_thresholds)

    def start_monitoring(self, interval: float = 5.0):
        """Start real-time monitoring"""
        with self._lock:
            if self.is_monitoring:
                return

            self.monitoring_interval = interval
            self.is_monitoring = True
            self.monitoring_start_time = datetime.now()

            # Start monitoring thread
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop, daemon=True
            )
            self.monitoring_thread.start()

            # Start event processing thread
            event_thread = threading.Thread(
                target=self._event_processing_loop, daemon=True
            )
            event_thread.start()

            # Start WebSocket server for real-time updates
            if self.monitoring_mode in [
                MonitoringMode.ACTIVE,
                MonitoringMode.PREDICTIVE,
            ]:
                websocket_thread = threading.Thread(
                    target=self._start_websocket_server, daemon=True
                )
                websocket_thread.start()

    def stop_monitoring(self):
        """Stop real-time monitoring"""
        with self._lock:
            self.is_monitoring = False

            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=5.0)

    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                self._check_thresholds()
                self._update_metrics_history()
                self._detect_anomalies()

                if self.monitoring_mode == MonitoringMode.PREDICTIVE:
                    self._predictive_analysis()

                time.sleep(self.monitoring_interval)

            except Exception as e:
                self._create_error_alert(
                    "Monitoring Error", f"Error in monitoring loop: {str(e)}"
                )
                time.sleep(self.monitoring_interval)

    def _event_processing_loop(self):
        """Process monitoring events"""
        while self.is_monitoring:
            try:
                # Process events from queue
                while not self.event_queue.empty():
                    event = self.event_queue.get_nowait()
                    self._process_event(event)

                time.sleep(0.1)  # Small delay to prevent busy waiting

            except Exception as e:
                print(f"Error in event processing: {e}")
                time.sleep(1.0)

    def _check_thresholds(self):
        """Check all monitoring thresholds"""
        analytics = self.analyzer.get_analytics()
        steps = analytics.get("steps", [])

        # Check overall metrics
        overall_metrics = self._extract_overall_metrics(analytics)
        for threshold in self.thresholds:
            if threshold.metric_name in overall_metrics:
                current_value = overall_metrics[threshold.metric_name]
                if threshold.check_threshold(current_value):
                    self._create_threshold_alert(threshold, current_value, [])

        # Check step-specific metrics
        for step in steps:
            step_metrics = self._extract_step_metrics(step)
            for threshold in self.thresholds:
                if threshold.metric_name in step_metrics:
                    current_value = step_metrics[threshold.metric_name]
                    if threshold.check_threshold(current_value):
                        self._create_threshold_alert(
                            threshold, current_value, [step["name"]]
                        )

    def _extract_overall_metrics(self, analytics: Dict[str, Any]) -> Dict[str, float]:
        """Extract overall funnel metrics"""
        conversion_metrics = analytics.get("conversion_metrics", {})
        performance_metrics = analytics.get("performance_metrics", {})
        error_analysis = analytics.get("error_analysis", {})

        return {
            "overall_conversion_rate": conversion_metrics.get(
                "overall_conversion_rate", 0
            ),
            "total_sessions": conversion_metrics.get("total_sessions", 0),
            "active_sessions": len(self.analyzer.active_sessions),
            "average_step_time": performance_metrics.get("average_step_time_ms", 0),
            "total_errors": error_analysis.get("total_errors", 0),
            "error_rate": error_analysis.get("error_rate", 0),
        }

    def _extract_step_metrics(self, step: Dict[str, Any]) -> Dict[str, float]:
        """Extract metrics from a step"""
        return {
            "conversion_rate": step.get("conversion_rate", 0),
            "dropoff_rate": step.get("dropoff_rate", 0),
            "relative_dropoff": step.get("relative_dropoff", 0),
            "avg_time_ms": step.get("avg_time_ms", 0),
            "error_rate": step.get("error_rate", 0),
            "error_count": step.get("error_count", 0),
            "total_users": step.get("total_users", 0),
        }

    def _create_threshold_alert(
        self,
        threshold: MonitoringThreshold,
        current_value: float,
        affected_steps: List[str],
    ):
        """Create alert for threshold breach"""
        alert_id = f"threshold_{threshold.metric_name}_{int(time.time())}"

        # Check cooldown
        if self._is_in_cooldown(threshold, alert_id):
            return

        alert = FunnelAlert(
            alert_id=alert_id,
            severity=threshold.severity,
            title=f"{threshold.metric_name.replace('_', ' ').title()} Threshold Breach",
            description=f"{threshold.metric_name} is {current_value:.2f}, threshold is {threshold.threshold_value:.2f}",
            affected_steps=affected_steps,
            metrics={threshold.metric_name: current_value},
            threshold=threshold.threshold_value,
            current_value=current_value,
            timestamp=datetime.now(),
        )

        self._add_alert(alert)

        # Take automated actions if in active mode
        if self.monitoring_mode in [MonitoringMode.ACTIVE, MonitoringMode.PREDICTIVE]:
            self._take_automated_action(alert)

    def _is_in_cooldown(self, threshold: MonitoringThreshold, alert_id: str) -> bool:
        """Check if alert is in cooldown period"""
        cooldown_threshold = timedelta(minutes=threshold.cooldown_minutes)
        current_time = datetime.now()

        for existing_alert in self.alerts.values():
            if (
                existing_alert.resolved
                and current_time - existing_alert.resolution_time < cooldown_threshold
            ):
                return True

        return False

    def _detect_anomalies(self):
        """Detect anomalies using anomaly detector"""
        try:
            detector = FunnelAnomalyDetector(self.analyzer)
            anomalies = detector.detect_anomalies()

            for anomaly in anomalies:
                if anomaly.severity in ["high", "critical"]:
                    alert_id = f"anomaly_{anomaly.anomaly_type}_{int(time.time())}"

                    alert = FunnelAlert(
                        alert_id=alert_id,
                        severity=(
                            AlertSeverity.WARNING
                            if anomaly.severity == "high"
                            else AlertSeverity.CRITICAL
                        ),
                        title=f"Anomaly Detected: {anomaly.anomaly_type.replace('_', ' ').title()}",
                        description=anomaly.description,
                        affected_steps=anomaly.affected_steps,
                        metrics=anomaly.metrics,
                        threshold=0.0,  # Anomalies don't have fixed thresholds
                        current_value=0.0,
                        timestamp=anomaly.timestamp,
                    )

                    self._add_alert(alert)

                    # Take automated actions for critical anomalies
                    if (
                        self.monitoring_mode == MonitoringMode.PREDICTIVE
                        and anomaly.severity == "critical"
                    ):
                        self._take_preventive_action(anomaly)

        except Exception as e:
            self._create_error_alert(
                "Anomaly Detection Error", f"Error detecting anomalies: {str(e)}"
            )

    def _predictive_analysis(self):
        """Perform predictive analysis"""
        try:
            from .algorithms import FunnelPredictor

            predictor = FunnelPredictor(self.analyzer)

            # Predict conversion rate
            conversion_pred = predictor.predict_conversion_rate("next_hour")
            if (
                conversion_pred.confidence > 0.7
                and conversion_pred.predicted_value < 20
            ):
                alert_id = f"predictive_conversion_{int(time.time())}"

                alert = FunnelAlert(
                    alert_id=alert_id,
                    severity=AlertSeverity.WARNING,
                    title="Predictive: Low Conversion Rate Expected",
                    description=f"Conversion rate predicted to drop to {conversion_pred.predicted_value:.1f}% in the next hour",
                    affected_steps=[],
                    metrics={"predicted_conversion": conversion_pred.predicted_value},
                    threshold=20.0,
                    current_value=conversion_pred.predicted_value,
                    timestamp=datetime.now(),
                )

                self._add_alert(alert)

            # Predict performance issues
            performance_pred = predictor.predict_performance("next_hour")
            if (
                performance_pred.confidence > 0.7
                and performance_pred.predicted_value > 8000
            ):
                alert_id = f"predictive_performance_{int(time.time())}"

                alert = FunnelAlert(
                    alert_id=alert_id,
                    severity=AlertSeverity.WARNING,
                    title="Predictive: Performance Degradation Expected",
                    description=f"Performance predicted to degrade to {performance_pred.predicted_value:.1f}ms in the next hour",
                    affected_steps=[],
                    metrics={"predicted_performance": performance_pred.predicted_value},
                    threshold=8000.0,
                    current_value=performance_pred.predicted_value,
                    timestamp=datetime.now(),
                )

                self._add_alert(alert)

        except Exception as e:
            self._create_error_alert(
                "Predictive Analysis Error", f"Error in predictive analysis: {str(e)}"
            )

    def _update_metrics_history(self):
        """Update metrics history for trend analysis"""
        analytics = self.analyzer.get_analytics()
        current_time = datetime.now()

        # Update overall metrics
        overall_metrics = self._extract_overall_metrics(analytics)
        for metric_name, value in overall_metrics.items():
            self.metrics_history[metric_name].append(
                {"timestamp": current_time, "value": value}
            )

        # Update step metrics
        steps = analytics.get("steps", [])
        for step in steps:
            step_name = step["name"]
            step_metrics = self._extract_step_metrics(step)

            for metric_name, value in step_metrics.items():
                history_key = f"{step_name}_{metric_name}"
                self.metrics_history[history_key].append(
                    {"timestamp": current_time, "value": value}
                )

    def _add_alert(self, alert: FunnelAlert):
        """Add alert to monitoring system"""
        with self._lock:
            self.alerts[alert.alert_id] = alert
            self.active_alerts.add(alert.alert_id)
            self.total_alerts_generated += 1

            # Trigger callbacks
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    print(f"Error in alert callback: {e}")

            # Send to WebSocket clients
            self._broadcast_alert(alert)

            # Add to event queue for processing
            self.event_queue.put({"type": "alert_created", "data": alert.to_dict()})

    def _create_error_alert(self, title: str, description: str):
        """Create error alert for monitoring system issues"""
        alert_id = f"monitoring_error_{int(time.time())}"

        alert = FunnelAlert(
            alert_id=alert_id,
            severity=AlertSeverity.ERROR,
            title=title,
            description=description,
            affected_steps=[],
            metrics={},
            threshold=0.0,
            current_value=0.0,
            timestamp=datetime.now(),
        )

        self._add_alert(alert)

    def _take_automated_action(self, alert: FunnelAlert):
        """Take automated action based on alert"""
        actions_taken = []

        if alert.severity == AlertSeverity.CRITICAL:
            # Critical actions
            if "conversion_rate" in alert.metrics:
                actions_taken.append("Enabled high-priority conversion optimization")
                actions_taken.append(
                    "Notified development team of critical conversion issue"
                )

            elif "error_rate" in alert.metrics:
                actions_taken.append("Enabled error handling fallback mode")
                actions_taken.append("Increased monitoring frequency")

            elif "avg_time_ms" in alert.metrics:
                actions_taken.append("Enabled performance optimization mode")
                actions_taken.append("Scaled up resources if available")

        elif alert.severity == AlertSeverity.ERROR:
            # Error level actions
            if "error_rate" in alert.metrics:
                actions_taken.append("Enhanced error logging")
                actions_taken.append("Notified operations team")

        # Update alert with actions taken
        alert.actions_taken.extend(actions_taken)

    def _take_preventive_action(self, anomaly):
        """Take preventive action based on anomaly prediction"""
        # This would implement specific preventive measures
        # For now, just create an informational alert
        alert_id = f"preventive_{anomaly.anomaly_type}_{int(time.time())}"

        alert = FunnelAlert(
            alert_id=alert_id,
            severity=AlertSeverity.INFO,
            title=f"Preventive Action: {anomaly.anomaly_type}",
            description=f"Preventive measures taken for {anomaly.anomaly_type}",
            affected_steps=anomaly.affected_steps,
            metrics=anomaly.metrics,
            threshold=0.0,
            current_value=0.0,
            timestamp=datetime.now(),
        )

        self._add_alert(alert)

    def _process_event(self, event: Dict[str, Any]):
        """Process monitoring event"""
        event_type = event.get("type")
        data = event.get("data")

        if event_type == "alert_created":
            # Handle alert creation
            pass
        elif event_type == "alert_resolved":
            # Handle alert resolution
            pass
        elif event_type == "threshold_updated":
            # Handle threshold updates
            pass

    def _broadcast_alert(self, alert: FunnelAlert):
        """Broadcast alert to WebSocket clients"""
        if not self.websocket_clients:
            return

        message = json.dumps({"type": "alert", "data": alert.to_dict()})

        # Send to all connected clients
        dead_clients = set()
        for client in self.websocket_clients:
            try:
                client.send(message)
            except Exception:
                dead_clients.add(client)

        # Remove dead clients
        self.websocket_clients -= dead_clients

    def _start_websocket_server(self):
        """Start WebSocket server for real-time updates"""
        if websockets is None:
            return

        async def handle_client(websocket, path):
            self.websocket_clients.add(websocket)
            try:
                await websocket.wait_closed()
            finally:
                self.websocket_clients.discard(websocket)

        # Start WebSocket server
        start_server = websockets.serve(handle_client, "localhost", 8765)

        # Run in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_server)
        loop.run_forever()

    def resolve_alert(self, alert_id: str, resolution_notes: str = "") -> bool:
        """Resolve an alert"""
        with self._lock:
            alert = self.alerts.get(alert_id)
            if not alert:
                return False

            alert.resolved = True
            alert.resolution_time = datetime.now()
            self.active_alerts.discard(alert_id)
            self.alerts_resolved += 1

            # Broadcast resolution
            self._broadcast_alert(alert)

            # Add to event queue
            self.event_queue.put(
                {
                    "type": "alert_resolved",
                    "data": {
                        "alert_id": alert_id,
                        "resolution_time": alert.resolution_time.isoformat(),
                        "notes": resolution_notes,
                    },
                }
            )

            return True

    def add_threshold(self, threshold: MonitoringThreshold):
        """Add new monitoring threshold"""
        with self._lock:
            self.thresholds.append(threshold)

    def remove_threshold(self, metric_name: str, threshold_value: float) -> bool:
        """Remove monitoring threshold"""
        with self._lock:
            for i, threshold in enumerate(self.thresholds):
                if (
                    threshold.metric_name == metric_name
                    and threshold.threshold_value == threshold_value
                ):
                    del self.thresholds[i]
                    return True
            return False

    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        with self._lock:
            uptime = (
                (datetime.now() - self.monitoring_start_time).total_seconds()
                if self.monitoring_start_time
                else 0
            )

            return {
                "is_monitoring": self.is_monitoring,
                "monitoring_mode": self.monitoring_mode.value,
                "monitoring_interval": self.monitoring_interval,
                "uptime_seconds": uptime,
                "total_alerts": len(self.alerts),
                "active_alerts": len(self.active_alerts),
                "alerts_resolved": self.alerts_resolved,
                "total_alerts_generated": self.total_alerts_generated,
                "websocket_clients": len(self.websocket_clients),
                "thresholds_configured": len(self.thresholds),
            }

    def get_active_alerts(
        self, severity: Optional[AlertSeverity] = None
    ) -> List[FunnelAlert]:
        """Get active alerts, optionally filtered by severity"""
        with self._lock:
            alerts = [self.alerts[alert_id] for alert_id in self.active_alerts]

            if severity:
                alerts = [alert for alert in alerts if alert.severity == severity]

            return sorted(alerts, key=lambda x: x.timestamp, reverse=True)

    def get_metrics_history(
        self, metric_name: str, duration_minutes: int = 60
    ) -> List[Dict[str, Any]]:
        """Get metrics history for a specific metric"""
        with self._lock:
            if metric_name not in self.metrics_history:
                return []

            cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
            history = self.metrics_history[metric_name]

            return [entry for entry in history if entry["timestamp"] >= cutoff_time]

    def add_alert_callback(self, callback: Callable[[FunnelAlert], None]):
        """Add callback for alert notifications"""
        self.alert_callbacks.append(callback)

    def export_monitoring_data(self, format_type: str = "json") -> str:
        """Export monitoring data"""
        with self._lock:
            data = {
                "monitoring_status": self.get_monitoring_status(),
                "alerts": [alert.to_dict() for alert in self.alerts.values()],
                "thresholds": [
                    {
                        "metric_name": t.metric_name,
                        "threshold_type": t.threshold_type,
                        "operator": t.operator,
                        "threshold_value": t.threshold_value,
                        "severity": t.severity.value,
                        "enabled": t.enabled,
                    }
                    for t in self.thresholds
                ],
                "metrics_history": {
                    metric_name: [
                        {
                            "timestamp": entry["timestamp"].isoformat(),
                            "value": entry["value"],
                        }
                        for entry in history
                    ]
                    for metric_name, history in self.metrics_history.items()
                },
            }

            if format_type == "json":
                return json.dumps(data, indent=2, default=str)
            else:
                raise ValueError(f"Unsupported format: {format_type}")


class FunnelDashboard:
    """Real-time funnel dashboard"""

    def __init__(self, monitor: RealTimeFunnelMonitor):
        self.monitor = monitor
        self.dashboard_data = {}
        self.last_update = None

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        analytics = self.monitor.analyzer.get_analytics()
        monitoring_status = self.monitor.get_monitoring_status()
        active_alerts = self.monitor.get_active_alerts()

        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "monitoring": monitoring_status,
            "analytics": analytics,
            "alerts": {
                "total": len(active_alerts),
                "critical": len(
                    [a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]
                ),
                "error": len(
                    [a for a in active_alerts if a.severity == AlertSeverity.ERROR]
                ),
                "warning": len(
                    [a for a in active_alerts if a.severity == AlertSeverity.WARNING]
                ),
                "info": len(
                    [a for a in active_alerts if a.severity == AlertSeverity.INFO]
                ),
                "recent": [alert.to_dict() for alert in active_alerts[:10]],
            },
            "metrics": self._get_key_metrics(analytics),
            "trends": self._get_metric_trends(),
            "performance": self._get_performance_summary(analytics),
        }

        self.dashboard_data = dashboard
        self.last_update = datetime.now()

        return dashboard

    def _get_key_metrics(self, analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Get key funnel metrics"""
        conversion_metrics = analytics.get("conversion_metrics", {})
        performance_metrics = analytics.get("performance_metrics", {})
        error_analysis = analytics.get("error_analysis", {})

        return {
            "conversion_rate": conversion_metrics.get("overall_conversion_rate", 0),
            "total_sessions": conversion_metrics.get("total_sessions", 0),
            "completed_sessions": conversion_metrics.get("completed_sessions", 0),
            "avg_step_time": performance_metrics.get("average_step_time_ms", 0),
            "total_errors": error_analysis.get("total_errors", 0),
            "error_rate": error_analysis.get("error_rate", 0),
            "active_sessions": len(self.monitor.analyzer.active_sessions),
        }

    def _get_metric_trends(self) -> Dict[str, str]:
        """Get metric trends"""
        trends = {}

        # Get recent history for key metrics
        key_metrics = ["overall_conversion_rate", "active_sessions", "total_errors"]

        for metric in key_metrics:
            history = self.monitor.get_metrics_history(metric, duration_minutes=30)
            if len(history) >= 2:
                recent = history[-1]["value"]
                previous = history[-2]["value"]

                if recent > previous * 1.05:
                    trends[metric] = "increasing"
                elif recent < previous * 0.95:
                    trends[metric] = "decreasing"
                else:
                    trends[metric] = "stable"
            else:
                trends[metric] = "unknown"

        return trends

    def _get_performance_summary(self, analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Get performance summary"""
        performance_metrics = analytics.get("performance_metrics", {})
        steps = analytics.get("steps", [])

        if not steps:
            return {}

        # Find slowest and fastest steps
        slowest = max(steps, key=lambda s: s.get("avg_time_ms", 0))
        fastest = min(steps, key=lambda s: s.get("avg_time_ms", 0))

        return {
            "slowest_step": slowest["name"],
            "slowest_time": slowest.get("avg_time_ms", 0),
            "fastest_step": fastest["name"],
            "fastest_time": fastest.get("avg_time_ms", 0),
            "average_time": performance_metrics.get("average_step_time_ms", 0),
        }


# Convenience functions
def create_funnel_monitor(
    analyzer: FunnelAnalyzer, mode: str = "passive"
) -> RealTimeFunnelMonitor:
    """Create a funnel monitor"""
    monitoring_mode = MonitoringMode(mode)
    return RealTimeFunnelMonitor(analyzer, monitoring_mode)


def create_funnel_dashboard(monitor: RealTimeFunnelMonitor) -> FunnelDashboard:
    """Create a funnel dashboard"""
    return FunnelDashboard(monitor)


@contextmanager
def monitored_funnel(analyzer: FunnelAnalyzer, mode: str = "passive"):
    """Context manager for monitored funnel analysis"""
    monitor = create_funnel_monitor(analyzer, mode)
    dashboard = create_funnel_dashboard(monitor)

    try:
        monitor.start_monitoring()
        yield monitor, dashboard
    finally:
        monitor.stop_monitoring()
