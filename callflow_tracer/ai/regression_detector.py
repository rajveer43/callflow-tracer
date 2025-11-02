"""
Performance regression detection module for CallFlow Tracer.

Detects performance regressions by comparing current traces against baseline
or historical data. Provides statistical analysis and trend detection.

Example:
    from callflow_tracer.ai import RegressionDetector
    
    detector = RegressionDetector(baseline_trace)
    result = detector.detect(current_trace)
    
    if result['has_regression']:
        print(f"Regression detected: {result['severity']}")
        print(f"Affected functions: {result['affected_functions']}")
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import statistics
from datetime import datetime


@dataclass
class RegressionMetric:
    """Metrics for a single regression."""
    function_name: str
    module: str
    baseline_time: float
    current_time: float
    delta: float
    percent_change: float
    z_score: float
    confidence: float
    severity: str  # 'critical', 'high', 'medium', 'low'


@dataclass
class RegressionResult:
    """Complete regression detection result."""
    timestamp: str
    has_regression: bool
    severity: str  # 'critical', 'high', 'medium', 'low', 'none'
    affected_functions: List[RegressionMetric]
    critical_regressions: List[RegressionMetric]
    statistical_summary: Dict[str, Any]
    recommendations: List[str]


class RegressionDetector:
    """Detect performance regressions in execution traces."""
    
    def __init__(self, baseline_trace: Dict[str, Any], 
                 historical_traces: Optional[List[Dict[str, Any]]] = None,
                 z_score_threshold: float = 2.0,
                 percent_threshold: float = 0.1):
        """
        Initialize regression detector.
        
        Args:
            baseline_trace: Reference trace for comparison
            historical_traces: Optional list of historical traces for statistical analysis
            z_score_threshold: Z-score threshold for anomaly detection (default 2.0)
            percent_threshold: Percentage threshold for regression (default 10%)
        """
        self.baseline_trace = baseline_trace
        self.historical_traces = historical_traces or []
        self.z_score_threshold = z_score_threshold
        self.percent_threshold = percent_threshold
        self.baseline_nodes = self._extract_nodes(baseline_trace)
        self.historical_stats = self._compute_historical_stats()
    
    def detect(self, current_trace: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect regressions in current trace.
        
        Args:
            current_trace: Current execution trace
            
        Returns:
            RegressionResult with detection details
        """
        current_nodes = self._extract_nodes(current_trace)
        regressions = []
        critical_regressions = []
        
        for node_key, baseline_node in self.baseline_nodes.items():
            if node_key in current_nodes:
                current_node = current_nodes[node_key]
                metric = self._analyze_regression(baseline_node, current_node, node_key)
                
                if metric and metric.percent_change >= self.percent_threshold * 100:
                    regressions.append(metric)
                    if metric.severity == 'critical':
                        critical_regressions.append(metric)
        
        # Sort by severity
        regressions.sort(key=lambda x: (x.severity != 'critical', x.percent_change), reverse=True)
        
        # Determine overall severity
        overall_severity = self._determine_severity(regressions)
        has_regression = len(regressions) > 0
        
        # Generate recommendations
        recommendations = self._generate_recommendations(regressions)
        
        # Compute statistical summary
        stats = self._compute_statistical_summary(regressions)
        
        result = RegressionResult(
            timestamp=datetime.now().isoformat(),
            has_regression=has_regression,
            severity=overall_severity,
            affected_functions=regressions,
            critical_regressions=critical_regressions,
            statistical_summary=stats,
            recommendations=recommendations
        )
        
        return {
            'timestamp': result.timestamp,
            'has_regression': result.has_regression,
            'severity': result.severity,
            'affected_functions': [asdict(f) for f in result.affected_functions],
            'critical_regressions': [asdict(c) for c in result.critical_regressions],
            'statistical_summary': result.statistical_summary,
            'recommendations': result.recommendations
        }
    
    def _extract_nodes(self, graph: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Extract nodes from graph structure."""
        nodes = {}
        
        if isinstance(graph, dict):
            if 'nodes' in graph:
                for node in graph['nodes']:
                    key = f"{node.get('module', 'unknown')}:{node.get('name', 'unknown')}"
                    nodes[key] = node
            elif 'data' in graph and 'nodes' in graph['data']:
                for node in graph['data']['nodes']:
                    key = f"{node.get('module', 'unknown')}:{node.get('name', 'unknown')}"
                    nodes[key] = node
        
        return nodes
    
    def _compute_historical_stats(self) -> Dict[str, Dict[str, float]]:
        """Compute statistics from historical traces."""
        stats = {}
        
        if not self.historical_traces:
            return stats
        
        # Group times by function
        function_times = {}
        
        for trace in self.historical_traces:
            nodes = self._extract_nodes(trace)
            for node_key, node in nodes.items():
                if node_key not in function_times:
                    function_times[node_key] = []
                function_times[node_key].append(node.get('total_time', 0))
        
        # Compute statistics
        for node_key, times in function_times.items():
            if len(times) > 1:
                stats[node_key] = {
                    'mean': statistics.mean(times),
                    'stdev': statistics.stdev(times),
                    'min': min(times),
                    'max': max(times),
                    'count': len(times)
                }
        
        return stats
    
    def _analyze_regression(self, baseline_node: Dict[str, Any],
                           current_node: Dict[str, Any],
                           node_key: str) -> Optional[RegressionMetric]:
        """Analyze a single node for regression."""
        baseline_time = baseline_node.get('total_time', 0)
        current_time = current_node.get('total_time', 0)
        delta = current_time - baseline_time
        
        if baseline_time == 0:
            return None
        
        percent_change = (delta / baseline_time) * 100
        
        # Calculate z-score if historical data available
        z_score = 0.0
        confidence = 0.0
        
        if node_key in self.historical_stats:
            stats = self.historical_stats[node_key]
            if stats['stdev'] > 0:
                z_score = (current_time - stats['mean']) / stats['stdev']
                confidence = min(1.0, abs(z_score) / self.z_score_threshold)
        
        # Determine severity
        severity = self._calculate_severity(percent_change, z_score)
        
        return RegressionMetric(
            function_name=current_node.get('name', 'unknown'),
            module=current_node.get('module', 'unknown'),
            baseline_time=baseline_time,
            current_time=current_time,
            delta=delta,
            percent_change=percent_change,
            z_score=z_score,
            confidence=confidence,
            severity=severity
        )
    
    def _calculate_severity(self, percent_change: float, z_score: float) -> str:
        """Calculate severity based on percent change and z-score."""
        if percent_change >= 50 or abs(z_score) >= 3.0:
            return 'critical'
        elif percent_change >= 25 or abs(z_score) >= 2.5:
            return 'high'
        elif percent_change >= 10 or abs(z_score) >= 2.0:
            return 'medium'
        else:
            return 'low'
    
    def _determine_severity(self, regressions: List[RegressionMetric]) -> str:
        """Determine overall severity from all regressions."""
        if not regressions:
            return 'none'
        
        severities = [r.severity for r in regressions]
        
        if 'critical' in severities:
            return 'critical'
        elif 'high' in severities:
            return 'high'
        elif 'medium' in severities:
            return 'medium'
        else:
            return 'low'
    
    def _generate_recommendations(self, regressions: List[RegressionMetric]) -> List[str]:
        """Generate recommendations based on regressions."""
        recommendations = []
        
        if not regressions:
            return recommendations
        
        # Critical regressions
        critical = [r for r in regressions if r.severity == 'critical']
        if critical:
            recommendations.append(
                f"⚠️ CRITICAL: {len(critical)} function(s) show critical regression. "
                f"Investigate immediately: {', '.join([r.function_name for r in critical[:3]])}"
            )
        
        # High regressions
        high = [r for r in regressions if r.severity == 'high']
        if high:
            recommendations.append(
                f"⚠️ HIGH: {len(high)} function(s) show high regression. "
                f"Review and optimize: {', '.join([r.function_name for r in high[:3]])}"
            )
        
        # Recommendations by type
        if any(r.percent_change > 100 for r in regressions):
            recommendations.append(
                "🔍 Some functions doubled in execution time. Check for algorithmic changes or new loops."
            )
        
        if any(r.delta > 1.0 for r in regressions):
            recommendations.append(
                "⏱️ Some functions take >1 second. Consider profiling and optimization."
            )
        
        # Positive note if few regressions
        if len(regressions) <= 2:
            recommendations.append(
                "✅ Overall good - only minor regressions detected."
            )
        
        return recommendations
    
    def _compute_statistical_summary(self, regressions: List[RegressionMetric]) -> Dict[str, Any]:
        """Compute statistical summary of regressions."""
        if not regressions:
            return {
                'total_regressions': 0,
                'average_percent_change': 0.0,
                'max_percent_change': 0.0,
                'total_time_delta': 0.0
            }
        
        percent_changes = [r.percent_change for r in regressions]
        time_deltas = [r.delta for r in regressions]
        
        return {
            'total_regressions': len(regressions),
            'average_percent_change': statistics.mean(percent_changes),
            'max_percent_change': max(percent_changes),
            'min_percent_change': min(percent_changes),
            'total_time_delta': sum(time_deltas),
            'median_percent_change': statistics.median(percent_changes),
            'stdev_percent_change': statistics.stdev(percent_changes) if len(percent_changes) > 1 else 0.0
        }


def detect_regressions(baseline_trace: Dict[str, Any],
                      current_trace: Dict[str, Any],
                      threshold: float = 0.1) -> Dict[str, Any]:
    """
    Detect performance regressions.
    
    Args:
        baseline_trace: Reference trace
        current_trace: Current trace to check
        threshold: Regression threshold (default 10%)
        
    Returns:
        Dictionary with regression detection results
    """
    detector = RegressionDetector(baseline_trace, percent_threshold=threshold)
    return detector.detect(current_trace)
