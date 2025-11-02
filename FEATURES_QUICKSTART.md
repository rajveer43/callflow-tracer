# CallFlow Tracer - New Features Quick Start

## 🚀 Quick Start Guide

### Installation

```bash
cd callflow-tracer
pip install -e .
```

### Verify Installation

```bash
callflow --version
callflow --help
```

## 📊 Feature 1: Code Quality Analysis

### What It Does
Analyzes your code for complexity, maintainability, and technical debt.

### Quick Example

```bash
# Analyze current directory
callflow quality

# Analyze specific directory
callflow quality ./src -o quality_report.html

# Track trends over time
callflow quality --track-trends
```

### Python API

```python
from callflow_tracer import analyze_codebase

# Analyze entire codebase
results = analyze_codebase("./src")

print(f"Functions: {results['summary']['total_functions']}")
print(f"Avg Complexity: {results['summary']['average_complexity']:.1f}")
print(f"Avg Maintainability: {results['summary']['average_maintainability']:.1f}")
print(f"Critical Issues: {results['summary']['critical_issues']}")
```

### What You Get

- **Cyclomatic Complexity**: How complex is each function?
- **Maintainability Index**: How easy is it to maintain? (0-100)
- **Technical Debt**: Which functions need refactoring?
- **Trend Tracking**: Is quality improving or degrading?

### Metrics Explained

| Complexity | Rating | Action |
|------------|--------|--------|
| 1-5 | ✅ Simple | Good! |
| 6-10 | ⚠️ Moderate | Monitor |
| 11-20 | 🔶 Complex | Consider refactoring |
| 21+ | 🔴 Critical | Refactor now! |

| Maintainability | Rating | Action |
|-----------------|--------|--------|
| 80-100 | ✅ Excellent | Great! |
| 60-79 | ⚠️ Good | Acceptable |
| 40-59 | 🔶 Fair | Needs improvement |
| 0-39 | 🔴 Poor | Urgent refactoring |

---

## 🔮 Feature 2: Performance Prediction

### What It Does
Predicts future performance issues based on historical trace data.

### Quick Example

```bash
# Collect traces over time
callflow trace app.py --format json -o trace_day1.json
callflow trace app.py --format json -o trace_day2.json
callflow trace app.py --format json -o trace_day3.json

# Combine traces
jq -s '.' trace_*.json > trace_history.json

# Predict future performance
callflow predict trace_history.json -o predictions.html
```

### Python API

```python
from callflow_tracer import PerformancePredictor

# Load historical data
predictor = PerformancePredictor("trace_history.json")

# Predict issues
predictions = predictor.predict_performance_issues(current_trace)

for pred in predictions:
    if pred.risk_level in ["Critical", "High"]:
        print(f"⚠️  {pred.function_name}")
        print(f"   Current: {pred.current_avg_time:.4f}s")
        print(f"   Predicted: {pred.predicted_time:.4f}s")
        print(f"   Confidence: {pred.confidence:.1%}")
```

### What You Get

- **Performance Trends**: Is performance degrading?
- **Risk Assessment**: Which functions are at risk?
- **Confidence Scores**: How reliable is the prediction?
- **Recommendations**: What should you do?

---

## 📈 Feature 3: Scalability Analysis

### What It Does
Determines how your code scales with input size (O notation).

### Quick Example

```python
from callflow_tracer import ScalabilityAnalyzer

# Test with different loads
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

print(f"Complexity: {analysis.complexity_class}")
print(f"Scalability Score: {analysis.scalability_score}/100")
print(f"Max Recommended Load: {analysis.max_recommended_load}")
```

### What You Get

- **Complexity Class**: O(1), O(log n), O(n), O(n²), etc.
- **Scalability Score**: 0-100 (higher is better)
- **Performance Predictions**: How will it perform at scale?
- **Bottleneck Risk**: Low, Medium, or High

---

## 🔥 Feature 4: Code Churn Analysis

### What It Does
Identifies frequently changed files (hotspots) using git history.

### Quick Example

```bash
# Analyze last 90 days
callflow churn

# Custom time period
callflow churn --days 180 -o churn_report.html

# Specific directory
callflow churn ./src --days 30
```

### Python API

```python
from callflow_tracer import CodeChurnAnalyzer, generate_churn_report

# Analyze specific file
analyzer = CodeChurnAnalyzer(".")
churn = analyzer.analyze_file_churn("mymodule.py", days=90)

print(f"Commits: {churn.total_commits}")
print(f"Changes: {churn.lines_modified}")
print(f"Churn Rate: {churn.churn_rate:.2f} changes/day")
print(f"Hotspot Score: {churn.hotspot_score:.1f}/100")

# Full report
report = generate_churn_report(".", days=90)
print(f"High Risk Files: {report['summary']['high_risk_files']}")
```

### What You Get

- **Hotspot Detection**: Which files change most often?
- **Churn Rate**: How fast is code changing?
- **Author Analysis**: Who's working on what?
- **Quality Correlation**: Does churn correlate with bugs?

---

## 💾 Feature 5: Resource Forecasting

### What It Does
Predicts future resource usage (CPU, memory, disk).

### Quick Example

