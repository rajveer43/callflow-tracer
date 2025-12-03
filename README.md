# CallFlow Tracer 🧠

> **A comprehensive Python library for tracing, profiling, and visualizing function call flows with interactive graphs, call graphs, and OpenTelemetry export. Perfect for understanding code flow, debugging performance bottlenecks, and optimizing code with production-ready observability.**

[![PyPI version](https://badge.fury.io/py/callflow-tracer.svg)](https://badge.fury.io/py/callflow-tracer)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/callflow-tracer)](https://pepy.tech/project/callflow-tracer)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Features

### Advanced OpenTelemetry Export (Production Ready!)

Export your traces to any OpenTelemetry-compatible backend with production-ready features:

#### Quick Examples

```python
# Basic OTel export
from callflow_tracer.opentelemetry_exporter import export_callgraph_to_otel

with trace_scope() as graph:
    your_code()

result = export_callgraph_to_otel(
    graph,
    service_name="my-service",
    sampling_rate=0.5,
    environment="production"
)
print(f"Exported {result['span_count']} spans")

# CLI usage
callflow-tracer otel trace.json --service-name my-service --sampling-rate 0.5
```

#### Key Features

- **Exemplars**: Link custom metrics to trace spans for correlation
- **Sampling**: Configurable sampling rates (0.0-1.0) to reduce overhead
- **Resource Attributes**: Attach metadata (version, environment, host)
- **Config Files**: YAML/JSON configuration with auto-detection
- **Environment Variables**: CALLFLOW_OTEL_* overrides for deployment
- **Multiple Exporters**: Console, OTLP/gRPC, OTLP/HTTP, Jaeger
- **Semantic Conventions**: OpenTelemetry standard attributes
- **Batch Processing**: Configurable processor settings
- **CLI Integration**: Dedicated `otel` subcommand with advanced options
- **VS Code Integration**: Advanced export with interactive prompts
- **Python API**: Direct function calls for programmatic use
- **Comprehensive Tests**: 40+ unit tests + integration tests
- **Full Documentation**: 1,500+ lines of guides and examples

### Advanced SLA/SLO & Experiments

Multi-dimensional SLAs with rolling windows and dynamic thresholds:

```python
from callflow_tracer.custom_metrics import (
    SLO, SLI, ErrorBudgetTracker, ExperimentAnalyzer, track_metric
)

# Availability SLO (>= 99% success in last hour)
slo = SLO(
    name="checkout-availability",
    objective=0.99,
    time_window=3600,
    sli_type="availability",
    metric_name="checkout_success",  # 1=success, 0=failure
)
print(slo.compute(tags={"service": "api"}))

# Error budget
budget = ErrorBudgetTracker(slo).compute_budget(tags={"service": "api"})
print(budget)

# Canary comparison (baseline vs canary)
report = ExperimentAnalyzer.canary(
    metric_name="latency_ms",
    baseline_value="baseline",
    canary_value="canary",
    group_tag_key="deployment",
    time_window=1800,
)
print(report)
```

#### Key Features

- **Multi-dimensional SLAs**: Multiple conditions per metric with operators (gt/lt/eq/gte/lte)
- **Rolling Time Windows**: Compliance over configurable windows (e.g., 1m, 5m, 1h)
- **Dynamic Thresholds**: Auto-adjust using IQR-based statistics (stdlib-only)
- **SLI/SLO Framework**: Availability, error-rate, latency percentile targets
- **Error Budgets**: Compute allowed error, consumed/remaining budget, burn rate
- **Canary & A/B Analysis**: Compare baseline vs canary, or A vs B variants via tags with p95 and deltas

### Code Quality Analysis

Analyze code quality metrics with complexity analysis and technical debt scoring:

```bash
# Analyze code quality
callflow-tracer quality . -o quality_report.html

# Track trends over time
callflow-tracer quality . --track-trends --format json
```

```python
from callflow_tracer.code_quality import analyze_codebase

results = analyze_codebase("./src")
print(f"Average Complexity: {results['summary']['average_complexity']:.2f}")
print(f"Critical Issues: {results['summary']['critical_issues']}")
```

#### Key Features

- **Complexity Metrics**: Cyclomatic and cognitive complexity calculation
- **Maintainability Index**: 0-100 scale with detailed metrics
- **Technical Debt Scoring**: Identify and quantify technical debt
- **Quality Trends**: Track code quality over time
- **Halstead Metrics**: Volume, difficulty, effort analysis

### Predictive Analysis

Predict future performance issues and capacity planning:

```bash
# Predict performance issues
callflow-tracer predict history.json -o predictions.html
```

```python
from callflow_tracer.predictive_analysis import PerformancePredictor

predictor = PerformancePredictor("history.json")
predictions = predictor.predict_performance_issues(current_trace)

for pred in predictions:
    if pred.risk_level == "Critical":
        print(f"CRITICAL: {pred.function_name}")
        print(f"  Predicted time: {pred.predicted_time:.4f}s")
```

#### Key Features

- **Performance Prediction**: Predict future performance degradation
- **Capacity Planning**: Forecast when limits will be reached
- **Scalability Analysis**: Assess code scalability characteristics
- **Resource Forecasting**: Predict resource usage trends
- **Risk Assessment**: Multi-factor risk evaluation
- **Confidence Scoring**: Data-driven confidence levels

### Code Churn Analysis

Identify high-risk files using git history and quality correlation:

```bash
# Analyze code churn
callflow-tracer churn . --days 90 -o churn_report.html
```

```python
from callflow_tracer.code_churn import generate_churn_report

report = generate_churn_report(".", days=90)
print(f"High risk files: {report['summary']['high_risk_files']}")

for hotspot in report['hotspots'][:5]:
    print(f"{hotspot['file_path']}: {hotspot['hotspot_score']:.1f}")
```

#### Key Features

- **Git History Analysis**: Analyze commits and changes
- **Hotspot Identification**: Find high-risk files
- **Churn Correlation**: Correlate with quality metrics
- **Bug Prediction**: Estimate bug correlation
- **Risk Assessment**: Comprehensive risk evaluation
- **Actionable Recommendations**: Specific improvement suggestions

### Framework Integration Setup

Ready-to-use integrations for popular Python frameworks:

#### Supported Frameworks

- **Flask Integration**: Automatic request tracing
- **FastAPI Integration**: Async endpoint tracing
- **Django Integration**: View and middleware tracing
- **SQLAlchemy Integration**: Database query monitoring
- **psycopg2 Integration**: PostgreSQL query tracing
- **Code Snippet Insertion**: Ready-to-use integration code

### Command-Line Interface

Complete terminal interface for all features - no Python code needed:

#### Quick Start

```bash
# Analyze code quality
callflow-tracer quality . -o quality_report.html

# Predict performance issues
callflow-tracer predict history.json -o predictions.html

# Analyze code churn
callflow-tracer churn . --days 90 -o churn_report.html

# Trace function calls
callflow-tracer trace script.py -o trace.html

# Generate flamegraph
callflow-tracer flamegraph script.py -o flamegraph.html

# Export to OpenTelemetry
callflow-tracer otel trace.json --service-name my-service
```

#### Key Features

- **11 CLI Commands**: Complete CLI for all features
- **No Python Code Needed**: Run analysis from terminal
- **HTML/JSON Output**: Multiple export formats
- **Progress Notifications**: Real-time feedback
- **Batch Processing**: Analyze entire projects

### Advanced Visualization Features

#### Flamegraph Features

- **Statistics Dashboard**: Total time, calls, depth, slowest function
- **5 Color Schemes**: Choose the best view for your analysis
- **Real-time Search**: Find functions instantly
- **SVG Export**: High-quality graphics for reports
- **Performance Colors**: Green=fast, Red=slow (perfect for optimization!)
- **Responsive Design**: Works on all screen sizes

#### Profiling Features

- **CPU Profiling**: cProfile integration with detailed statistics
- **Memory Tracking**: Current and peak memory usage
- **I/O Wait Time**: Measure time spent waiting
- **Health Indicators**: Visual performance status
- **Bottleneck Detection**: Automatically identifies slow functions

#### Visualization Features

- **Interactive Network**: Zoom, pan, explore call relationships
- **Multiple Layouts**: Hierarchical, Force-Directed, Circular, Timeline
- **Module Filtering**: Focus on specific parts of your code
- **Rich Tooltips**: Detailed metrics on hover
- **Color Coding**: Performance-based coloring

#### Enhanced Features

- **Statistics Panel**: See total functions, calls, execution time, and bottlenecks at a glance
- **Search Functionality**: Find specific functions quickly in large graphs
- **SVG Export**: Export high-quality vector graphics for presentations
- **Modern UI**: Responsive design with gradients and smooth animations
- **Fixed CPU Profiling**: Working cProfile integration with actual execution times
- **Working Module Filter**: Filter by Python module with smooth animations
- **All Layouts Working**: Hierarchical, Force-Directed, Circular, Timeline
- **JSON Export**: Fixed export functionality with proper metadata
- **Jupyter Integration**: Magic commands and inline visualizations

### Core Features

#### Core Capabilities

### **Core Capabilities**
- **Simple API**: Decorator or context manager - your choice
- **Interactive Visualizations**: Beautiful HTML graphs with zoom, pan, and filtering
- **Async/Await Support**: Full support for modern async Python code
- **Comparison Mode**: Side-by-side before/after optimization analysis
- **Memory Leak Detection**: Track allocations, find leaks, visualize growth
- **Performance Profiling**: CPU time, memory usage, I/O wait tracking
- **Flamegraph Support**: Identify bottlenecks with flame graphs
- **Call Graph Analysis**: Understand function relationships
- **Jupyter Integration**: Works seamlessly in notebooks
- **Multiple Export Formats**: HTML, JSON, SVG
- **Zero Config**: Works out of the box

### **OpenTelemetry Export**
- **Production Ready**: Full OTel compliance
- **Exemplars**: Link metrics to spans
- **Sampling**: Reduce overhead in production
- **Config Management**: YAML/JSON + environment variables
- **Multiple Exporters**: Console, OTLP, Jaeger
- **CLI Integration**: `callflow-tracer otel` command
- **VS Code Integration**: Export from editor

### **Code Quality Analysis**
- **Complexity Metrics**: Cyclomatic and cognitive complexity
- **Maintainability Index**: 0-100 scale with detailed analysis
- **Technical Debt Scoring**: Identify and quantify debt
- **Quality Trends**: Track metrics over time
- **Halstead Metrics**: Volume, difficulty, effort analysis

### **Predictive Analysis**
- **Performance Prediction**: Predict future degradation
- **Capacity Planning**: Forecast limit breaches
- **Scalability Analysis**: Assess scalability characteristics
- **Resource Forecasting**: Predict resource usage
- **Risk Assessment**: Multi-factor evaluation

### **Code Churn Analysis**
- **Git History Analysis**: Analyze commits and changes
- **Hotspot Identification**: Find high-risk files
- **Quality Correlation**: Correlate with quality metrics
- **Bug Prediction**: Estimate bug correlation
- **Actionable Recommendations**: Specific improvements

### **Command-Line Interface**
- **11 CLI Commands**: Complete terminal interface (including `otel`)
- **No Code Required**: Run analysis from command line
- **Batch Processing**: Analyze entire projects
- **Multiple Formats**: HTML and JSON output

---

## 🔥 Advanced Visualization Features

### **Flamegraph Features**
- **Statistics Dashboard**: Total time, calls, depth, slowest function
- **5 Color Schemes**: Choose the best view for your analysis
- **Real-time Search**: Find functions instantly
- **SVG Export**: High-quality graphics for reports
- **Performance Colors**: Green=fast, Red=slow (perfect for optimization!)
- **Responsive Design**: Works on all screen sizes

### **Profiling Features**
- **CPU Profiling**: cProfile integration with detailed statistics
- **Memory Tracking**: Current and peak memory usage
- **I/O Wait Time**: Measure time spent waiting
- **Health Indicators**: Visual performance status
- **Bottleneck Detection**: Automatically identifies slow functions

### **Visualization Features**
- **Interactive Network**: Zoom, pan, explore call relationships
- **Multiple Layouts**: Hierarchical, Force-Directed, Circular, Timeline
- **Module Filtering**: Focus on specific parts of your code
- **Rich Tooltips**: Detailed metrics on hover
- **Color Coding**: Performance-based coloring

### **Enhanced Features**
- **Statistics Panel**: See total functions, calls, execution time, and bottlenecks at a glance
- **Search Functionality**: Find specific functions quickly in large graphs
- **SVG Export**: Export high-quality vector graphics for presentations
- **Modern UI**: Responsive design with gradients and smooth animations
- **Fixed CPU Profiling**: Working cProfile integration with actual execution times
- **Working Module Filter**: Filter by Python module with smooth animations
- **All Layouts Working**: Hierarchical, Force-Directed, Circular, Timeline
- **JSON Export**: Fixed export functionality with proper metadata
- **Jupyter Integration**: Magic commands and inline visualizations

---

## 🚀 Quick Start

### Installation

#### From PyPI (Recommended)
```bash
# Basic installation
pip install callflow-tracer

# With OpenTelemetry support
pip install callflow-tracer[otel]

# With all optional dependencies
pip install callflow-tracer[all]
```

#### From Source
```bash
git clone https://github.com/rajveer43/callflow-tracer.git
cd callflow-tracer
pip install -e .

# With OpenTelemetry support
pip install -e ".[otel]"
```

#### For Development
```bash
pip install -e .[dev]
```

#### OpenTelemetry Dependencies

The OpenTelemetry export functionality requires additional packages. Install with:

```bash
pip install callflow-tracer[otel]
```

This includes:
- `opentelemetry-api>=1.20.0` - Core OpenTelemetry API
- `opentelemetry-sdk>=1.20.0` - OpenTelemetry SDK
- `opentelemetry-exporter-otlp>=1.20.0` - OTLP exporter
- `opentelemetry-exporter-jaeger>=1.20.0` - Jaeger exporter
- `opentelemetry-exporter-prometheus>=1.20.0` - Prometheus exporter
- `protobuf>=3.20.0` - Protocol buffers for OTLP
- `grpcio>=1.50.0` - gRPC transport

**Note**: OpenTelemetry support is optional. The core library works without these dependencies.

### Basic Usage

```python
from callflow_tracer import trace_scope, export_html

def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

# Trace execution
with trace_scope() as graph:
    result = calculate_fibonacci(10)
    print(f"Result: {result}")

# Export to interactive HTML
export_html(graph, "fibonacci.html", title="Fibonacci Call Graph")
```

Open `fibonacci.html` in your browser to see the interactive visualization!

---

## 🔥 OpenTelemetry Export

Export your traces to any OpenTelemetry-compatible backend with production-ready features:

### Quick Start

```bash
# Generate config file
callflow-tracer otel --init-config

# Export trace to OTel
callflow-tracer otel trace.json --service-name my-service

# Advanced export
callflow-tracer otel trace.json \
  --service-name my-service \
  --environment production \
  --sampling-rate 0.5 \
  --include-metrics
```

### Configuration File

**`.callflow_otel.yaml`** (auto-generated)
```yaml
service_name: my-service
environment: production
sampling_rate: 1.0

exporter:
  type: otlp_grpc
  endpoint: http://localhost:4317

resource_attributes:
  service.version: "1.0.0"
```

### Python API

```python
from callflow_tracer.opentelemetry_exporter import export_callgraph_to_otel

# Basic export
result = export_callgraph_to_otel(graph, service_name="my-service")

# Advanced export with exemplars
result = export_callgraph_to_otel(
    graph,
    service_name="my-service",
    sampling_rate=0.5,
    environment="production",
    resource_attributes={"service.version": "1.0.0"}
)

# With metrics bridging
from callflow_tracer.opentelemetry_exporter import export_callgraph_with_metrics
result = export_callgraph_with_metrics(graph, metrics, service_name="my-service")
```

**What You Get:**
- **Production Ready**: Full OTel compliance with semantic conventions
- **Exemplars**: Link custom metrics to trace spans for correlation
- **Sampling**: Configurable sampling rates (0.0-1.0) to reduce overhead
- **Resource Attributes**: Attach metadata (version, environment, host)
- **Config Management**: YAML/JSON files with environment variable overrides
- **Multiple Exporters**: Console, OTLP/gRPC, OTLP/HTTP, Jaeger
- **Batch Processing**: Configurable processor settings for efficiency
- **Error Handling**: Graceful degradation if OTel not installed

---

## 📊 Code Quality Analysis

Analyze code quality metrics with a single command:

```bash
# Analyze code quality
callflow-tracer quality . -o quality_report.html

# Track trends over time
callflow-tracer quality . --track-trends --format json
```

**What You Get:**
- **Complexity Metrics**: Cyclomatic and cognitive complexity
- **Maintainability Index**: 0-100 scale
- **Technical Debt**: Quantified debt scoring
- **Halstead Metrics**: Volume, difficulty, effort
- **Trend Analysis**: Track metrics over time

**Python API:**
```python
from callflow_tracer.code_quality import analyze_codebase

results = analyze_codebase("./src")
print(f"Average Complexity: {results['summary']['average_complexity']:.2f}")
print(f"Critical Issues: {results['summary']['critical_issues']}")
```

---

## 🔮 Predictive Analysis

Predict future performance issues:

```bash
# Predict performance issues
callflow-tracer predict history.json -o predictions.html
```

**What You Get:**
- **Performance Prediction**: Predict degradation
- **Capacity Planning**: Forecast limit breaches
- **Scalability Analysis**: Assess scalability
- **Risk Assessment**: Multi-factor evaluation
- **Confidence Scoring**: Data-driven confidence

**Python API:**
```python
from callflow_tracer.predictive_analysis import PerformancePredictor

predictor = PerformancePredictor("history.json")
predictions = predictor.predict_performance_issues(current_trace)

for pred in predictions:
    if pred.risk_level == "Critical":
        print(f"CRITICAL: {pred.function_name}")
        print(f"  Predicted time: {pred.predicted_time:.4f}s")
```

---

## 📈 Code Churn Analysis

Identify high-risk files using git history:

```bash
# Analyze code churn
callflow-tracer churn . --days 90 -o churn_report.html
```

**What You Get:**
- **Hotspot Identification**: Find high-risk files
- **Churn Metrics**: Commits, changes, authors
- **Quality Correlation**: Correlate with quality
- **Bug Prediction**: Estimate bug correlation
- **Recommendations**: Actionable improvements

**Python API:**
```python
from callflow_tracer.code_churn import generate_churn_report

report = generate_churn_report(".", days=90)
print(f"High risk files: {report['summary']['high_risk_files']}")

for hotspot in report['hotspots'][:5]:
    print(f"{hotspot['file_path']}: {hotspot['hotspot_score']:.1f}")
```

---

## Flamegraph - Find Bottlenecks Fast!

```python
from callflow_tracer import trace_scope
from callflow_tracer.flamegraph import generate_flamegraph
import time

def slow_function():
    time.sleep(0.1)  # Bottleneck!
    return sum(range(10000))

def fast_function():
    return sum(range(100))

def main():
    return slow_function() + fast_function()

# Trace execution
with trace_scope() as graph:
    result = main()

# Generate flamegraph with performance colors
generate_flamegraph(
    graph,
    "flamegraph.html",
    color_scheme="performance",  # Green=fast, Red=slow
    show_stats=True,             # Show statistics
    search_enabled=True          # Enable search
)
```

**Open `flamegraph.html` and look for wide RED bars - those are your bottlenecks!** 

---

## Async/Await Support - Trace Modern Python!

CallFlow Tracer now fully supports async/await patterns:

```python
import asyncio
from callflow_tracer.async_tracer import trace_async, trace_scope_async, gather_traced

@trace_async
async def fetch_data(item_id: int):
    """Async function with tracing."""
    await asyncio.sleep(0.1)
    return f"Data {item_id}"

@trace_async
async def process_data(item_id: int):
    """Process data asynchronously."""
    data = await fetch_data(item_id)
    await asyncio.sleep(0.05)
    return data.upper()

async def main():
    # Trace async code
    async with trace_scope_async("async_trace.html") as graph:
        # Concurrent execution
        tasks = [process_data(i) for i in range(10)]
        results = await gather_traced(*tasks)
        print(f"Processed {len(results)} items concurrently")
    
    # Get async statistics
    from callflow_tracer.async_tracer import get_async_stats
    stats = get_async_stats(graph)
    print(f"Max concurrent tasks: {stats['max_concurrent_tasks']}")
    print(f"Efficiency: {stats['efficiency']:.2f}%")

# Run it
asyncio.run(main())
```

**Async Features:**
- **Concurrent Execution Tracking**: See which tasks run in parallel
- **Await Time Analysis**: Separate active time from wait time
- **Concurrency Metrics**: Max concurrent tasks, timeline events
- **gather_traced()**: Drop-in replacement for asyncio.gather with tracing

---

## Comparison Mode - Validate Your Optimizations!

Compare two versions of your code side-by-side:

```python
from callflow_tracer import trace_scope
from callflow_tracer.comparison import export_comparison_html

# Before optimization
def fibonacci_slow(n):
    if n <= 1:
        return n
    return fibonacci_slow(n-1) + fibonacci_slow(n-2)

# After optimization (memoization)
_cache = {}
def fibonacci_fast(n):
    if n in _cache:
        return _cache[n]
    if n <= 1:
        return n
    result = fibonacci_fast(n-1) + fibonacci_fast(n-2)
    _cache[n] = result
    return result

# Trace both versions
with trace_scope() as graph_before:
    result = fibonacci_slow(20)

with trace_scope() as graph_after:
    result = fibonacci_fast(20)

# Generate comparison report
export_comparison_html(
    graph_before, graph_after,
    "optimization_comparison.html",
    label1="Before (Naive)",
    label2="After (Memoized)",
    title="Fibonacci Optimization"
)
```

**Open `optimization_comparison.html` to see:**
- **Side-by-Side Graphs**: Visual comparison of call patterns
- **Performance Metrics**: Time saved, percentage improvement
- **Improvements**: Functions that got faster (green highlighting)
- **Regressions**: Functions that got slower (red highlighting)
- **Detailed Table**: Function-by-function comparison
- **Summary Stats**: Added/removed/modified functions

---

## Complete Performance Analysis

Combine tracing and profiling for comprehensive analysis:

```python
from callflow_tracer import trace_scope, profile_section, export_html
from callflow_tracer.flamegraph import generate_flamegraph

def application():
    # Your application code
    process_data()
    analyze_results()

# Trace and profile together
with profile_section("Application") as perf_stats:
    with trace_scope() as graph:
        application()

# Export call graph with profiling data
export_html(
    graph,
    "callgraph.html",
    title="Application Analysis",
    profiling_stats=perf_stats.to_dict()
)

# Export flamegraph
generate_flamegraph(
    graph,
    "flamegraph.html",
    title="Performance Flamegraph",
    color_scheme="performance",
    show_stats=True
)
```

You get:
- **callgraph.html**: Interactive network showing function relationships + CPU profile
- **flamegraph.html**: Stacked bars showing time distribution + statistics

---

## Framework Integration Examples

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
from callflow_tracer import trace_scope
from callflow_tracer.integrations.fastapi_integration import setup_fastapi_tracing

# Define Pydantic models
class Item(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    price: float = Field(..., gt=0)
    in_stock: bool = True

class ItemResponse(Item):
    id: int
    created_at: str

# Setup tracing with lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global _cft_scope
    _cft_scope = trace_scope("fastapi_trace.html")
    _cft_scope.__enter__()
    yield
    # Shutdown
    _cft_scope.__exit__(None, None, None)

# Create FastAPI app
app = FastAPI(
    title="My API",
    lifespan=lifespan
)

# Setup automatic tracing
setup_fastapi_tracing(app)

# Add CORS middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define endpoints
@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    if item_id not in database:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found"
        )
    return {"id": item_id, **database[item_id]}

@app.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    new_id = max(database.keys(), default=0) + 1
    database[new_id] = item.dict()
    return {"id": new_id, **database[new_id]}
```

**Run it:**
```bash
uvicorn app:app --reload
# Visit http://localhost:8000/docs for interactive API docs
# Trace saved to fastapi_trace.html
```

---

### Flask Integration

```python
from flask import Flask, jsonify, request
from callflow_tracer import trace_scope
from callflow_tracer.integrations.flask_integration import setup_flask_tracing

app = Flask(__name__)

# Setup automatic tracing
setup_flask_tracing(app)

# Initialize trace scope
trace_context = trace_scope("flask_trace.html")
trace_context.__enter__()

@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    user = database.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    user_id = len(database) + 1
    database[user_id] = data
    return jsonify({"id": user_id, **data}), 201

if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        trace_context.__exit__(None, None, None)
```

---

### Django Integration

```python
# settings.py
MIDDLEWARE = [
    'callflow_tracer.integrations.django_integration.CallFlowTracerMiddleware',
    # ... other middleware
]

# views.py
from django.http import JsonResponse
from callflow_tracer.integrations.django_integration import trace_view

@trace_view
def user_list(request):
    users = User.objects.all()
    return JsonResponse({
        'users': list(users.values())
    })

@trace_view
def user_detail(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        return JsonResponse(user.to_dict())
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
```

---

### SQLAlchemy Integration

```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from callflow_tracer import trace_scope
from callflow_tracer.integrations.sqlalchemy_integration import setup_sqlalchemy_tracing

# Create engine
engine = create_engine('sqlite:///example.db')
Base = declarative_base()

# Define model
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)

# Setup tracing
setup_sqlalchemy_tracing(engine)

# Use with trace scope
with trace_scope("sqlalchemy_trace.html"):
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Queries will be traced
    users = session.query(User).filter(User.name.like('%John%')).all()
    
    # Inserts will be traced
    new_user = User(name="John Doe", email="john@example.com")
    session.add(new_user)
    session.commit()
```

---

### Psycopg2 Integration

```python
import psycopg2
from callflow_tracer import trace_scope
from callflow_tracer.integrations.psycopg2_integration import setup_psycopg2_tracing

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="mydb",
    user="user",
    password="password",
    host="localhost"
)

# Setup tracing
setup_psycopg2_tracing(conn)

# Use with trace scope
with trace_scope("postgres_trace.html"):
    cursor = conn.cursor()
    
    # Queries will be traced with execution time
    cursor.execute("SELECT * FROM users WHERE age > %s", (18,))
    users = cursor.fetchall()
    
    cursor.execute("""
        INSERT INTO users (name, email, age) 
        VALUES (%s, %s, %s)
    """, ("Jane Doe", "jane@example.com", 25))
    
    conn.commit()
    cursor.close()
```

---

## VSCode Extension Usage

### Installation
1. Open VS Code
2. Press `Ctrl+Shift+X` (or `Cmd+Shift+X` on Mac)
3. Search for "CallFlow Tracer"
4. Click **Install**

### Quick Start
1. Open any Python file
2. Right-click in the editor
3. Select **"CallFlow: Trace Current File"**
4. View the interactive visualization in the side panel

### Features
- **One-Click Tracing**: Trace entire files or selected functions
- **Interactive Graphs**: Zoom, pan, and explore call relationships
- **3D Visualization**: View call graphs in 3D space
- **Multiple Layouts**: Switch between hierarchical, force-directed, circular, and timeline
- **Export Options**: Save as PNG or JSON
- **Performance Profiling**: Built-in CPU profiling
- **Module Filtering**: Filter by Python modules

### Commands
- `CallFlow: Trace Current File` - Trace the entire file
- `CallFlow: Trace Selected Function` - Trace only selected function
- `CallFlow: Show Visualization` - Open visualization panel
- `CallFlow: Show 3D Visualization` - View in 3D
- `CallFlow: Export as PNG` - Export as image
- `CallFlow: Export as JSON` - Export trace data

### Settings
```json
{
  "callflowTracer.pythonPath": "python3",
  "callflowTracer.defaultLayout": "force",
  "callflowTracer.autoTrace": false,
  "callflowTracer.enableProfiling": true
}
```

---

## Custom Metrics Tracking (NEW in v0.3.1)

Track business logic metrics, monitor SLA compliance, and export performance data:

### Basic Usage with Decorator

```python
from callflow_tracer import custom_metric, track_metric, MetricsCollector

# Automatic metric tracking with decorator
@custom_metric("order_processing_time", sla_threshold=1.0)
def process_order(order_id, amount):
    # Your business logic here
    return {"status": "completed", "amount": amount}

# Manual metric tracking
def calculate_total(items):
    total = sum(item['price'] * item['quantity'] for item in items)
    track_metric("order_total", total, tags={"currency": "USD"})
    return total

# Run your code
for i in range(10):
    process_order(i, 99.99)

# Export metrics
MetricsCollector.export_metrics("metrics.json")
```

### SLA Monitoring

```python
from callflow_tracer import SLAMonitor

sla_monitor = SLAMonitor()

# Set SLA thresholds
sla_monitor.set_threshold("api_response_time", 0.5)  # 500ms
sla_monitor.set_threshold("database_query_time", 1.0)  # 1 second

# Get compliance report
report = sla_monitor.get_compliance_report()
for metric_name, compliance in report.items():
    print(f"{metric_name}: {compliance['compliance_rate']}% compliant")

# Export report
sla_monitor.export_report("sla_report.json")
```

### Business Metrics Tracking

```python
from callflow_tracer import get_business_tracker

tracker = get_business_tracker()

# Track counters
tracker.increment_counter("orders_processed")
tracker.increment_counter("orders_failed")

# Track gauges
tracker.set_gauge("current_queue_size", 42)
tracker.set_gauge("success_rate", 98.5)

# Export metrics
tracker.export_metrics("business_metrics.json")
```

**What You Get:**
- 📈 **Automatic Tracking**: @custom_metric decorator tracks execution time
- 🎯 **SLA Monitoring**: Monitor compliance with service level agreements
- 📊 **Business Metrics**: Track counters and gauges for business logic
- 🏷️ **Tag-Based Filtering**: Organize metrics with tags
- 📁 **Multiple Export Formats**: JSON and CSV export
- 📋 **Compliance Reports**: Detailed SLA violation reports
- 🔍 **Statistical Analysis**: Mean, median, min, max, stddev calculations

---

## 🛡️ SLO/SLI, Error Budgets, and Experiments (NEW in v3.2.0)

### Service Level Indicators (SLI) and Objectives (SLO)
```python
from callflow_tracer.custom_metrics import SLO

# Latency objective: 95th percentile <= 300ms over 5 minutes
latency_slo = SLO(
    name="checkout-latency-p95<=300ms",
    objective=1.0,  # 1.0 means target met
    time_window=300,
    sli_type="latency",
    metric_name="latency_ms",
    params={"threshold": 300.0, "percentile": 95.0},
)
print(latency_slo.compute(tags={"service": "api"}))
```

### Error Budgets
```python
from callflow_tracer.custom_metrics import ErrorBudgetTracker

availability_slo = SLO(
    name="availability>=99.9%",
    objective=0.999,
    time_window=86400,  # 1 day
    sli_type="availability",
    metric_name="request_success",
    params={"success_value": 1.0},
)
eb = ErrorBudgetTracker(availability_slo).compute_budget(tags={"region": "us-east-1"})
print(eb)
```

### Canary & A/B Testing
```python
from callflow_tracer.custom_metrics import ExperimentAnalyzer, track_metric

# While generating metrics, tag them with deployment/variant
track_metric("latency_ms", 240, tags={"deployment": "baseline"})
track_metric("latency_ms", 260, tags={"deployment": "canary"})

canary = ExperimentAnalyzer.canary(
    metric_name="latency_ms",
    baseline_value="baseline",
    canary_value="canary",
    group_tag_key="deployment",
    time_window=3600,
)
print(canary)

ab = ExperimentAnalyzer.ab_test(
    metric_name="conversion_flag",  # 1.0=converted, 0.0=not
    variant_a="A",
    variant_b="B",
    group_tag_key="variant",
    time_window=7200,
)
print(ab)
```

### Multi-dimensional SLAs and Dynamic Thresholds
```python
from callflow_tracer.custom_metrics import SLAMonitor

monitor = SLAMonitor()
# Multiple conditions per metric with rolling windows and dynamic thresholds
monitor.set_threshold("latency_ms", 300, operator="lte", time_window=300, dynamic=True)
monitor.set_threshold("latency_ms", 500, operator="lte", time_window=60, dynamic=False)

# Feed data
monitor.record_metric("latency_ms", 350)
monitor.record_metric("latency_ms", 240)

print(monitor.get_compliance_report(time_window=3600))
```

---

## 📓 Jupyter Notebook Support

```python
# In Jupyter notebook
from callflow_tracer import trace_scope, profile_section
from callflow_tracer.jupyter import display_callgraph

def my_function():
    return sum(range(1000))

# Trace and display inline
with trace_scope() as graph:
    result = my_function()

# Display interactive graph in notebook
display_callgraph(graph.to_dict(), height="600px")

# Or use magic commands
%%callflow_cell_trace

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(10)
```

---

## 🔍 Advanced Profiling Examples

### Memory and Performance Profiling

```python
from callflow_tracer import profile_function, profile_section, get_memory_usage
import time
import random
import numpy as np

@profile_function
def process_data(data_size: int) -> float:
    """Process data with CPU and memory profiling."""
    # Allocate memory
    data = [random.random() for _ in range(data_size)]
    
    # CPU-intensive work
    total = sum(data) / len(data) if data else 0
    
    # Simulate I/O
    time.sleep(0.1)
    
    return total

def analyze_performance():
    """Example using profile_section context manager."""
    with profile_section("Data Processing"):
        # Process different data sizes
        for size in [1000, 10000, 100000]:
            with profile_section(f"Processing {size} elements"):
                result = process_data(size)
                print(f"Result: {result:.4f}")
                
                # Get memory usage
                mem_usage = get_memory_usage()
                print(f"Memory usage: {mem_usage:.2f} MB")

if __name__ == "__main__":
    analyze_performance()
    
    # Export the profile data to HTML
    from callflow_tracer import export_html
    export_html("performance_profile.html")
```

### Visualizing Performance Data

After running the above code, you can view the performance data in an interactive HTML report that includes:

- Call hierarchy with timing information
- Memory usage over time
- Hotspots and bottlenecks
- Function execution statistics

## 🛠 Basic Usage

### Option 1: Decorator Approach
```python
from callflow_tracer import trace, trace_scope

@trace
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

@trace
def main():
    result = calculate_fibonacci(10)
    print(f"Fibonacci(10) = {result}")

# Trace everything and export to HTML
with trace_scope("fibonacci_trace.html"):
    main()
```

#### Option 2: Context Manager Approach
```python
from callflow_tracer import trace_scope

def process_data():
    data = load_data()
    cleaned = clean_data(data)
    result = analyze_data(cleaned)
    return result

def load_data():
    return [1, 2, 3, 4, 5]

def clean_data(data):
    return [x * 2 for x in data if x > 2]

def analyze_data(data):
    return sum(data) / len(data)

# Trace the entire process
with trace_scope("data_processing.html"):
    result = process_data()
    print(f"Analysis result: {result}")
```

## 📊 What You Get

After running your traced code, you'll get an interactive HTML file showing:

- **Function Nodes**: Each function as a colored node (color indicates performance)
- **Call Relationships**: Arrows showing which functions call which others
- **Performance Metrics**: Hover over nodes to see call counts and timing
- **Interactive Controls**: Filter by module, toggle physics, change layout
- **Statistics**: Total functions, call relationships, and execution time

## 🎯 Advanced Usage

### Custom Export Options

```python
from callflow_tracer import trace_scope, export_json, export_html

with trace_scope() as graph:
    # Your code here
    my_application()
    
# Export to different formats
export_json(graph, "trace.json")
export_html(graph, "trace.html", title="My App Call Flow")
```

### Selective Tracing

```python
from callflow_tracer import trace

# Only trace specific functions
@trace
def critical_function():
    # This will be traced
    pass

def regular_function():
    # This won't be traced
    pass

# Use context manager for broader tracing
with trace_scope("selective_trace.html"):
    critical_function()  # Traced
    regular_function()   # Not traced
```

### Performance Analysis

```python
from callflow_tracer import trace_scope, get_current_graph

with trace_scope("performance_analysis.html"):
    # Your performance-critical code
    optimize_algorithm()
    
# Get the graph for programmatic analysis
graph = get_current_graph()
for node in graph.nodes.values():
    if node.avg_time > 0.1:  # Functions taking > 100ms
        print(f"Slow function: {node.full_name} ({node.avg_time:.3f}s avg)")
```

## 🔧 Configuration

### HTML Export Options

```python
from callflow_tracer import export_html

# Customize the HTML output
export_html(
    graph, 
    "custom_trace.html",
    title="My Custom Title",
    include_vis_js=True  # Include vis.js from CDN (requires internet)
)
```

### Privacy Settings

The library automatically truncates function arguments to 100 characters for privacy. For production use, you can modify the `CallNode.add_call()` method to further anonymize or exclude sensitive data.

## 📁 Project Structure

```
callflow-tracer/
├── callflow_tracer/
│   ├── __init__.py              # Main API
│   ├── tracer.py                # Core tracing logic
│   ├── exporter.py              # HTML/JSON export
│   ├── profiling.py             # Performance profiling
│   ├── flamegraph.py            # Flamegraph generation
│   ├── flamegraph_enhanced.py   # Enhanced flamegraph UI
│   └── jupyter.py               # Jupyter integration
├── examples/
│   ├── flamegraph_example.py    # 7 flamegraph examples
│   ├── flamegraph_enhanced_demo.py  # Enhanced features demo
│   ├── jupyter_example.ipynb    # Jupyter notebook examples
│   ├── jupyter_standalone_demo.py   # Standalone Jupyter demo
│   ├── FLAMEGRAPH_README.md     # Flamegraph guide
│   └── JUPYTER_README.md        # Jupyter guide
├── tests/
│   ├── test_flamegraph.py       # Flamegraph tests (10 tests)
│   ├── test_flamegraph_enhanced.py  # Enhanced features tests (10 tests)
│   ├── test_jupyter_integration.py  # Jupyter tests (7 tests)
│   └── test_cprofile_fix.py     # CPU profiling tests
├── docs/
│   ├── API_DOCUMENTATION.md     # Complete API reference
│   ├── FEATURES_COMPLETE.md     # All features documented
│   ├── INSTALLATION_GUIDE.md    # Installation guide
│   └── USER_GUIDE.md            # User guide
├── CHANGELOG.md                 # Version history
├── TESTING_GUIDE.md             # Testing guide
├── QUICK_TEST.md                # Quick test reference
├── ENHANCED_FEATURES.md         # Enhanced features guide
├── pyproject.toml               # Package configuration
├── README.md                    # This file
└── LICENSE                      # MIT License
```

## 🎨 Visualization Features

### Call Graph Visualization

- **Interactive Network**: Zoom, pan, and explore your call graph
- **4 Layout Options**: 
  - Hierarchical (top-down tree)
  - Force-Directed (physics-based)
  - Circular (equal spacing)
  - Timeline (sorted by execution time)
- **Module Filtering**: Filter by Python module (FIXED!)
- **Color Coding**: 
  - 🔴 Red: Slow functions (>100ms)
  - 🟢 Teal: Medium functions (10-100ms)  
  - 🔵 Blue: Fast functions (<10ms)
- **Export Options**: PNG images and JSON data
- **Rich Tooltips**: Detailed performance metrics

### Flamegraph Visualization

- **Stacked Bar Chart**: Width = time, Height = depth
- **Statistics Panel**: Key metrics at a glance
- **5 Color Schemes**: Default, Hot, Cool, Rainbow, Performance
- **Search Functionality**: Find functions quickly
- **SVG Export**: High-quality vector graphics
- **Interactive Zoom**: Click to zoom, hover for details
- **Optimization Tips**: Built-in guidance

### CPU Profile Analysis

- **Execution Time**: Actual CPU time (FIXED!)
- **Function Calls**: Accurate call counts
- **Hot Spots**: Automatically identified
- **Detailed Output**: Complete cProfile data
- **Health Indicators**: Visual status
- **Collapsible UI**: Modern, clean interface

## 🚨 Important Notes

- **Performance Impact**: Tracing adds overhead. Use selectively for production code
- **Thread Safety**: The tracer is thread-safe and can handle concurrent code
- **Memory Usage**: Large applications may generate substantial trace data
- **Privacy**: Function arguments are truncated by default for security

## 📚 Documentation

### 🆕 v0.3.2 Documentation (NEW!)
- **[OTEL_QUICK_REFERENCE.md](OTEL_QUICK_REFERENCE.md)** - One-page OpenTelemetry cheat sheet
- **[docs/OTEL_ADVANCED_GUIDE.md](docs/OTEL_ADVANCED_GUIDE.md)** - Comprehensive OpenTelemetry guide
- **[OTEL_TESTING_GUIDE.md](OTEL_TESTING_GUIDE.md)** - Testing workflow and CI/CD
- **[OTEL_IMPLEMENTATION_SUMMARY.md](OTEL_IMPLEMENTATION_SUMMARY.md)** - Feature overview
- **[OTEL_INDEX.md](OTEL_INDEX.md)** - Master index & navigation
- **[examples/README_OTEL.md](examples/README_OTEL.md)** - OpenTelemetry examples

### 🆕 v0.3.1 Documentation (NEW!)
- **[CUSTOM_METRICS_GUIDE.md](docs/CUSTOM_METRICS_GUIDE.md)** - Custom metrics tracking guide (NEW!)

### 🆕 v0.3.0 Documentation
- **[NEW_FEATURES_INDEX.md](docs/NEW_FEATURES_INDEX.md)** - Complete v0.3.0 feature index
- **[CLI_GUIDE.md](docs/CLI_GUIDE.md)** - Command-line interface reference
- **[CODE_QUALITY_GUIDE.md](docs/CODE_QUALITY_GUIDE.md)** - Code quality analysis guide
- **[PREDICTIVE_ANALYSIS_GUIDE.md](docs/PREDICTIVE_ANALYSIS_GUIDE.md)** - Predictive analytics guide
- **[CODE_CHURN_GUIDE.md](docs/CODE_CHURN_GUIDE.md)** - Code churn analysis guide
- **[INTEGRATIONS_GUIDE.md](docs/INTEGRATIONS_GUIDE.md)** - Framework integrations guide
- **[v0_3_0_RELEASE_NOTES.md](docs/v0_3_0_RELEASE_NOTES.md)** - Release notes
- **[FEATURE_MAPPING.md](docs/FEATURE_MAPPING.md)** - Feature mapping and cross-reference

### Quick References
- **[Quick Test Guide](QUICK_TEST.md)** - Fast testing reference
- **[Testing Guide](TESTING_GUIDE.md)** - Comprehensive testing
- **[Enhanced Features](ENHANCED_FEATURES.md)** - New features guide
- **[Changelog](CHANGELOG.md)** - Version history

### Complete Guides
- **[API Documentation](docs/API_DOCUMENTATION.md)** - Complete API reference
- **[Features Documentation](docs/FEATURES_COMPLETE.md)** - All features explained
- **[Installation Guide](docs/INSTALLATION_GUIDE.md)** - Setup and configuration
- **[Flamegraph Guide](examples/FLAMEGRAPH_README.md)** - Flamegraph documentation
- **[Jupyter Guide](examples/JUPYTER_README.md)** - Jupyter integration guide

### Examples
- `examples/flamegraph_example.py` - 7 flamegraph examples
- `examples/flamegraph_enhanced_demo.py` - Enhanced features demo (12 examples)
- `examples/jupyter_example.ipynb` - Interactive Jupyter notebook
- `examples/jupyter_standalone_demo.py` - Standalone demos
- `examples/example_otel_export.py` - OpenTelemetry export examples (NEW!)

### Tests
- `tests/test_flamegraph.py` - 10 flamegraph tests
- `tests/test_flamegraph_enhanced.py` - 10 enhanced feature tests
- `tests/test_jupyter_integration.py` - 7 Jupyter tests
- `tests/test_cprofile_fix.py` - CPU profiling tests
- `tests/test_otel_export.py` - 40+ OpenTelemetry tests (NEW!)
- `test_otel_integration.py` - OpenTelemetry integration tests (NEW!)

---

## 🧪 Testing

### Run All Tests

```bash
# Test flamegraph functionality
python tests/test_flamegraph.py
python tests/test_flamegraph_enhanced.py

# Test Jupyter integration
python tests/test_jupyter_integration.py

# Test CPU profiling fix
python tests/test_cprofile_fix.py

# Test OpenTelemetry export (NEW in v0.3.2)
pytest tests/test_otel_export.py -v
python test_otel_integration.py
```

### Run Examples

```bash
# Flamegraph examples (generates 7 HTML files)
python examples/flamegraph_example.py

# Enhanced flamegraph demo (generates 12 HTML files)
python examples/flamegraph_enhanced_demo.py

# Jupyter standalone demo (generates 5 HTML files)
python examples/jupyter_standalone_demo.py

# OpenTelemetry export examples (NEW in v0.3.2)
python examples/example_otel_export.py
```

All tests should pass with:
```
============================================================
RESULTS: X passed, 0 failed
============================================================
✓ ALL TESTS PASSED!
```

---

## 🎯 Use Cases

### 1. Finding Performance Bottlenecks
```python
generate_flamegraph(graph, "bottlenecks.html", color_scheme="performance")
# Wide RED bars = bottlenecks!
```

### 2. Understanding Code Flow
```python
export_html(graph, "flow.html", layout="hierarchical")
# See top-down execution flow
```

### 3. Comparing Optimizations
```python
# Before
with trace_scope() as before:
    unoptimized_code()

# After
with trace_scope() as after:
    optimized_code()

# Compare flamegraphs side by side
```

### 4. Jupyter Analysis
```python
# In notebook
with trace_scope() as graph:
    ml_pipeline()

display_callgraph(graph.to_dict())
```

---

## 🚨 Important Notes

- **Performance Impact**: Tracing adds ~10-30% overhead. Use selectively for production code
- **Thread Safety**: The tracer is thread-safe and can handle concurrent code
- **Memory Usage**: Large applications may generate substantial trace data
- **Privacy**: Function arguments are truncated by default for security
- **Browser**: Requires modern browser with JavaScript for visualizations
- **Internet**: CDN resources require internet connection (or use offline mode)

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

For major changes, please open an issue first to discuss.

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

### Technologies
- **NetworkX**: Graph operations
- **vis.js**: Interactive call graph visualizations
- **D3.js**: Flamegraph rendering
- **cProfile**: CPU profiling
- **tracemalloc**: Memory tracking

### Inspiration
- Inspired by the need for better code understanding and debugging tools
- Built for developers who want to optimize their Python applications
- Community-driven improvements and feedback

---

## 📞 Support

- 📧 **Email**: rathodrajveer1311@gmail.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/rajveer43/callflow-tracer/issues)
- 📖 **Documentation**: [GitHub Wiki](https://github.com/rajveer43/callflow-tracer/wiki)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/rajveer43/callflow-tracer/discussions)

---

## 🌟 Star Us!

If you find CallFlow Tracer useful, please star the repository on GitHub! ⭐

---

**Happy Tracing! 🎉**

*CallFlow Tracer - Making Python performance analysis beautiful and intuitive*

```python
from callflow_tracer import trace_scope
from callflow_tracer.flamegraph import generate_flamegraph

with trace_scope() as graph:
    your_amazing_code()

generate_flamegraph(graph, "amazing.html", color_scheme="performance")
# Find your bottlenecks in seconds! 🔥
```
