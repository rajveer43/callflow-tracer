# Predictive Analysis Guide

Complete documentation for predictive analytics and forecasting.

**Location**: `callflow_tracer/predictive_analysis.py` (627 lines)

---

## Overview

The Predictive Analysis module predicts future performance issues, capacity limits, and scalability characteristics using historical data and statistical analysis.

## Key Components

### PerformancePrediction (Dataclass)

Predicts future performance issues.

**Attributes**:
- `function_name` - Function name
- `module` - Module name
- `current_avg_time` - Current average execution time
- `predicted_time` - Predicted execution time
- `confidence` - Confidence level (0-1)
- `risk_level` - Low, Medium, High, Critical
- `prediction_basis` - Basis for prediction
- `recommendations` - List of recommendations

**Risk Levels**:
- Low: predicted_time ≤ current × 1.2
- Medium: predicted_time ≤ current × 1.5
- High: predicted_time ≤ current × 2.0
- Critical: predicted_time > current × 2.0

### CapacityPrediction (Dataclass)

Predicts capacity limit breaches.

**Attributes**:
- `metric_name` - Metric name (e.g., "requests")
- `current_value` - Current value
- `predicted_value` - Predicted value
- `prediction_date` - Prediction date
- `capacity_limit` - Maximum capacity
- `utilization_percent` - Current utilization %
- `days_until_limit` - Days until limit reached
- `recommendations` - List of recommendations

### ScalabilityAnalysis (Dataclass)

Analyzes scalability characteristics.

**Attributes**:
- `function_name` - Function name
- `complexity_class` - O(1), O(log n), O(n), O(n log n), O(n²)
- `scalability_score` - Score (0-100)
- `bottleneck_risk` - Low, Medium, High
- `max_recommended_load` - Maximum recommended load
- `performance_at_scale` - Dict of load → predicted time

### ResourceForecast (Dataclass)

Forecasts resource usage.

**Attributes**:
- `resource_type` - CPU, Memory, Disk, Network
- `current_usage` - Current usage value
- `forecasted_usage` - Dict of date → usage
- `peak_prediction` - Tuple of (date, peak_value)
- `trend` - increasing, decreasing, stable
- `alert_threshold` - Alert threshold
- `days_to_threshold` - Days until threshold

## Classes

### PerformancePredictor

Predicts performance issues using historical data.

**Methods**:
- `predict_performance_issues(current_trace)` - Predict issues
- `_get_historical_times(func_name)` - Get historical data
- `_predict_function_performance(...)` - Predict for function
- `_calculate_trend(values)` - Calculate trend
- `_linear_regression_predict(values)` - Linear regression
- `_calculate_confidence(values, std_dev, mean)` - Calculate confidence

**Confidence Calculation**:
- Data confidence: min(len(values) / 10, 1.0)
- Consistency confidence: max(0, 1 - coefficient_of_variation)
- Final: average of both

### CapacityPlanner

Plans for capacity limits.

**Methods**:
- `predict_capacity(metric_history, capacity_limit, metric_name)` - Predict capacity
- `_exponential_smoothing(values, alpha)` - Smooth values
- `_calculate_growth_rate(values)` - Calculate growth rate
- `_predict_days_to_limit(...)` - Predict days

### ScalabilityAnalyzer

Analyzes scalability.

**Methods**:
- `analyze_scalability(func_name, module, load_performance)` - Analyze
- `_determine_complexity_class(load_perf)` - Determine complexity
- `_calculate_scalability_score(load_perf)` - Calculate score
- `_assess_bottleneck_risk(score, complexity)` - Assess risk
- `_predict_max_load(load_perf, max_acceptable_time)` - Predict max load
- `_predict_performance_at_scale(load_perf, complexity)` - Predict at scale

**Complexity Classes**:
- O(1): Constant time
- O(log n): Logarithmic
- O(n): Linear
- O(n log n): Linearithmic
- O(n²) or worse: Quadratic or worse

### ResourceForecaster

Forecasts resource usage.

**Methods**:
- `forecast_resource(resource_type, usage_history, days_ahead, alert_threshold)` - Forecast
- `_calculate_trend(values)` - Calculate trend
- `_forecast_values(values, days)` - Forecast using exponential smoothing

