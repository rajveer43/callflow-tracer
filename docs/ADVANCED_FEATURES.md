# Advanced Features Documentation

## 🔥 Root Cause Analysis + ⚡ Anomaly Detection

CallFlow Tracer includes two powerful advanced features for comprehensive debugging and monitoring.

---

## 🔥 Feature 1: Root Cause Analysis

**Uses graph algorithms + LLM to identify root causes and debug faster.**

### Overview

Root Cause Analysis traces performance issues, errors, and bottlenecks to their source using:
- **Graph traversal algorithms** to trace dependencies
- **Impact analysis** to measure downstream effects
- **LLM insights** for intelligent recommendations (optional)

### Quick Start

```python
from callflow_tracer import trace_scope
from callflow_tracer.ai import analyze_root_cause

# Trace your application
with trace_scope() as graph:
    your_slow_application()

# Analyze root causes
analysis = analyze_root_cause(graph, issue_type='performance')

# View results
for root in analysis['root_causes']:
    print(f"{root['function']}: {root['total_time']:.3f}s")
    print(f"  Confidence: {root['confidence']:.0%}")
    print(f"  Impact: {root['affected_nodes']} nodes")
```

### Issue Types

| Type | Description | Use Case |
|------|-------------|----------|
| `performance` | Slow execution times | Find performance bottlenecks |
| `error` | Functions with errors | Trace error sources |
| `bottleneck` | High self-time or call count | Identify CPU/IO bottlenecks |

### Output Structure

```python
{
    'issue_type': 'performance',
    'total_issues': 10,
    'total_root_causes': 3,
    'root_causes': [
        {
            'node_id': '...',
            'function': 'slow_database_query',
            'module': 'myapp.db',
            'total_time': 1.85,
            'self_time': 1.80,
            'call_count': 5,
            'affected_nodes': 12,
            'total_impact_time': 2.34,
            'upstream_path': ['main', 'process_data', 'slow_database_query'],
            'confidence': 0.9
        }
    ],
    'impact_analysis': {
        'total_affected_functions': 15,
        'total_time_impact': 3.45,
        'impact_percentage': 78.5
    },
    'llm_insights': '...'  # AI-generated insights (if LLM configured)
}
```

### Advanced Usage

#### Custom Threshold

```python
# Only analyze functions slower than 0.1s
analysis = analyze_root_cause(graph, issue_type='performance', threshold=0.1)
```

#### With Specific LLM Provider

```python
from callflow_tracer.ai import RootCauseAnalyzer, OpenAIProvider

provider = OpenAIProvider(model="gpt-4o")
analyzer = RootCauseAnalyzer(provider=provider)
analysis = analyzer.analyze(graph, issue_type='performance')
```

#### Error Tracing

```python
# Trace errors to their source
analysis = analyze_root_cause(graph, issue_type='error')
```

### How It Works

1. **Extract Graph Data** - Nodes and edges from CallGraph
2. **Build Dependency Graph** - Caller/callee relationships
3. **Identify Problems** - Based on issue type and threshold
4. **Traverse Upstream** - Follow call chain to root
5. **Calculate Impact** - Measure downstream effects
6. **Compute Confidence** - Score based on path length and impact
7. **Get LLM Insights** - AI analysis (if available)

### Use Cases

- 🐛 **Debug Performance Issues** - Find the true source of slowness
- 🔍 **Trace Errors** - Follow errors to their origin
- 📊 **Impact Analysis** - Understand cascading effects
- 🚀 **Optimization** - Focus on high-impact fixes

---

## ⚡ Feature 2: Anomaly Detection

**Uses statistical analysis to detect anomalies proactively. No LLM required!**

### Overview

Anomaly Detection identifies unusual patterns using:
- **Statistical methods** (Z-score, IQR)
- **Baseline comparison** (optional)
- **Pattern recognition** (N+1 queries, excessive fan-out)
- **Multiple anomaly types**

