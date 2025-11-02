# Code Quality & Predictive Analysis Guide

## Overview

CallFlow Tracer now includes powerful code quality metrics and predictive analysis features:

- **Code Quality Metrics**: Cyclomatic complexity, maintainability index, technical debt
- **Predictive Analysis**: Performance issue prediction, capacity planning, scalability analysis
- **Code Churn Analysis**: Track code changes and correlate with quality/performance

## Features

### 1. Code Quality Metrics

Analyze your codebase for:
- **Cyclomatic Complexity**: Measure code complexity (McCabe metric)
- **Cognitive Complexity**: Human-oriented complexity measurement
- **Maintainability Index**: 0-100 score based on Halstead metrics
- **Technical Debt**: Identify problematic code that needs refactoring
- **Quality Trends**: Track quality metrics over time

### 2. Predictive Analysis

Predict future issues:
- **Performance Predictions**: Forecast performance degradation
- **Capacity Planning**: Predict when limits will be reached
- **Scalability Analysis**: Determine algorithmic complexity (O notation)
- **Resource Forecasting**: Predict CPU, memory, disk usage

### 3. Code Churn Analysis

Understand code stability:
- **Churn Metrics**: Track file changes over time
- **Hotspot Detection**: Identify frequently changed files
- **Quality Correlation**: Link churn to bugs and quality issues

## CLI Usage

### Quality Analysis

```bash
# Analyze current directory
callflow quality

# Analyze specific directory
callflow quality ./src -o quality_report.html

# Track quality trends over time
callflow quality --track-trends

# Export as JSON
callflow quality --format json -o quality.json
```

### Predictive Analysis

```bash
# Predict performance issues from trace history
callflow predict trace_history.json -o predictions.html

# Export predictions as JSON
callflow predict trace_history.json --format json
```

### Code Churn Analysis

```bash
# Analyze last 90 days of changes
callflow churn

# Custom time period
callflow churn --days 180

# Analyze specific directory
callflow churn ./src --days 30 -o churn_report.html
```

## Python API Usage

### Code Quality Analysis

```python
from callflow_tracer import analyze_codebase, ComplexityAnalyzer, MaintainabilityAnalyzer

# Analyze entire codebase
results = analyze_codebase("./src")

print(f"Total functions: {results['summary']['total_functions']}")
print(f"Average complexity: {results['summary']['average_complexity']:.2f}")
print(f"Average maintainability: {results['summary']['average_maintainability']:.2f}")

# Analyze specific file
analyzer = ComplexityAnalyzer()
metrics = analyzer.analyze_file("mymodule.py")

for metric in metrics:
    print(f"{metric.function_name}: Complexity={metric.cyclomatic_complexity}")
    print(f"  Rating: {metric.complexity_rating}")
```

### Maintainability Analysis

```python
from callflow_tracer import MaintainabilityAnalyzer

analyzer = MaintainabilityAnalyzer()
metrics = analyzer.analyze_file("mymodule.py")

for metric in metrics:
    print(f"{metric.function_name}:")
    print(f"  Maintainability Index: {metric.maintainability_index:.1f}")
    print(f"  Rating: {metric.maintainability_rating}")
    print(f"  Halstead Volume: {metric.halstead_volume:.2f}")
```

### Technical Debt Analysis

```python
from callflow_tracer import TechnicalDebtAnalyzer, ComplexityAnalyzer, MaintainabilityAnalyzer

# Get metrics
comp_analyzer = ComplexityAnalyzer()
maint_analyzer = MaintainabilityAnalyzer()

complexity_metrics = comp_analyzer.analyze_file("mymodule.py")
maintainability_metrics = maint_analyzer.analyze_file("mymodule.py")

# Analyze technical debt
debt_analyzer = TechnicalDebtAnalyzer()
debt_indicators = debt_analyzer.analyze_from_metrics(
    complexity_metrics,
    maintainability_metrics
)

for debt in debt_indicators:
    print(f"{debt.function_name}:")
    print(f"  Debt Score: {debt.debt_score:.1f}")
    print(f"  Severity: {debt.severity}")
    print(f"  Estimated Hours to Fix: {debt.estimated_hours:.1f}")
    print(f"  Issues: {', '.join(debt.issues)}")
```

