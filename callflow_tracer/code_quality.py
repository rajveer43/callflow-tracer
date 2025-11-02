"""
Code Quality Metrics Module for CallFlow Tracer.

This module analyzes code quality from execution traces including:
- Cyclomatic complexity estimation
- Maintainability index calculation
- Code quality trends
- Technical debt indicators
"""

import ast
import os
import math
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ComplexityMetrics:
    """Cyclomatic complexity metrics for a function."""
    function_name: str
    module: str
    cyclomatic_complexity: int
    cognitive_complexity: int
    nesting_depth: int
    num_branches: int
    num_loops: int
    num_returns: int
    lines_of_code: int
    
    def to_dict(self):
        return asdict(self)
    
    @property
    def complexity_rating(self) -> str:
        """Get complexity rating based on cyclomatic complexity."""
        if self.cyclomatic_complexity <= 5:
            return "Simple"
        elif self.cyclomatic_complexity <= 10:
            return "Moderate"
        elif self.cyclomatic_complexity <= 20:
            return "Complex"
        else:
            return "Very Complex"


@dataclass
class MaintainabilityMetrics:
    """Maintainability index and related metrics."""
    function_name: str
    module: str
    maintainability_index: float  # 0-100, higher is better
    halstead_volume: float
    halstead_difficulty: float
    halstead_effort: float
    lines_of_code: int
    comment_ratio: float
    
    def to_dict(self):
        return asdict(self)
    
    @property
    def maintainability_rating(self) -> str:
        """Get maintainability rating."""
        if self.maintainability_index >= 80:
            return "Excellent"
        elif self.maintainability_index >= 60:
            return "Good"
        elif self.maintainability_index >= 40:
            return "Fair"
        elif self.maintainability_index >= 20:
            return "Poor"
        else:
            return "Critical"


@dataclass
class TechnicalDebtIndicator:
    """Technical debt indicators for a function."""
    function_name: str
    module: str
    debt_score: float  # 0-100, higher is worse
    issues: List[str]
    severity: str  # Low, Medium, High, Critical
    estimated_hours: float  # Estimated hours to fix
    
    def to_dict(self):
        return asdict(self)


@dataclass
class QualityTrend:
    """Quality trend data over time."""
    timestamp: str
    average_complexity: float
    average_maintainability: float
    total_debt_score: float
    num_functions: int
    num_issues: int
    
    def to_dict(self):
        return asdict(self)


class ComplexityAnalyzer:
    """Analyze cyclomatic complexity from source code."""
    
    def __init__(self):
        self.metrics = {}
    
    def analyze_function(self, func_node: ast.FunctionDef, module: str = "") -> ComplexityMetrics:
        """Analyze a single function for complexity metrics."""
        complexity = self._calculate_cyclomatic_complexity(func_node)
        cognitive = self._calculate_cognitive_complexity(func_node)
        nesting = self._calculate_max_nesting_depth(func_node)
        branches = self._count_branches(func_node)
        loops = self._count_loops(func_node)
        returns = self._count_returns(func_node)
        loc = self._count_lines_of_code(func_node)
        
        return ComplexityMetrics(
            function_name=func_node.name,
            module=module,
            cyclomatic_complexity=complexity,
            cognitive_complexity=cognitive,
            nesting_depth=nesting,
            num_branches=branches,
            num_loops=loops,
            num_returns=returns,
            lines_of_code=loc
        )
    
    def analyze_file(self, filepath: str) -> List[ComplexityMetrics]:
        """Analyze all functions in a file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            module_name = Path(filepath).stem
            
            metrics = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metric = self.analyze_function(node, module_name)
                    metrics.append(metric)
            
            return metrics
        except Exception as e:
            print(f"Error analyzing {filepath}: {e}")
            return []
    
    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity (McCabe)."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            # Decision points
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.With):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # Each 'and'/'or' adds complexity
                complexity += len(child.values) - 1
            elif isinstance(child, ast.comprehension):
                complexity += 1
                if child.ifs:
                    complexity += len(child.ifs)
        
        return complexity
    
    def _calculate_cognitive_complexity(self, node: ast.AST, nesting: int = 0) -> int:
        """Calculate cognitive complexity (more human-oriented)."""
        complexity = 0
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1 + nesting
                complexity += self._calculate_cognitive_complexity(child, nesting + 1)
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            else:
                complexity += self._calculate_cognitive_complexity(child, nesting)
        
        return complexity
    
    def _calculate_max_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth."""
        max_depth = current_depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.With, ast.Try)):
                child_depth = self._calculate_max_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._calculate_max_nesting_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def _count_branches(self, node: ast.AST) -> int:
        """Count number of branches (if/elif/else)."""
        count = 0
        for child in ast.walk(node):
            if isinstance(child, ast.If):
                count += 1
                if child.orelse:
                    count += 1
        return count
    
    def _count_loops(self, node: ast.AST) -> int:
        """Count number of loops."""
        count = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.For, ast.While, ast.AsyncFor)):
                count += 1
        return count
    
    def _count_returns(self, node: ast.AST) -> int:
        """Count number of return statements."""
        count = 0
        for child in ast.walk(node):
            if isinstance(child, ast.Return):
                count += 1
        return count
    
    def _count_lines_of_code(self, node: ast.AST) -> int:
        """Count lines of code (excluding comments and blank lines)."""
        if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
            return node.end_lineno - node.lineno + 1
        return 0


