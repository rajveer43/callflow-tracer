# CallFlow Tracer AI Features - Quick Reference

## Feature Matrix

| Feature | Priority | Complexity | Use Case | Import |
|---------|----------|-----------|----------|--------|
| Trace Comparison | 🔥🔥🔥🔥🔥 | Medium | CI/CD gates | `compare_traces` |
| Regression Detection | 🔥🔥🔥🔥🔥 | Medium | Performance testing | `detect_regressions` |
| Continuous Profiling | 🔥🔥🔥🔥🔥 | High | Production monitoring | `ContinuousProfiler` |
| Auto-Fix Generation | 🔥🔥🔥🔥🔥 | Very High | Code optimization | `generate_fixes` |
| Distributed Tracing | 🔥🔥🔥🔥🔥 | High | Microservices | `DistributedTracer` |
| Test Generation | 🔥🔥🔥🔥 | High | Automated testing | `generate_performance_tests` |
| Refactoring Suggestions | 🔥🔥🔥🔥 | High | Code quality | `suggest_refactoring` |
| Cost Analysis | 🔥🔥🔥🔥 | Low | Budget planning | `analyze_costs` |
| Dependency Analysis | 🔥🔥🔥🔥 | Medium | Architecture | `analyze_dependencies` |
| Trend Analysis | 🔥🔥🔥🔥 | Medium | Forecasting | `TrendAnalyzer` |
| Security Analysis | 🔥🔥🔥 | Medium | Compliance | `analyze_security` |
| Alert Management | 🔥🔥🔥🔥 | Low | Notifications | `AlertManager` |
| Load Analysis | 🔥🔥🔥 | Medium | Capacity planning | `analyze_load_behavior` |
| Documentation | 🔥🔥🔥 | Medium | Reporting | `generate_documentation` |
| Instrumentation | 🔥🔥🔥🔥 | Low | Coverage | `suggest_instrumentation` |
| Visual Debugging | 🔥🔥🔥 | Medium | Interactive debug | `VisualDebugger` |

---

## One-Liners

### Trace Comparison
```python
from callflow_tracer.ai import compare_traces
result = compare_traces(baseline, current, threshold=0.1)
```

### Regression Detection
```python
from callflow_tracer.ai import detect_regressions
result = detect_regressions(baseline, current)
```

### Continuous Profiling
```python
from callflow_tracer.ai import ContinuousProfiler
profiler = ContinuousProfiler(sampling_rate=0.01)
profiler.start()
```

### Auto-Fix Generation
```python
from callflow_tracer.ai import generate_fixes
fixes = generate_fixes(graph, root_cause_analysis=analysis)
```

### Distributed Tracing
```python
from callflow_tracer.ai import DistributedTracer
tracer = DistributedTracer(backend='jaeger', service_name='my-service')
```

### Test Generation
```python
from callflow_tracer.ai import generate_performance_tests
tests = generate_performance_tests(graph, test_framework='pytest')
```

### Refactoring Suggestions
```python
from callflow_tracer.ai import suggest_refactoring
suggestions = suggest_refactoring(graph, include_code_examples=True)
```

### Cost Analysis
```python
from callflow_tracer.ai import analyze_costs
costs = analyze_costs(graph, pricing={'compute': 0.0001, 'database': 0.001})
```

### Dependency Analysis
```python
from callflow_tracer.ai import analyze_dependencies
deps = analyze_dependencies(graph)
```

### Trend Analysis
```python
from callflow_tracer.ai import TrendAnalyzer
analyzer = TrendAnalyzer()
for trace in traces: analyzer.add_trace(trace)
trends = analyzer.analyze_trends()
```

### Security Analysis
```python
from callflow_tracer.ai import analyze_security
security = analyze_security(graph)
```

### Alert Management
```python
from callflow_tracer.ai import AlertManager
alerts = AlertManager(webhooks={'slack': 'YOUR_URL'})
alerts.send_alert('high', 'Performance Issue', 'Database slow')
```

### Load Analysis
```python
from callflow_tracer.ai import analyze_load_behavior
analysis = analyze_load_behavior(traces, concurrent_users=[10, 50, 100])
```

### Documentation Generation
```python
from callflow_tracer.ai import generate_documentation
docs = generate_documentation(graph, format='markdown', include_diagrams=True)
```