### Quality Trend Tracking

```python
from callflow_tracer import QualityTrendAnalyzer

# Initialize trend analyzer
trend_analyzer = QualityTrendAnalyzer("quality_history.json")

# Add snapshot
trend = trend_analyzer.add_snapshot(
    complexity_metrics,
    maintainability_metrics,
    debt_indicators
)

# Analyze trends
trends = trend_analyzer.analyze_trends()
print(f"Complexity trend: {trends['complexity_trend']}")
print(f"Maintainability trend: {trends['maintainability_trend']}")
print(f"Debt trend: {trends['debt_trend']}")
```

### Performance Prediction

```python
from callflow_tracer import PerformancePredictor

# Load historical traces
predictor = PerformancePredictor("trace_history.json")

# Predict performance issues
predictions = predictor.predict_performance_issues(current_trace)

for pred in predictions:
    if pred.risk_level in ["Critical", "High"]:
        print(f"⚠️  {pred.function_name}:")
        print(f"   Current: {pred.current_avg_time:.6f}s")
        print(f"   Predicted: {pred.predicted_time:.6f}s")
        print(f"   Risk: {pred.risk_level}")
        print(f"   Confidence: {pred.confidence:.1%}")
```

### Capacity Planning

```python
from callflow_tracer import CapacityPlanner
from datetime import datetime

# Prepare metric history (date, value pairs)
metric_history = [
    (datetime(2024, 1, 1), 1000),
    (datetime(2024, 2, 1), 1500),
    (datetime(2024, 3, 1), 2200),
    # ... more data points
]

planner = CapacityPlanner()
prediction = planner.predict_capacity(
    metric_history,
    capacity_limit=10000,
    metric_name="requests_per_day"
)

print(f"Current: {prediction.current_value}")
print(f"Predicted (30 days): {prediction.predicted_value}")
print(f"Utilization: {prediction.utilization_percent:.1f}%")
if prediction.days_until_limit:
    print(f"Days until limit: {prediction.days_until_limit}")
```

### Scalability Analysis

```python
from callflow_tracer import ScalabilityAnalyzer

# Load performance data at different loads
load_performance = {
    100: 0.05,    # 100 items: 0.05s
    500: 0.28,    # 500 items: 0.28s
    1000: 0.58,   # 1000 items: 0.58s
    5000: 3.12,   # 5000 items: 3.12s
}

analyzer = ScalabilityAnalyzer()
analysis = analyzer.analyze_scalability(
    "process_data",
    "mymodule",
    load_performance
)

print(f"Complexity Class: {analysis.complexity_class}")
print(f"Scalability Score: {analysis.scalability_score:.1f}/100")
print(f"Bottleneck Risk: {analysis.bottleneck_risk}")
print(f"Max Recommended Load: {analysis.max_recommended_load}")

print("\nPredicted Performance at Scale:")
for load, time in analysis.performance_at_scale.items():
    print(f"  {load} items: {time:.4f}s")
```

### Resource Forecasting

```python
from callflow_tracer import ResourceForecaster
from datetime import datetime, timedelta

# Prepare usage history
usage_history = [
    (datetime.now() - timedelta(days=i), 50 + i * 2)
    for i in range(30, 0, -1)
]

forecaster = ResourceForecaster()
forecast = forecaster.forecast_resource(
    resource_type="CPU",
    usage_history=usage_history,
    days_ahead=30,
    alert_threshold=90.0
)

print(f"Current Usage: {forecast.current_usage:.1f}%")
print(f"Trend: {forecast.trend}")
print(f"Peak Prediction: {forecast.peak_prediction[1]:.1f}% on {forecast.peak_prediction[0]}")

if forecast.days_to_threshold:
    print(f"⚠️  Alert threshold will be reached in {forecast.days_to_threshold} days")
```

