# Feature Mapping and Cross-Reference Guide

Complete mapping of all new v0.3.0 features with cross-references.

---

## 📍 Feature Location Map

### CLI Module (`cli.py`)

**File**: `callflow_tracer/cli.py` (850 lines)

**Main Class**: `CallflowCLI`

**Commands**:
| Command | Handler | Guide | Lines |
|---------|---------|-------|-------|
| trace | `_handle_trace()` | [CLI_GUIDE.md](CLI_GUIDE.md) | 40 |
| flamegraph | `_handle_flamegraph()` | [CLI_GUIDE.md](CLI_GUIDE.md) | 25 |
| profile | `_handle_profile()` | [CLI_GUIDE.md](CLI_GUIDE.md) | 70 |
| memory-leak | `_handle_memory_leak()` | [CLI_GUIDE.md](CLI_GUIDE.md) | 35 |
| compare | `_handle_compare()` | [CLI_GUIDE.md](CLI_GUIDE.md) | 30 |
| export | `_handle_export()` | [CLI_GUIDE.md](CLI_GUIDE.md) | 25 |
| info | `_handle_info()` | [CLI_GUIDE.md](CLI_GUIDE.md) | 45 |
| quality | `_handle_quality()` | [CLI_GUIDE.md](CLI_GUIDE.md) + [CODE_QUALITY_GUIDE.md](CODE_QUALITY_GUIDE.md) | 55 |
| predict | `_handle_predict()` | [CLI_GUIDE.md](CLI_GUIDE.md) + [PREDICTIVE_ANALYSIS_GUIDE.md](PREDICTIVE_ANALYSIS_GUIDE.md) | 60 |
| churn | `_handle_churn()` | [CLI_GUIDE.md](CLI_GUIDE.md) + [CODE_CHURN_GUIDE.md](CODE_CHURN_GUIDE.md) | 45 |

---

### Code Quality Module (`code_quality.py`)

**File**: `callflow_tracer/code_quality.py` (633 lines)

**Guide**: [CODE_QUALITY_GUIDE.md](CODE_QUALITY_GUIDE.md)

**Dataclasses**:
| Class | Purpose | Lines |
|-------|---------|-------|
| `ComplexityMetrics` | Cyclomatic/cognitive complexity | 20 |
| `MaintainabilityMetrics` | Maintainability index | 25 |
| `TechnicalDebtIndicator` | Technical debt scoring | 15 |
| `QualityTrend` | Quality trend tracking | 12 |

**Analyzer Classes**:
| Class | Purpose | Methods | Lines |
|-------|---------|---------|-------|
| `ComplexityAnalyzer` | Analyze complexity | 9 | 130 |
| `MaintainabilityAnalyzer` | Analyze maintainability | 8 | 165 |
| `TechnicalDebtAnalyzer` | Identify debt | 1 | 75 |
| `QualityTrendAnalyzer` | Track trends | 6 | 105 |

**Key Functions**:
- `analyze_codebase(directory, file_pattern)` - Analyze entire codebase

**CLI Integration**:
- Command: `quality`
- Handler: `_handle_quality()` in `cli.py`
- Output: HTML/JSON reports

---

### Predictive Analysis Module (`predictive_analysis.py`)

**File**: `callflow_tracer/predictive_analysis.py` (627 lines)

**Guide**: [PREDICTIVE_ANALYSIS_GUIDE.md](PREDICTIVE_ANALYSIS_GUIDE.md)

**Dataclasses**:
| Class | Purpose | Lines |
|-------|---------|-------|
| `PerformancePrediction` | Performance predictions | 12 |
| `CapacityPrediction` | Capacity forecasts | 12 |
| `ScalabilityAnalysis` | Scalability analysis | 10 |
| `ResourceForecast` | Resource forecasts | 12 |

**Analyzer Classes**:
| Class | Purpose | Methods | Lines |
|-------|---------|---------|-------|
| `PerformancePredictor` | Predict issues | 8 | 155 |
| `CapacityPlanner` | Plan capacity | 5 | 95 |
| `ScalabilityAnalyzer` | Analyze scalability | 8 | 140 |
| `ResourceForecaster` | Forecast resources | 4 | 100 |

**Key Functions**:
- `generate_predictive_report(trace_history, current_trace)` - Generate report