### Instrumentation Suggestions
```python
from callflow_tracer.ai import suggest_instrumentation
suggestions = suggest_instrumentation(graph)
```

### Visual Debugging
```python
from callflow_tracer.ai import VisualDebugger
debugger = VisualDebugger(graph)
stack = debugger.get_call_stack()
```

---

## Common Workflows

### 1. CI/CD Performance Gate

```python
from callflow_tracer.ai import compare_traces, detect_regressions

# Get baseline and current
baseline = load_baseline_trace()
current = run_performance_test()

# Compare
comparison = compare_traces(baseline, current, threshold=0.1)

# Check for regressions
if comparison['summary']['critical_regressions']:
    print("FAIL: Critical regressions detected")
    exit(1)
else:
    print("PASS: Performance acceptable")
    exit(0)
```

### 2. Production Monitoring

```python
from callflow_tracer.ai import ContinuousProfiler, AlertManager

profiler = ContinuousProfiler(sampling_rate=0.01)
alerts = AlertManager(webhooks={'slack': 'YOUR_URL'})

profiler.start()

# In request handler
def handle_request(req):
    with trace_scope() as graph:
        result = process(req)
    profiler.record_trace(graph)
    
    # Check for anomalies
    snapshot = profiler.get_latest_snapshot()
    if snapshot and snapshot['anomalies']:
        alerts.send_alert('high', 'Anomaly detected', str(snapshot['anomalies']))
    
    return result
```

### 3. Performance Analysis Report

```python
from callflow_tracer.ai import (
    analyze_costs, analyze_dependencies, 
    suggest_refactoring, generate_documentation
)

graph = load_trace()

# Analyze
costs = analyze_costs(graph)
deps = analyze_dependencies(graph)
refactoring = suggest_refactoring(graph)
docs = generate_documentation(graph)

# Report
print(f"Cost: ${costs['total_cost']:.4f}")
print(f"Functions: {deps['total_functions']}")
print(f"Refactoring opportunities: {len(refactoring)}")

# Save documentation
with open('report.md', 'w') as f:
    f.write(docs['content'])
```

### 4. Load Testing Analysis

```python
from callflow_tracer.ai import analyze_load_behavior

# Run load tests at different concurrency levels
traces_10 = run_load_test(concurrent_users=10)
traces_50 = run_load_test(concurrent_users=50)
traces_100 = run_load_test(concurrent_users=100)

# Analyze
analysis = analyze_load_behavior(
    traces=traces_10 + traces_50 + traces_100,
    concurrent_users=[10, 50, 100]
)

# Report
print(f"Breaking point: {analysis['breaking_point']['concurrent_users']} users")
for rec in analysis['scaling_recommendations']:
    print(f"  - {rec}")
```

### 5. Security Audit

```python
from callflow_tracer.ai import analyze_security

graph = load_trace()
security = analyze_security(graph)

print(f"Critical issues: {security['critical_issues']}")
print(f"High issues: {security['high_issues']}")

for issue in security['all_issues']:
    print(f"  {issue['issue_type']}: {issue['function_name']}")

print("\nRecommendations:")
for rec in security['recommendations']:
    print(f"  - {rec}")
```

---

## Configuration Presets

### Development
```python
from callflow_tracer.ai import ContinuousProfiler

profiler = ContinuousProfiler(
    sampling_rate=1.0,           # Profile everything
    aggregation_window='1m',     # Fast feedback
    storage='memory',            # In-memory storage
    anomaly_threshold=1.0        # Sensitive detection
)
```

### Staging
```python
profiler = ContinuousProfiler(
    sampling_rate=0.1,           # 10% sampling
    aggregation_window='5m',
    storage='memory',
    anomaly_threshold=2.0
)
```

### Production
```python
profiler = ContinuousProfiler(
    sampling_rate=0.01,          # 1% sampling
    aggregation_window='10m',    # Longer window
    storage='redis',             # Persistent storage
    anomaly_threshold=3.0        # Less sensitive
)
```

---

## Threshold Recommendations

| Metric | Development | Staging | Production |
|--------|-------------|---------|------------|
| Regression Threshold | 5% | 10% | 15% |
| Z-Score Threshold | 1.0 | 2.0 | 3.0 |
| Sampling Rate | 100% | 10% | 1% |
| Aggregation Window | 1m | 5m | 10m |
| Alert Threshold | Low | Medium | High |