### Quick Start

```python
from callflow_tracer import trace_scope
from callflow_tracer.ai import detect_anomalies

# Trace your application
with trace_scope() as graph:
    your_application()

# Detect anomalies
anomalies = detect_anomalies(graph)

# View results
print(f"Total anomalies: {anomalies['severity_summary']['total']}")
print(f"Severity: {anomalies['severity_summary']['overall_severity']}")

for anomaly in anomalies['time_anomalies']:
    print(f"⚠️  {anomaly['function']}: {anomaly['description']}")
```

### Anomaly Types

| Type | Description | Detection Method |
|------|-------------|------------------|
| **Time** | Unusually slow execution | Z-score analysis |
| **Frequency** | Too many calls | Z-score analysis |
| **Pattern** | N+1 queries, excessive fan-out | Pattern matching |
| **Outlier** | Statistical outliers | IQR method |

### Output Structure

```python
{
    'time_anomalies': [
        {
            'type': 'time',
            'function': 'slow_function',
            'value': 0.523,
            'expected': 0.105,
            'deviation': 0.418,
            'z_score': 3.2,
            'severity': 'high',
            'description': '...'
        }
    ],
    'frequency_anomalies': [...],
    'pattern_anomalies': [...],
    'outlier_anomalies': [...],
    'severity_summary': {
        'total': 12,
        'critical': 1,
        'high': 3,
        'medium': 5,
        'low': 3,
        'overall_severity': 'high'
    },
    'recommendations': [
        '⚠️  Investigate slow_function - taking 0.418s longer than expected',
        '🔥 Potential N+1 query pattern detected - batch operations'
    ]
}
```

### Advanced Usage

#### Baseline Comparison

```python
from callflow_tracer.ai import AnomalyDetector

# Create baseline from normal executions
baseline_graphs = []
for i in range(5):
    with trace_scope() as graph:
        normal_execution()
    baseline_graphs.append(graph)

# Detect anomalies against baseline
detector = AnomalyDetector(baseline_graphs=baseline_graphs)

with trace_scope() as test_graph:
    test_execution()

anomalies = detector.detect(test_graph)
```

#### Sensitivity Tuning

```python
# More sensitive (detects more anomalies)
anomalies = detect_anomalies(graph, sensitivity=1.5)

# Less sensitive (detects fewer anomalies)
anomalies = detect_anomalies(graph, sensitivity=3.0)

# Default is 2.0 (2 standard deviations)
```

#### Specific Anomaly Types

```python
# Only detect time anomalies
anomalies = detect_anomalies(graph, detect_types=['time'])

# Only detect patterns
anomalies = detect_anomalies(graph, detect_types=['pattern'])

# Multiple types
anomalies = detect_anomalies(graph, detect_types=['time', 'frequency'])
```

#### Continuous Monitoring

```python
detector = AnomalyDetector(sensitivity=2.0)

# Build baseline
for i in range(10):
    with trace_scope() as graph:
        normal_operation()
    detector.add_baseline(graph)

# Monitor production
while True:
    with trace_scope() as graph:
        handle_request()
    
    anomalies = detector.detect(graph)
    if anomalies['severity_summary']['total'] > 0:
        alert_team(anomalies)
```

### Severity Levels

| Severity | Z-Score | Action |
|----------|---------|--------|
| **Critical** | > 3.0 | Immediate action required |
| **High** | 2.5 - 3.0 | Investigate soon |
| **Medium** | 2.0 - 2.5 | Monitor closely |
| **Low** | < 2.0 | Note for review |

### Use Cases

- 📊 **Production Monitoring** - Detect issues proactively
- 🔄 **CI/CD Gates** - Block deployments with anomalies
- 🔍 **N+1 Detection** - Find query patterns automatically
- 📈 **Performance Regression** - Compare against baseline
- ⚠️ **Alerting** - Trigger alerts on anomalies

