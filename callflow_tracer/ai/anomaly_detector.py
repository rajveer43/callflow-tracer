"""
Anomaly Detection for CallFlow Tracer.

Uses statistical analysis to detect anomalies in execution patterns.
Helps proactively identify performance issues before they become critical.
"""

from typing import Dict, List, Optional, Any, Tuple
import statistics
from collections import defaultdict
import math


class AnomalyDetector:
    """
    Detects anomalies in execution traces using statistical analysis.
    
    Identifies unusual patterns in:
    - Execution time
    - Call frequency
    - Memory usage (if available)
    - Call patterns
    """
    
    def __init__(self, baseline_graphs: Optional[List] = None, sensitivity: float = 2.0):
        """
        Initialize anomaly detector.
        
        Args:
            baseline_graphs: Optional list of baseline CallGraphs for comparison
            sensitivity: Sensitivity threshold (std deviations), default 2.0
        """
        self.baseline_graphs = baseline_graphs or []
        self.sensitivity = sensitivity
        self.baseline_stats = None
        
        if self.baseline_graphs:
            self._compute_baseline_stats()
    
    def detect(self, graph, detect_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Detect anomalies in a call graph.
        
        Args:
            graph: CallGraph to analyze
            detect_types: Types of anomalies to detect
                         ['time', 'frequency', 'pattern', 'outlier']
        
        Returns:
            Dict with detected anomalies and analysis
        """
        if detect_types is None:
            detect_types = ['time', 'frequency', 'pattern', 'outlier']
        
        # Extract data
        nodes = self._extract_nodes(graph)
        edges = self._extract_edges(graph)
        
        anomalies = {
            'time_anomalies': [],
            'frequency_anomalies': [],
            'pattern_anomalies': [],
            'outlier_anomalies': [],
            'severity_summary': {}
        }
        
        # Detect different types of anomalies
        if 'time' in detect_types:
            anomalies['time_anomalies'] = self._detect_time_anomalies(nodes)
        
        if 'frequency' in detect_types:
            anomalies['frequency_anomalies'] = self._detect_frequency_anomalies(nodes)
        
        if 'pattern' in detect_types:
            anomalies['pattern_anomalies'] = self._detect_pattern_anomalies(nodes, edges)
        
        if 'outlier' in detect_types:
            anomalies['outlier_anomalies'] = self._detect_statistical_outliers(nodes)
        
        # Calculate severity
        anomalies['severity_summary'] = self._calculate_severity(anomalies)
        
        # Add recommendations
        anomalies['recommendations'] = self._generate_recommendations(anomalies)
        
        return anomalies
    
    def add_baseline(self, graph):
        """Add a graph to the baseline for comparison."""
        self.baseline_graphs.append(graph)
        self._compute_baseline_stats()
    
    def _extract_nodes(self, graph) -> Dict[str, Dict[str, Any]]:
        """Extract node information from graph."""
        nodes = {}
        for node_id, node in graph.nodes.items():
            nodes[node_id] = {
                'id': node_id,
                'function': node.name,
                'module': node.module,
                'total_time': node.total_time,
                'self_time': node.total_time,  # CallNode doesn't have self_time, use total_time
                'call_count': node.call_count,
                'avg_time': node.total_time / node.call_count if node.call_count > 0 else 0
            }
        return nodes
    
    def _extract_edges(self, graph) -> List[Tuple[str, str]]:
        """Extract edges (caller -> callee relationships)."""
        edges = []
        for (caller, callee), edge in graph.edges.items():
            edges.append((caller, callee))
        return edges
    
    def _compute_baseline_stats(self):
        """Compute baseline statistics from baseline graphs."""
        if not self.baseline_graphs:
            return
        
        # Aggregate stats by function name
        function_stats = defaultdict(lambda: {'times': [], 'counts': []})
        
        for graph in self.baseline_graphs:
            for node_id, node in graph.nodes.items():
                key = f"{node.module}.{node.name}"
                function_stats[key]['times'].append(node.total_time)
                function_stats[key]['counts'].append(node.call_count)
        
        # Calculate mean and std dev
        self.baseline_stats = {}
        for func, stats in function_stats.items():
            if len(stats['times']) > 1:
                self.baseline_stats[func] = {
                    'mean_time': statistics.mean(stats['times']),
                    'std_time': statistics.stdev(stats['times']),
                    'mean_count': statistics.mean(stats['counts']),
                    'std_count': statistics.stdev(stats['counts'])
                }
    
    def _detect_time_anomalies(self, nodes: Dict) -> List[Dict[str, Any]]:
        """Detect time-based anomalies."""
        anomalies = []
        
        # Calculate statistics
        times = [n['total_time'] for n in nodes.values()]
        if len(times) < 2:
            return anomalies
        
        mean_time = statistics.mean(times)
        std_time = statistics.stdev(times)
        threshold = mean_time + (self.sensitivity * std_time)
        
        for node_id, node in nodes.items():
            # Check against current distribution
            if node['total_time'] > threshold:
                z_score = (node['total_time'] - mean_time) / std_time if std_time > 0 else 0
                
                anomaly = {
                    'type': 'time',
                    'node_id': node_id,
                    'function': node['function'],
                    'module': node['module'],
                    'value': node['total_time'],
                    'expected': mean_time,
                    'deviation': node['total_time'] - mean_time,
                    'z_score': z_score,
                    'severity': self._calculate_anomaly_severity(z_score),
                    'description': f"{node['function']} took {node['total_time']:.3f}s (expected ~{mean_time:.3f}s)"
                }
                
                # Check against baseline if available
                if self.baseline_stats:
                    func_key = f"{node['module']}.{node['function']}"
                    if func_key in self.baseline_stats:
                        baseline = self.baseline_stats[func_key]
                        baseline_threshold = baseline['mean_time'] + (self.sensitivity * baseline['std_time'])
                        if node['total_time'] > baseline_threshold:
                            anomaly['baseline_deviation'] = node['total_time'] - baseline['mean_time']
                            anomaly['description'] += f" (baseline: {baseline['mean_time']:.3f}s)"
                
                anomalies.append(anomaly)
        
        return sorted(anomalies, key=lambda x: x['severity'], reverse=True)
    
    def _detect_frequency_anomalies(self, nodes: Dict) -> List[Dict[str, Any]]:
        """Detect call frequency anomalies."""
        anomalies = []
        
        counts = [n['call_count'] for n in nodes.values()]
        if len(counts) < 2:
            return anomalies
        
        mean_count = statistics.mean(counts)
        std_count = statistics.stdev(counts)
        threshold = mean_count + (self.sensitivity * std_count)
        
        for node_id, node in nodes.items():
            if node['call_count'] > threshold:
                z_score = (node['call_count'] - mean_count) / std_count if std_count > 0 else 0
                
                anomalies.append({
                    'type': 'frequency',
                    'node_id': node_id,
                    'function': node['function'],
                    'module': node['module'],
                    'value': node['call_count'],
                    'expected': mean_count,
                    'deviation': node['call_count'] - mean_count,
                    'z_score': z_score,
                    'severity': self._calculate_anomaly_severity(z_score),
                    'description': f"{node['function']} called {node['call_count']} times (expected ~{mean_count:.0f})"
                })
        
        return sorted(anomalies, key=lambda x: x['severity'], reverse=True)
    
    def _detect_pattern_anomalies(self, nodes: Dict, edges: List[Tuple]) -> List[Dict[str, Any]]:
        """Detect unusual call patterns."""
        anomalies = []
        
        # Build call pattern map
        call_patterns = defaultdict(list)
        for caller_id, callee_id in edges:
            if caller_id in nodes and callee_id in nodes:
                caller = nodes[caller_id]
                callee = nodes[callee_id]
                call_patterns[caller_id].append(callee_id)
        
        # Detect unusual patterns
        for caller_id, callees in call_patterns.items():
            caller = nodes[caller_id]
            
            # Detect excessive fan-out (calling too many functions)
            if len(callees) > 10:
                anomalies.append({
                    'type': 'pattern',
                    'subtype': 'excessive_fanout',
                    'node_id': caller_id,
                    'function': caller['function'],
                    'module': caller['module'],
                    'value': len(callees),
                    'severity': 'medium',
                    'description': f"{caller['function']} calls {len(callees)} different functions (high complexity)"
                })
            
            # Detect potential N+1 patterns
            callee_times = [nodes[c]['total_time'] for c in callees]
            if len(callee_times) > 3:
                # Check if callees have similar execution times (potential N+1)
                if len(set(round(t, 3) for t in callee_times)) == 1:
                    anomalies.append({
                        'type': 'pattern',
                        'subtype': 'n_plus_one',
                        'node_id': caller_id,
                        'function': caller['function'],
                        'module': caller['module'],
                        'value': len(callees),
                        'severity': 'high',
                        'description': f"Potential N+1 pattern: {caller['function']} makes {len(callees)} similar calls"
                    })
        
        return anomalies
    
    def _detect_statistical_outliers(self, nodes: Dict) -> List[Dict[str, Any]]:
        """Detect statistical outliers using IQR method."""
        anomalies = []
        
        # Collect metrics
        times = sorted([n['total_time'] for n in nodes.values()])
        counts = sorted([n['call_count'] for n in nodes.values()])
        
        if len(times) < 4:
            return anomalies
        
        # Calculate IQR for times
        q1_time = times[len(times) // 4]
        q3_time = times[3 * len(times) // 4]
        iqr_time = q3_time - q1_time
        time_outlier_threshold = q3_time + (1.5 * iqr_time)
        
        # Calculate IQR for counts
        q1_count = counts[len(counts) // 4]
        q3_count = counts[3 * len(counts) // 4]
        iqr_count = q3_count - q1_count
        count_outlier_threshold = q3_count + (1.5 * iqr_count)
        
        for node_id, node in nodes.items():
            # Time outliers
            if node['total_time'] > time_outlier_threshold:
                anomalies.append({
                    'type': 'outlier',
                    'subtype': 'time',
                    'node_id': node_id,
                    'function': node['function'],
                    'module': node['module'],
                    'value': node['total_time'],
                    'threshold': time_outlier_threshold,
                    'severity': 'high',
                    'description': f"{node['function']} is a time outlier ({node['total_time']:.3f}s)"
                })
            
            # Frequency outliers
            if node['call_count'] > count_outlier_threshold:
                anomalies.append({
                    'type': 'outlier',
                    'subtype': 'frequency',
                    'node_id': node_id,
                    'function': node['function'],
                    'module': node['module'],
                    'value': node['call_count'],
                    'threshold': count_outlier_threshold,
                    'severity': 'medium',
                    'description': f"{node['function']} is a frequency outlier ({node['call_count']} calls)"
                })
        
        return anomalies
    
    def _calculate_anomaly_severity(self, z_score: float) -> str:
        """Calculate severity based on z-score."""
        abs_z = abs(z_score)
        if abs_z > 3:
            return 'critical'
        elif abs_z > 2.5:
            return 'high'
        elif abs_z > 2:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_severity(self, anomalies: Dict) -> Dict[str, Any]:
        """Calculate overall severity summary."""
        severity_counts = defaultdict(int)
        total_anomalies = 0
        
        for anomaly_type in ['time_anomalies', 'frequency_anomalies', 'pattern_anomalies', 'outlier_anomalies']:
            for anomaly in anomalies.get(anomaly_type, []):
                severity = anomaly.get('severity', 'low')
                severity_counts[severity] += 1
                total_anomalies += 1
        
        return {
            'total': total_anomalies,
            'critical': severity_counts['critical'],
            'high': severity_counts['high'],
            'medium': severity_counts['medium'],
            'low': severity_counts['low'],
            'overall_severity': self._determine_overall_severity(severity_counts)
        }
    
    def _determine_overall_severity(self, counts: Dict[str, int]) -> str:
        """Determine overall severity level."""
        if counts['critical'] > 0:
            return 'critical'
        elif counts['high'] > 2:
            return 'high'
        elif counts['high'] > 0 or counts['medium'] > 3:
            return 'medium'
        else:
            return 'low'
    
    def _generate_recommendations(self, anomalies: Dict) -> List[str]:
        """Generate recommendations based on detected anomalies."""
        recommendations = []
        
        # Time anomalies
        if anomalies['time_anomalies']:
            top_time = anomalies['time_anomalies'][0]
            recommendations.append(
                f"⚠️  Investigate {top_time['function']} - taking {top_time['deviation']:.3f}s longer than expected"
            )
        
        # Frequency anomalies
        if anomalies['frequency_anomalies']:
            top_freq = anomalies['frequency_anomalies'][0]
            recommendations.append(
                f"⚠️  {top_freq['function']} called {top_freq['value']} times - consider caching or batching"
            )
        
        # Pattern anomalies
        n_plus_one = [a for a in anomalies['pattern_anomalies'] if a.get('subtype') == 'n_plus_one']
        if n_plus_one:
            recommendations.append(
                f"🔥 Potential N+1 query pattern detected in {n_plus_one[0]['function']} - batch operations"
            )
        
        # Outliers
        if anomalies['outlier_anomalies']:
            recommendations.append(
                f"📊 {len(anomalies['outlier_anomalies'])} statistical outliers detected - review for optimization"
            )
        
        if not recommendations:
            recommendations.append("✅ No significant anomalies detected")
        
        return recommendations


def detect_anomalies(graph, baseline_graphs: Optional[List] = None,
                     sensitivity: float = 2.0,
                     detect_types: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Convenience function for anomaly detection.
    
    Args:
        graph: CallGraph to analyze
        baseline_graphs: Optional list of baseline graphs for comparison
        sensitivity: Sensitivity threshold (std deviations)
        detect_types: Types of anomalies to detect
    
    Returns:
        Dict with detected anomalies
    
    Example:
        >>> with trace_scope() as graph:
        ...     my_function()
        >>> anomalies = detect_anomalies(graph)
        >>> print(anomalies['severity_summary'])
    """
    detector = AnomalyDetector(baseline_graphs=baseline_graphs, sensitivity=sensitivity)
    return detector.detect(graph, detect_types=detect_types)
