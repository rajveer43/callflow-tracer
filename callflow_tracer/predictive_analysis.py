"""
Predictive Analysis Module for CallFlow Tracer.

This module provides predictive analytics for:
- Performance issue prediction
- Capacity planning
- Load testing insights
- Scalability analysis
- Resource forecasting
"""

import json
import math
import statistics
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict


@dataclass
class PerformancePrediction:
    """Prediction of future performance issues."""
    function_name: str
    module: str
    current_avg_time: float
    predicted_time: float
    confidence: float  # 0-1
    risk_level: str  # Low, Medium, High, Critical
    prediction_basis: str
    recommendations: List[str]
    
    def to_dict(self):
        return asdict(self)


@dataclass
class CapacityPrediction:
    """Capacity planning predictions."""
    metric_name: str
    current_value: float
    predicted_value: float
    prediction_date: str
    capacity_limit: float
    utilization_percent: float
    days_until_limit: int
    recommendations: List[str]
    
    def to_dict(self):
        return asdict(self)


@dataclass
class ScalabilityAnalysis:
    """Scalability analysis results."""
    function_name: str
    complexity_class: str  # O(1), O(log n), O(n), O(n log n), O(n²), etc.
    scalability_score: float  # 0-100, higher is better
    bottleneck_risk: str  # Low, Medium, High
    max_recommended_load: int
    performance_at_scale: Dict[int, float]  # load -> predicted time
    
    def to_dict(self):
        return asdict(self)


@dataclass
class ResourceForecast:
    """Resource usage forecast."""
    resource_type: str  # CPU, Memory, Disk, Network
    current_usage: float
    forecasted_usage: Dict[str, float]  # date -> usage
    peak_prediction: Tuple[str, float]  # (date, peak_value)
    trend: str  # increasing, decreasing, stable
    alert_threshold: float
    days_to_threshold: Optional[int]
    
    def to_dict(self):
        result = asdict(self)
        result['peak_prediction'] = {
            'date': self.peak_prediction[0],
            'value': self.peak_prediction[1]
        }
        return result