---

## 🚀 Combined Usage

**Use both features together for comprehensive debugging!**

### Complete Debugging Workflow

```python
from callflow_tracer import trace_scope
from callflow_tracer.ai import detect_anomalies, analyze_root_cause

# Step 1: Trace application
with trace_scope() as graph:
    your_application()

# Step 2: Detect anomalies (WHAT is wrong)
anomalies = detect_anomalies(graph)
print(f"Found {anomalies['severity_summary']['total']} anomalies")

# Step 3: Analyze root causes (WHY it's wrong)
root_analysis = analyze_root_cause(graph, issue_type='performance')
print(f"Traced to {root_analysis['total_root_causes']} root causes")

# Step 4: Take action
for root in root_analysis['root_causes'][:3]:
    print(f"Fix: {root['function']} (impact: {root['total_impact_time']:.3f}s)")
```

### Production Monitoring

```python
from callflow_tracer.ai import AnomalyDetector

# Setup
detector = AnomalyDetector(baseline_graphs=baseline, sensitivity=2.0)

# Monitor each request
with trace_scope() as graph:
    handle_request()

# Check for anomalies
anomalies = detector.detect(graph)

if anomalies['severity_summary']['critical'] > 0:
    # Critical anomaly - analyze root cause
    root_analysis = analyze_root_cause(graph, issue_type='performance')
    alert_team({
        'anomalies': anomalies,
        'root_causes': root_analysis['root_causes'],
        'recommendations': anomalies['recommendations']
    })
```

### CI/CD Performance Gate

```python
def performance_gate(graph):
    """CI/CD performance gate."""
    # Detect anomalies
    anomalies = detect_anomalies(graph, sensitivity=2.5)
    
    # Analyze root causes
    root_analysis = analyze_root_cause(graph, issue_type='performance')
    
    # Check thresholds
    if anomalies['severity_summary']['critical'] > 0:
        return False, "Critical anomalies detected"
    
    if root_analysis['impact_analysis']['total_time_impact'] > 2.0:
        return False, "Performance impact too high"
    
    return True, "Performance acceptable"

# In CI/CD pipeline
with trace_scope() as graph:
    run_performance_tests()

passed, message = performance_gate(graph)
if not passed:
    sys.exit(1)  # Fail build
```

---

## 📊 Comparison

| Feature | Root Cause Analysis | Anomaly Detection |
|---------|---------------------|-------------------|
| **Purpose** | Find WHY issues occur | Find WHAT is wrong |
| **Method** | Graph algorithms + LLM | Statistical analysis |
| **LLM Required** | Optional (enhanced) | No |
| **Best For** | Debugging, tracing | Monitoring, alerting |
| **Output** | Root causes, impact | Anomalies, severity |
| **Use Case** | Post-incident analysis | Proactive detection |

---

## 💡 Best Practices

### 1. Start with Anomaly Detection
- Quick scan for issues
- No LLM required
- Good for continuous monitoring

### 2. Follow Up with Root Cause Analysis
- Deep dive into detected anomalies
- Understand the "why"
- Get actionable recommendations

### 3. Use Baselines in Production
- Establish normal behavior
- Detect deviations early
- Reduce false positives

### 4. Tune Sensitivity
- Start with default (2.0)
- Increase for fewer alerts
- Decrease for more coverage

### 5. Combine with LLM
- Enhanced root cause insights
- Better recommendations
- Faster debugging

---

## 🔧 Configuration

### Root Cause Analysis

```python
from callflow_tracer.ai import RootCauseAnalyzer, OpenAIProvider

# With LLM
provider = OpenAIProvider(model="gpt-4o-mini")
analyzer = RootCauseAnalyzer(provider=provider)

# Without LLM (basic analysis)
analyzer = RootCauseAnalyzer()

# Analyze
analysis = analyzer.analyze(
    graph,
    issue_type='performance',  # or 'error', 'bottleneck'
    threshold=0.1  # optional threshold in seconds
)
```