class MaintainabilityAnalyzer:
    """Analyze code maintainability using Halstead metrics and MI."""
    
    def __init__(self):
        self.metrics = {}
    
    def analyze_function(self, func_node: ast.FunctionDef, module: str = "", 
                        source_lines: List[str] = None) -> MaintainabilityMetrics:
        """Analyze maintainability of a function."""
        halstead = self._calculate_halstead_metrics(func_node)
        loc = self._count_lines_of_code(func_node)
        comment_ratio = self._calculate_comment_ratio(func_node, source_lines)
        complexity = ComplexityAnalyzer()._calculate_cyclomatic_complexity(func_node)
        
        # Calculate Maintainability Index
        mi = self._calculate_maintainability_index(
            halstead['volume'],
            complexity,
            loc
        )
        
        return MaintainabilityMetrics(
            function_name=func_node.name,
            module=module,
            maintainability_index=mi,
            halstead_volume=halstead['volume'],
            halstead_difficulty=halstead['difficulty'],
            halstead_effort=halstead['effort'],
            lines_of_code=loc,
            comment_ratio=comment_ratio
        )
    
    def analyze_file(self, filepath: str) -> List[MaintainabilityMetrics]:
        """Analyze all functions in a file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
                source_lines = source.split('\n')
            
            tree = ast.parse(source)
            module_name = Path(filepath).stem
            
            metrics = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metric = self.analyze_function(node, module_name, source_lines)
                    metrics.append(metric)
            
            return metrics
        except Exception as e:
            print(f"Error analyzing {filepath}: {e}")
            return []
    
    def _calculate_halstead_metrics(self, node: ast.AST) -> Dict[str, float]:
        """Calculate Halstead complexity metrics."""
        operators = set()
        operands = set()
        operator_count = 0
        operand_count = 0
        
        for child in ast.walk(node):
            # Operators
            if isinstance(child, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod,
                                 ast.Pow, ast.LShift, ast.RShift, ast.BitOr,
                                 ast.BitXor, ast.BitAnd, ast.FloorDiv)):
                operators.add(type(child).__name__)
                operator_count += 1
            elif isinstance(child, (ast.And, ast.Or, ast.Not)):
                operators.add(type(child).__name__)
                operator_count += 1
            elif isinstance(child, (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE)):
                operators.add(type(child).__name__)
                operator_count += 1
            elif isinstance(child, (ast.If, ast.For, ast.While, ast.FunctionDef)):
                operators.add(type(child).__name__)
                operator_count += 1
            
            # Operands
            elif isinstance(child, ast.Name):
                operands.add(child.id)
                operand_count += 1
            elif isinstance(child, (ast.Constant, ast.Num, ast.Str)):
                operands.add(str(getattr(child, 'value', 'const')))
                operand_count += 1
        
        n1 = len(operators)  # Unique operators
        n2 = len(operands)   # Unique operands
        N1 = operator_count  # Total operators
        N2 = operand_count   # Total operands
        
        # Avoid division by zero
        if n1 == 0 or n2 == 0:
            return {
                'volume': 0,
                'difficulty': 0,
                'effort': 0,
                'time': 0,
                'bugs': 0
            }
        
        # Halstead metrics
        vocabulary = n1 + n2
        length = N1 + N2
        volume = length * math.log2(vocabulary) if vocabulary > 0 else 0
        difficulty = (n1 / 2) * (N2 / n2) if n2 > 0 else 0
        effort = volume * difficulty
        time = effort / 18  # Time in seconds
        bugs = volume / 3000  # Estimated bugs
        
        return {
            'volume': volume,
            'difficulty': difficulty,
            'effort': effort,
            'time': time,
            'bugs': bugs
        }
    
    def _calculate_maintainability_index(self, volume: float, complexity: int, 
                                        loc: int) -> float:
        """Calculate Maintainability Index (0-100)."""
        if loc == 0:
            return 100.0
        
        # MI = 171 - 5.2 * ln(V) - 0.23 * G - 16.2 * ln(LOC)
        # Where V = Halstead Volume, G = Cyclomatic Complexity, LOC = Lines of Code
        
        try:
            mi = 171
            mi -= 5.2 * math.log(volume) if volume > 0 else 0
            mi -= 0.23 * complexity
            mi -= 16.2 * math.log(loc) if loc > 0 else 0
            
            # Normalize to 0-100
            mi = max(0, min(100, (mi / 171) * 100))
            
            return round(mi, 2)
        except:
            return 50.0  # Default to middle value on error
    
    def _count_lines_of_code(self, node: ast.AST) -> int:
        """Count lines of code."""
        if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
            return node.end_lineno - node.lineno + 1
        return 0
    
    def _calculate_comment_ratio(self, node: ast.AST, source_lines: List[str]) -> float:
        """Calculate ratio of comments to code."""
        if not source_lines or not hasattr(node, 'lineno'):
            return 0.0
        
        start = node.lineno - 1
        end = node.end_lineno if hasattr(node, 'end_lineno') else start + 1
        
        comment_lines = 0
        code_lines = 0
        
        for i in range(start, min(end, len(source_lines))):
            line = source_lines[i].strip()
            if line.startswith('#'):
                comment_lines += 1
            elif line and not line.startswith('#'):
                code_lines += 1
        
        total = comment_lines + code_lines
        return comment_lines / total if total > 0 else 0.0


class TechnicalDebtAnalyzer:
    """Analyze technical debt from code metrics."""
    
    def __init__(self):
        self.debt_indicators = []
    
    def analyze_from_metrics(self, complexity_metrics: List[ComplexityMetrics],
                            maintainability_metrics: List[MaintainabilityMetrics]) -> List[TechnicalDebtIndicator]:
        """Analyze technical debt from complexity and maintainability metrics."""
        debt_indicators = []
        
        # Create lookup for maintainability
        maint_lookup = {m.function_name: m for m in maintainability_metrics}
        
        for comp in complexity_metrics:
            issues = []
            debt_score = 0.0
            
            # Check complexity issues
            if comp.cyclomatic_complexity > 20:
                issues.append(f"Very high cyclomatic complexity ({comp.cyclomatic_complexity})")
                debt_score += 30
            elif comp.cyclomatic_complexity > 10:
                issues.append(f"High cyclomatic complexity ({comp.cyclomatic_complexity})")
                debt_score += 15
            
            if comp.cognitive_complexity > 15:
                issues.append(f"High cognitive complexity ({comp.cognitive_complexity})")
                debt_score += 20
            
            if comp.nesting_depth > 4:
                issues.append(f"Deep nesting ({comp.nesting_depth} levels)")
                debt_score += 15
            
            if comp.lines_of_code > 100:
                issues.append(f"Function too long ({comp.lines_of_code} lines)")
                debt_score += 10
            
            # Check maintainability issues
            maint = maint_lookup.get(comp.function_name)
            if maint:
                if maint.maintainability_index < 20:
                    issues.append(f"Critical maintainability ({maint.maintainability_index:.1f})")
                    debt_score += 40
                elif maint.maintainability_index < 40:
                    issues.append(f"Poor maintainability ({maint.maintainability_index:.1f})")
                    debt_score += 25
                
                if maint.comment_ratio < 0.1:
                    issues.append("Insufficient documentation")
                    debt_score += 10
            
            # Determine severity
            if debt_score >= 60:
                severity = "Critical"
            elif debt_score >= 40:
                severity = "High"
            elif debt_score >= 20:
                severity = "Medium"
            else:
                severity = "Low"
            
            # Estimate hours to fix (rough estimate)
            estimated_hours = debt_score / 10
            
            if issues:  # Only add if there are issues
                indicator = TechnicalDebtIndicator(
                    function_name=comp.function_name,
                    module=comp.module,
                    debt_score=debt_score,
                    issues=issues,
                    severity=severity,
                    estimated_hours=estimated_hours
                )
                debt_indicators.append(indicator)
        
        return sorted(debt_indicators, key=lambda x: x.debt_score, reverse=True)


class QualityTrendAnalyzer:
    """Track quality trends over time."""
    
    def __init__(self, history_file: Optional[str] = None):
        self.history_file = history_file or "quality_history.json"
        self.history = self._load_history()
    
    def _load_history(self) -> List[QualityTrend]:
        """Load historical quality data."""
        import json
        
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    return [QualityTrend(**item) for item in data]
            except:
                return []
        return []
    
    def _save_history(self):
        """Save historical quality data."""
        import json
        
        with open(self.history_file, 'w') as f:
            json.dump([trend.to_dict() for trend in self.history], f, indent=2)
    
    def add_snapshot(self, complexity_metrics: List[ComplexityMetrics],
                    maintainability_metrics: List[MaintainabilityMetrics],
                    debt_indicators: List[TechnicalDebtIndicator]):
        """Add a quality snapshot to history."""
        avg_complexity = sum(m.cyclomatic_complexity for m in complexity_metrics) / len(complexity_metrics) if complexity_metrics else 0
        avg_maintainability = sum(m.maintainability_index for m in maintainability_metrics) / len(maintainability_metrics) if maintainability_metrics else 0
        total_debt = sum(d.debt_score for d in debt_indicators)
        
        trend = QualityTrend(
            timestamp=datetime.now().isoformat(),
            average_complexity=round(avg_complexity, 2),
            average_maintainability=round(avg_maintainability, 2),
            total_debt_score=round(total_debt, 2),
            num_functions=len(complexity_metrics),
            num_issues=sum(len(d.issues) for d in debt_indicators)
        )
        
        self.history.append(trend)
        self._save_history()
        
        return trend
    
    def get_trends(self, days: int = 30) -> List[QualityTrend]:
        """Get quality trends for the last N days."""
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        
        return [
            trend for trend in self.history
            if datetime.fromisoformat(trend.timestamp) >= cutoff
        ]
    
    def analyze_trends(self) -> Dict[str, Any]:
        """Analyze quality trends."""
        if len(self.history) < 2:
            return {"status": "insufficient_data"}
        
        recent = self.history[-10:]  # Last 10 snapshots
        
        # Calculate trends
        complexity_trend = self._calculate_trend([t.average_complexity for t in recent])
        maintainability_trend = self._calculate_trend([t.average_maintainability for t in recent])
        debt_trend = self._calculate_trend([t.total_debt_score for t in recent])
        
        return {
            "complexity_trend": complexity_trend,
            "maintainability_trend": maintainability_trend,
            "debt_trend": debt_trend,
            "current_complexity": recent[-1].average_complexity,
            "current_maintainability": recent[-1].average_maintainability,
            "current_debt": recent[-1].total_debt_score,
            "snapshots_analyzed": len(recent)
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction."""
        if len(values) < 2:
            return "stable"
        
        # Simple linear regression slope
        n = len(values)
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return "stable"
        
        slope = numerator / denominator
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"


