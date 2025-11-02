"""
Load testing insights module for CallFlow Tracer.

Analyze behavior under load and predict capacity limits.
Provides scaling recommendations based on load test results.

Example:
    from callflow_tracer.ai import analyze_load_behavior
    
    load_analysis = analyze_load_behavior(
        traces=load_test_traces,
        concurrent_users=[10, 50, 100, 500]
    )
    
    print(load_analysis['bottlenecks_under_load'])
    print(load_analysis['breaking_point'])
    print(load_analysis['scaling_recommendations'])
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import statistics


@dataclass
class LoadTestResult:
    """Result for a load test at specific concurrency."""
    concurrent_users: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    p95_response_time: float
    p99_response_time: float
    max_response_time: float
    throughput: float  # requests per second
    error_rate: float


@dataclass
class LoadAnalysis:
    """Complete load analysis."""
    timestamp: str
    test_results: List[LoadTestResult]
    bottlenecks_under_load: List[Dict[str, Any]]
    breaking_point: Dict[str, Any]
    scaling_recommendations: List[str]
    capacity_forecast: Dict[str, Any]


class LoadAnalyzer:
    """Analyze load testing results."""
    
    def __init__(self):
        """Initialize load analyzer."""
        pass
    
    def analyze(self, traces: List[Dict[str, Any]],
               concurrent_users: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Analyze load test results.
        
        Args:
            traces: List of execution traces from load test
            concurrent_users: List of concurrency levels tested
            
        Returns:
            Load analysis results
        """
        if concurrent_users is None:
            concurrent_users = [10, 50, 100, 500]
        
        # Group traces by load level
        test_results = []
        
        # Simulate load test results from traces
        # In real scenario, traces would be tagged with load level
        for load_level in concurrent_users:
            result = self._analyze_load_level(traces, load_level)
            test_results.append(result)
        
        # Find bottlenecks
        bottlenecks = self._find_bottlenecks_under_load(traces, test_results)
        
        # Find breaking point
        breaking_point = self._find_breaking_point(test_results)
        
        # Generate recommendations
        recommendations = self._generate_scaling_recommendations(test_results, breaking_point)
        
        # Forecast capacity
        capacity = self._forecast_capacity(test_results)
        
        analysis = LoadAnalysis(
            timestamp=datetime.now().isoformat(),
            test_results=test_results,
            bottlenecks_under_load=bottlenecks,
            breaking_point=breaking_point,
            scaling_recommendations=recommendations,
            capacity_forecast=capacity
        )
        
        return {
            'timestamp': analysis.timestamp,
            'test_results': [asdict(r) for r in analysis.test_results],
            'bottlenecks_under_load': analysis.bottlenecks_under_load,
            'breaking_point': analysis.breaking_point,
            'scaling_recommendations': analysis.scaling_recommendations,
            'capacity_forecast': analysis.capacity_forecast
        }
    
    def _analyze_load_level(self, traces: List[Dict[str, Any]],
                           concurrent_users: int) -> LoadTestResult:
        """Analyze results at specific load level."""
        if not traces:
            return LoadTestResult(
                concurrent_users=concurrent_users,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                average_response_time=0,
                p95_response_time=0,
                p99_response_time=0,
                max_response_time=0,
                throughput=0,
                error_rate=0
            )
        
        # Extract response times
        response_times = []
        for trace in traces:
            total_time = self._get_total_time(trace)
            response_times.append(total_time)
        
        # Calculate statistics
        avg_time = statistics.mean(response_times)
        sorted_times = sorted(response_times)
        
        p95_idx = int(len(sorted_times) * 0.95)
        p99_idx = int(len(sorted_times) * 0.99)
        
        p95_time = sorted_times[p95_idx] if p95_idx < len(sorted_times) else sorted_times[-1]
        p99_time = sorted_times[p99_idx] if p99_idx < len(sorted_times) else sorted_times[-1]
        max_time = max(response_times)
        
        # Estimate throughput (requests per second)
        total_duration = sum(response_times)
        throughput = len(response_times) / total_duration if total_duration > 0 else 0
        
        # Simulate error rate (in real scenario, would track actual errors)
        error_rate = 0.0 if avg_time < 2.0 else (avg_time - 2.0) * 0.1
        
        return LoadTestResult(
            concurrent_users=concurrent_users,
            total_requests=len(traces),
            successful_requests=len(traces),
            failed_requests=0,
            average_response_time=avg_time,
            p95_response_time=p95_time,
            p99_response_time=p99_time,
            max_response_time=max_time,
            throughput=throughput,
            error_rate=error_rate
        )
    
    def _find_bottlenecks_under_load(self, traces: List[Dict[str, Any]],
                                    test_results: List[LoadTestResult]) -> List[Dict[str, Any]]:
        """Find bottlenecks that appear under load."""
        bottlenecks = []
        
        # Extract all functions from traces
        all_nodes = {}
        for trace in traces:
            nodes = self._extract_nodes(trace)
            for node_key, node in nodes.items():
                if node_key not in all_nodes:
                    all_nodes[node_key] = []
                all_nodes[node_key].append(node.get('total_time', 0))
        
        # Find functions that degrade under load
        for node_key, times in all_nodes.items():
            if len(times) > 1:
                avg_time = statistics.mean(times)
                max_time = max(times)
                
                # If max time is significantly higher than average, it's a bottleneck
                if max_time > avg_time * 2:
                    func_name = node_key.split(':')[-1]
                    bottlenecks.append({
                        'function': func_name,
                        'average_time': avg_time,
                        'max_time': max_time,
                        'degradation': (max_time - avg_time) / avg_time * 100,
                        'severity': 'high' if max_time > 1.0 else 'medium'
                    })
        
        # Sort by degradation
        bottlenecks.sort(key=lambda x: x['degradation'], reverse=True)
        
        return bottlenecks[:10]
    
    def _find_breaking_point(self, test_results: List[LoadTestResult]) -> Dict[str, Any]:
        """Find the breaking point where system starts failing."""
        breaking_point = None
        
        for result in test_results:
            if result.error_rate > 0.05 or result.average_response_time > 5.0:
                breaking_point = {
                    'concurrent_users': result.concurrent_users,
                    'average_response_time': result.average_response_time,
                    'error_rate': result.error_rate,
                    'throughput': result.throughput,
                    'reason': 'High error rate' if result.error_rate > 0.05 else 'High response time'
                }
                break
        
        if breaking_point is None:
            # No breaking point found, estimate based on trend
            if test_results:
                last_result = test_results[-1]
                breaking_point = {
                    'concurrent_users': last_result.concurrent_users * 2,
                    'estimated': True,
                    'reason': 'Extrapolated from trend'
                }
        
        return breaking_point or {}
    
    def _generate_scaling_recommendations(self, test_results: List[LoadTestResult],
                                         breaking_point: Dict[str, Any]) -> List[str]:
        """Generate scaling recommendations."""
        recommendations = []
        
        if not test_results:
            return recommendations
        
        # Check response time trend
        response_times = [r.average_response_time for r in test_results]
        
        if response_times[-1] > response_times[0] * 2:
            recommendations.append(
                "⚠️ Response time degradation detected. Consider horizontal scaling or optimization."
            )
        
        # Check throughput
        throughputs = [r.throughput for r in test_results]
        if throughputs[-1] < throughputs[0] * 0.5:
            recommendations.append(
                "📉 Throughput declining under load. Investigate bottlenecks and optimize."
            )
        
        # Check error rate
        error_rates = [r.error_rate for r in test_results]
        if error_rates[-1] > 0.01:
            recommendations.append(
                "🔴 Errors detected under load. Implement circuit breakers and retry logic."
            )
        
        # Breaking point
        if breaking_point and 'concurrent_users' in breaking_point:
            safe_capacity = breaking_point['concurrent_users'] * 0.7
            recommendations.append(
                f"📊 Safe capacity: ~{int(safe_capacity)} concurrent users. "
                f"Breaking point at {breaking_point['concurrent_users']} users."
            )
        
        # General recommendations
        if not recommendations:
            recommendations.append(
                "✅ System handles load well. Monitor for any degradation."
            )
        
        return recommendations
    
    def _forecast_capacity(self, test_results: List[LoadTestResult]) -> Dict[str, Any]:
        """Forecast capacity based on test results."""
        if len(test_results) < 2:
            return {}
        
        # Simple linear extrapolation
        x = [r.concurrent_users for r in test_results]
        y = [r.average_response_time for r in test_results]
        
        # Calculate slope
        slope = (y[-1] - y[0]) / (x[-1] - x[0]) if x[-1] != x[0] else 0
        
        # Forecast when response time reaches 5 seconds (unacceptable)
        if slope > 0:
            forecast_users = x[-1] + (5.0 - y[-1]) / slope
        else:
            forecast_users = x[-1] * 10
        
        return {
            'estimated_max_concurrent_users': int(forecast_users),
            'estimated_max_response_time': 5.0,
            'confidence': 'medium' if len(test_results) >= 3 else 'low',
            'based_on_tests': len(test_results)
        }
    
    def _extract_nodes(self, graph: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Extract nodes from graph."""
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
        """Get total time from graph."""
        if isinstance(graph, dict):
            if 'total_time' in graph:
                return graph['total_time']
            elif 'data' in graph and 'total_time' in graph['data']:
                return graph['data']['total_time']
        return 0.0


def analyze_load_behavior(traces: List[Dict[str, Any]],
                         concurrent_users: Optional[List[int]] = None) -> Dict[str, Any]:
    """
    Analyze load test behavior.
    
    Args:
        traces: List of execution traces
        concurrent_users: List of concurrency levels
        
    Returns:
        Load analysis results
    """
    analyzer = LoadAnalyzer()
    return analyzer.analyze(traces, concurrent_users)
