"""
Advanced analysis capabilities.

Provides:
- Cross-trace comparative analysis
- Architecture advisor
- Regression detection
- Refactoring recommendations
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging

from .llm_provider import LLMProvider

logger = logging.getLogger(__name__)


@dataclass
class TraceMetrics:
    """Metrics extracted from a trace."""
    total_time_ms: float
    total_calls: int
    unique_functions: int
    max_depth: int
    avg_call_time_ms: float
    hottest_function: str
    hottest_function_time_ms: float


@dataclass
class RegressionAnalysis:
    """Result of regression analysis."""
    has_regression: bool
    regression_severity: str  # "critical", "high", "medium", "low"
    affected_functions: List[str]
    performance_delta_percent: float
    root_causes: List[str]
    recommendations: List[str]


@dataclass
class ArchitectureRecommendation:
    """Recommendation for architectural improvement."""
    recommendation: str
    rationale: str
    affected_components: List[str]
    estimated_benefit: str
    implementation_effort: str  # "low", "medium", "high"
    risk_level: str  # "low", "medium", "high"


class ComparativeAnalyzer:
    """
    Analyzes differences between two execution traces.
    
    Detects:
    - Performance regressions
    - New bottlenecks
    - Improved functions
    - Behavior changes
    """
    
    def __init__(self, provider: LLMProvider):
        """Initialize comparative analyzer."""
        self.provider = provider
    
    def compare_traces(
        self,
        before_trace: str,
        after_trace: str,
        context: Optional[str] = None,
    ) -> RegressionAnalysis:
        """
        Compare two execution traces.
        
        Args:
            before_trace: Baseline execution trace
            after_trace: New execution trace
            context: Additional context (e.g., what changed)
            
        Returns:
            RegressionAnalysis with findings
        """
        # Extract metrics
        before_metrics = self._extract_metrics(before_trace)
        after_metrics = self._extract_metrics(after_trace)
        
        # Calculate deltas
        performance_delta = (
            (after_metrics.total_time_ms - before_metrics.total_time_ms)
            / before_metrics.total_time_ms * 100
        )
        
        # Determine severity
        if performance_delta > 20:
            severity = "critical"
        elif performance_delta > 10:
            severity = "high"
        elif performance_delta > 5:
            severity = "medium"
        else:
            severity = "low"
        
        has_regression = performance_delta > 5
        
        # Get LLM analysis
        llm_analysis = self._get_llm_analysis(
            before_trace, after_trace, context, performance_delta
        )
        
        root_causes, recommendations = self._parse_llm_analysis(llm_analysis)
        
        # Identify affected functions
        affected = self._identify_affected_functions(before_trace, after_trace)
        
        logger.info(
            f"Comparative analysis: {performance_delta:+.1f}% delta, "
            f"severity={severity}, affected={len(affected)} functions"
        )
        
        return RegressionAnalysis(
            has_regression=has_regression,
            regression_severity=severity,
            affected_functions=affected,
            performance_delta_percent=performance_delta,
            root_causes=root_causes,
            recommendations=recommendations,
        )
    
    def _extract_metrics(self, trace: str) -> TraceMetrics:
        """Extract metrics from trace."""
        # Placeholder: would parse actual trace
        lines = trace.split('\n')
        
        return TraceMetrics(
            total_time_ms=1000.0,  # Placeholder
            total_calls=len(lines),
            unique_functions=len(set(lines)),
            max_depth=10,
            avg_call_time_ms=1000.0 / len(lines) if lines else 0,
            hottest_function="main",
            hottest_function_time_ms=500.0,
        )
    
    def _get_llm_analysis(
        self,
        before_trace: str,
        after_trace: str,
        context: Optional[str],
        delta: float,
    ) -> str:
        """Get LLM analysis of regression."""
        prompt = f"""Analyze this performance regression between two execution traces.

PERFORMANCE DELTA: {delta:+.1f}%

BEFORE TRACE (baseline):
{before_trace[:1000]}

AFTER TRACE (new):
{after_trace[:1000]}

"""
        
        if context:
            prompt += f"CONTEXT (what changed):\n{context}\n"
        
        prompt += """ANALYSIS REQUIRED:
1. Root causes of the regression
2. Which functions are affected
3. Why the regression occurred
4. Recommendations to fix it

Be specific and data-driven."""
        
        response = self.provider.generate(
            prompt,
            system="""You are a performance analyst comparing execution traces.
