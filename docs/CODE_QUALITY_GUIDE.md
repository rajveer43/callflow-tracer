# Code Quality Analysis Guide

Complete documentation for code quality metrics and analysis.

**Location**: `callflow_tracer/code_quality.py` (633 lines)

---

## Overview

The Code Quality module analyzes Python code for complexity, maintainability, and technical debt metrics using AST analysis.

## Key Components

### ComplexityMetrics (Dataclass)

Measures cyclomatic and cognitive complexity.

**Attributes**:
- `function_name` - Function name
- `module` - Module name
- `cyclomatic_complexity` - McCabe complexity (1-based)
- `cognitive_complexity` - Human-oriented complexity
- `nesting_depth` - Maximum nesting level
- `num_branches` - Number of if/elif/else branches
- `num_loops` - Number of loops
- `num_returns` - Number of return statements
- `lines_of_code` - Function length

**Complexity Ratings**:
- Simple: ≤ 5
- Moderate: 6-10
- Complex: 11-20
- Very Complex: > 20

### MaintainabilityMetrics (Dataclass)

Measures code maintainability using Halstead metrics.

**Attributes**:
- `function_name` - Function name
- `module` - Module name
- `maintainability_index` - MI score (0-100)
- `halstead_volume` - Code volume metric
- `halstead_difficulty` - Difficulty metric
- `halstead_effort` - Effort to understand
- `lines_of_code` - Function length
- `comment_ratio` - Comments to code ratio

**Maintainability Ratings**:
- Excellent: ≥ 80
- Good: 60-79
- Fair: 40-59
- Poor: 20-39
- Critical: < 20

### TechnicalDebtIndicator (Dataclass)

Identifies technical debt in code.

**Attributes**:
- `function_name` - Function name
- `module` - Module name
- `debt_score` - Debt score (0-100)
- `issues` - List of issues
- `severity` - Low, Medium, High, Critical
- `estimated_hours` - Hours to fix

### ComplexityAnalyzer (Class)

Analyzes cyclomatic complexity using AST.

**Methods**:
- `analyze_function(func_node, module)` - Analyze single function
- `analyze_file(filepath)` - Analyze all functions
- `_calculate_cyclomatic_complexity(node)` - Calculate McCabe complexity
- `_calculate_cognitive_complexity(node, nesting)` - Calculate cognitive complexity
- `_calculate_max_nesting_depth(node)` - Find max nesting
- `_count_branches(node)` - Count if/elif/else
- `_count_loops(node)` - Count loops
- `_count_returns(node)` - Count returns
- `_count_lines_of_code(node)` - Count LOC

### MaintainabilityAnalyzer (Class)

Analyzes maintainability using Halstead metrics.

**Methods**:
- `analyze_function(func_node, module, source_lines)` - Analyze function
- `analyze_file(filepath)` - Analyze all functions
- `_calculate_halstead_metrics(node)` - Calculate Halstead metrics
- `_calculate_maintainability_index(volume, complexity, loc)` - Calculate MI
- `_calculate_comment_ratio(node, source_lines)` - Calculate comment ratio

### TechnicalDebtAnalyzer (Class)

Identifies technical debt issues.

**Methods**:
- `analyze_from_metrics(complexity_metrics, maintainability_metrics)` - Analyze debt

**Debt Scoring**:
- Very high cyclomatic complexity (>20): +30 points
- High cyclomatic complexity (>10): +15 points
- High cognitive complexity (>15): +20 points
- Deep nesting (>4 levels): +15 points
- Long functions (>100 lines): +10 points
- Critical maintainability (<20): +40 points
- Poor maintainability (<40): +25 points
- Insufficient documentation: +10 points

### QualityTrendAnalyzer (Class)

Tracks quality metrics over time.

**Methods**:
- `add_snapshot(complexity_metrics, maintainability_metrics, debt_indicators)` - Add snapshot
- `get_trends(days)` - Get trends for N days
- `analyze_trends()` - Analyze trend direction
- `_calculate_trend(values)` - Calculate trend

## Usage Examples

### Analyze Single File
```python
from callflow_tracer.code_quality import ComplexityAnalyzer

analyzer = ComplexityAnalyzer()
metrics = analyzer.analyze_file("my_module.py")

for metric in metrics:
    print(f"{metric.function_name}: {metric.complexity_rating}")
```

### Analyze Entire Codebase
```python
from callflow_tracer.code_quality import analyze_codebase

results = analyze_codebase("./src")
print(f"Average Complexity: {results['summary']['average_complexity']:.2f}")
print(f"Critical Issues: {results['summary']['critical_issues']}")
```

### Track Quality Trends
```python
from callflow_tracer.code_quality import QualityTrendAnalyzer

trend_analyzer = QualityTrendAnalyzer()
trend = trend_analyzer.add_snapshot(complexity, maintainability, debt)
trends = trend_analyzer.analyze_trends()
print(f"Complexity Trend: {trends['complexity_trend']}")
```

### Identify Technical Debt
```python
from callflow_tracer.code_quality import TechnicalDebtAnalyzer

debt_analyzer = TechnicalDebtAnalyzer()
debt_indicators = debt_analyzer.analyze_from_metrics(complexity, maintainability)

for indicator in debt_indicators:
    if indicator.severity == "Critical":
        print(f"CRITICAL: {indicator.function_name}")
        print(f"  Issues: {', '.join(indicator.issues)}")
```

## CLI Usage

```bash
# Analyze code quality
callflow-tracer quality . -o quality_report.html

# With trend tracking
callflow-tracer quality . --track-trends --format json

# Specific directory
callflow-tracer quality ./src -o src_quality.html
```

## Output Format

```json
{
  "complexity_metrics": [
    {
      "function_name": "process_data",
      "module": "data_processor",
      "cyclomatic_complexity": 8,
      "cognitive_complexity": 6,
      "nesting_depth": 3,
      "num_branches": 4,
      "num_loops": 2,
      "num_returns": 3,
      "lines_of_code": 45
    }
  ],
  "maintainability_metrics": [
    {
      "function_name": "process_data",
      "module": "data_processor",
      "maintainability_index": 72.5,
      "halstead_volume": 245.3,
      "halstead_difficulty": 12.4,
      "halstead_effort": 3041.7,
      "lines_of_code": 45,
      "comment_ratio": 0.15
    }
  ],
  "debt_indicators": [
    {
      "function_name": "process_data",
      "module": "data_processor",
      "debt_score": 25.0,
      "issues": ["High cyclomatic complexity (8)"],
      "severity": "Medium",
      "estimated_hours": 2.5
    }
  ],
  "summary": {
    "total_functions": 42,
    "average_complexity": 6.8,
    "average_maintainability": 68.3,
    "total_debt_score": 245.0,
    "critical_issues": 2,
    "high_issues": 5
  }
}
```

## Interpretation Guide

### Complexity Levels
- **Simple (≤5)**: Easy to understand and maintain
- **Moderate (6-10)**: Acceptable complexity
- **Complex (11-20)**: Difficult to understand, refactor recommended
- **Very Complex (>20)**: Extremely difficult, refactoring required

### Maintainability Index
- **Excellent (≥80)**: Highly maintainable
- **Good (60-79)**: Maintainable
- **Fair (40-59)**: Moderate effort to maintain
- **Poor (20-39)**: Difficult to maintain
- **Critical (<20)**: Very difficult to maintain

### Technical Debt
- **Low (<20)**: Minimal debt, acceptable
- **Medium (20-40)**: Some debt, should address
- **High (40-60)**: Significant debt, prioritize fixes
- **Critical (>60)**: Severe debt, immediate action needed
