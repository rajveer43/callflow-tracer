"""
Trend analysis and forecasting module for CallFlow Tracer.

Track performance trends over time and predict future issues.
Provides statistical analysis and anomaly detection.

Example:
    from callflow_tracer.ai import TrendAnalyzer
    
    analyzer = TrendAnalyzer()
    
    for trace in historical_traces:
        analyzer.add_trace(trace, timestamp=trace.timestamp)
    
    trends = analyzer.analyze_trends()
    
    print(trends['degrading_functions'])
    print(trends['forecast'])
    print(trends['anomaly_frequency'])
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import statistics
from collections import defaultdict


@dataclass
class FunctionTrend:
    """Trend for a single function."""
    function_name: str
    module: str
    measurements: List[Tuple[str, float]]  # (timestamp, value)
    trend_direction: str  # 'improving', 'degrading', 'stable'
    trend_strength: float  # 0.0 to 1.0
    forecast_value: float
    forecast_confidence: float
    anomaly_count: int


@dataclass
class TrendAnalysisResult:
    """Complete trend analysis result."""
    timestamp: str
    analysis_period: str
    total_traces: int
    degrading_functions: List[FunctionTrend]
    improving_functions: List[FunctionTrend]
    stable_functions: List[FunctionTrend]
    forecast: Dict[str, Any]
    anomaly_frequency: Dict[str, float]
    recommendations: List[str]


class TrendAnalyzer:
    """Analyze performance trends over time."""
    
    def __init__(self, window_size: int = 10):
        """
        Initialize trend analyzer.
        
        Args:
            window_size: Number of traces to use for trend calculation
        """
        self.window_size = window_size
        self.traces: List[Dict[str, Any]] = []
        self.function_history: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
    
    def add_trace(self, graph: Dict[str, Any], timestamp: Optional[str] = None) -> None:
        """
        Add a trace to the analyzer.
        
        Args:
            graph: Execution trace graph
            timestamp: Optional timestamp (uses current time if not provided)
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        self.traces.append(graph)
        
        # Extract function times
        nodes = self._extract_nodes(graph)
        for node_key, node in nodes.items():
            total_time = node.get('total_time', 0)
            self.function_history[node_key].append((timestamp, total_time))
    
    def analyze_trends(self) -> Dict[str, Any]:
        """
        Analyze trends in collected traces.
        
        Returns:
            Trend analysis results
        """
        if len(self.traces) < 2:
            return {
                'error': 'Not enough traces for trend analysis',
                'traces_collected': len(self.traces)
            }
        
        degrading = []
        improving = []
        stable = []
        
        # Analyze each function
        for func_key, measurements in self.function_history.items():
            if len(measurements) < 2:
                continue
            
            trend = self._analyze_function_trend(func_key, measurements)
            
            if trend.trend_direction == 'degrading':
                degrading.append(trend)
            elif trend.trend_direction == 'improving':
                improving.append(trend)
            else:
                stable.append(trend)
        
        # Sort by trend strength
        degrading.sort(key=lambda x: x.trend_strength, reverse=True)
        improving.sort(key=lambda x: x.trend_strength, reverse=True)
        
        # Generate forecast
        forecast = self._generate_forecast(degrading, improving)
        
        # Analyze anomaly frequency
        anomaly_freq = self._analyze_anomaly_frequency()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(degrading, improving, forecast)
        
        analysis = TrendAnalysisResult(
            timestamp=datetime.now().isoformat(),
            analysis_period=f"{len(self.traces)} traces",
            total_traces=len(self.traces),
            degrading_functions=degrading[:10],
            improving_functions=improving[:10],
            stable_functions=stable[:10],
            forecast=forecast,
            anomaly_frequency=anomaly_freq,
            recommendations=recommendations
        )
        
        return {
            'timestamp': analysis.timestamp,
            'analysis_period': analysis.analysis_period,
            'total_traces': analysis.total_traces,
            'degrading_functions': [asdict(f) for f in analysis.degrading_functions],
            'improving_functions': [asdict(f) for f in analysis.improving_functions],
            'stable_functions': [asdict(f) for f in analysis.stable_functions],
            'forecast': analysis.forecast,
            'anomaly_frequency': analysis.anomaly_frequency,
            'recommendations': analysis.recommendations
        }
    
    def _analyze_function_trend(self, func_key: str,
                               measurements: List[Tuple[str, float]]) -> FunctionTrend:
        """Analyze trend for a single function."""
        func_name = func_key.split(':')[-1]
        module = func_key.split(':')[0]
        
        # Extract values
        values = [v for _, v in measurements[-self.window_size:]]
        
        if len(values) < 2:
            return FunctionTrend(
                function_name=func_name,
                module=module,
                measurements=measurements,
                trend_direction='stable',
                trend_strength=0.0,
                forecast_value=values[-1] if values else 0,
                forecast_confidence=0.0,
                anomaly_count=0
            )
        
        # Calculate trend using linear regression
        trend_direction, trend_strength = self._calculate_trend(values)
        
        # Forecast next value
        forecast_value = self._forecast_next_value(values)
        forecast_confidence = self._calculate_forecast_confidence(values)
        
        # Count anomalies
        anomaly_count = self._count_anomalies(values)
        
        return FunctionTrend(
            function_name=func_name,
            module=module,
            measurements=measurements[-self.window_size:],
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            forecast_value=forecast_value,
            forecast_confidence=forecast_confidence,
            anomaly_count=anomaly_count
        )
    
    def _calculate_trend(self, values: List[float]) -> Tuple[str, float]:
        """Calculate trend direction and strength."""
        if len(values) < 2:
            return 'stable', 0.0
        
        # Simple linear regression
        n = len(values)
        x = list(range(n))
        y = values
        
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 'stable', 0.0
        
        slope = numerator / denominator
        
        # Determine direction
        if slope > 0.01:
            direction = 'degrading'
        elif slope < -0.01:
            direction = 'improving'
        else:
            direction = 'stable'
        
        # Calculate strength (R-squared)
        ss_res = sum((y[i] - (slope * x[i] + (y_mean - slope * x_mean))) ** 2 for i in range(n))
        ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))
        
        if ss_tot == 0:
            strength = 0.0
        else:
            strength = 1 - (ss_res / ss_tot)
            strength = max(0.0, min(1.0, strength))
        
        return direction, strength
    
    def _forecast_next_value(self, values: List[float]) -> float:
        """Forecast next value using exponential smoothing."""
        if not values:
            return 0.0
        
        if len(values) == 1:
            return values[0]
        
        # Simple exponential smoothing
        alpha = 0.3
        forecast = values[0]
        
        for value in values[1:]:
            forecast = alpha * value + (1 - alpha) * forecast
        
        return forecast
    
    def _calculate_forecast_confidence(self, values: List[float]) -> float:
        """Calculate confidence in forecast."""
        if len(values) < 2:
            return 0.0
        
        # Confidence based on consistency (inverse of coefficient of variation)
        mean = statistics.mean(values)
        if mean == 0:
            return 0.0
        
        stdev = statistics.stdev(values) if len(values) > 1 else 0
        cv = stdev / mean if mean != 0 else 0
        
        # Lower CV = higher confidence
        confidence = max(0.0, 1.0 - cv)
        return min(1.0, confidence)
    
    def _count_anomalies(self, values: List[float]) -> int:
        """Count anomalies in values."""
        if len(values) < 3:
            return 0
        
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)
        
        if stdev == 0:
            return 0
        
        anomalies = 0
        for value in values:
            z_score = abs((value - mean) / stdev)
            if z_score > 2.0:
                anomalies += 1
        
        return anomalies
    
    def _generate_forecast(self, degrading: List[FunctionTrend],
                          improving: List[FunctionTrend]) -> Dict[str, Any]:
        """Generate forecast."""
        forecast = {
            'degrading_functions_forecast': [],
            'improving_functions_forecast': [],
            'predicted_critical_functions': []
        }
        
        # Forecast degrading functions
        for func in degrading[:5]:
            forecast['degrading_functions_forecast'].append({
                'function': func.function_name,
                'current_value': func.measurements[-1][1] if func.measurements else 0,
                'forecast_value': func.forecast_value,
                'forecast_confidence': func.forecast_confidence,
                'days_to_critical': self._estimate_days_to_critical(func)
            })
        
        # Identify functions that might become critical
        for func in degrading[:3]:
            if func.forecast_value > 1.0:  # Might exceed 1 second
                forecast['predicted_critical_functions'].append({
                    'function': func.function_name,
                    'estimated_time': func.forecast_value,
                    'risk_level': 'high'
                })
        
        return forecast
    
    def _estimate_days_to_critical(self, trend: FunctionTrend) -> float:
        """Estimate days until function becomes critical."""
        if not trend.measurements or len(trend.measurements) < 2:
            return float('inf')
        
        values = [v for _, v in trend.measurements]
        
        # Simple linear extrapolation
        if len(values) < 2:
            return float('inf')
        
        slope = (values[-1] - values[0]) / len(values)
        
        if slope <= 0:
            return float('inf')
        
        # Days until 1 second
        days_to_critical = (1.0 - values[-1]) / (slope * len(self.traces))
        
        return max(0, days_to_critical)
    
    def _analyze_anomaly_frequency(self) -> Dict[str, float]:
        """Analyze frequency of anomalies."""
        anomaly_freq = {}
        
        for func_key, measurements in self.function_history.items():
            if len(measurements) < 3:
                continue
            
            values = [v for _, v in measurements]
            anomaly_count = self._count_anomalies(values)
            frequency = anomaly_count / len(values) if values else 0
            
            if frequency > 0:
                anomaly_freq[func_key] = frequency
        
        return anomaly_freq
    
    def _generate_recommendations(self, degrading: List[FunctionTrend],
                                 improving: List[FunctionTrend],
                                 forecast: Dict[str, Any]) -> List[str]:
        """Generate recommendations."""
        recommendations = []
        
        if degrading:
            recommendations.append(
                f"⚠️ {len(degrading)} function(s) showing performance degradation. "
                f"Top concern: {degrading[0].function_name}"
            )
        
        if improving:
            recommendations.append(
                f"✅ {len(improving)} function(s) showing performance improvement."
            )
        
        critical_funcs = forecast.get('predicted_critical_functions', [])
        if critical_funcs:
            recommendations.append(
                f"🔴 {len(critical_funcs)} function(s) predicted to become critical. "
                f"Investigate: {critical_funcs[0]['function']}"
            )
        
        if not degrading and not improving:
            recommendations.append("✅ Performance is stable across all functions.")
        
        return recommendations
    
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


def analyze_trends(analyzer: 'TrendAnalyzer') -> Dict[str, Any]:
    """
    Analyze trends from collected traces.
    
    Args:
        analyzer: TrendAnalyzer instance
        
    Returns:
        Trend analysis results
    """
    return analyzer.analyze_trends()
