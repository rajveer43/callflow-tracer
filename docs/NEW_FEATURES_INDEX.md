# New Features Index - CallFlow Tracer v0.3.0

Complete index and mapping of all newly created features.

---

## 📋 Table of Contents

1. [Feature Overview](#feature-overview)
2. [Documentation Mapping](#documentation-mapping)
3. [Module Structure](#module-structure)
4. [Quick Reference](#quick-reference)
5. [Integration Map](#integration-map)

---

## Feature Overview

### New Features in v0.3.0

| Feature | Module | Type | Status |
|---------|--------|------|--------|
| Command-Line Interface | `cli.py` | Core | ✅ Complete |
| Code Quality Analysis | `code_quality.py` | Analysis | ✅ Complete |
| Predictive Analysis | `predictive_analysis.py` | Analysis | ✅ Complete |
| Code Churn Analysis | `code_churn.py` | Analysis | ✅ Complete |
| Flask Integration | `integrations/flask_integration.py` | Integration | ✅ Complete |
| FastAPI Integration | `integrations/fastapi_integration.py` | Integration | ✅ Complete |
| Django Integration | `integrations/django_integration.py` | Integration | ✅ Complete |
| SQLAlchemy Integration | `integrations/sqlalchemy_integration.py` | Integration | ✅ Complete |
| psycopg2 Integration | `integrations/psycopg2_integration.py` | Integration | ✅ Complete |

---

## Documentation Mapping

### 1. CLI Guide
**File**: `docs/CLI_GUIDE.md`

**Covers**:
- 10 CLI commands
- Command options and arguments
- Usage examples
- Exit codes
- Environment variables

**Commands**:
- `trace` - Trace function calls
- `flamegraph` - Generate flamegraph
- `profile` - Profile performance
- `memory-leak` - Detect memory leaks
- `compare` - Compare traces
- `export` - Export traces
- `info` - Show trace information
- `quality` - Analyze code quality
- `predict` - Predict performance issues
- `churn` - Analyze code churn

### 2. Code Quality Guide
**File**: `docs/CODE_QUALITY_GUIDE.md`

**Covers**:
- Complexity metrics (cyclomatic, cognitive)
- Maintainability metrics (Halstead, MI)
- Technical debt indicators
- Quality trend analysis
- 4 analyzer classes
- Usage examples
- Output format

**Key Classes**:
- `ComplexityAnalyzer` - Analyze complexity
- `MaintainabilityAnalyzer` - Analyze maintainability
- `TechnicalDebtAnalyzer` - Identify debt
- `QualityTrendAnalyzer` - Track trends

**Metrics**:
- Cyclomatic complexity (1-based)
- Cognitive complexity
- Maintainability index (0-100)
- Technical debt score (0-100)

### 3. Predictive Analysis Guide
**File**: `docs/PREDICTIVE_ANALYSIS_GUIDE.md`

**Covers**:
- Performance prediction
- Capacity planning
- Scalability analysis
- Resource forecasting
- 4 analyzer classes
- Usage examples
- Output format

**Key Classes**:
- `PerformancePredictor` - Predict issues
- `CapacityPlanner` - Plan capacity
- `ScalabilityAnalyzer` - Analyze scalability
- `ResourceForecaster` - Forecast resources

**Predictions**:
- Performance degradation
- Capacity limit breaches
- Scalability characteristics
- Resource usage trends

### 4. Code Churn Guide
**File**: `docs/CODE_CHURN_GUIDE.md`

**Covers**:
- Code churn metrics
- Churn correlation analysis
- Git history analysis
- Hotspot identification
- 2 analyzer classes
- Usage examples
- Output format

**Key Classes**:
- `CodeChurnAnalyzer` - Analyze churn
- `ChurnCorrelationAnalyzer` - Correlate metrics

**Metrics**:
- Commits count
- Lines added/deleted/modified
- Churn rate (changes/day)
- Hotspot score (0-100)

### 5. Integrations Guide
**File**: `docs/INTEGRATIONS_GUIDE.md`

**Covers**:
- 5 framework integrations
- Setup instructions
- Configuration options
- Usage examples
- Best practices
- Troubleshooting

**Integrations**:
- Flask
- FastAPI
- Django
- SQLAlchemy
- psycopg2

---

## Module Structure

### Core Modules

```
callflow_tracer/
├── cli.py (850 lines)
│   ├── CallflowCLI class
│   ├── 10 command handlers
│   └── HTML report generation
│
├── code_quality.py (633 lines)
│   ├── ComplexityMetrics dataclass
│   ├── MaintainabilityMetrics dataclass
│   ├── TechnicalDebtIndicator dataclass
│   ├── QualityTrend dataclass
│   ├── ComplexityAnalyzer class
│   ├── MaintainabilityAnalyzer class
│   ├── TechnicalDebtAnalyzer class
│   ├── QualityTrendAnalyzer class
│   └── analyze_codebase() function
│
├── predictive_analysis.py (627 lines)
│   ├── PerformancePrediction dataclass
│   ├── CapacityPrediction dataclass
│   ├── ScalabilityAnalysis dataclass
│   ├── ResourceForecast dataclass
│   ├── PerformancePredictor class
│   ├── CapacityPlanner class
│   ├── ScalabilityAnalyzer class
│   ├── ResourceForecaster class
│   └── generate_predictive_report() function
│
├── code_churn.py (382 lines)
│   ├── ChurnMetrics dataclass
│   ├── ChurnCorrelation dataclass
│   ├── CodeChurnAnalyzer class
│   ├── ChurnCorrelationAnalyzer class
│   └── generate_churn_report() function
│
└── integrations/
    ├── __init__.py
    ├── flask_integration.py (2586 bytes)
    ├── fastapi_integration.py (2105 bytes)
    ├── django_integration.py (2586 bytes)
    ├── sqlalchemy_integration.py (1725 bytes)
    └── psycopg2_integration.py (3744 bytes)
```

---

## Quick Reference

### CLI Commands Quick Reference

```bash
# Tracing
callflow-tracer trace script.py -o output.html
callflow-tracer flamegraph script.py -o flamegraph.html
callflow-tracer profile script.py --memory --cpu

# Analysis
callflow-tracer quality . -o quality_report.html
callflow-tracer predict history.json -o predictions.html
callflow-tracer churn . -o churn_report.html

# Utilities
callflow-tracer compare trace1.json trace2.json -o comparison.html
callflow-tracer export trace.json -o output.html --format html
callflow-tracer info trace.json --detailed
callflow-tracer memory-leak script.py -o report.html
```

### Python API Quick Reference

```python
# Code Quality
from callflow_tracer.code_quality import analyze_codebase
results = analyze_codebase("./src")

# Predictive Analysis
from callflow_tracer.predictive_analysis import PerformancePredictor
predictor = PerformancePredictor("history.json")
predictions = predictor.predict_performance_issues(current_trace)

# Code Churn
from callflow_tracer.code_churn import generate_churn_report
report = generate_churn_report(".", days=90)

# Framework Integration
from callflow_tracer.integrations.flask_integration import setup_flask_tracing
setup_flask_tracing(app)
```

---

## Integration Map

### Framework Support Matrix

| Framework | Module | Type | Features |
|-----------|--------|------|----------|
| Flask | `flask_integration.py` | Web | Request tracing, endpoint profiling |
| FastAPI | `fastapi_integration.py` | Web | Async support, endpoint profiling |
| Django | `django_integration.py` | Web | Middleware, view tracing, DB monitoring |
| SQLAlchemy | `sqlalchemy_integration.py` | ORM | Query tracing, performance monitoring |
| psycopg2 | `psycopg2_integration.py` | DB | Query tracing, connection monitoring |

### Integration Setup Patterns

#### Web Frameworks
```python
from callflow_tracer.integrations.{framework}_integration import setup_{framework}_tracing
setup_{framework}_tracing(app, output_dir="traces")
```

#### Database Libraries
```python
from callflow_tracer.integrations.{db}_integration import setup_{db}_tracing
setup_{db}_tracing(connection_or_engine)
```

---

## Feature Capabilities

### Code Quality Analysis
- ✅ Cyclomatic complexity calculation
- ✅ Cognitive complexity measurement
- ✅ Maintainability index (0-100)
- ✅ Halstead metrics
- ✅ Technical debt scoring
- ✅ Trend tracking over time
- ✅ HTML/JSON reporting

### Predictive Analysis
- ✅ Performance degradation prediction
- ✅ Capacity limit forecasting
- ✅ Scalability analysis
- ✅ Resource usage forecasting
- ✅ Confidence scoring
- ✅ Risk assessment
- ✅ Trend analysis

### Code Churn Analysis
- ✅ Git history analysis
- ✅ Hotspot identification
- ✅ Churn correlation with quality
- ✅ Bug correlation estimation
- ✅ Risk assessment
- ✅ Recommendations generation
- ✅ HTML/JSON reporting

### Framework Integrations
- ✅ Automatic request tracing
- ✅ Async/await support
- ✅ Database query monitoring
- ✅ Performance metrics
- ✅ HTML visualization
- ✅ Zero-code integration

---

## Statistics

### Code Metrics
- **Total new lines**: ~3,200
- **Total new modules**: 9
- **Total new classes**: 20+
- **Total new functions**: 50+
- **Total new dataclasses**: 8

### Documentation
- **CLI Guide**: 150+ lines
- **Code Quality Guide**: 200+ lines
- **Predictive Analysis Guide**: 220+ lines
- **Code Churn Guide**: 200+ lines
- **Integrations Guide**: 250+ lines
- **Total documentation**: 1,000+ lines

### Test Coverage
- CLI commands: 10 commands
- Analysis modules: 4 modules
- Integration modules: 5 modules
- Dataclasses: 8 dataclasses

---

## Learning Path

### Beginner
1. Read [CLI_GUIDE.md](CLI_GUIDE.md)
2. Try CLI commands
3. Generate first quality report
4. Explore output formats

### Intermediate
1. Read [CODE_QUALITY_GUIDE.md](CODE_QUALITY_GUIDE.md)
2. Read [CODE_CHURN_GUIDE.md](CODE_CHURN_GUIDE.md)
3. Use Python API
4. Integrate with CI/CD

### Advanced
1. Read [PREDICTIVE_ANALYSIS_GUIDE.md](PREDICTIVE_ANALYSIS_GUIDE.md)
2. Read [INTEGRATIONS_GUIDE.md](INTEGRATIONS_GUIDE.md)
3. Combine multiple analyses
4. Create custom workflows

---

## Cross-Reference

### By Use Case

#### Finding Code Quality Issues
- **Start**: [CODE_QUALITY_GUIDE.md](CODE_QUALITY_GUIDE.md)
- **CLI**: `callflow-tracer quality`
- **Python**: `analyze_codebase()`

#### Identifying High-Risk Files
- **Start**: [CODE_CHURN_GUIDE.md](CODE_CHURN_GUIDE.md)
- **CLI**: `callflow-tracer churn`
- **Python**: `generate_churn_report()`

#### Predicting Performance Issues
- **Start**: [PREDICTIVE_ANALYSIS_GUIDE.md](PREDICTIVE_ANALYSIS_GUIDE.md)
- **CLI**: `callflow-tracer predict`
- **Python**: `PerformancePredictor`

#### Integrating with Web Frameworks
- **Start**: [INTEGRATIONS_GUIDE.md](INTEGRATIONS_GUIDE.md)
- **Frameworks**: Flask, FastAPI, Django
- **Databases**: SQLAlchemy, psycopg2

### By Module

#### cli.py
- **Guide**: [CLI_GUIDE.md](CLI_GUIDE.md)
- **Commands**: 10 available
- **Lines**: 850

#### code_quality.py
- **Guide**: [CODE_QUALITY_GUIDE.md](CODE_QUALITY_GUIDE.md)
- **Classes**: 4 analyzer classes
- **Lines**: 633

#### predictive_analysis.py
- **Guide**: [PREDICTIVE_ANALYSIS_GUIDE.md](PREDICTIVE_ANALYSIS_GUIDE.md)
- **Classes**: 4 analyzer classes
- **Lines**: 627

#### code_churn.py
- **Guide**: [CODE_CHURN_GUIDE.md](CODE_CHURN_GUIDE.md)
- **Classes**: 2 analyzer classes
- **Lines**: 382

#### integrations/
- **Guide**: [INTEGRATIONS_GUIDE.md](INTEGRATIONS_GUIDE.md)
- **Modules**: 5 integrations
- **Total lines**: ~12,000 bytes

---

## Version Information

- **Version**: v0.3.0
- **Release Date**: 2025-01-15
- **Status**: Stable
- **Documentation Status**: Complete

---

## Next Steps

1. **Read the guides** in order of interest
2. **Try the CLI commands** to get familiar
3. **Use the Python API** for programmatic access
4. **Integrate with frameworks** for automatic tracing
5. **Combine analyses** for comprehensive insights

---

*Documentation Index - New Features v0.3.0*
*Last Updated: 2025-01-15*