class PerformancePredictor:
    """Predict future performance issues based on historical data."""
    
    def __init__(self, history_file: Optional[str] = None):
        self.history_file = history_file
        self.history = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        """Load historical trace data."""
        if not self.history_file:
            return []
        
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def predict_performance_issues(self, current_trace: Dict) -> List[PerformancePrediction]:
        """Predict potential performance issues."""
        predictions = []
        
        if not self.history or len(self.history) < 3:
            return predictions
        
        # Analyze each function
        for node in current_trace.get('nodes', []):
            func_name = node['full_name']
            current_time = node['total_time']
            
            # Get historical data for this function
            historical_times = self._get_historical_times(func_name)
            
            if len(historical_times) >= 3:
                prediction = self._predict_function_performance(
                    func_name,
                    node.get('module', ''),
                    current_time,
                    historical_times
                )
                if prediction:
                    predictions.append(prediction)
        
        return sorted(predictions, key=lambda x: x.confidence, reverse=True)
    
    def _get_historical_times(self, func_name: str) -> List[float]:
        """Get historical execution times for a function."""
        times = []
        for trace in self.history:
            for node in trace.get('nodes', []):
                if node['full_name'] == func_name:
                    times.append(node['total_time'])
        return times
    
    def _predict_function_performance(self, func_name: str, module: str,
                                     current_time: float, 
                                     historical_times: List[float]) -> Optional[PerformancePrediction]:
        """Predict performance for a specific function."""
        if len(historical_times) < 3:
            return None
        
        # Calculate trend
        trend = self._calculate_trend(historical_times)
        mean_time = statistics.mean(historical_times)
        std_dev = statistics.stdev(historical_times) if len(historical_times) > 1 else 0
        
        # Predict next value using linear regression
        predicted_time = self._linear_regression_predict(historical_times)
        
        # Calculate confidence based on consistency
        confidence = self._calculate_confidence(historical_times, std_dev, mean_time)
        
        # Determine risk level
        if predicted_time > mean_time * 2:
            risk_level = "Critical"
        elif predicted_time > mean_time * 1.5:
            risk_level = "High"
        elif predicted_time > mean_time * 1.2:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        # Generate recommendations
        recommendations = []
        if trend == "increasing":
            recommendations.append("Performance is degrading over time")
            recommendations.append("Consider profiling and optimization")
        if std_dev > mean_time * 0.5:
            recommendations.append("High variance in execution time - investigate inconsistency")
        if predicted_time > current_time * 1.3:
            recommendations.append("Predicted slowdown - monitor closely")
        
        return PerformancePrediction(
            function_name=func_name,
            module=module,
            current_avg_time=current_time,
            predicted_time=predicted_time,
            confidence=confidence,
            risk_level=risk_level,
            prediction_basis=f"Based on {len(historical_times)} historical measurements",
            recommendations=recommendations
        )
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction."""
        if len(values) < 2:
            return "stable"
        
        # Simple moving average comparison
        first_half = statistics.mean(values[:len(values)//2])
        second_half = statistics.mean(values[len(values)//2:])
        
        change_percent = ((second_half - first_half) / first_half * 100) if first_half > 0 else 0
        
        if change_percent > 10:
            return "increasing"
        elif change_percent < -10:
            return "decreasing"
        else:
            return "stable"
    
    def _linear_regression_predict(self, values: List[float]) -> float:
        """Predict next value using linear regression."""
        n = len(values)
        x = list(range(n))
        
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return y_mean
        
        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        
        # Predict next value
        next_x = n
        return max(0, slope * next_x + intercept)
    
    def _calculate_confidence(self, values: List[float], std_dev: float, mean: float) -> float:
        """Calculate prediction confidence (0-1)."""
        if mean == 0:
            return 0.5
        
        # Coefficient of variation
        cv = std_dev / mean if mean > 0 else 1
        
        # Lower CV = higher confidence
        # More data points = higher confidence
        data_confidence = min(len(values) / 10, 1.0)
        consistency_confidence = max(0, 1 - cv)
        
        return (data_confidence + consistency_confidence) / 2


class CapacityPlanner:
    """Perform capacity planning based on trends."""
    
    def __init__(self):
        self.forecasts = []
    
    def predict_capacity(self, metric_history: List[Tuple[datetime, float]],
                        capacity_limit: float,
                        metric_name: str = "requests") -> CapacityPrediction:
        """Predict when capacity limit will be reached."""
        if len(metric_history) < 2:
            return None
        
        # Extract values and calculate trend
        dates = [d for d, _ in metric_history]
        values = [v for _, v in metric_history]
        
        current_value = values[-1]
        
        # Predict future value using exponential smoothing
        predicted_value = self._exponential_smoothing(values, alpha=0.3)
        
        # Calculate growth rate
        growth_rate = self._calculate_growth_rate(values)
        
        # Predict when limit will be reached
        days_until_limit = self._predict_days_to_limit(
            current_value, predicted_value, capacity_limit, growth_rate
        )
        
        # Calculate utilization
        utilization = (current_value / capacity_limit * 100) if capacity_limit > 0 else 0
        
        # Generate recommendations
        recommendations = []
        if utilization > 80:
            recommendations.append("Critical: Capacity utilization above 80%")
            recommendations.append("Immediate action required")
        elif utilization > 60:
            recommendations.append("Warning: Capacity utilization above 60%")
            recommendations.append("Plan for capacity increase")
        
        if days_until_limit and days_until_limit < 30:
            recommendations.append(f"Capacity limit will be reached in ~{days_until_limit} days")
        
        prediction_date = (datetime.now() + timedelta(days=30)).isoformat()
        
        return CapacityPrediction(
            metric_name=metric_name,
            current_value=current_value,
            predicted_value=predicted_value,
            prediction_date=prediction_date,
            capacity_limit=capacity_limit,
            utilization_percent=utilization,
            days_until_limit=days_until_limit,
            recommendations=recommendations
        )
    
    def _exponential_smoothing(self, values: List[float], alpha: float = 0.3) -> float:
        """Exponential smoothing for prediction."""
        if not values:
            return 0
        
        smoothed = values[0]
        for value in values[1:]:
            smoothed = alpha * value + (1 - alpha) * smoothed
        
        return smoothed
    
    def _calculate_growth_rate(self, values: List[float]) -> float:
        """Calculate average growth rate."""
        if len(values) < 2:
            return 0
        
        growth_rates = []
        for i in range(1, len(values)):
            if values[i-1] > 0:
                rate = (values[i] - values[i-1]) / values[i-1]
                growth_rates.append(rate)
        
        return statistics.mean(growth_rates) if growth_rates else 0
    
    def _predict_days_to_limit(self, current: float, predicted: float,
                               limit: float, growth_rate: float) -> Optional[int]:
        """Predict days until capacity limit is reached."""
        if growth_rate <= 0 or current >= limit:
            return None
        
        # Using exponential growth formula: limit = current * (1 + rate)^days
        if current > 0 and growth_rate > 0:
            days = math.log(limit / current) / math.log(1 + growth_rate)
            return int(days) if days > 0 else None
        
        return None


class ScalabilityAnalyzer:
    """Analyze scalability characteristics."""
    
    def analyze_scalability(self, func_name: str, module: str,
                           load_performance: Dict[int, float]) -> ScalabilityAnalysis:
        """Analyze scalability of a function based on load tests."""
        # Determine complexity class
        complexity_class = self._determine_complexity_class(load_performance)
        
        # Calculate scalability score
        scalability_score = self._calculate_scalability_score(load_performance)
        
        # Determine bottleneck risk
        bottleneck_risk = self._assess_bottleneck_risk(scalability_score, complexity_class)
        
        # Predict max recommended load
        max_load = self._predict_max_load(load_performance)
        
        # Predict performance at various scales
        performance_at_scale = self._predict_performance_at_scale(
            load_performance, complexity_class
        )
        
        return ScalabilityAnalysis(
            function_name=func_name,
            module=module,
            complexity_class=complexity_class,
            scalability_score=scalability_score,
            bottleneck_risk=bottleneck_risk,
            max_recommended_load=max_load,
            performance_at_scale=performance_at_scale
        )
    
    def _determine_complexity_class(self, load_perf: Dict[int, float]) -> str:
        """Determine algorithmic complexity class."""
        if len(load_perf) < 3:
            return "Unknown"
        
        loads = sorted(load_perf.keys())
        times = [load_perf[l] for l in loads]
        
        # Calculate ratios
        ratios = []
        for i in range(1, len(loads)):
            load_ratio = loads[i] / loads[i-1]
            time_ratio = times[i] / times[i-1] if times[i-1] > 0 else 1
            ratios.append(time_ratio / load_ratio)
        
        avg_ratio = statistics.mean(ratios)
        
        # Classify based on ratio
        if avg_ratio < 0.1:
            return "O(1)"
        elif avg_ratio < 0.5:
            return "O(log n)"
        elif avg_ratio < 1.5:
            return "O(n)"
        elif avg_ratio < 3:
            return "O(n log n)"
        else:
            return "O(n²) or worse"
    
    def _calculate_scalability_score(self, load_perf: Dict[int, float]) -> float:
        """Calculate scalability score (0-100)."""
        if len(load_perf) < 2:
            return 50.0
        
        loads = sorted(load_perf.keys())
        times = [load_perf[l] for l in loads]
        
        # Calculate efficiency degradation
        initial_efficiency = loads[0] / times[0] if times[0] > 0 else 0
        final_efficiency = loads[-1] / times[-1] if times[-1] > 0 else 0
        
        if initial_efficiency == 0:
            return 50.0
        
        efficiency_retention = (final_efficiency / initial_efficiency) * 100
        
        # Score based on efficiency retention
        score = min(100, max(0, efficiency_retention))
        
        return round(score, 2)
    
    def _assess_bottleneck_risk(self, score: float, complexity: str) -> str:
        """Assess bottleneck risk."""
        if score < 30 or complexity in ["O(n²) or worse"]:
            return "High"
        elif score < 60 or complexity in ["O(n log n)"]:
            return "Medium"
        else:
            return "Low"
    
    def _predict_max_load(self, load_perf: Dict[int, float],
                         max_acceptable_time: float = 1.0) -> int:
        """Predict maximum recommended load."""
        loads = sorted(load_perf.keys())
        
        # Find the load where time exceeds threshold
        for load in loads:
            if load_perf[load] > max_acceptable_time:
                return max(1, load - 1)
        
        # If no threshold exceeded, extrapolate
        return loads[-1] * 2
    
    def _predict_performance_at_scale(self, load_perf: Dict[int, float],
                                      complexity: str) -> Dict[int, float]:
        """Predict performance at various scales."""
        loads = sorted(load_perf.keys())
        max_load = loads[-1]
        
        predictions = {}
        
        # Predict for 2x, 5x, 10x current max load
        for multiplier in [2, 5, 10]:
            target_load = max_load * multiplier
            predicted_time = self._extrapolate_time(load_perf, target_load, complexity)
            predictions[target_load] = round(predicted_time, 4)
        
        return predictions
    
    def _extrapolate_time(self, load_perf: Dict[int, float],
                         target_load: int, complexity: str) -> float:
        """Extrapolate execution time for a given load."""
        loads = sorted(load_perf.keys())
        base_load = loads[-1]
        base_time = load_perf[base_load]
        
        ratio = target_load / base_load
        
        # Apply complexity-based scaling
        if complexity == "O(1)":
            return base_time
        elif complexity == "O(log n)":
            return base_time * math.log(ratio + 1)
        elif complexity == "O(n)":
            return base_time * ratio
        elif complexity == "O(n log n)":
            return base_time * ratio * math.log(ratio + 1)
        else:  # O(n²) or worse
            return base_time * (ratio ** 2)


class ResourceForecaster:
    """Forecast resource usage."""
    
    def forecast_resource(self, resource_type: str,
                         usage_history: List[Tuple[datetime, float]],
                         days_ahead: int = 30,
                         alert_threshold: float = 80.0) -> ResourceForecast:
        """Forecast resource usage."""
        if len(usage_history) < 2:
            return None
        
        dates = [d for d, _ in usage_history]
        values = [v for _, v in usage_history]
        
        current_usage = values[-1]
        
        # Calculate trend
        trend = self._calculate_trend(values)
        
        # Forecast future values
        forecasted = self._forecast_values(values, days_ahead)
        
        # Create date-value mapping
        forecast_dict = {}
        for i, value in enumerate(forecasted):
            future_date = datetime.now() + timedelta(days=i+1)
            forecast_dict[future_date.isoformat()[:10]] = round(value, 2)
        
        # Find peak
        peak_value = max(forecasted)
        peak_index = forecasted.index(peak_value)
        peak_date = (datetime.now() + timedelta(days=peak_index+1)).isoformat()[:10]
        
        # Calculate days to threshold
        days_to_threshold = None
        for i, value in enumerate(forecasted):
            if value >= alert_threshold:
                days_to_threshold = i + 1
                break
        
        return ResourceForecast(
            resource_type=resource_type,
            current_usage=current_usage,
            forecasted_usage=forecast_dict,
            peak_prediction=(peak_date, peak_value),
            trend=trend,
            alert_threshold=alert_threshold,
            days_to_threshold=days_to_threshold
        )
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction."""
        if len(values) < 2:
            return "stable"
        
        # Linear regression slope
        n = len(values)
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return "stable"
        
        slope = numerator / denominator
        
        if slope > 0.5:
            return "increasing"
        elif slope < -0.5:
            return "decreasing"
        else:
            return "stable"
    
    def _forecast_values(self, values: List[float], days: int) -> List[float]:
        """Forecast future values using exponential smoothing."""
        alpha = 0.3
        beta = 0.1
        
        # Initialize
        level = values[0]
        trend = 0
        
        # Fit the model
        for value in values[1:]:
            last_level = level
            level = alpha * value + (1 - alpha) * (level + trend)
            trend = beta * (level - last_level) + (1 - beta) * trend
        
        # Forecast
        forecasted = []
        for i in range(days):
            forecast = level + (i + 1) * trend
            forecasted.append(max(0, forecast))  # Ensure non-negative
        
        return forecasted


