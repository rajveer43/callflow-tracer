# Code Churn Analysis Guide

Complete documentation for code churn analysis and correlation.

**Location**: `callflow_tracer/code_churn.py` (382 lines)

---

## Overview

The Code Churn module analyzes code changes using git history and correlates them with quality and performance metrics to identify high-risk files.

## Key Components

### ChurnMetrics (Dataclass)

Measures code churn for files.

**Attributes**:
- `file_path` - Path to file
- `function_name` - Function name (optional)
- `total_commits` - Number of commits
- `lines_added` - Lines added
- `lines_deleted` - Lines deleted
- `lines_modified` - Total modifications
- `churn_rate` - Changes per day
- `last_modified` - Last modification date
- `authors` - List of authors
- `hotspot_score` - Hotspot score (0-100)

**Hotspot Score Calculation**:
- Commit score: min(commits / 10, 1.0) × 40 (max 40 points)
- Change score: min(lines_changed / 1000, 1.0) × 40 (max 40 points)
- Author score: min(num_authors / 5, 1.0) × 20 (max 20 points)
- Total: 0-100

### ChurnCorrelation (Dataclass)

Correlates churn with quality/performance.

**Attributes**:
- `file_path` - File path
- `churn_score` - Churn hotspot score
- `complexity_score` - Code complexity (0-100)
- `performance_score` - Performance score (0-100)
- `bug_correlation` - Bug correlation (-1 to 1)
- `quality_correlation` - Quality correlation (-1 to 1)
- `risk_assessment` - Low, Medium, High, Critical
- `recommendations` - List of recommendations

## Classes

### CodeChurnAnalyzer

Analyzes code churn using git history.

**Methods**:
- `analyze_file_churn(file_path, days)` - Analyze single file
- `analyze_directory_churn(directory, days)` - Analyze directory
- `identify_hotspots(directory, days, top_n)` - Find hotspots
- `_get_commit_count(file_path, since_date)` - Get commits
- `_get_line_changes(file_path, since_date)` - Get line changes
- `_get_authors(file_path, since_date)` - Get authors
- `_get_last_modified(file_path)` - Get last modified
- `_calculate_hotspot_score(commits, lines_changed, num_authors)` - Calculate score

**Requirements**: Git repository with history

### ChurnCorrelationAnalyzer

Correlates churn with quality metrics.

**Methods**:
- `correlate_churn_with_quality(churn_metrics, complexity_metrics, performance_data)` - Correlate
- `_get_complexity_score(file_path, complexity_metrics)` - Get complexity
- `_get_performance_score(file_path, performance_data)` - Get performance
- `_estimate_bug_correlation(churn_score, complexity_score)` - Estimate bugs
- `_estimate_quality_correlation(churn_rate, complexity_score)` - Estimate quality
- `_assess_risk(churn_score, complexity_score, performance_score)` - Assess risk
- `_generate_recommendations(churn, complexity, performance, risk)` - Generate recommendations

**Risk Assessment**:
- Critical: risk_score ≥ 80
- High: risk_score ≥ 60
- Medium: risk_score ≥ 40
- Low: risk_score < 40

## Usage Examples

### Analyze File Churn
```python
from callflow_tracer.code_churn import CodeChurnAnalyzer

analyzer = CodeChurnAnalyzer(".")
metrics = analyzer.analyze_file_churn("src/main.py", days=90)

print(f"Commits: {metrics.total_commits}")
print(f"Lines modified: {metrics.lines_modified}")
print(f"Churn rate: {metrics.churn_rate:.2f} changes/day")
print(f"Hotspot score: {metrics.hotspot_score:.1f}")
print(f"Authors: {', '.join(metrics.authors)}")
```

### Identify Hotspots
```python
from callflow_tracer.code_churn import CodeChurnAnalyzer

analyzer = CodeChurnAnalyzer(".")
hotspots = analyzer.identify_hotspots(".", days=90, top_n=10)

for i, hotspot in enumerate(hotspots, 1):
    print(f"{i}. {hotspot.file_path}")
    print(f"   Hotspot Score: {hotspot.hotspot_score:.1f}")
    print(f"   Commits: {hotspot.total_commits}")
    print(f"   Churn Rate: {hotspot.churn_rate:.2f}")
```

