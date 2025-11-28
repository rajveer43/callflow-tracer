"""
Custom metrics tracking for CallFlow Tracer.

This module provides decorators and utilities for tracking business logic metrics,
SLA monitoring, and custom performance indicators.

Example usage:
    from callflow_tracer import custom_metric, MetricsCollector
    
    @custom_metric("orders_processed")
    def process_order(order):
        # Metric automatically tracked
        return order.process()
    
    # Export metrics
    metrics = MetricsCollector.get_metrics()
    MetricsCollector.export_metrics("metrics.json")
"""

import time
import json
import threading
from typing import Dict, List, Any, Callable, Optional
from functools import wraps
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
import statistics


@dataclass
class MetricPoint:
    """Represents a single metric measurement."""
    name: str
    value: float
    timestamp: float
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self):
        return {
            'name': self.name,
            'value': self.value,
            'timestamp': self.timestamp,
            'datetime': datetime.fromtimestamp(self.timestamp).isoformat(),
            'tags': self.tags,
            'metadata': self.metadata
        }


@dataclass
class MetricStats:
    """Statistics for a metric."""
    name: str
    count: int
    total: float
    min: float
    max: float
    mean: float
    median: float
    stddev: float
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self):
        return {
            'name': self.name,
            'count': self.count,
            'total': round(self.total, 6),
            'min': round(self.min, 6),
            'max': round(self.max, 6),
            'mean': round(self.mean, 6),
            'median': round(self.median, 6),
            'stddev': round(self.stddev, 6),
            'tags': self.tags
        }