### Code Churn Analysis

```python
from callflow_tracer import CodeChurnAnalyzer, generate_churn_report

# Analyze specific file
analyzer = CodeChurnAnalyzer(".")
churn = analyzer.analyze_file_churn("mymodule.py", days=90)

print(f"File: {churn.file_path}")
print(f"Total Commits: {churn.total_commits}")
print(f"Lines Added: {churn.lines_added}")
print(f"Lines Deleted: {churn.lines_deleted}")
print(f"Churn Rate: {churn.churn_rate:.2f} changes/day")
print(f"Hotspot Score: {churn.hotspot_score:.1f}/100")
print(f"Authors: {', '.join(churn.authors)}")

# Generate full report
report = generate_churn_report(".", days=90)

print(f"\nHotspots (top 5):")
for hotspot in report['hotspots'][:5]:
    print(f"  {hotspot['file_path']}: {hotspot['hotspot_score']:.1f}")
```

### Churn-Quality Correlation

```python
from callflow_tracer import ChurnCorrelationAnalyzer

# Get churn and quality metrics
churn_metrics = analyzer.analyze_directory_churn(".", days=90)
quality_results = analyze_codebase(".")

# Correlate
correlator = ChurnCorrelationAnalyzer()
correlations = correlator.correlate_churn_with_quality(
    churn_metrics,
    quality_results['complexity_metrics'],
    {}  # performance_data if available
)

for corr in correlations:
    if corr.risk_assessment in ["Critical", "High"]:
        print(f"🔥 {corr.file_path}:")
        print(f"   Churn Score: {corr.churn_score:.1f}")
        print(f"   Complexity Score: {corr.complexity_score:.1f}")
        print(f"   Risk: {corr.risk_assessment}")
        print(f"   Recommendations:")
        for rec in corr.recommendations:
            print(f"     • {rec}")
```

## Understanding the Metrics

### Cyclomatic Complexity

- **1-5**: Simple, easy to understand
- **6-10**: Moderate complexity
- **11-20**: Complex, consider refactoring
- **21+**: Very complex, high risk

### Maintainability Index

- **80-100**: Excellent maintainability
- **60-79**: Good maintainability
- **40-59**: Fair maintainability
- **20-39**: Poor maintainability
- **0-19**: Critical, immediate attention needed

### Technical Debt Score

- **0-20**: Low debt
- **21-40**: Medium debt
- **41-60**: High debt
- **61+**: Critical debt

### Hotspot Score

- **0-30**: Stable code
- **31-60**: Moderate churn
- **61-80**: High churn, monitor closely
- **81-100**: Critical hotspot, investigate

## Best Practices

### 1. Regular Quality Checks

```bash
# Run weekly quality analysis
callflow quality --track-trends

# Monitor trends
callflow quality --format json | jq '.trend_analysis'
```

### 2. Pre-Commit Hooks

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check quality of changed files
callflow quality --format json > /tmp/quality.json

# Fail if critical issues found
critical=$(jq '.summary.critical_issues' /tmp/quality.json)
if [ "$critical" -gt 0 ]; then
    echo "❌ Critical quality issues found!"
    exit 1
fi
```

### 3. CI/CD Integration

```yaml
# GitHub Actions
- name: Quality Analysis
  run: |
    callflow quality --format json -o quality.json
    callflow churn --days 30 --format json -o churn.json
    
- name: Check Quality Thresholds
  run: |
    python scripts/check_quality_thresholds.py
```

### 4. Performance Monitoring

```python
# Collect traces regularly
import schedule

def collect_trace():
    with trace_scope("trace_history.json", format="json"):
        run_application()

schedule.every().hour.do(collect_trace)

# Analyze trends weekly
def analyze_trends():
    report = generate_predictive_report(load_history(), get_current_trace())
    send_alert_if_critical(report)

