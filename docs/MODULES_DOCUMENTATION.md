# CallFlow Tracer - Complete Module Documentation

## Table of Contents

1. [Core Modules](#core-modules)
2. [AI Modules](#ai-modules)
3. [Integration Modules](#integration-modules)
4. [Utility Modules](#utility-modules)
5. [Export & Visualization](#export--visualization)

---

## Core Modules

### 1. `__init__.py`
**Location**: `callflow_tracer/__init__.py`
**Purpose**: Package initialization and main API exports
**Size**: ~5KB

#### Key Exports:
- `CallTracer` - Main tracing class
- `trace_scope` - Context manager for tracing
- `@trace` - Decorator for function tracing
- `export_html` - HTML export functionality
- `export_json` - JSON export functionality

#### Usage:
```python
from callflow_tracer import CallTracer, trace_scope, trace

# Using context manager
with trace_scope() as graph:
    # Your code here
    pass

# Using decorator
@trace
def my_function():
    pass

# Export results
export_html(graph, 'output.html')
```

---

### 2. `tracer.py`
**Location**: `callflow_tracer/tracer.py`
**Purpose**: Core tracing engine and call graph building
**Size**: ~12KB

#### Key Classes:
- `CallTracer` - Main tracer class
- `TraceNode` - Represents a function in the call graph
- `TraceEdge` - Represents a call relationship

#### Key Methods:
```python
class CallTracer:
    def __init__(self, enabled=True):
        """Initialize tracer"""
    
    def start(self):
        """Start tracing"""
    
    def stop(self):
        """Stop tracing"""
    
    def get_graph(self):
        """Get execution trace graph"""
    
    def get_call_tree(self):
        """Get call tree structure"""
    
    def get_statistics(self):
        """Get performance statistics"""
```

#### Features:
- Automatic function call tracking
- Execution time measurement
- Call frequency counting
- Memory usage tracking
- Call graph construction

#### Example:
```python
from callflow_tracer import CallTracer

tracer = CallTracer()
tracer.start()

# Your code here
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(10)

tracer.stop()
graph = tracer.get_graph()
```

---

### 3. `profiling.py`
**Location**: `callflow_tracer/profiling.py`
**Purpose**: Performance profiling utilities
**Size**: ~6.5KB

#### Key Functions:
```python
def profile_function(func, *args, **kwargs):
    """Profile a single function call"""

def get_cpu_profile():
    """Get CPU profiling data"""

def get_memory_profile():
    """Get memory profiling data"""

def compare_profiles(profile1, profile2):
    """Compare two profiles"""
```

#### Features:
- CPU time measurement
- Memory allocation tracking
- Call count statistics
- Performance comparison

#### Example:
```python
from callflow_tracer.profiling import profile_function

def slow_function():
    total = 0
    for i in range(1000000):
        total += i
    return total

profile = profile_function(slow_function)
print(f"Time: {profile['time']:.3f}s")
print(f"Memory: {profile['memory']:.2f}MB")
```

---

## AI Modules

### 4. `ai/comparison.py`
**Location**: `callflow_tracer/ai/comparison.py`
**Purpose**: Trace comparison and regression detection
**Size**: ~22KB

#### Key Classes:
- `TraceComparator` - Compares two execution traces
- `NodeComparison` - Comparison result for a node
- `ComparisonResult` - Overall comparison results

#### Key Methods:
```python
class TraceComparator:
    def compare(self, before_graph, after_graph, threshold=0.1):
        """Compare two traces"""
    
    def get_regressions(self):
        """Get performance regressions"""
    
    def get_improvements(self):
        """Get performance improvements"""
```

#### Example:
```python
from callflow_tracer.ai import compare_traces

result = compare_traces(baseline, current, threshold=0.1)
print(f"Regressions: {len(result['regressions'])}")
print(f"Improvements: {len(result['improvements'])}")
```

---

### 5. `ai/regression_detector.py`
**Location**: `callflow_tracer/ai/regression_detector.py`
**Purpose**: Statistical regression detection
**Size**: ~14KB

#### Key Classes:
- `RegressionDetector` - Detects performance regressions
- `RegressionMetric` - Metric data for regression
- `RegressionResult` - Detection results

#### Features:
- Z-score based detection
- Historical statistics
- Severity classification
- Automated recommendations

#### Example:
```python
from callflow_tracer.ai import detect_regressions

result = detect_regressions(baseline, current, z_threshold=2.0)
if result['has_regression']:
    print(f"Severity: {result['severity']}")
```

---

### 6. `ai/continuous_profiler.py`
**Location**: `callflow_tracer/ai/continuous_profiler.py`
**Purpose**: Production profiling with sampling
**Size**: ~16KB

#### Key Classes:
- `ContinuousProfiler` - Always-on profiler
- `ProfileSnapshot` - Profiling snapshot
- `BaselineProfile` - Baseline profile data

#### Features:
- Configurable sampling rate
- Aggregation windows
- Anomaly detection
- Background threading

#### Example:
```python
from callflow_tracer.ai import ContinuousProfiler

profiler = ContinuousProfiler(sampling_rate=0.01)
profiler.start()

# Your code here
profiler.record_trace(graph)

anomalies = profiler.get_anomalies()
```

---

### 7. `ai/auto_fixer.py`
**Location**: `callflow_tracer/ai/auto_fixer.py`
**Purpose**: Automatic code fix generation
**Size**: ~14KB

#### Key Classes:
- `AutoFixer` - Generates code fixes
- `CodeFix` - Individual fix data

#### Detects:
- N+1 query patterns
- Inefficient loops
- Memory leaks
- Missing caches
- Excessive recursion

#### Example:
```python
from callflow_tracer.ai import generate_fixes

fixes = generate_fixes(graph, root_cause_analysis=analysis)
for fix in fixes:
    if fix['confidence'] > 0.8:
        print(f"Fix: {fix['issue']}")
```

---

### 8. `ai/distributed_tracer.py`
**Location**: `callflow_tracer/ai/distributed_tracer.py`
**Purpose**: Distributed tracing integration
**Size**: ~14KB

#### Key Classes:
- `DistributedTracer` - Distributed tracing
- `DistributedSpan` - Span data
- `DistributedTraceAnalysis` - Analysis results

#### Supported Backends:
- Jaeger
- Zipkin
- OpenTelemetry

#### Example:
```python
from callflow_tracer.ai import DistributedTracer

tracer = DistributedTracer(backend='jaeger', service_name='api')
with tracer.trace_scope('request'):
    # Your code here
    pass
```

---

### 9. `ai/test_generator.py`
**Location**: `callflow_tracer/ai/test_generator.py`
**Purpose**: Automatic test generation
**Size**: ~16KB

#### Key Classes:
- `TestGenerator` - Generates tests
- `GeneratedTest` - Test data

#### Supported Frameworks:
- pytest
- unittest

#### Example:
```python
from callflow_tracer.ai import generate_performance_tests

tests = generate_performance_tests(graph, test_framework='pytest')
for test in tests:
    with open(f"test_{test['test_name']}.py", 'w') as f:
        f.write(test['test_code'])
```

---

### 10. `ai/refactoring_suggester.py`
**Location**: `callflow_tracer/ai/refactoring_suggester.py`
**Purpose**: Code refactoring recommendations
**Size**: ~12KB

#### Key Classes:
- `RefactoringSuggester` - Generates suggestions
- `RefactoringSuggestion` - Suggestion data

#### Detects:
- Long functions
- High complexity
- Tight coupling
- N+1 patterns
- Dead code

#### Example:
```python
from callflow_tracer.ai import suggest_refactoring

suggestions = suggest_refactoring(graph, include_code_examples=True)
for s in suggestions:
    print(f"{s['function_name']}: {s['recommendation']}")
```

---

### 11. `ai/cost_analyzer.py`
**Location**: `callflow_tracer/ai/cost_analyzer.py`
**Purpose**: Infrastructure cost analysis
**Size**: ~12KB

#### Key Classes:
- `CostAnalyzer` - Analyzes costs
- `FunctionCost` - Cost per function
- `CostAnalysis` - Analysis results

#### Features:
- Compute cost calculation
- Database cost tracking
- API call costs
- Optimization suggestions

#### Example:
```python
from callflow_tracer.ai import analyze_costs

costs = analyze_costs(graph, pricing={
    'compute': 0.0001,
    'database': 0.001
})
print(f"Total: ${costs['total_cost']:.4f}")
```

---

### 12. `ai/dependency_analyzer.py`
**Location**: `callflow_tracer/ai/dependency_analyzer.py`
**Purpose**: Code dependency analysis
**Size**: ~14KB

#### Key Classes:
- `DependencyAnalyzer` - Analyzes dependencies
- `DependencyAnalysis` - Analysis results

#### Features:
- Circular dependency detection
- Coupling analysis
- Dead code detection
- Critical path computation

#### Example:
```python
from callflow_tracer.ai import analyze_dependencies

deps = analyze_dependencies(graph)
print(f"Circular: {deps['circular_dependencies']}")
print(f"Coupling: {deps['tight_coupling']}")
```

---

### 13. `ai/trend_analyzer.py`
**Location**: `callflow_tracer/ai/trend_analyzer.py`
**Purpose**: Performance trend analysis
**Size**: ~16KB

#### Key Classes:
- `TrendAnalyzer` - Analyzes trends
- `FunctionTrend` - Trend data
- `TrendAnalysisResult` - Results

#### Features:
- Linear regression analysis
- Exponential smoothing
- Degradation detection
- Predictive forecasting

#### Example:
```python
from callflow_tracer.ai import TrendAnalyzer

analyzer = TrendAnalyzer(window_size=10)
for trace in traces:
    analyzer.add_trace(trace)

trends = analyzer.analyze_trends()
```

---

### 14. `ai/security_analyzer.py`
**Location**: `callflow_tracer/ai/security_analyzer.py`
**Purpose**: Security vulnerability detection
**Size**: ~10KB

#### Key Classes:
- `SecurityAnalyzer` - Analyzes security
- `SecurityIssue` - Issue data

#### Detects:
- Insecure functions
- SQL injection risks
- Weak cryptography
- Excessive permissions
- PII patterns

#### Example:
```python
from callflow_tracer.ai import analyze_security

security = analyze_security(graph)
print(f"Critical: {security['critical_issues']}")
```

---

### 15. `ai/alert_manager.py`
**Location**: `callflow_tracer/ai/alert_manager.py`
**Purpose**: Alert management and webhooks
**Size**: ~14KB

#### Key Classes:
- `AlertManager` - Manages alerts
- `Alert` - Alert data
- `AlertRule` - Alert rules

#### Supported Channels:
- Slack
- PagerDuty
- Email

#### Example:
```python
from callflow_tracer.ai import AlertManager

alerts = AlertManager(webhooks={
    'slack': 'https://hooks.slack.com/...'
})
alerts.send_alert('high', 'Issue', 'Details')
```

---

### 16. `ai/load_analyzer.py`
**Location**: `callflow_tracer/ai/load_analyzer.py`
**Purpose**: Load testing analysis
**Size**: ~14KB

#### Key Classes:
- `LoadAnalyzer` - Analyzes load tests
- `LoadTestResult` - Result data
- `LoadAnalysis` - Analysis results

#### Features:
- Bottleneck identification
- Breaking point detection
- Capacity forecasting
- Scaling recommendations

#### Example:
```python
from callflow_tracer.ai import analyze_load_behavior

analysis = analyze_load_behavior(traces, concurrent_users=[10, 50, 100])
print(f"Breaking point: {analysis['breaking_point']}")
```

---

### 17. `ai/doc_generator.py`
**Location**: `callflow_tracer/ai/doc_generator.py`
**Purpose**: Automatic documentation generation
**Size**: ~14KB

#### Key Classes:
- `DocumentationGenerator` - Generates docs
- `Documentation` - Doc data

#### Formats:
- Markdown
- HTML
- Mermaid diagrams

#### Example:
```python
from callflow_tracer.ai import generate_documentation

docs = generate_documentation(graph, format='markdown')
with open('report.md', 'w') as f:
    f.write(docs['content'])
```

---

### 18. `ai/instrumentation_suggester.py`
**Location**: `callflow_tracer/ai/instrumentation_suggester.py`
**Purpose**: Instrumentation coverage suggestions
**Size**: ~6KB

#### Key Classes:
- `InstrumentationSuggester` - Suggests instrumentation
- `InstrumentationSuggestion` - Suggestion data

#### Features:
- Missing coverage detection
- High-value targets
- Breakpoint recommendations

#### Example:
```python
from callflow_tracer.ai import suggest_instrumentation

suggestions = suggest_instrumentation(graph)
print(f"Missing: {suggestions['missing_coverage']}")
```

---

### 19. `ai/visual_debugger.py`
**Location**: `callflow_tracer/ai/visual_debugger.py`
**Purpose**: Interactive visual debugging
**Size**: ~12KB

#### Key Classes:
- `VisualDebugger` - Visual debugging
- `DebugFrame` - Frame data
- `ExecutionEvent` - Event data

#### Features:
- Call stack inspection
- Variable inspection
- Execution timeline
- Performance hotspots

#### Example:
```python
from callflow_tracer.ai import VisualDebugger

debugger = VisualDebugger(graph)
stack = debugger.get_call_stack()
hotspots = debugger.get_performance_hotspots()
```

---

## Integration Modules

### 20. `integrations/` Directory
**Location**: `callflow_tracer/integrations/`
**Purpose**: Third-party service integrations

#### Modules:
- `slack.py` - Slack integration
- `pagerduty.py` - PagerDuty integration
- `datadog.py` - Datadog integration
- `newrelic.py` - New Relic integration

#### Example:
```python
from callflow_tracer.integrations import SlackIntegration

slack = SlackIntegration(webhook_url='...')
slack.send_message('Performance alert!')
```

---

## Utility Modules

### 21. `cli.py`
**Location**: `callflow_tracer/cli.py`
**Purpose**: Command-line interface
**Size**: ~36KB

#### Key Commands:
```bash
# Basic tracing
callflow-tracer trace script.py

# Generate report
callflow-tracer report trace.json

# Compare traces
callflow-tracer compare trace1.json trace2.json

# Export visualization
callflow-tracer export trace.json --format html
```

#### Features:
- Script tracing
- Report generation
- Trace comparison
- Format conversion
- Batch processing

---

### 22. `code_quality.py`
**Location**: `callflow_tracer/code_quality.py`
**Purpose**: Code quality analysis
**Size**: ~23KB

#### Key Classes:
- `CodeQualityAnalyzer` - Analyzes code quality
- `QualityMetric` - Quality metrics
- `QualityReport` - Quality report

#### Metrics:
- Cyclomatic complexity
- Code duplication
- Function length
- Coupling metrics
- Cohesion metrics

#### Example:
```python
from callflow_tracer.code_quality import CodeQualityAnalyzer

analyzer = CodeQualityAnalyzer()
report = analyzer.analyze(graph)
print(f"Complexity: {report['avg_complexity']}")
```

---

### 23. `code_churn.py`
**Location**: `callflow_tracer/code_churn.py`
**Purpose**: Code churn analysis
**Size**: ~14KB

#### Key Classes:
- `CodeChurnAnalyzer` - Analyzes code churn
- `ChurnMetrics` - Churn metrics

#### Features:
- Change frequency tracking
- Hotspot identification
- Risk assessment
- Refactoring priority

#### Example:
```python
from callflow_tracer.code_churn import CodeChurnAnalyzer

analyzer = CodeChurnAnalyzer()
metrics = analyzer.analyze(git_log)
print(f"Hotspots: {metrics['hotspots']}")
```

---

### 24. `memory_leak_detector.py`
**Location**: `callflow_tracer/memory_leak_detector.py`
**Purpose**: Memory leak detection
**Size**: ~14KB

#### Key Classes:
- `MemoryLeakDetector` - Detects leaks
- `LeakPattern` - Leak pattern data
- `LeakReport` - Leak report

#### Features:
- Reference cycle detection
- Unreleased resource tracking
- Memory growth analysis
- Leak pattern matching

#### Example:
```python
from callflow_tracer.memory_leak_detector import MemoryLeakDetector

detector = MemoryLeakDetector()
leaks = detector.detect(graph)
print(f"Potential leaks: {len(leaks)}")
```

---

### 25. `memory_leak_visualizer.py`
**Location**: `callflow_tracer/memory_leak_visualizer.py`
**Purpose**: Memory leak visualization
**Size**: ~18KB

#### Key Classes:
- `MemoryLeakVisualizer` - Visualizes leaks
- `LeakVisualization` - Visualization data

#### Features:
- Interactive visualization
- Reference graph display
- Memory timeline
- Leak highlighting

#### Example:
```python
from callflow_tracer.memory_leak_visualizer import MemoryLeakVisualizer

viz = MemoryLeakVisualizer()
html = viz.visualize(leaks)
with open('leaks.html', 'w') as f:
    f.write(html)
```

---

### 26. `predictive_analysis.py`
**Location**: `callflow_tracer/predictive_analysis.py`
**Purpose**: Predictive performance analysis
**Size**: ~22KB

#### Key Classes:
- `PredictiveAnalyzer` - Predictive analysis
- `Prediction` - Prediction data
- `PredictionModel` - ML model

#### Features:
- Performance forecasting
- Anomaly prediction
- Bottleneck prediction
- Capacity planning

#### Example:
```python
from callflow_tracer.predictive_analysis import PredictiveAnalyzer

analyzer = PredictiveAnalyzer()
predictions = analyzer.predict(historical_traces)
print(f"Predicted bottleneck: {predictions['bottleneck']}")
```

---

### 27. `async_tracer.py`
**Location**: `callflow_tracer/async_tracer.py`
**Purpose**: Asynchronous code tracing
**Size**: ~9KB

#### Key Classes:
- `AsyncTracer` - Traces async code
- `AsyncSpan` - Async span data

#### Features:
- Async/await tracking
- Coroutine tracing
- Task correlation
- Concurrency analysis

#### Example:
```python
from callflow_tracer.async_tracer import AsyncTracer

tracer = AsyncTracer()
tracer.start()

# Async code here
await my_async_function()

tracer.stop()
graph = tracer.get_graph()
```

---

### 28. `comparison.py`
**Location**: `callflow_tracer/comparison.py`
**Purpose**: Trace comparison utilities
**Size**: ~22KB

#### Key Functions:
```python
def compare_traces(trace1, trace2):
    """Compare two traces"""

def get_diff(trace1, trace2):
    """Get differences"""

def generate_comparison_report(comparison):
    """Generate report"""
```

#### Example:
```python
from callflow_tracer.comparison import compare_traces

diff = compare_traces(baseline, current)
print(f"Differences: {diff}")
```

---

### 29. `flamegraph.py`
**Location**: `callflow_tracer/flamegraph.py`
**Purpose**: Flamegraph generation
**Size**: ~14KB

#### Key Classes:
- `FlamegraphGenerator` - Generates flamegraphs
- `FlamegraphFrame` - Frame data

#### Features:
- SVG generation
- Interactive visualization
- Color coding
- Zoom/search functionality

#### Example:
```python
from callflow_tracer.flamegraph import FlamegraphGenerator

gen = FlamegraphGenerator()
svg = gen.generate(graph)
with open('flamegraph.svg', 'w') as f:
    f.write(svg)
```

---

### 30. `flamegraph_enhanced.py`
**Location**: `callflow_tracer/flamegraph_enhanced.py`
**Purpose**: Enhanced flamegraph features
**Size**: ~20KB

#### Features:
- Advanced filtering
- Statistical analysis
- Custom color schemes
- Export options

#### Example:
```python
from callflow_tracer.flamegraph_enhanced import EnhancedFlamegraph

fg = EnhancedFlamegraph()
html = fg.generate_interactive(graph)
```

---

### 31. `jupyter.py`
**Location**: `callflow_tracer/jupyter.py`
**Purpose**: Jupyter notebook integration
**Size**: ~8KB

#### Key Classes:
- `JupyterTracer` - Jupyter integration
- `NotebookVisualizer` - Visualization

#### Features:
- Inline visualization
- Interactive widgets
- Cell-level tracing
- Notebook export

#### Example:
```python
# In Jupyter notebook
from callflow_tracer.jupyter import JupyterTracer

tracer = JupyterTracer()
tracer.start()

# Your code here

tracer.display()
```

---

## Export & Visualization

### 32. `exporter.py`
**Location**: `callflow_tracer/exporter.py`
**Purpose**: Export to multiple formats
**Size**: ~209KB (largest module)

#### Key Classes:
- `HTMLExporter` - HTML export
- `JSONExporter` - JSON export
- `CSVExporter` - CSV export
- `SVGExporter` - SVG export

#### Formats Supported:
- HTML (interactive)
- JSON (structured)
- CSV (tabular)
- SVG (vector graphics)
- Flamegraph (performance)

#### Example:
```python
from callflow_tracer import export_html, export_json

export_html(graph, 'output.html')
export_json(graph, 'output.json')
```

---

## Module Dependency Graph

```
tracer.py (core)
    ├── profiling.py
    ├── comparison.py
    ├── flamegraph.py
    ├── async_tracer.py
    └── exporter.py (largest)
        ├── jupyter.py
        └── flamegraph_enhanced.py

ai/ (AI features)
    ├── comparison.py
    ├── regression_detector.py
    ├── continuous_profiler.py
    ├── auto_fixer.py
    ├── distributed_tracer.py
    ├── test_generator.py
    ├── refactoring_suggester.py
    ├── cost_analyzer.py
    ├── dependency_analyzer.py
    ├── trend_analyzer.py
    ├── security_analyzer.py
    ├── alert_manager.py
    ├── load_analyzer.py
    ├── doc_generator.py
    ├── instrumentation_suggester.py
    └── visual_debugger.py

Analysis Modules
    ├── code_quality.py
    ├── code_churn.py
    ├── memory_leak_detector.py
    ├── memory_leak_visualizer.py
    └── predictive_analysis.py

Integration
    ├── integrations/
    ├── cli.py
    └── jupyter.py
```

---

## Quick Reference

### Most Used Modules:
1. **tracer.py** - Start here for basic tracing
2. **exporter.py** - Export results
3. **ai/comparison.py** - Compare traces
4. **cli.py** - Command-line usage

### For Performance Analysis:
- `profiling.py` - Basic profiling
- `predictive_analysis.py` - Forecasting
- `code_quality.py` - Quality metrics

### For Debugging:
- `memory_leak_detector.py` - Memory issues
- `ai/visual_debugger.py` - Interactive debugging
- `async_tracer.py` - Async code

### For Production:
- `ai/continuous_profiler.py` - Always-on profiling
- `ai/alert_manager.py` - Alerting
- `integrations/` - Third-party services

---

## Summary

| Module | Purpose | Size | Priority |
|--------|---------|------|----------|
| tracer.py | Core tracing | 12KB | 🔥🔥🔥 |
| exporter.py | Export formats | 209KB | 🔥🔥🔥 |
| ai/comparison.py | Trace comparison | 22KB | 🔥🔥🔥 |
| profiling.py | Performance profiling | 6.5KB | 🔥🔥 |
| code_quality.py | Quality analysis | 23KB | 🔥🔥 |
| memory_leak_detector.py | Memory leaks | 14KB | 🔥🔥 |
| cli.py | Command-line | 36KB | 🔥🔥 |
| predictive_analysis.py | Forecasting | 22KB | 🔥 |

---

**Total Codebase**: ~1000+ KB across 32 modules
**AI Features**: 16 specialized modules
**Export Formats**: 4+ formats supported
**Integration Points**: Slack, PagerDuty, Datadog, New Relic