Identify root causes of regressions and provide actionable recommendations.""",
            temperature=0.3,
        )
        
        return response
    
    def _parse_llm_analysis(self, analysis: str) -> Tuple[List[str], List[str]]:
        """Parse LLM analysis response."""
        root_causes = []
        recommendations = []
        
        lines = analysis.split('\n')
        current_section = None
        
        for line in lines:
            if 'root cause' in line.lower():
                current_section = 'root_causes'
            elif 'recommendation' in line.lower():
                current_section = 'recommendations'
            elif line.strip().startswith('-') or line.strip().startswith('*'):
                if current_section == 'root_causes':
                    root_causes.append(line.strip()[1:].strip())
                elif current_section == 'recommendations':
                    recommendations.append(line.strip()[1:].strip())
        
        return root_causes, recommendations
    
    def _identify_affected_functions(
        self, before_trace: str, after_trace: str
    ) -> List[str]:
        """Identify functions affected by regression."""
        # Placeholder: would parse traces and compare
        return ["main", "process_data", "query_database"]


class ArchitectureAdvisor:
    """
    Provides architectural recommendations based on call graphs.
    
    Suggests:
    - CQRS pattern for read-heavy workloads
    - Caching strategies
    - Microservice boundaries
    - Async/await opportunities
    - Batch processing opportunities
    """
    
    def __init__(self, provider: LLMProvider):
        """Initialize architecture advisor."""
        self.provider = provider
    
    def analyze_architecture(
        self,
        call_graph: str,
        hot_paths: List[str],
        current_architecture: Optional[str] = None,
    ) -> List[ArchitectureRecommendation]:
        """
        Analyze architecture and provide recommendations.
        
        Args:
            call_graph: Call graph representation
            hot_paths: List of hot execution paths
            current_architecture: Description of current architecture
            
        Returns:
            List of architecture recommendations
        """
        # Get LLM analysis
        llm_recommendations = self._get_llm_recommendations(
            call_graph, hot_paths, current_architecture
        )
        
        # Parse recommendations
        recommendations = self._parse_recommendations(llm_recommendations)
        
        logger.info(f"Architecture analysis: {len(recommendations)} recommendations")
        
        return recommendations
    
    def _get_llm_recommendations(
        self,
        call_graph: str,
        hot_paths: List[str],
        current_architecture: Optional[str],
    ) -> str:
        """Get LLM architecture recommendations."""
        prompt = f"""Analyze this application architecture and provide recommendations.

CALL GRAPH:
{call_graph[:1000]}

HOT EXECUTION PATHS (performance-critical):
{chr(10).join(hot_paths[:5])}

"""
        
        if current_architecture:
            prompt += f"CURRENT ARCHITECTURE:\n{current_architecture}\n"
        
        prompt += """PROVIDE RECOMMENDATIONS FOR:
1. Caching opportunities (what to cache, where)
2. Async/await opportunities (which operations should be async)
3. Batch processing opportunities (where to batch operations)
4. Microservice boundaries (if applicable)
5. Design pattern applications (CQRS, Event Sourcing, etc.)
6. Load balancing and scaling strategies

For each recommendation, explain:
- What to change
- Why it helps
- Estimated performance improvement
- Implementation effort (low/medium/high)
- Risk level (low/medium/high)"""
        
        response = self.provider.generate(
            prompt,
            system="""You are a software architect specializing in performance and scalability.
Analyze call graphs and provide specific, implementable architectural recommendations.
Focus on high-impact changes that improve performance and maintainability.""",
            temperature=0.3,
        )
        
        return response
    
    def _parse_recommendations(self, llm_response: str) -> List[ArchitectureRecommendation]:
        """Parse LLM recommendations."""
        recommendations = []
        
        # Placeholder: would parse structured response
        # In production, would use JSON parsing or structured output
        
        lines = llm_response.split('\n')
        current_rec = None
        
        for line in lines:
            if line.startswith('##') or line.startswith('###'):
                if current_rec:
                    recommendations.append(current_rec)
                
                current_rec = ArchitectureRecommendation(
                    recommendation=line.strip('#').strip(),
                    rationale="",
                    affected_components=[],
                    estimated_benefit="",
                    implementation_effort="medium",
                    risk_level="medium",
                )
        
        if current_rec:
            recommendations.append(current_rec)
        
        return recommendations


class RefactoringAdvisor:
    """
    Provides refactoring recommendations based on code analysis.
    
    Suggests:
    - Extract methods
    - Reduce complexity
    - Apply design patterns
    - Improve testability
    """
    
    def __init__(self, provider: LLMProvider):
        """Initialize refactoring advisor."""
        self.provider = provider
    
    def suggest_refactorings(
        self,
        code: str,
        metrics: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Suggest refactorings for code.
        
        Args:
            code: Source code to analyze
            metrics: Code metrics (complexity, length, etc.)
            constraints: Constraints (e.g., backward compatibility)
            
        Returns:
            List of refactoring suggestions
        """
        prompt = f"""Analyze this code and suggest refactorings.

CODE:
{code[:2000]}

METRICS:
{chr(10).join(f"- {k}: {v}" for k, v in metrics.items())}

"""
        
        if constraints:
            prompt += f"CONSTRAINTS:\n{chr(10).join(f'- {k}: {v}' for k, v in constraints.items())}\n"
        
        prompt += """SUGGEST REFACTORINGS FOR:
1. Reducing complexity (cyclomatic, cognitive)
2. Improving readability
3. Enhancing testability
4. Applying design patterns
5. Reducing code duplication

For each refactoring:
- Explain the change
- Show before/after code snippets
- Estimate complexity reduction
- Assess implementation effort
- Identify risks"""
        
        response = self.provider.generate(
            prompt,
            system="""You are a code refactoring expert.
Provide specific, implementable refactoring suggestions that improve code quality.
Focus on high-impact changes that reduce complexity and improve maintainability.""",
            temperature=0.3,
        )
        
        return self._parse_refactorings(response)
    
    def _parse_refactorings(self, response: str) -> List[Dict[str, Any]]:
        """Parse refactoring suggestions."""
        # Placeholder: would parse structured response
        return [
            {
                "suggestion": "Extract method",
                "rationale": "Reduce complexity",
                "effort": "low",
                "impact": "high",
            }
        ]