---

## Performance Impact

```
Feature                 Overhead    Sampling    Latency Impact
─────────────────────────────────────────────────────────────
Trace Comparison        <1ms        N/A         None
Regression Detection    <1ms        N/A         None
Continuous Profiling    <0.1ms      1-10%       <1ms
Auto-Fix Generation     100-500ms   N/A         Async
Distributed Tracing     <1ms        N/A         <1ms
Test Generation         <1ms        N/A         None
Cost Analysis           <1ms        N/A         None
Dependency Analysis     <5ms        N/A         None
Trend Analysis          <1ms        N/A         None
Security Analysis       <5ms        N/A         None
Alert Management        <1ms        N/A         <1ms
Load Analysis           <5ms        N/A         None
Documentation           <10ms       N/A         None
Instrumentation         <1ms        N/A         None
Visual Debugging        <1ms        N/A         None
```

---

## Error Handling

```python
from callflow_tracer.ai import compare_traces

try:
    result = compare_traces(baseline, current)
except ValueError as e:
    print(f"Invalid input: {e}")
except Exception as e:
    print(f"Analysis failed: {e}")
    # Fallback to basic comparison
    result = {'error': str(e)}
```

---

## Environment Variables

```bash
# LLM Configuration
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="..."

# Webhook Configuration
export SLACK_WEBHOOK_URL="https://hooks.slack.com/..."
export PAGERDUTY_WEBHOOK_URL="https://events.pagerduty.com/..."

# Tracing Configuration
export JAEGER_AGENT_HOST="localhost"
export JAEGER_AGENT_PORT="6831"
export ZIPKIN_ENDPOINT="http://localhost:9411"
```

---

## Integration with CI/CD

### GitHub Actions
```yaml
- name: Performance Test
  run: |
    python -m pytest tests/performance_test.py
    python scripts/check_performance.py
```

### GitLab CI
```yaml
performance_test:
  script:
    - python -m pytest tests/performance_test.py
    - python scripts/check_performance.py
```

### Jenkins
```groovy
stage('Performance Test') {
    steps {
        sh 'python -m pytest tests/performance_test.py'
        sh 'python scripts/check_performance.py'
    }
}
```

---

## Useful Patterns

### Pattern 1: Baseline Comparison
```python
baseline = load_or_create_baseline()
current = run_test()
result = compare_traces(baseline, current)
if result['summary']['critical_regressions']:
    raise PerformanceRegressionError()
```

### Pattern 2: Continuous Monitoring
```python
profiler = ContinuousProfiler()
profiler.start()
# ... application runs ...
anomalies = profiler.get_anomalies()
if anomalies:
    notify_team(anomalies)
```

### Pattern 3: Automated Optimization
```python
fixes = generate_fixes(graph, root_cause_analysis=analysis)
for fix in fixes:
    if fix['confidence'] > 0.9:
        apply_fix(fix)
        test_fix()
```

### Pattern 4: Cost Optimization
```python
costs = analyze_costs(graph)
for opp in costs['optimization_opportunities']:
    print(f"Save ${opp['potential_savings']}: {opp['recommendation']}")
```

---

## Debugging Tips

1. **Enable verbose logging**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Check trace structure**
   ```python
   import json
   print(json.dumps(graph, indent=2))
   ```

3. **Validate inputs**
   ```python
   assert 'nodes' in graph
   assert 'edges' in graph
   assert graph['total_time'] > 0
   ```

4. **Test with sample data**
   ```python
   from examples import sample_trace
   result = compare_traces(sample_trace, sample_trace)
   ```

---

## Resources

- **Full Guide**: See `AI_FEATURES_GUIDE.md`
- **Examples**: See `examples/` directory
- **Tests**: Run `pytest tests/ai/`
- **API Docs**: Generated with `pdoc`

---

## Version History

- **v1.0.0** (Current): All 16 AI features implemented
- **v0.9.0**: Initial AI features (comparison, regression, profiling)
- **v0.8.0**: Base tracing functionality

---

## Support

- **Issues**: Report on GitHub
- **Discussions**: GitHub Discussions
- **Email**: support@callflow-tracer.dev