**CLI Integration**:
- Command: `predict`
- Handler: `_handle_predict()` in `cli.py`
- Output: HTML/JSON reports

---

### Code Churn Module (`code_churn.py`)

**File**: `callflow_tracer/code_churn.py` (382 lines)

**Guide**: [CODE_CHURN_GUIDE.md](CODE_CHURN_GUIDE.md)

**Dataclasses**:
| Class | Purpose | Lines |
|-------|---------|-------|
| `ChurnMetrics` | Churn metrics | 15 |
| `ChurnCorrelation` | Churn correlation | 12 |

**Analyzer Classes**:
| Class | Purpose | Methods | Lines |
|-------|---------|---------|-------|
| `CodeChurnAnalyzer` | Analyze churn | 8 | 165 |
| `ChurnCorrelationAnalyzer` | Correlate metrics | 7 | 135 |

**Key Functions**:
- `generate_churn_report(repo_path, days, complexity_metrics, performance_data)` - Generate report

**CLI Integration**:
- Command: `churn`
- Handler: `_handle_churn()` in `cli.py`
- Output: HTML/JSON reports

**Requirements**: Git repository with history

---

### Integrations Module (`integrations/`)

**Directory**: `callflow_tracer/integrations/`

**Guide**: [INTEGRATIONS_GUIDE.md](INTEGRATIONS_GUIDE.md)

**Integration Modules**:

#### Flask Integration
- **File**: `flask_integration.py` (2,586 bytes)
- **Setup Function**: `setup_flask_tracing(app, output_dir, auto_open, include_args)`
- **Features**: Request tracing, endpoint profiling
- **Async Support**: No
- **Example**: [INTEGRATIONS_GUIDE.md#example-1-flask-with-tracing](INTEGRATIONS_GUIDE.md)

#### FastAPI Integration
- **File**: `fastapi_integration.py` (2,105 bytes)
- **Setup Function**: `setup_fastapi_tracing(app, output_dir, auto_open, include_args)`
- **Features**: Async support, endpoint profiling
- **Async Support**: Yes
- **Example**: [INTEGRATIONS_GUIDE.md#example-2-fastapi-with-async](INTEGRATIONS_GUIDE.md)

#### Django Integration
- **File**: `django_integration.py` (2,586 bytes)
- **Setup Function**: Middleware-based
- **Features**: View tracing, DB monitoring
- **Async Support**: Partial
- **Example**: [INTEGRATIONS_GUIDE.md#example-3-django-with-middleware](INTEGRATIONS_GUIDE.md)

#### SQLAlchemy Integration
- **File**: `sqlalchemy_integration.py` (1,725 bytes)
- **Setup Function**: `setup_sqlalchemy_tracing(engine, log_queries, slow_query_threshold, include_params)`
- **Features**: Query tracing, performance monitoring
- **Async Support**: Yes
- **Example**: [INTEGRATIONS_GUIDE.md#example-4-sqlalchemy-integration](INTEGRATIONS_GUIDE.md)

#### psycopg2 Integration
- **File**: `psycopg2_integration.py` (3,744 bytes)
- **Setup Function**: `setup_psycopg2_tracing(log_queries, slow_query_threshold, include_params)`
- **Features**: Query tracing, connection monitoring
- **Async Support**: No
- **Example**: [INTEGRATIONS_GUIDE.md#example-5-psycopg2-integration](INTEGRATIONS_GUIDE.md)

---

## 🔗 Documentation Cross-Reference

### By Feature

#### CLI
- **Primary Guide**: [CLI_GUIDE.md](CLI_GUIDE.md)
- **Release Notes**: [v0_3_0_RELEASE_NOTES.md](v0_3_0_RELEASE_NOTES.md)
- **Index**: [NEW_FEATURES_INDEX.md](NEW_FEATURES_INDEX.md)
- **Main Index**: [index.md](index.md)

#### Code Quality
- **Primary Guide**: [CODE_QUALITY_GUIDE.md](CODE_QUALITY_GUIDE.md)
- **CLI Command**: `quality`
- **Python API**: `analyze_codebase()`
- **Release Notes**: [v0_3_0_RELEASE_NOTES.md](v0_3_0_RELEASE_NOTES.md)
- **Index**: [NEW_FEATURES_INDEX.md](NEW_FEATURES_INDEX.md)

#### Predictive Analysis
- **Primary Guide**: [PREDICTIVE_ANALYSIS_GUIDE.md](PREDICTIVE_ANALYSIS_GUIDE.md)
- **CLI Command**: `predict`
- **Python API**: `PerformancePredictor`, `CapacityPlanner`, `ScalabilityAnalyzer`, `ResourceForecaster`
- **Release Notes**: [v0_3_0_RELEASE_NOTES.md](v0_3_0_RELEASE_NOTES.md)
- **Index**: [NEW_FEATURES_INDEX.md](NEW_FEATURES_INDEX.md)

#### Code Churn
- **Primary Guide**: [CODE_CHURN_GUIDE.md](CODE_CHURN_GUIDE.md)
- **CLI Command**: `churn`
- **Python API**: `generate_churn_report()`
- **Release Notes**: [v0_3_0_RELEASE_NOTES.md](v0_3_0_RELEASE_NOTES.md)
- **Index**: [NEW_FEATURES_INDEX.md](NEW_FEATURES_INDEX.md)

#### Integrations
- **Primary Guide**: [INTEGRATIONS_GUIDE.md](INTEGRATIONS_GUIDE.md)
- **Frameworks**: Flask, FastAPI, Django, SQLAlchemy, psycopg2
- **Release Notes**: [v0_3_0_RELEASE_NOTES.md](v0_3_0_RELEASE_NOTES.md)
- **Index**: [NEW_FEATURES_INDEX.md](NEW_FEATURES_INDEX.md)

---

## 📊 Feature Matrix

### By Use Case

| Use Case | Feature | CLI | Python API | Guide |
|----------|---------|-----|-----------|-------|
| Find quality issues | Code Quality | `quality` | `analyze_codebase()` | [CODE_QUALITY_GUIDE.md](CODE_QUALITY_GUIDE.md) |
| Identify hotspots | Code Churn | `churn` | `generate_churn_report()` | [CODE_CHURN_GUIDE.md](CODE_CHURN_GUIDE.md) |
| Predict problems | Predictive | `predict` | `PerformancePredictor` | [PREDICTIVE_ANALYSIS_GUIDE.md](PREDICTIVE_ANALYSIS_GUIDE.md) |
| Trace web requests | Integrations | N/A | `setup_*_tracing()` | [INTEGRATIONS_GUIDE.md](INTEGRATIONS_GUIDE.md) |
| Monitor database | Integrations | N/A | `setup_*_tracing()` | [INTEGRATIONS_GUIDE.md](INTEGRATIONS_GUIDE.md) |

### By Framework

| Framework | Integration | Setup | Guide |
|-----------|-------------|-------|-------|
| Flask | `flask_integration.py` | `setup_flask_tracing()` | [INTEGRATIONS_GUIDE.md](INTEGRATIONS_GUIDE.md) |
| FastAPI | `fastapi_integration.py` | `setup_fastapi_tracing()` | [INTEGRATIONS_GUIDE.md](INTEGRATIONS_GUIDE.md) |
| Django | `django_integration.py` | Middleware | [INTEGRATIONS_GUIDE.md](INTEGRATIONS_GUIDE.md) |
| SQLAlchemy | `sqlalchemy_integration.py` | `setup_sqlalchemy_tracing()` | [INTEGRATIONS_GUIDE.md](INTEGRATIONS_GUIDE.md) |
| psycopg2 | `psycopg2_integration.py` | `setup_psycopg2_tracing()` | [INTEGRATIONS_GUIDE.md](INTEGRATIONS_GUIDE.md) |

---

## 🎯 Quick Navigation

### I want to...

#### Use CLI
→ [CLI_GUIDE.md](CLI_GUIDE.md)

#### Analyze code quality
→ [CODE_QUALITY_GUIDE.md](CODE_QUALITY_GUIDE.md)

#### Predict performance issues
→ [PREDICTIVE_ANALYSIS_GUIDE.md](PREDICTIVE_ANALYSIS_GUIDE.md)

#### Find high-risk files
→ [CODE_CHURN_GUIDE.md](CODE_CHURN_GUIDE.md)

#### Integrate with my framework
→ [INTEGRATIONS_GUIDE.md](INTEGRATIONS_GUIDE.md)

#### See all new features
→ [NEW_FEATURES_INDEX.md](NEW_FEATURES_INDEX.md)

#### Read release notes
→ [v0_3_0_RELEASE_NOTES.md](v0_3_0_RELEASE_NOTES.md)

---

## 📈 Feature Statistics

### Code Metrics
- **Total New Modules**: 9
- **Total New Classes**: 20+
- **Total New Functions**: 50+
- **Total New Lines**: 3,200+

### Documentation
- **Total New Guides**: 6
- **Total New Lines**: 1,000+
- **Total Documentation**: 7,000+ lines

### Module Sizes
- `cli.py`: 850 lines
- `code_quality.py`: 633 lines
- `predictive_analysis.py`: 627 lines
- `code_churn.py`: 382 lines
- `integrations/`: 5 modules, ~12,000 bytes

---

## 🔄 Integration Points

### CLI → Analysis Modules
```
cli.py
├── quality command → code_quality.py
├── predict command → predictive_analysis.py
└── churn command → code_churn.py
```

### CLI → Framework Integrations
```
cli.py
└── trace/profile commands → integrations/*
```

### Python API → Analysis Modules
```
code_quality.py → analyze_codebase()
predictive_analysis.py → generate_predictive_report()
code_churn.py → generate_churn_report()
```

### Python API → Framework Integrations
```
integrations/
├── flask_integration.py → setup_flask_tracing()
├── fastapi_integration.py → setup_fastapi_tracing()
├── django_integration.py → middleware
├── sqlalchemy_integration.py → setup_sqlalchemy_tracing()
└── psycopg2_integration.py → setup_psycopg2_tracing()
```

---

## 📝 Documentation Structure

```
docs/
├── index.md (main index, updated)
├── NEW_FEATURES_INDEX.md (new features overview)
├── v0_3_0_RELEASE_NOTES.md (release notes)
├── FEATURE_MAPPING.md (this file)
├── CLI_GUIDE.md (CLI reference)
├── CODE_QUALITY_GUIDE.md (quality analysis)
├── PREDICTIVE_ANALYSIS_GUIDE.md (predictions)
├── CODE_CHURN_GUIDE.md (churn analysis)
└── INTEGRATIONS_GUIDE.md (framework integrations)
```

---

## 🚀 Getting Started Paths

### Path 1: CLI User
1. Read [CLI_GUIDE.md](CLI_GUIDE.md)
2. Try `callflow-tracer quality`
3. Try `callflow-tracer churn`
4. Try `callflow-tracer predict`

### Path 2: Python Developer
1. Read [NEW_FEATURES_INDEX.md](NEW_FEATURES_INDEX.md)
2. Read [CODE_QUALITY_GUIDE.md](CODE_QUALITY_GUIDE.md)
3. Use `analyze_codebase()`
4. Integrate with your code

### Path 3: Web Framework User
1. Read [INTEGRATIONS_GUIDE.md](INTEGRATIONS_GUIDE.md)
2. Choose your framework
3. Call `setup_*_tracing()`
4. Traces generated automatically

### Path 4: Comprehensive Analysis
1. Read [NEW_FEATURES_INDEX.md](NEW_FEATURES_INDEX.md)
2. Read all 6 guides
3. Combine multiple analyses
4. Generate comprehensive reports

---

## 📞 Support Resources

### Documentation
- [NEW_FEATURES_INDEX.md](NEW_FEATURES_INDEX.md) - Start here
- [v0_3_0_RELEASE_NOTES.md](v0_3_0_RELEASE_NOTES.md) - What's new
- [FEATURE_MAPPING.md](FEATURE_MAPPING.md) - This file

### Guides
- [CLI_GUIDE.md](CLI_GUIDE.md)
- [CODE_QUALITY_GUIDE.md](CODE_QUALITY_GUIDE.md)
- [PREDICTIVE_ANALYSIS_GUIDE.md](PREDICTIVE_ANALYSIS_GUIDE.md)
- [CODE_CHURN_GUIDE.md](CODE_CHURN_GUIDE.md)
- [INTEGRATIONS_GUIDE.md](INTEGRATIONS_GUIDE.md)

### Main Documentation
- [index.md](index.md) - Main documentation index

---

*Feature Mapping Guide - v0.3.0*
*Last Updated: 2025-01-15*