schedule.every().week.do(analyze_trends)
```

## Example Workflows

### Workflow 1: Code Quality Audit

```bash
# 1. Analyze codebase
callflow quality ./src -o quality_report.html --track-trends

# 2. Identify hotspots
callflow churn ./src --days 180 -o churn_report.html

# 3. Review reports and prioritize fixes
```

### Workflow 2: Performance Optimization

```bash
# 1. Collect baseline traces
callflow trace app.py --format json -o baseline.json

# 2. Make optimizations
# ... code changes ...

# 3. Collect new traces
callflow trace app.py --format json -o optimized.json

# 4. Compare
callflow compare baseline.json optimized.json

# 5. Predict future performance
callflow predict traces.json -o predictions.html
```

### Workflow 3: Technical Debt Management

```python
from callflow_tracer import analyze_codebase, TechnicalDebtAnalyzer

# Analyze codebase
results = analyze_codebase("./src")

# Sort by debt score
debt_items = sorted(
    results['debt_indicators'],
    key=lambda x: x['debt_score'],
    reverse=True
)

# Create action plan
print("Technical Debt Action Plan:")
for i, debt in enumerate(debt_items[:10], 1):
    print(f"\n{i}. {debt['function_name']} ({debt['module']})")
    print(f"   Priority: {debt['severity']}")
    print(f"   Estimated Hours: {debt['estimated_hours']:.1f}")
    print(f"   Issues:")
    for issue in debt['issues']:
        print(f"     - {issue}")
```

## Troubleshooting

### Issue: "Not a git repository"

**Solution**: Code churn analysis requires a git repository.

```bash
git init
# or run from within a git repository
```

### Issue: High memory usage during analysis

**Solution**: Analyze smaller directories or specific files.

```bash
# Instead of analyzing everything
callflow quality ./src/module1
callflow quality ./src/module2
```

### Issue: Predictions require multiple traces

**Solution**: Collect traces over time.

```bash
# Collect traces regularly
callflow trace app.py --format json -o trace_$(date +%Y%m%d).json

# Combine into history
jq -s '.' trace_*.json > trace_history.json

# Then predict
callflow predict trace_history.json
```

## Advanced Usage

### Custom Quality Thresholds

```python
from callflow_tracer import analyze_codebase

results = analyze_codebase("./src")

# Define custom thresholds
COMPLEXITY_THRESHOLD = 15
MAINTAINABILITY_THRESHOLD = 60

violations = []

for metric in results['complexity_metrics']:
    if metric['cyclomatic_complexity'] > COMPLEXITY_THRESHOLD:
        violations.append(f"{metric['function_name']}: Complexity too high")

for metric in results['maintainability_metrics']:
    if metric['maintainability_index'] < MAINTAINABILITY_THRESHOLD:
        violations.append(f"{metric['function_name']}: Maintainability too low")

if violations:
    print("Quality Violations:")
    for v in violations:
        print(f"  ❌ {v}")
    exit(1)
```

### Automated Reporting

```python
import json
from datetime import datetime

def generate_weekly_report():
    # Analyze quality
    quality = analyze_codebase("./src")
    
    # Analyze churn
    churn = generate_churn_report(".", days=7)
    
    # Create report
    report = {
        "date": datetime.now().isoformat(),
        "quality_summary": quality['summary'],
        "top_debt": quality['debt_indicators'][:5],
        "hotspots": churn['hotspots'][:5],
        "recommendations": []
    }
    
    # Add recommendations
    if quality['summary']['critical_issues'] > 0:
        report['recommendations'].append("Address critical quality issues immediately")
    
    if churn['summary']['high_risk_files'] > 5:
        report['recommendations'].append("High code churn detected - review stability")
    
    # Save report
    with open(f"reports/weekly_{datetime.now():%Y%m%d}.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    return report
```

---

For more information, see:
- [CLI Guide](CLI_GUIDE.md)
- [Main README](README.md)
- [GitHub Repository](https://github.com/rajveer43/callflow-tracer)
