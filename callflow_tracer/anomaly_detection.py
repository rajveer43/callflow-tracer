"""
Anomaly Detection System for CallFlow Tracer

Detects anomalies in durations and metrics with baseline learning and drift alerts.
"""

import json
import time
import statistics
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict, deque


@dataclass
class AnomalyAlert:
    """Represents an anomaly detection alert."""
    timestamp: datetime
    metric_name: str
    value: float
    baseline_mean: float
    baseline_std: float
    z_score: float
    severity: str  # "low", "medium", "high", "critical"
    description: str
    context: Dict[str, Any]


@dataclass
class BaselineStats:
    """Baseline statistics for a metric."""
    metric_name: str
    samples: List[float]
    mean: float
    std: float
    min: float
    max: float
    percentile_95: float
    percentile_99: float
    last_updated: datetime
    sample_count: int


class BaselineLearner:
    """Learns and maintains baselines for metrics."""
    
    def __init__(self, min_samples: int = 30, max_samples: int = 1000):
        self.min_samples = min_samples
        self.max_samples = max_samples
        self.baselines: Dict[str, BaselineStats] = {}
        self.learning_enabled = True
        
    def add_sample(self, metric_name: str, value: float) -> None:
        """Add a new sample for baseline learning."""
        if metric_name not in self.baselines:
            self.baselines[metric_name] = BaselineStats(
                metric_name=metric_name,
                samples=[],
                mean=0.0,
                std=0.0,
                min=float('inf'),
                max=float('-inf'),
                percentile_95=0.0,
                percentile_99=0.0,
                last_updated=datetime.now(),
                sample_count=0
            )
        
        baseline = self.baselines[metric_name]
        baseline.samples.append(value)
        
        # Keep only the most recent samples
        if len(baseline.samples) > self.max_samples:
            baseline.samples = baseline.samples[-self.max_samples:]
        
        # Update statistics
        if len(baseline.samples) >= self.min_samples:
            baseline.mean = statistics.mean(baseline.samples)
            baseline.std = statistics.stdev(baseline.samples) if len(baseline.samples) > 1 else 0.0
            baseline.min = min(baseline.samples)
            baseline.max = max(baseline.samples)
            baseline.percentile_95 = np.percentile(baseline.samples, 95)
            baseline.percentile_99 = np.percentile(baseline.samples, 99)
            baseline.last_updated = datetime.now()
            baseline.sample_count = len(baseline.samples)
    
    def get_baseline(self, metric_name: str) -> Optional[BaselineStats]:
        """Get baseline statistics for a metric."""
        return self.baselines.get(metric_name)
    
    def is_ready(self, metric_name: str) -> bool:
        """Check if baseline is ready for anomaly detection."""
        baseline = self.baselines.get(metric_name)
        return baseline is not None and baseline.sample_count >= self.min_samples
    
    def export_baselines(self) -> Dict[str, Any]:
        """Export all baselines to JSON."""
        return {
            metric_name: asdict(baseline) 
            for metric_name, baseline in self.baselines.items()
        }
    
    def import_baselines(self, data: Dict[str, Any]) -> None:
        """Import baselines from JSON."""
        for metric_name, baseline_data in data.items():
            # Convert datetime strings back to datetime objects
            if isinstance(baseline_data.get('last_updated'), str):
                baseline_data['last_updated'] = datetime.fromisoformat(baseline_data['last_updated'])
            
            self.baselines[metric_name] = BaselineStats(**baseline_data)


