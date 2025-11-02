"""
Trace comparison and diffing module for CallFlow Tracer.

Compares two execution traces to detect performance regressions, improvements,
and identify new bottlenecks. Useful for CI/CD performance gates, A/B testing,
and release validation.

Example:
    from callflow_tracer.ai import compare_traces
    
    comparison = compare_traces(
        before_graph=baseline_trace,
        after_graph=current_trace,
        threshold=0.1  # 10% regression threshold
    )
    
    print(comparison['regressions'])  # Functions that got slower
    print(comparison['improvements'])  # Functions that got faster
    print(comparison['new_bottlenecks'])  # New performance issues
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import json
from datetime import datetime


@dataclass
class NodeComparison:
    """Comparison result for a single node/function."""
    name: str
    module: str
    before_time: float
    after_time: float
    time_delta: float
    percent_change: float
    call_count_before: int
    call_count_after: int
    call_count_delta: int
    status: str  # 'regression', 'improvement', 'stable', 'new', 'removed'
    severity: str  # 'critical', 'high', 'medium', 'low'


@dataclass
class ComparisonResult:
    """Complete comparison result between two traces."""
    timestamp: str
    before_total_time: float
    after_total_time: float
    overall_delta: float
    overall_percent_change: float
    regressions: List[NodeComparison]
    improvements: List[NodeComparison]
    stable: List[NodeComparison]
    new_functions: List[NodeComparison]
    removed_functions: List[NodeComparison]
    new_bottlenecks: List[NodeComparison]
    critical_regressions: List[NodeComparison]
    summary: Dict[str, Any]


class TraceComparator:
    """Compare two execution traces to detect performance changes."""
    
    def __init__(self, regression_threshold: float = 0.1, 
                 improvement_threshold: float = 0.1):
        """
        Initialize the trace comparator.
        
        Args:
            regression_threshold: Percentage threshold for regression (default 10%)
            improvement_threshold: Percentage threshold for improvement (default 10%)
        """
        self.regression_threshold = regression_threshold
        self.improvement_threshold = improvement_threshold
    
    def compare(self, before_graph: Dict[str, Any], 
                after_graph: Dict[str, Any]) -> ComparisonResult:
        """
        Compare two execution traces.
        
        Args:
            before_graph: Baseline trace graph
            after_graph: Current trace graph
            
        Returns:
            ComparisonResult with detailed comparison data
        """
        before_nodes = self._extract_nodes(before_graph)
        after_nodes = self._extract_nodes(after_graph)
        
        before_total = self._get_total_time(before_graph)
        after_total = self._get_total_time(after_graph)
        
        regressions = []
        improvements = []
        stable = []
        new_functions = []
        removed_functions = []
        new_bottlenecks = []
        critical_regressions = []
        
        # Compare common functions
        for node_key, before_node in before_nodes.items():
            if node_key in after_nodes:
                after_node = after_nodes[node_key]
                comparison = self._compare_nodes(before_node, after_node)
                
                if comparison.status == 'regression':
                    regressions.append(comparison)
                    if comparison.severity == 'critical':
                        critical_regressions.append(comparison)
                elif comparison.status == 'improvement':
                    improvements.append(comparison)
                else:
                    stable.append(comparison)
            else:
                # Function was removed
                removed_node = NodeComparison(
                    name=before_node.get('name', 'unknown'),
                    module=before_node.get('module', 'unknown'),
                    before_time=before_node.get('total_time', 0),
                    after_time=0,
                    time_delta=-before_node.get('total_time', 0),
                    percent_change=-100.0,
                    call_count_before=before_node.get('call_count', 0),
                    call_count_after=0,
                    call_count_delta=-before_node.get('call_count', 0),
                    status='removed',
                    severity='low'
                )
                removed_functions.append(removed_node)
        
        # Find new functions
        for node_key, after_node in after_nodes.items():
            if node_key not in before_nodes:
                new_node = NodeComparison(
                    name=after_node.get('name', 'unknown'),
                    module=after_node.get('module', 'unknown'),
                    before_time=0,
                    after_time=after_node.get('total_time', 0),
                    time_delta=after_node.get('total_time', 0),
                    percent_change=100.0,
                    call_count_before=0,
                    call_count_after=after_node.get('call_count', 0),
                    call_count_delta=after_node.get('call_count', 0),
                    status='new',
                    severity='medium' if after_node.get('total_time', 0) > 0.1 else 'low'
                )
                new_functions.append(new_node)
        
        # Identify new bottlenecks (functions that are now slow)
        new_bottlenecks = self._identify_new_bottlenecks(
            before_nodes, after_nodes, regressions
        )
        
        # Sort by impact
        regressions.sort(key=lambda x: abs(x.time_delta), reverse=True)
        improvements.sort(key=lambda x: abs(x.time_delta), reverse=True)
        new_bottlenecks.sort(key=lambda x: x.after_time, reverse=True)
        
        summary = {
            'total_regressions': len(regressions),
            'total_improvements': len(improvements),
            'total_stable': len(stable),
            'new_functions': len(new_functions),
            'removed_functions': len(removed_functions),
            'new_bottlenecks': len(new_bottlenecks),
            'critical_regressions': len(critical_regressions),
            'overall_status': self._determine_overall_status(
                regressions, improvements, after_total, before_total
            )
        }
        
        return ComparisonResult(
            timestamp=datetime.now().isoformat(),
            before_total_time=before_total,
            after_total_time=after_total,
            overall_delta=after_total - before_total,
            overall_percent_change=(after_total - before_total) / before_total * 100 if before_total > 0 else 0,
            regressions=regressions,
            improvements=improvements,
            stable=stable,
            new_functions=new_functions,
            removed_functions=removed_functions,
            new_bottlenecks=new_bottlenecks,
            critical_regressions=critical_regressions,
            summary=summary
        )
    
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
    
    def _get_total_time(self, graph: Dict[str, Any]) -> float:
        """Get total execution time from graph."""
        if isinstance(graph, dict):
            if 'total_time' in graph:
                return graph['total_time']
            elif 'data' in graph and 'total_time' in graph['data']:
                return graph['data']['total_time']
        return 0.0
    
    def _compare_nodes(self, before_node: Dict[str, Any], 
                       after_node: Dict[str, Any]) -> NodeComparison:
        """Compare two nodes and determine status."""
        before_time = before_node.get('total_time', 0)
        after_time = after_node.get('total_time', 0)
        time_delta = after_time - before_time
        percent_change = (time_delta / before_time * 100) if before_time > 0 else 0
        
        # Determine status
        if percent_change >= self.regression_threshold * 100:
            status = 'regression'
        elif percent_change <= -self.improvement_threshold * 100:
            status = 'improvement'
        else:
            status = 'stable'
        
        # Determine severity
        if status == 'regression':
            if percent_change >= 50:
                severity = 'critical'
            elif percent_change >= 25:
                severity = 'high'
            elif percent_change >= 10:
                severity = 'medium'
            else:
                severity = 'low'
        else:
            severity = 'low'
        
        return NodeComparison(
            name=before_node.get('name', 'unknown'),
            module=before_node.get('module', 'unknown'),
            before_time=before_time,
            after_time=after_time,
            time_delta=time_delta,
            percent_change=percent_change,
            call_count_before=before_node.get('call_count', 0),
            call_count_after=after_node.get('call_count', 0),
            call_count_delta=after_node.get('call_count', 0) - before_node.get('call_count', 0),
            status=status,
            severity=severity
        )
    
    def _identify_new_bottlenecks(self, before_nodes: Dict[str, Dict[str, Any]],
                                  after_nodes: Dict[str, Dict[str, Any]],
                                  regressions: List[NodeComparison]) -> List[NodeComparison]:
        """Identify functions that became bottlenecks."""
        bottlenecks = []
        
        # Get top functions by time in after_graph
        after_sorted = sorted(
            after_nodes.items(),
            key=lambda x: x[1].get('total_time', 0),
            reverse=True
        )
        
        # Check top 10% for new bottlenecks
        top_count = max(1, len(after_sorted) // 10)
        
        for node_key, after_node in after_sorted[:top_count]:
            if node_key in before_nodes:
                before_node = before_nodes[node_key]
                before_time = before_node.get('total_time', 0)
                after_time = after_node.get('total_time', 0)
                
                # Check if this was not a bottleneck before but is now
                if before_time < 0.05 and after_time > 0.1:
                    bottleneck = NodeComparison(
                        name=after_node.get('name', 'unknown'),
                        module=after_node.get('module', 'unknown'),
                        before_time=before_time,
                        after_time=after_time,
                        time_delta=after_time - before_time,
                        percent_change=(after_time - before_time) / before_time * 100 if before_time > 0 else 100,
                        call_count_before=before_node.get('call_count', 0),
                        call_count_after=after_node.get('call_count', 0),
                        call_count_delta=after_node.get('call_count', 0) - before_node.get('call_count', 0),
                        status='new_bottleneck',
                        severity='high'
                    )
                    bottlenecks.append(bottleneck)
        
        return bottlenecks
    
    def _determine_overall_status(self, regressions: List[NodeComparison],
                                 improvements: List[NodeComparison],
                                 after_total: float,
                                 before_total: float) -> str:
        """Determine overall comparison status."""
        if len(regressions) == 0:
            return 'improved'
        elif len(improvements) > len(regressions):
            return 'mixed_positive'
        elif len(improvements) < len(regressions):
            return 'mixed_negative'
        else:
            return 'mixed'


def compare_traces(before_graph: Dict[str, Any], 
                  after_graph: Dict[str, Any],
                  threshold: float = 0.1) -> Dict[str, Any]:
    """
    Compare two execution traces.
    
    Args:
        before_graph: Baseline trace graph
        after_graph: Current trace graph
        threshold: Regression threshold (default 10%)
        
    Returns:
        Dictionary with comparison results
    """
    comparator = TraceComparator(regression_threshold=threshold)
    result = comparator.compare(before_graph, after_graph)
    
    return {
        'timestamp': result.timestamp,
        'before_total_time': result.before_total_time,
        'after_total_time': result.after_total_time,
        'overall_delta': result.overall_delta,
        'overall_percent_change': result.overall_percent_change,
        'regressions': [asdict(r) for r in result.regressions],
        'improvements': [asdict(i) for i in result.improvements],
        'stable': [asdict(s) for s in result.stable],
        'new_functions': [asdict(n) for n in result.new_functions],
        'removed_functions': [asdict(r) for r in result.removed_functions],
        'new_bottlenecks': [asdict(b) for b in result.new_bottlenecks],
        'critical_regressions': [asdict(c) for c in result.critical_regressions],
        'summary': result.summary
    }