def analyze_codebase(directory: str, file_pattern: str = "*.py") -> Dict[str, Any]:
    """Analyze entire codebase for quality metrics."""
    from glob import glob
    
    complexity_analyzer = ComplexityAnalyzer()
    maintainability_analyzer = MaintainabilityAnalyzer()
    debt_analyzer = TechnicalDebtAnalyzer()
    
    all_complexity = []
    all_maintainability = []
    
    # Find all Python files
    pattern = os.path.join(directory, "**", file_pattern)
    files = glob(pattern, recursive=True)
    
    for filepath in files:
        comp_metrics = complexity_analyzer.analyze_file(filepath)
        maint_metrics = maintainability_analyzer.analyze_file(filepath)
        
        all_complexity.extend(comp_metrics)
        all_maintainability.extend(maint_metrics)
    
    # Analyze technical debt
    debt_indicators = debt_analyzer.analyze_from_metrics(all_complexity, all_maintainability)
    
    return {
        "complexity_metrics": [m.to_dict() for m in all_complexity],
        "maintainability_metrics": [m.to_dict() for m in all_maintainability],
        "debt_indicators": [d.to_dict() for d in debt_indicators],
        "summary": {
            "total_functions": len(all_complexity),
            "average_complexity": sum(m.cyclomatic_complexity for m in all_complexity) / len(all_complexity) if all_complexity else 0,
            "average_maintainability": sum(m.maintainability_index for m in all_maintainability) / len(all_maintainability) if all_maintainability else 0,
            "total_debt_score": sum(d.debt_score for d in debt_indicators),
            "critical_issues": len([d for d in debt_indicators if d.severity == "Critical"]),
            "high_issues": len([d for d in debt_indicators if d.severity == "High"])
        }
    }