class AnomalyDetector:
    """Detects anomalies in metrics using statistical methods."""
    
    def __init__(self, 
                 z_score_threshold: float = 3.0,
                 drift_threshold: float = 0.2,
                 window_size: int = 100):
        self.z_score_threshold = z_score_threshold
        self.drift_threshold = drift_threshold
        self.window_size = window_size
        self.baseline_learner = BaselineLearner()
        self.alerts: List[AnomalyAlert] = []
        self.drift_windows: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        
    def analyze_metric(self, metric_name: str, value: float, 
                      context: Optional[Dict[str, Any]] = None) -> Optional[AnomalyAlert]:
        """Analyze a metric value for anomalies."""
        context = context or {}
        
        # Add sample to baseline learner
        self.baseline_learner.add_sample(metric_name, value)
        
        # Check if baseline is ready
        if not self.baseline_learner.is_ready(metric_name):
            return None
        
        baseline = self.baseline_learner.get_baseline(metric_name)
        
        # Calculate Z-score
        if baseline.std == 0:
            return None
        
        z_score = abs(value - baseline.mean) / baseline.std
        
        # Check for anomaly
        if z_score >= self.z_score_threshold:
            severity = self._calculate_severity(z_score)
            alert = AnomalyAlert(
                timestamp=datetime.now(),
                metric_name=metric_name,
                value=value,
                baseline_mean=baseline.mean,
                baseline_std=baseline.std,
                z_score=z_score,
                severity=severity,
                description=self._generate_description(metric_name, value, baseline, z_score),
                context=context
            )
            
            self.alerts.append(alert)
            return alert
        
        # Check for drift
        self._check_drift(metric_name, value, baseline)
        
        return None
    
    def _calculate_severity(self, z_score: float) -> str:
        """Calculate anomaly severity based on Z-score."""
        if z_score >= 5.0:
            return "critical"
        elif z_score >= 4.0:
            return "high"
        elif z_score >= 3.0:
            return "medium"
        else:
            return "low"
    
    def _generate_description(self, metric_name: str, value: float, 
                            baseline: BaselineStats, z_score: float) -> str:
        """Generate human-readable anomaly description."""
        if value > baseline.mean:
            direction = "higher"
            diff_percent = ((value - baseline.mean) / baseline.mean) * 100
        else:
            direction = "lower"
            diff_percent = ((baseline.mean - value) / baseline.mean) * 100
        
        return (f"{metric_name} is {direction} than normal by {diff_percent:.1f}% "
                f"(value: {value:.3f}, baseline: {baseline.mean:.3f}, "
                f"z-score: {z_score:.2f})")
    
    def _check_drift(self, metric_name: str, value: float, baseline: BaselineStats) -> None:
        """Check for concept drift in the metric."""
        window = self.drift_windows[metric_name]
        window.append(value)
        
        if len(window) == self.window_size:
            window_mean = statistics.mean(window)
            
            # Calculate drift percentage
            if baseline.mean != 0:
                drift_percent = abs(window_mean - baseline.mean) / baseline.mean
            else:
                drift_percent = 0.0
            
            if drift_percent > self.drift_threshold:
                # Create drift alert
                alert = AnomalyAlert(
                    timestamp=datetime.now(),
                    metric_name=f"{metric_name}_drift",
                    value=window_mean,
                    baseline_mean=baseline.mean,
                    baseline_std=baseline.std,
                    z_score=drift_percent / (baseline.std if baseline.std > 0 else 1.0),
                    severity="medium",
                    description=f"Concept drift detected in {metric_name}: "
                               f"recent average ({window_mean:.3f}) differs from "
                               f"baseline ({baseline.mean:.3f}) by {drift_percent*100:.1f}%",
                    context={"window_size": self.window_size, "drift_type": "concept_drift"}
                )
                self.alerts.append(alert)
    
    def get_recent_alerts(self, hours: int = 24) -> List[AnomalyAlert]:
        """Get alerts from the last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alerts if alert.timestamp >= cutoff]
    
    def get_alerts_by_severity(self, severity: str) -> List[AnomalyAlert]:
        """Get alerts by severity level."""
        return [alert for alert in self.alerts if alert.severity == severity]
    
    def generate_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate an anomaly detection report."""
        recent_alerts = self.get_recent_alerts(hours)
        
        # Group alerts by metric
        alerts_by_metric = defaultdict(list)
        for alert in recent_alerts:
            alerts_by_metric[alert.metric_name].append(alert)
        
        # Calculate statistics
        severity_counts = defaultdict(int)
        for alert in recent_alerts:
            severity_counts[alert.severity] += 1
        
        return {
            "report_generated": datetime.now().isoformat(),
            "period_hours": hours,
            "total_alerts": len(recent_alerts),
            "severity_breakdown": dict(severity_counts),
            "alerts_by_metric": {
                metric: [asdict(alert) for alert in alerts]
                for metric, alerts in alerts_by_metric.items()
            },
            "top_anomalies": sorted(
                [asdict(alert) for alert in recent_alerts],
                key=lambda x: x["z_score"],
                reverse=True
            )[:10],
            "baseline_status": {
                metric: {
                    "sample_count": baseline.sample_count,
                    "ready": baseline.sample_count >= self.baseline_learner.min_samples,
                    "last_updated": baseline.last_updated.isoformat()
                }
                for metric, baseline in self.baseline_learner.baselines.items()
            }
        }
    
    def export_alerts(self, filename: str, hours: int = 24) -> None:
        """Export alerts to JSON file."""
        report = self.generate_report(hours)
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
    
    def clear_alerts(self, older_than_hours: int = 168) -> None:  # Default: 1 week
        """Clear old alerts."""
        cutoff = datetime.now() - timedelta(hours=older_than_hours)
        self.alerts = [alert for alert in self.alerts if alert.timestamp >= cutoff]


# Global anomaly detector instance
_global_detector = None


def get_anomaly_detector() -> AnomalyDetector:
    """Get the global anomaly detector instance."""
    global _global_detector
    if _global_detector is None:
        _global_detector = AnomalyDetector()
    return _global_detector


def analyze_function_duration(function_name: str, duration: float, 
                             context: Optional[Dict[str, Any]] = None) -> Optional[AnomalyAlert]:
    """Analyze function duration for anomalies."""
    detector = get_anomaly_detector()
    metric_name = f"function_duration.{function_name}"
    return detector.analyze_metric(metric_name, duration, context)


def analyze_custom_metric(metric_name: str, value: float, 
                         context: Optional[Dict[str, Any]] = None) -> Optional[AnomalyAlert]:
    """Analyze custom metric for anomalies."""
    detector = get_anomaly_detector()
    return detector.analyze_metric(metric_name, value, context)


def generate_anomaly_report(hours: int = 24) -> Dict[str, Any]:
    """Generate anomaly detection report."""
    detector = get_anomaly_detector()
    return detector.generate_report(hours)


def export_anomaly_report(filename: str, hours: int = 24) -> None:
    """Export anomaly detection report to file."""
    detector = get_anomaly_detector()
    detector.export_alerts(filename, hours)