## Usage Examples

### Predict Performance Issues
```python
from callflow_tracer.predictive_analysis import PerformancePredictor

predictor = PerformancePredictor("trace_history.json")
predictions = predictor.predict_performance_issues(current_trace)

for pred in predictions:
    if pred.risk_level == "Critical":
        print(f"CRITICAL: {pred.function_name}")
        print(f"  Current: {pred.current_avg_time:.4f}s")
        print(f"  Predicted: {pred.predicted_time:.4f}s")
        print(f"  Confidence: {pred.confidence:.1%}")
```

### Plan Capacity
```python
from callflow_tracer.predictive_analysis import CapacityPlanner
from datetime import datetime, timedelta

planner = CapacityPlanner()
history = [(datetime.now() - timedelta(days=i), 100 + i*5) for i in range(30)]
prediction = planner.predict_capacity(history, capacity_limit=500)

print(f"Days until limit: {prediction.days_until_limit}")
print(f"Current utilization: {prediction.utilization_percent:.1f}%")
print(f"Recommendations: {prediction.recommendations}")
```

### Analyze Scalability
```python
from callflow_tracer.predictive_analysis import ScalabilityAnalyzer

analyzer = ScalabilityAnalyzer()
load_perf = {100: 0.1, 1000: 1.0, 10000: 100.0}
analysis = analyzer.analyze_scalability("my_func", "my_module", load_perf)

print(f"Complexity: {analysis.complexity_class}")
print(f"Scalability Score: {analysis.scalability_score:.1f}")
print(f"Bottleneck Risk: {analysis.bottleneck_risk}")
print(f"Max Recommended Load: {analysis.max_recommended_load}")
```

### Forecast Resources
```python
from callflow_tracer.predictive_analysis import ResourceForecaster
from datetime import datetime, timedelta

forecaster = ResourceForecaster()
history = [(datetime.now() - timedelta(days=i), 50 + i*2) for i in range(30)]
forecast = forecaster.forecast_resource("Memory", history, days_ahead=30)

print(f"Peak: {forecast.peak_prediction}")
print(f"Trend: {forecast.trend}")
print(f"Days to threshold: {forecast.days_to_threshold}")
print(f"Forecasted usage: {forecast.forecasted_usage}")
```

## CLI Usage

```bash
# Generate predictions from trace history
callflow-tracer predict history.json -o predictions.html

# JSON output
callflow-tracer predict history.json --format json

# Custom output file
callflow-tracer predict history.json -o my_predictions.html
```

## Output Format

```json
{
  "performance_predictions": [
    {
      "function_name": "process_data",
      "module": "data_processor",
      "current_avg_time": 0.5,
      "predicted_time": 0.75,
      "confidence": 0.85,
      "risk_level": "High",
      "prediction_basis": "Based on 10 historical measurements",
      "recommendations": [
        "Performance is degrading over time",
        "Consider profiling and optimization"
      ]
    }
  ],
  "summary": {
    "total_predictions": 15,
    "critical_risks": 2,
    "high_risks": 5,
    "average_confidence": 0.82
  },
  "recommendations": [
    "URGENT: 2 functions predicted to have critical performance issues",
    "WARNING: 5 functions showing high performance degradation risk"
  ]
}
```

## Interpretation Guide

### Risk Levels
- **Low**: Performance stable or improving
- **Medium**: Slight degradation expected
- **High**: Significant degradation predicted
- **Critical**: Severe degradation or failure risk

### Confidence Levels
- **0.0-0.3**: Low confidence, limited data
- **0.3-0.6**: Moderate confidence, some data
- **0.6-0.8**: Good confidence, sufficient data
- **0.8-1.0**: High confidence, extensive data

### Scalability Scores
- **0-30**: Poor scalability, bottleneck risk
- **30-60**: Moderate scalability
- **60-80**: Good scalability
- **80-100**: Excellent scalability

### Complexity Classes
- **O(1)**: Constant time, excellent scalability
- **O(log n)**: Logarithmic, very good scalability
- **O(n)**: Linear, good scalability
- **O(n log n)**: Linearithmic, acceptable scalability
- **O(n²) or worse**: Quadratic or worse, poor scalability