def generate_predictive_report(trace_history: List[Dict],
                               current_trace: Dict) -> Dict[str, Any]:
    """Generate comprehensive predictive analysis report."""
    predictor = PerformancePredictor()
    predictor.history = trace_history
    
    # Performance predictions
    perf_predictions = predictor.predict_performance_issues(current_trace)
    
    # Generate summary
    critical_predictions = [p for p in perf_predictions if p.risk_level == "Critical"]
    high_predictions = [p for p in perf_predictions if p.risk_level == "High"]
    
    return {
        "performance_predictions": [p.to_dict() for p in perf_predictions],
        "summary": {
            "total_predictions": len(perf_predictions),
            "critical_risks": len(critical_predictions),
            "high_risks": len(high_predictions),
            "average_confidence": statistics.mean([p.confidence for p in perf_predictions]) if perf_predictions else 0
        },
        "recommendations": _generate_overall_recommendations(perf_predictions)
    }


def _generate_overall_recommendations(predictions: List[PerformancePrediction]) -> List[str]:
    """Generate overall recommendations from predictions."""
    recommendations = []
    
    critical = [p for p in predictions if p.risk_level == "Critical"]
    if critical:
        recommendations.append(f"URGENT: {len(critical)} functions predicted to have critical performance issues")
        recommendations.append("Immediate optimization required for: " + ", ".join(p.function_name for p in critical[:3]))
    
    high = [p for p in predictions if p.risk_level == "High"]
    if high:
        recommendations.append(f"WARNING: {len(high)} functions showing high performance degradation risk")
    
    if len(predictions) > 10:
        recommendations.append("Consider comprehensive performance audit")
    
    return recommendations