```python
from callflow_tracer import ResourceForecaster
from datetime import datetime, timedelta

# Historical usage data
usage_history = [
    (datetime.now() - timedelta(days=30-i), 50 + i * 2)
    for i in range(30)
]

forecaster = ResourceForecaster()
forecast = forecaster.forecast_resource(
    resource_type="CPU",
    usage_history=usage_history,
    days_ahead=30,
    alert_threshold=90.0
)

print(f"Current: {forecast.current_usage:.1f}%")
print(f"Trend: {forecast.trend}")
print(f"Peak: {forecast.peak_prediction[1]:.1f}%")

if forecast.days_to_threshold:
    print(f"⚠️  Threshold in {forecast.days_to_threshold} days")
```

### What You Get

- **Usage Trends**: Increasing, decreasing, or stable?
- **Peak Predictions**: When will usage peak?
- **Threshold Alerts**: When will limits be reached?
- **30-Day Forecast**: Daily predictions

---

## 📦 Feature 6: Capacity Planning

### What It Does
Predicts when you'll hit capacity limits.

### Quick Example

```python
from callflow_tracer import CapacityPlanner
from datetime import datetime

# Metric history
metric_history = [
    (datetime(2024, 1, 1), 1000),
    (datetime(2024, 2, 1), 1500),
    (datetime(2024, 3, 1), 2200),
]

planner = CapacityPlanner()
prediction = planner.predict_capacity(
    metric_history,
    capacity_limit=10000,
    metric_name="requests_per_day"
)

print(f"Current: {prediction.current_value}")
print(f"Utilization: {prediction.utilization_percent:.1f}%")

if prediction.days_until_limit:
    print(f"Days until limit: {prediction.days_until_limit}")
```

### What You Get

- **Current Utilization**: How much capacity is used?
- **Growth Rate**: How fast is usage growing?
- **Days to Limit**: When will you hit the limit?
- **Recommendations**: What actions to take?

---

## 🎯 Common Workflows

### Workflow 1: Weekly Quality Check

```bash
#!/bin/bash
# weekly_quality_check.sh

echo "Running weekly quality analysis..."

# Analyze quality
callflow quality ./src --track-trends -o reports/quality_$(date +%Y%m%d).html

# Analyze churn
callflow churn ./src --days 7 -o reports/churn_$(date +%Y%m%d).html

# Check thresholds
python scripts/check_quality_gates.py

echo "✓ Quality check complete!"
```

### Workflow 2: Performance Monitoring

```python
# monitor_performance.py

from callflow_tracer import trace_scope, generate_predictive_report
import json
from datetime import datetime

# Collect trace
output_file = f"traces/trace_{datetime.now():%Y%m%d_%H%M%S}.json"

with trace_scope(output_file, format="json"):
    run_application()

# Load history
with open("trace_history.json", "r") as f:
    history = json.load(f)

# Add new trace
with open(output_file, "r") as f:
    current = json.load(f)

history.append(current)

# Predict issues
report = generate_predictive_report(history[:-1], current)

# Alert on critical issues
if report['summary']['critical_risks'] > 0:
    send_alert(f"⚠️  {report['summary']['critical_risks']} critical performance risks detected!")

# Save updated history
with open("trace_history.json", "w") as f:
    json.dump(history[-10:], f)  # Keep last 10 traces
```

### Workflow 3: Pre-Commit Quality Gate

```python
# .git/hooks/pre-commit

#!/usr/bin/env python3

from callflow_tracer import analyze_codebase
import sys

# Analyze staged files
results = analyze_codebase(".")

# Check thresholds
if results['summary']['critical_issues'] > 0:
    print("❌ COMMIT BLOCKED: Critical quality issues found!")
    print(f"   Critical issues: {results['summary']['critical_issues']}")
    sys.exit(1)

if results['summary']['average_complexity'] > 15:
    print("⚠️  WARNING: Average complexity is high")
    print(f"   Average complexity: {results['summary']['average_complexity']:.1f}")

print("✅ Quality check passed!")
sys.exit(0)
```

---

## 🛠️ Troubleshooting

### Issue: "Not a git repository"
**Solution**: Code churn analysis requires git.
```bash
git init
```

### Issue: "Need at least 2 traces for prediction"
**Solution**: Collect multiple traces over time.
```bash
# Collect traces daily
callflow trace app.py --format json -o trace_$(date +%Y%m%d).json

# Combine after a few days
jq -s '.' trace_*.json > trace_history.json
```

### Issue: High memory usage during analysis
**Solution**: Analyze smaller directories.
```bash
# Instead of analyzing everything
callflow quality ./src/module1
callflow quality ./src/module2
```

---

## 📚 Learn More

- **Full Guide**: See `QUALITY_ANALYSIS_GUIDE.md`
- **CLI Reference**: See `CLI_GUIDE.md`
- **Examples**: Check `examples/` directory
- **GitHub**: https://github.com/rajveer43/callflow-tracer

---

## 🎓 Example Scripts

### Run the Demos

```bash
# Quality analysis demo
python examples/quality_analysis_demo.py

# Advanced features demo
python examples/advanced_analysis_demo.py

# CLI test suite
cd examples
./cli_test_commands.bat  # Windows
./cli_test_commands.sh   # Linux/Mac
```

---

## 💡 Pro Tips

1. **Track Trends**: Use `--track-trends` to see quality changes over time
2. **Automate**: Add quality checks to your CI/CD pipeline
3. **Set Thresholds**: Define acceptable complexity and maintainability levels
4. **Regular Analysis**: Run quality checks weekly
5. **Combine Features**: Use quality + churn + prediction together for best insights

---

**Happy Analyzing! 🚀**