### Anomaly Detection

```python
from callflow_tracer.ai import AnomalyDetector

# Basic
detector = AnomalyDetector()

# With baseline
detector = AnomalyDetector(
    baseline_graphs=[graph1, graph2, graph3],
    sensitivity=2.0  # standard deviations
)

# Detect
anomalies = detector.detect(
    graph,
    detect_types=['time', 'frequency', 'pattern', 'outlier']
)
```

---

## 📚 Examples

See comprehensive examples:
- `examples/root_cause_analysis_example.py` - Root cause analysis demos
- `examples/anomaly_detection_example.py` - Anomaly detection demos
- `examples/advanced_debugging_example.py` - Combined usage

Run examples:
```bash
python examples/root_cause_analysis_example.py
python examples/anomaly_detection_example.py
python examples/advanced_debugging_example.py
```

---

## 🧪 Testing

Run tests:
```bash
python tests/test_advanced_features.py
```

---

## 🎯 Real-World Scenarios

### Scenario 1: Slow API Endpoint

```python
# Detect the issue
with trace_scope() as graph:
    handle_api_request()

anomalies = detect_anomalies(graph)
# Found: time anomaly in database_query()

# Find root cause
root_analysis = analyze_root_cause(graph)
# Root cause: N+1 query pattern in get_user_orders()

# Fix: Batch database queries
```

### Scenario 2: Production Incident

```python
# During incident
with trace_scope() as graph:
    reproduce_issue()

# Quick scan
anomalies = detect_anomalies(graph)
print(f"Severity: {anomalies['severity_summary']['overall_severity']}")

# Deep analysis
root_analysis = analyze_root_cause(graph)
print(root_analysis['llm_insights'])  # AI recommendations

# Action: Fix top root cause
```

### Scenario 3: Performance Regression

```python
# Before deployment
with trace_scope() as before_graph:
    run_tests()

# After deployment
with trace_scope() as after_graph:
    run_tests()

# Compare
before_anomalies = detect_anomalies(before_graph)
after_anomalies = detect_anomalies(after_graph)

if after_anomalies['severity_summary']['total'] > before_anomalies['severity_summary']['total']:
    print("⚠️  Performance regression detected!")
    rollback_deployment()
```

---

## 🚨 Troubleshooting

### No Root Causes Found
- Lower the threshold
- Check if graph has data
- Verify issue_type is correct

### Too Many Anomalies
- Increase sensitivity (e.g., 2.5 or 3.0)
- Use baseline comparison
- Filter by severity

### LLM Insights Not Available
- Configure LLM provider (OpenAI, Anthropic, Gemini)
- Basic analysis still works without LLM
- Set API key environment variable

---

## 📖 API Reference

### `analyze_root_cause(graph, issue_type='performance', threshold=None, provider=None)`

Analyze root causes of issues in a call graph.

**Parameters:**
- `graph` (CallGraph): Trace to analyze
- `issue_type` (str): 'performance', 'error', or 'bottleneck'
- `threshold` (float, optional): Custom threshold
- `provider` (LLMProvider, optional): LLM provider for insights

**Returns:** Dict with root causes, impact analysis, and insights

### `detect_anomalies(graph, baseline_graphs=None, sensitivity=2.0, detect_types=None)`

Detect anomalies in a call graph.

**Parameters:**
- `graph` (CallGraph): Trace to analyze
- `baseline_graphs` (List[CallGraph], optional): Baseline for comparison
- `sensitivity` (float): Sensitivity threshold (std devs)
- `detect_types` (List[str], optional): Types to detect

**Returns:** Dict with anomalies, severity, and recommendations

---

For more information, see:
- [AI Features Documentation](AI_FEATURES.md)
- [Main README](../README.md)
- [Examples](../examples/)

(Truncated - response too long. Continuing in next message...)