class MetricsCollector:
    """Global metrics collector for tracking custom metrics."""
    
    _instance = None
    _lock = threading.Lock()
    _metrics: Dict[str, List[MetricPoint]] = {}
    _sla_thresholds: Dict[str, float] = {}
    _sla_violations: Dict[str, List[float]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def record_metric(cls, name: str, value: float, tags: Optional[Dict[str, str]] = None,
                     metadata: Optional[Dict[str, Any]] = None):
        """Record a custom metric."""
        instance = cls()
        with cls._lock:
            if name not in cls._metrics:
                cls._metrics[name] = []
            
            point = MetricPoint(
                name=name,
                value=value,
                timestamp=time.time(),
                tags=tags or {},
                metadata=metadata or {}
            )
            cls._metrics[name].append(point)
            
            # Check SLA violation
            if name in cls._sla_thresholds:
                threshold = cls._sla_thresholds[name]
                if value > threshold:
                    if name not in cls._sla_violations:
                        cls._sla_violations[name] = []
                    cls._sla_violations[name].append(value)
    
    @classmethod
    def set_sla_threshold(cls, metric_name: str, threshold: float):
        """Set SLA threshold for a metric."""
        with cls._lock:
            cls._sla_thresholds[metric_name] = threshold
    
    @classmethod
    def get_metrics(cls) -> Dict[str, List[Dict]]:
        """Get all recorded metrics."""
        with cls._lock:
            return {
                name: [point.to_dict() for point in points]
                for name, points in cls._metrics.items()
            }
    
    @classmethod
    def get_metric_stats(cls, metric_name: str) -> Optional[MetricStats]:
        """Get statistics for a specific metric."""
        with cls._lock:
            if metric_name not in cls._metrics:
                return None
            
            points = cls._metrics[metric_name]
            if not points:
                return None
            
            values = [p.value for p in points]
            
            return MetricStats(
                name=metric_name,
                count=len(values),
                total=sum(values),
                min=min(values),
                max=max(values),
                mean=statistics.mean(values),
                median=statistics.median(values),
                stddev=statistics.stdev(values) if len(values) > 1 else 0.0,
                tags=points[0].tags if points else {}
            )
    
    @classmethod
    def get_all_stats(cls) -> Dict[str, Dict]:
        """Get statistics for all metrics."""
        with cls._lock:
            stats = {}
            for metric_name in cls._metrics.keys():
                metric_stats = cls.get_metric_stats(metric_name)
                if metric_stats:
                    stats[metric_name] = metric_stats.to_dict()
            return stats
    
    @classmethod
    def get_sla_violations(cls) -> Dict[str, List[float]]:
        """Get SLA violations."""
        with cls._lock:
            return dict(cls._sla_violations)
    
    @classmethod
    def export_metrics(cls, output_file: str, format: str = "json"):
        """Export metrics to file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with cls._lock:
            if format == "json":
                data = {
                    "metrics": cls.get_metrics(),
                    "statistics": cls.get_all_stats(),
                    "sla_violations": cls.get_sla_violations(),
                    "export_timestamp": datetime.now().isoformat()
                }
                with open(output_path, 'w') as f:
                    json.dump(data, f, indent=2)
            elif format == "csv":
                cls._export_csv(output_path)
    
    @classmethod
    def _export_csv(cls, output_path: Path):
        """Export metrics to CSV format."""
        import csv
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Metric', 'Value', 'Timestamp', 'Tags', 'Metadata'])
            
            for metric_name, points in cls._metrics.items():
                for point in points:
                    writer.writerow([
                        point.name,
                        point.value,
                        datetime.fromtimestamp(point.timestamp).isoformat(),
                        json.dumps(point.tags),
                        json.dumps(point.metadata)
                    ])
    
    @classmethod
    def clear_metrics(cls):
        """Clear all recorded metrics."""
        with cls._lock:
            cls._metrics.clear()
            cls._sla_violations.clear()
    
    @classmethod
    def get_metric_by_tag(cls, tag_key: str, tag_value: str) -> List[MetricPoint]:
        """Get metrics filtered by tag."""
        with cls._lock:
            results = []
            for points in cls._metrics.values():
                for point in points:
                    if point.tags.get(tag_key) == tag_value:
                        results.append(point)
            return results


def custom_metric(metric_name: str, sla_threshold: Optional[float] = None,
                 tags: Optional[Dict[str, str]] = None):
    """
    Decorator to track custom metrics for a function.
    
    Args:
        metric_name: Name of the metric to track
        sla_threshold: Optional SLA threshold for this metric
        tags: Optional tags to associate with the metric
    
    Example:
        @custom_metric("orders_processed", sla_threshold=1.0)
        def process_order(order):
            return order.process()
    """
    if sla_threshold is not None:
        MetricsCollector.set_sla_threshold(metric_name, sla_threshold)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                MetricsCollector.record_metric(
                    metric_name,
                    duration,
                    tags=tags,
                    metadata={'function': func.__name__, 'module': func.__module__}
                )
        return wrapper
    return decorator


def track_metric(metric_name: str, value: float, tags: Optional[Dict[str, str]] = None,
                metadata: Optional[Dict[str, Any]] = None):
    """
    Manually record a metric value.
    
    Args:
        metric_name: Name of the metric
        value: Metric value
        tags: Optional tags
        metadata: Optional metadata
    
    Example:
        track_metric("orders_processed", 1, tags={"status": "success"})
        track_metric("response_time", 0.234, tags={"endpoint": "/api/orders"})
    """
    MetricsCollector.record_metric(metric_name, value, tags, metadata)


class SLACondition:
    """Represents a single SLA condition."""
    
    def __init__(self, 
                 metric_name: str, 
                 threshold: float, 
                 operator: str = 'gt',
                 time_window: Optional[int] = None,
                 dynamic: bool = False,
                 sensitivity: float = 1.5):
        """
        Initialize an SLA condition.
        
        Args:
            metric_name: Name of the metric to monitor
            threshold: Threshold value for the condition
            operator: Comparison operator ('gt', 'lt', 'eq', 'gte', 'lte')
            time_window: Time window in seconds for rolling window SLAs (None for all-time)
            dynamic: Whether to enable dynamic threshold adjustment
            sensitivity: Sensitivity factor for dynamic threshold adjustment (higher = more sensitive)
        """
        self.metric_name = metric_name
        self.threshold = threshold
        self.operator = operator
        self.time_window = time_window
        self.dynamic = dynamic
        self.sensitivity = sensitivity
        self.violations: List[Dict[str, Any]] = []
        
    def check_condition(self, value: float) -> bool:
        """Check if the value meets the condition."""
        ops = {
            'gt': lambda x: x > self.threshold,
            'lt': lambda x: x < self.threshold,
            'eq': lambda x: x == self.threshold,
            'gte': lambda x: x >= self.threshold,
            'lte': lambda x: x <= self.threshold
        }
        return ops.get(self.operator, lambda x: False)(value)
    
    def record_violation(self, value: float, timestamp: float = None):
        """Record a violation of this condition."""
        self.violations.append({
            'value': value,
            'timestamp': timestamp or time.time(),
            'threshold': self.threshold
        })
    
    def adjust_threshold(self, historical_values: List[float]):
        """Dynamically adjust threshold based on historical data."""
        if not historical_values or not self.dynamic:
            return
            
        # Use IQR method to detect outliers and adjust threshold
        try:
            qs = statistics.quantiles(historical_values, n=4, method='inclusive')
            # statistics.quantiles returns 3 cut points for quartiles
            q1 = qs[0]
            q3 = qs[2]
        except Exception:
            # Fallback simple computation
            sorted_vals = sorted(historical_values)
            idx_q1 = max(0, int(0.25 * (len(sorted_vals) - 1)))
            idx_q3 = max(0, int(0.75 * (len(sorted_vals) - 1)))
            q1 = sorted_vals[idx_q1]
            q3 = sorted_vals[idx_q3]
        iqr = q3 - q1
        
        if self.operator in ['gt', 'gte']:
            # For upper-bound thresholds, adjust based on Q3 + IQR
            self.threshold = q3 + (self.sensitivity * iqr)
        else:
            # For lower-bound thresholds, adjust based on Q1 - IQR
            self.threshold = q1 - (self.sensitivity * iqr)


class SLAMonitor:
    """Monitor SLA compliance for metrics with support for multi-dimensional conditions."""
    
    def __init__(self):
        self.conditions: Dict[str, List[SLACondition]] = {}
        self.metric_history: Dict[str, List[Dict[str, Any]]] = {}
        self.history_size = 1000  # Keep last 1000 data points per metric
    
    def add_condition(self, condition: SLACondition):
        """Add an SLA condition to monitor."""
        if condition.metric_name not in self.conditions:
            self.conditions[condition.metric_name] = []
        self.conditions[condition.metric_name].append(condition)
        
        # Initialize history if needed
        if condition.metric_name not in self.metric_history:
            self.metric_history[condition.metric_name] = []
    
    def set_threshold(self, 
                     metric_name: str, 
                     threshold: float, 
                     operator: str = 'gt',
                     time_window: Optional[int] = None,
                     dynamic: bool = False):
        """
        Set SLA threshold with additional options.
        
        Args:
            metric_name: Name of the metric
            threshold: Threshold value
            operator: Comparison operator ('gt', 'lt', 'eq', 'gte', 'lte')
            time_window: Time window in seconds for rolling window SLAs
            dynamic: Whether to enable dynamic threshold adjustment
        """
        condition = SLACondition(metric_name, threshold, operator, time_window, dynamic)
        self.add_condition(condition)
    
    def record_metric(self, metric_name: str, value: float, timestamp: float = None):
        """Record a metric value and check against SLA conditions."""
        if metric_name not in self.conditions:
            return
            
        ts = timestamp or time.time()
        
        # Update metric history
        if metric_name not in self.metric_history:
            self.metric_history[metric_name] = []
            
        self.metric_history[metric_name].append({'value': value, 'timestamp': ts})
        
        # Trim history if needed
        if len(self.metric_history[metric_name]) > self.history_size:
            self.metric_history[metric_name].pop(0)
        
        # Check conditions for this metric
        for condition in self.conditions.get(metric_name, []):
            # Get relevant historical data if time window is specified
            if condition.time_window:
                window_start = ts - condition.time_window
                values_in_window = [
                    m['value'] for m in self.metric_history[metric_name]
                    if m['timestamp'] >= window_start
                ]
                if not values_in_window:
                    continue
                    
                # For time windows, we might want to check aggregates (e.g., average over window)
                value_to_check = sum(values_in_window) / len(values_in_window)
            else:
                value_to_check = value
            
            # Check condition and record violations
            if not condition.check_condition(value_to_check):
                condition.record_violation(value_to_check, ts)
            
            # Adjust threshold if dynamic
            if condition.dynamic and len(self.metric_history[metric_name]) > 10:  # Need some history
                historical_values = [m['value'] for m in self.metric_history[metric_name][:-1]]
                condition.adjust_threshold(historical_values)
    
    def get_compliance_report(self, time_window: Optional[int] = None) -> Dict[str, Any]:
        """
        Get SLA compliance report.
        
        Args:
            time_window: Time window in seconds to consider (None for all-time)
            
        Returns:
            Dictionary with compliance metrics for each condition
        """
        report = {}
        now = time.time()
        
        for metric_name, conditions in self.conditions.items():
            report[metric_name] = []
            
            for condition in conditions:
                # Filter violations by time window if specified
                if time_window:
                    violations = [
                        v for v in condition.violations 
                        if (now - v['timestamp']) <= time_window
                    ]
                else:
                    violations = condition.violations
                
                # Calculate compliance rate
                total = len([m for m in self.metric_history.get(metric_name, []) 
                           if (not time_window) or ((now - m['timestamp']) <= time_window)])
                
                compliance_rate = 100.0
                if total > 0:
                    compliance_rate = ((total - len(violations)) / total) * 100
                
                report[metric_name].append({
                    'threshold': condition.threshold,
                    'operator': condition.operator,
                    'time_window': condition.time_window,
                    'dynamic': condition.dynamic,
                    'total_checks': total,
                    'violations': len(violations),
                    'compliance_rate': round(compliance_rate, 2),
                    'last_violation': max(v['timestamp'] for v in violations) if violations else None,
                    'status': self._get_status(compliance_rate)
                })
        
        return report
    
    def _get_status(self, compliance_rate: float) -> str:
        """Get status based on compliance rate."""
        if compliance_rate >= 95:
            return 'PASS'
        elif compliance_rate >= 80:
            return 'WARN'
        return 'FAIL'
    
    def export_report(self, output_file: str, time_window: Optional[int] = None):
        """
        Export SLA compliance report to a file.
        
        Args:
            output_file: Path to output file
            time_window: Time window in seconds to consider (None for all-time)
        """
        report = self.get_compliance_report(time_window)
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
    
    def get_violations(self, 
                      metric_name: Optional[str] = None,
                      time_window: Optional[int] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all SLA violations.
        
        Args:
            metric_name: Optional metric name to filter by
            time_window: Optional time window in seconds
            
        Returns:
            Dictionary of metric names to lists of violations
        """
        violations = {}
        now = time.time()
        
        for m_name, conditions in self.conditions.items():
            if metric_name and m_name != metric_name:
                continue
                
            violations[m_name] = []
            
            for condition in conditions:
                for violation in condition.violations:
                    if time_window and (now - violation['timestamp']) > time_window:
                        continue
                        
                    violations[m_name].append({
                        'timestamp': violation['timestamp'],
                        'value': violation['value'],
                        'threshold': violation['threshold'],
                        'operator': condition.operator
                    })
        
        return violations


class BusinessMetricsTracker:
    """Track business logic metrics."""
    
    def __init__(self):
        self.counters: Dict[str, int] = {}
        self.gauges: Dict[str, float] = {}
        self._lock = threading.Lock()
    
    def increment_counter(self, counter_name: str, amount: int = 1):
        """Increment a counter."""
        with self._lock:
            self.counters[counter_name] = self.counters.get(counter_name, 0) + amount
            track_metric(f"counter_{counter_name}", self.counters[counter_name])
    
    def set_gauge(self, gauge_name: str, value: float):
        """Set a gauge value."""
        with self._lock:
            self.gauges[gauge_name] = value
            track_metric(f"gauge_{gauge_name}", value)
    
    def get_counters(self) -> Dict[str, int]:
        """Get all counter values."""
        with self._lock:
            return dict(self.counters)
    
    def get_gauges(self) -> Dict[str, float]:
        """Get all gauge values."""
        with self._lock:
            return dict(self.gauges)
    
    def export_metrics(self, output_file: str):
        """Export business metrics."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with self._lock:
            data = {
                'counters': self.counters,
                'gauges': self.gauges,
                'timestamp': datetime.now().isoformat()
            }
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)


# -------------------- SLO/SLI, Error Budgets, and Experiment Analysis --------------------

def _percentile(values: List[float], p: float) -> Optional[float]:
    if not values:
        return None
    if p <= 0:
        return min(values)
    if p >= 100:
        return max(values)
    s = sorted(values)
    k = (len(s) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(s) - 1)
    if f == c:
        return s[f]
    return s[f] + (k - f) * (s[c] - s[f])


def _filter_points(metric_name: str,
                   time_window: Optional[int] = None,
                   tags: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
    all_metrics = MetricsCollector.get_metrics().get(metric_name, [])
    if not all_metrics:
        return []
    now_ts = time.time()
    def tag_match(t: Dict[str, str]) -> bool:
        if not tags:
            return True
        for k, v in tags.items():
            if t.get(k) != v:
                return False
        return True
    return [m for m in all_metrics
            if (time_window is None or (now_ts - m['timestamp']) <= time_window)
            and tag_match(m.get('tags', {}))]


class SLI:
    """Compute Service Level Indicators over metrics."""

    @staticmethod
    def availability(metric_name: str,
                     success_value: float = 1.0,
                     time_window: Optional[int] = None,
                     tags: Optional[Dict[str, str]] = None) -> Optional[float]:
        points = _filter_points(metric_name, time_window, tags)
        if not points:
            return None
        successes = sum(1 for m in points if float(m['value']) == float(success_value))
        return successes / len(points)

    @staticmethod
    def error_rate(metric_name: str,
                   error_value: float = 1.0,
                   time_window: Optional[int] = None,
                   tags: Optional[Dict[str, str]] = None) -> Optional[float]:
        points = _filter_points(metric_name, time_window, tags)
        if not points:
            return None
        errors = sum(1 for m in points if float(m['value']) == float(error_value))
        return errors / len(points)

    @staticmethod
    def latency_target_ratio(metric_name: str,
                             threshold: float,
                             percentile: float = 95.0,
                             time_window: Optional[int] = None,
                             tags: Optional[Dict[str, str]] = None) -> Optional[float]:
        points = _filter_points(metric_name, time_window, tags)
        if not points:
            return None
        lat_p = _percentile([float(m['value']) for m in points], percentile)
        if lat_p is None:
            return None
        return 1.0 if lat_p <= threshold else 0.0


@dataclass
class SLO:
    name: str
    objective: float  # e.g., 0.99 for 99%
    time_window: int  # seconds
    sli_type: str  # 'availability' | 'error_rate' | 'latency'
    metric_name: str
    params: Dict[str, Any] = field(default_factory=dict)

    def compute(self, tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        if self.sli_type == 'availability':
            value = SLI.availability(self.metric_name, time_window=self.time_window, tags=tags, **self.params)
        elif self.sli_type == 'error_rate':
            err = SLI.error_rate(self.metric_name, time_window=self.time_window, tags=tags, **self.params)
            value = None if err is None else (1.0 - err)
        elif self.sli_type == 'latency':
            value = SLI.latency_target_ratio(self.metric_name, time_window=self.time_window, tags=tags, **self.params)
        else:
            value = None
        compliant = (value is not None) and (value >= self.objective)
        return {
            'slo': self.name,
            'objective': self.objective,
            'observed': value,
            'window_seconds': self.time_window,
            'compliant': compliant
        }


@dataclass
class ErrorBudgetTracker:
    slo: SLO

    def compute_budget(self, tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        res = self.slo.compute(tags)
        observed = res['observed']
        if observed is None:
            return {
                'slo': self.slo.name,
                'error_budget': 1.0 - self.slo.objective,
                'consumed': None,
                'remaining': None,
                'burn_rate': None,
            }
        allowed_error = 1.0 - self.slo.objective
        actual_error = max(0.0, 1.0 - observed)
        consumed = min(1.0, actual_error / allowed_error) if allowed_error > 0 else (1.0 if actual_error > 0 else 0.0)
        remaining = max(0.0, 1.0 - consumed)
        # Simple burn rate = consumed per window
        burn_rate = consumed
        return {
            'slo': self.slo.name,
            'allowed_error': allowed_error,
            'actual_error': actual_error,
            'consumed': consumed,
            'remaining': remaining,
            'burn_rate': burn_rate,
            'window_seconds': self.slo.time_window,
        }


class ExperimentAnalyzer:
    """Utilities for Canary and A/B comparisons using tag grouping."""

    @staticmethod
    def compare_groups(metric_name: str,
                       group_tag_key: str,
                       group_values: List[str],
                       statistic: str = 'mean',
                       time_window: Optional[int] = None) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        for gv in group_values:
            pts = _filter_points(metric_name, time_window, tags={group_tag_key: gv})
            values = [float(m['value']) for m in pts]
            if not values:
                results[gv] = {'count': 0, 'stat': None, 'p95': None}
                continue
            if statistic == 'mean':
                stat = statistics.mean(values)
            elif statistic == 'median':
                stat = statistics.median(values)
            elif statistic == 'max':
                stat = max(values)
            else:
                stat = statistics.mean(values)
            results[gv] = {
                'count': len(values),
                'stat': stat,
                'p95': _percentile(values, 95)
            }
        # Compute deltas if exactly two groups
        if len(group_values) == 2 and all(g in results for g in group_values):
            a, b = group_values[0], group_values[1]
            va, vb = results[a]['stat'], results[b]['stat']
            if va is not None and vb is not None:
                results['delta'] = {
                    'absolute': vb - va,
                    'relative': ((vb - va) / va) if va != 0 else None
                }
        return results

    @staticmethod
    def canary(metric_name: str,
               baseline_value: str = 'baseline',
               canary_value: str = 'canary',
               group_tag_key: str = 'deployment',
               time_window: Optional[int] = None) -> Dict[str, Any]:
        return ExperimentAnalyzer.compare_groups(
            metric_name,
            group_tag_key,
            [baseline_value, canary_value],
            statistic='mean',
            time_window=time_window
        )

    @staticmethod
    def ab_test(metric_name: str,
                variant_a: str = 'A',
                variant_b: str = 'B',
                group_tag_key: str = 'variant',
                time_window: Optional[int] = None) -> Dict[str, Any]:
        return ExperimentAnalyzer.compare_groups(
            metric_name,
            group_tag_key,
            [variant_a, variant_b],
            statistic='mean',
            time_window=time_window
        )

# Global instance for convenience
_business_tracker = BusinessMetricsTracker()


def get_business_tracker() -> BusinessMetricsTracker:
    """Get the global business metrics tracker."""
    return _business_tracker