### Correlate with Quality
```python
from callflow_tracer.code_churn import (
    CodeChurnAnalyzer, 
    ChurnCorrelationAnalyzer
)

analyzer = CodeChurnAnalyzer(".")
churn_metrics = analyzer.analyze_directory_churn(".", days=90)

correlator = ChurnCorrelationAnalyzer()
correlations = correlator.correlate_churn_with_quality(
    churn_metrics, 
    complexity_metrics, 
    performance_data
)

for corr in correlations:
    if corr.risk_assessment == "Critical":
        print(f"CRITICAL: {corr.file_path}")
        print(f"  Churn Score: {corr.churn_score:.1f}")
        print(f"  Complexity: {corr.complexity_score:.1f}")
        print(f"  Performance: {corr.performance_score:.1f}")
        print(f"  Bug Correlation: {corr.bug_correlation:.2f}")
        print(f"  Recommendations:")
        for rec in corr.recommendations:
            print(f"    - {rec}")
```

### Generate Full Report
```python
from callflow_tracer.code_churn import generate_churn_report

report = generate_churn_report(".", days=180)

print(f"Total files: {report['summary']['total_files']}")
print(f"Total commits: {report['summary']['total_commits']}")
print(f"Total changes: {report['summary']['total_changes']}")
print(f"Average churn rate: {report['summary']['average_churn_rate']:.2f}")
print(f"High risk files: {report['summary']['high_risk_files']}")

print("\nTop Hotspots:")
for hotspot in report['hotspots'][:5]:
    print(f"  - {hotspot['file_path']}: {hotspot['hotspot_score']:.1f}")
```

## CLI Usage

```bash
# Analyze code churn
callflow-tracer churn . -o churn_report.html

# Custom time period
callflow-tracer churn . --days 180 -o churn_report.html

# JSON output
callflow-tracer churn . --format json -o churn_report.json

# Specific directory
callflow-tracer churn ./src -o src_churn.html
```

## Output Format

```json
{
  "churn_metrics": [
    {
      "file_path": "src/main.py",
      "function_name": null,
      "total_commits": 45,
      "lines_added": 320,
      "lines_deleted": 180,
      "lines_modified": 500,
      "churn_rate": 5.56,
      "last_modified": "2025-01-15",
      "authors": ["alice", "bob", "charlie"],
      "hotspot_score": 72.5
    }
  ],
  "hotspots": [
    {
      "file_path": "src/main.py",
      "hotspot_score": 72.5,
      "total_commits": 45,
      "lines_modified": 500
    }
  ],
  "correlations": [
    {
      "file_path": "src/main.py",
      "churn_score": 72.5,
      "complexity_score": 65.0,
      "performance_score": 45.0,
      "bug_correlation": 0.68,
      "quality_correlation": -0.55,
      "risk_assessment": "High",
      "recommendations": [
        "High churn detected - consider refactoring",
        "High complexity - simplify code structure",
        "Performance issues detected - profile and optimize"
      ]
    }
  ],
  "summary": {
    "total_files": 42,
    "total_commits": 1250,
    "total_changes": 15000,
    "average_churn_rate": 5.2,
    "analysis_period_days": 90,
    "high_risk_files": 8
  }
}
```

## Interpretation Guide

### Hotspot Scores
- **0-20**: Low churn, stable code
- **20-40**: Moderate churn, normal development
- **40-60**: High churn, active development
- **60-80**: Very high churn, potential instability
- **80-100**: Extreme churn, high risk

### Churn Rate
- **< 1 changes/day**: Stable, mature code
- **1-3 changes/day**: Normal development
- **3-5 changes/day**: Active development
- **5-10 changes/day**: High activity, potential issues
- **> 10 changes/day**: Very high activity, risk area

### Correlations
- **Bug Correlation**: Positive values indicate correlation with bugs
- **Quality Correlation**: Negative values indicate quality issues
- **Risk Assessment**: Combined assessment of all factors

### Recommendations
- **Refactoring**: High churn suggests code needs restructuring
- **Testing**: High churn increases bug risk
- **Documentation**: Multiple authors need clear documentation
- **Review**: High-risk files need code review
