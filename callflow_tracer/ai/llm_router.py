"""
LLM routing and orchestration for intelligent model selection.

Provides multi-LLM routing, ensemble capabilities, and task-specific model selection
based on cost, latency, complexity, and context window requirements.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from .llm_provider import (
    LLMProvider, OpenAIProvider, AnthropicProvider, 
    GoogleGeminiProvider, OllamaProvider
)

logger = logging.getLogger(__name__)


class TaskComplexity(Enum):
    """Task complexity levels for routing decisions."""
    SIMPLE = "simple"          # Simple queries, quick answers
    MODERATE = "moderate"      # Standard analysis, medium reasoning
    COMPLEX = "complex"        # Deep analysis, multi-step reasoning
    CRITICAL = "critical"      # Security, safety-critical decisions


class RoutingStrategy(Enum):
    """LLM routing strategies."""
    COST_OPTIMIZED = "cost_optimized"      # Prefer cheaper models
    LATENCY_OPTIMIZED = "latency_optimized"  # Prefer fastest models
    QUALITY_OPTIMIZED = "quality_optimized"  # Prefer best models
    BALANCED = "balanced"                   # Balance cost, latency, quality
    ENSEMBLE = "ensemble"                   # Use multiple models


@dataclass
class ModelMetrics:
    """Metrics for LLM model selection."""
    model_name: str
    cost_per_1k_tokens: float      # Cost in USD
    avg_latency_ms: float          # Average response time
    quality_score: float           # 0-100, based on benchmarks
    context_window: int            # Max tokens
    strengths: List[str]           # What this model excels at
    weaknesses: List[str]          # What this model struggles with


@dataclass
class RoutingDecision:
    """Decision from the router."""
    primary_model: str
    alternative_models: List[str]
    strategy: RoutingStrategy
    reasoning: str
    estimated_cost: float
    estimated_latency_ms: float


class LLMRouter:
    """
    Intelligent LLM router for task-specific model selection.
    
    Routes tasks to appropriate LLM providers based on:
    - Task complexity and type
    - Cost constraints
    - Latency requirements
    - Context window needs
    - Model strengths/weaknesses
    """
    
    def __init__(self):
        """Initialize the LLM router with model metrics."""
        self.providers: Dict[str, LLMProvider] = {}
        self.model_metrics: Dict[str, ModelMetrics] = self._initialize_model_metrics()
        self.routing_rules: Dict[str, Dict[str, str]] = self._initialize_routing_rules()
        
    def _initialize_model_metrics(self) -> Dict[str, ModelMetrics]:
        """Initialize metrics for available models."""
        return {
            # OpenAI models
            "gpt-4-turbo": ModelMetrics(
                model_name="gpt-4-turbo",
                cost_per_1k_tokens=0.03,
                avg_latency_ms=800,
                quality_score=95,
                context_window=128000,
                strengths=["complex reasoning", "code analysis", "security", "architecture"],
                weaknesses=["cost", "latency"]
            ),
            "gpt-4o": ModelMetrics(
                model_name="gpt-4o",
                cost_per_1k_tokens=0.015,
                avg_latency_ms=600,
                quality_score=92,
                context_window=128000,
                strengths=["balanced", "fast", "cost-effective", "reasoning"],
                weaknesses=["none"]
            ),
            "gpt-3.5-turbo": ModelMetrics(
                model_name="gpt-3.5-turbo",
                cost_per_1k_tokens=0.002,
                avg_latency_ms=400,
                quality_score=75,
                context_window=16000,
                strengths=["speed", "cost", "simple tasks"],
                weaknesses=["complex reasoning", "long context"]
            ),
            
            # Anthropic models
            "claude-3-opus": ModelMetrics(
                model_name="claude-3-opus",
                cost_per_1k_tokens=0.015,
                avg_latency_ms=1000,
                quality_score=96,
                context_window=200000,
                strengths=["code analysis", "long context", "reasoning", "safety"],
                weaknesses=["latency", "cost"]
            ),
            "claude-3-sonnet": ModelMetrics(
                model_name="claude-3-sonnet",
                cost_per_1k_tokens=0.003,
                avg_latency_ms=700,
                quality_score=88,
                context_window=200000,
                strengths=["balanced", "long context", "cost-effective"],
                weaknesses=["none"]
            ),
            "claude-3-haiku": ModelMetrics(
                model_name="claude-3-haiku",
                cost_per_1k_tokens=0.0008,
                avg_latency_ms=500,
                quality_score=78,
                context_window=200000,
                strengths=["speed", "cost", "long context"],
                weaknesses=["complex reasoning"]
            ),
            
            # Google Gemini models
            "gemini-1.5-pro": ModelMetrics(
                model_name="gemini-1.5-pro",
                cost_per_1k_tokens=0.0075,
                avg_latency_ms=900,
                quality_score=93,
                context_window=1000000,
                strengths=["long context", "reasoning", "code", "multimodal"],
                weaknesses=["latency"]
            ),
            "gemini-1.5-flash": ModelMetrics(
                model_name="gemini-1.5-flash",
                cost_per_1k_tokens=0.0005,
                avg_latency_ms=400,
                quality_score=82,
                context_window=1000000,
                strengths=["speed", "cost", "long context"],
                weaknesses=["complex reasoning"]
            ),
            
            # Local models
            "ollama-mistral": ModelMetrics(
                model_name="ollama-mistral",
                cost_per_1k_tokens=0.0,
                avg_latency_ms=2000,
                quality_score=70,
                context_window=32000,
                strengths=["free", "local", "privacy"],
                weaknesses=["quality", "latency", "context"]
            ),
        }
    
    def _initialize_routing_rules(self) -> Dict[str, Dict[str, str]]:
        """Initialize task-specific routing rules."""
        return {
            "performance_analysis": {
                TaskComplexity.SIMPLE.value: "gpt-3.5-turbo",
                TaskComplexity.MODERATE.value: "gpt-4o",
                TaskComplexity.COMPLEX.value: "gpt-4-turbo",
                TaskComplexity.CRITICAL.value: "claude-3-opus",
            },
            "root_cause_analysis": {
                TaskComplexity.SIMPLE.value: "claude-3-haiku",
                TaskComplexity.MODERATE.value: "claude-3-sonnet",
                TaskComplexity.COMPLEX.value: "claude-3-opus",
                TaskComplexity.CRITICAL.value: "claude-3-opus",
            },
            "code_fix": {
                TaskComplexity.SIMPLE.value: "gpt-3.5-turbo",
                TaskComplexity.MODERATE.value: "gpt-4o",
                TaskComplexity.COMPLEX.value: "gpt-4-turbo",
                TaskComplexity.CRITICAL.value: "gpt-4-turbo",
            },
            "security_analysis": {
                TaskComplexity.SIMPLE.value: "gpt-4o",
                TaskComplexity.MODERATE.value: "gpt-4-turbo",
                TaskComplexity.COMPLEX.value: "gpt-4-turbo",
                TaskComplexity.CRITICAL.value: "gpt-4-turbo",
            },
            "refactoring": {
                TaskComplexity.SIMPLE.value: "gpt-3.5-turbo",
                TaskComplexity.MODERATE.value: "gpt-4o",
                TaskComplexity.COMPLEX.value: "gpt-4-turbo",
                TaskComplexity.CRITICAL.value: "gpt-4-turbo",
            },
            "test_generation": {
                TaskComplexity.SIMPLE.value: "gpt-3.5-turbo",
                TaskComplexity.MODERATE.value: "gpt-4o",
                TaskComplexity.COMPLEX.value: "gpt-4-turbo",
                TaskComplexity.CRITICAL.value: "gpt-4-turbo",
            },
            "anomaly_analysis": {
                TaskComplexity.SIMPLE.value: "gpt-3.5-turbo",
                TaskComplexity.MODERATE.value: "gpt-4o",
                TaskComplexity.COMPLEX.value: "claude-3-sonnet",
                TaskComplexity.CRITICAL.value: "claude-3-opus",
            },
        }
    
    def route(
        self,
        task_type: str,
        complexity: TaskComplexity,
        strategy: RoutingStrategy = RoutingStrategy.BALANCED,
        budget_limit: Optional[float] = None,
        latency_limit_ms: Optional[float] = None,
        context_size: int = 4000,
    ) -> RoutingDecision:
        """
        Route a task to appropriate LLM provider.
        
        Args:
            task_type: Type of task (e.g., 'performance_analysis')
            complexity: Task complexity level
            strategy: Routing strategy to use
            budget_limit: Maximum cost in USD (optional)
            latency_limit_ms: Maximum latency in milliseconds (optional)
            context_size: Estimated context size needed
            
        Returns:
            RoutingDecision with primary and alternative models
        """
        # Get base model from rules
        base_model = self.routing_rules.get(task_type, {}).get(
            complexity.value, "gpt-4o"
        )
        
        # Apply strategy
        if strategy == RoutingStrategy.COST_OPTIMIZED:
            candidates = self._get_cost_optimized_models(
                task_type, context_size, budget_limit
            )
        elif strategy == RoutingStrategy.LATENCY_OPTIMIZED:
            candidates = self._get_latency_optimized_models(
                task_type, latency_limit_ms
            )
        elif strategy == RoutingStrategy.QUALITY_OPTIMIZED:
            candidates = self._get_quality_optimized_models(task_type)
        elif strategy == RoutingStrategy.ENSEMBLE:
            candidates = self._get_ensemble_models(task_type, complexity)
        else:  # BALANCED
            candidates = self._get_balanced_models(
                task_type, complexity, budget_limit, latency_limit_ms
            )
        
        # Select primary and alternatives
        primary = candidates[0] if candidates else base_model
        alternatives = candidates[1:3] if len(candidates) > 1 else []
        
        # Calculate metrics
        primary_metrics = self.model_metrics.get(primary)
        estimated_cost = (context_size / 1000) * primary_metrics.cost_per_1k_tokens
        estimated_latency = primary_metrics.avg_latency_ms
        
        reasoning = self._generate_routing_reasoning(
            primary, strategy, complexity, candidates
        )
        
        logger.info(f"Routed {task_type} ({complexity.value}) to {primary}")
        
        return RoutingDecision(
            primary_model=primary,
            alternative_models=alternatives,
            strategy=strategy,
            reasoning=reasoning,
            estimated_cost=estimated_cost,
            estimated_latency_ms=estimated_latency,
        )
    
    def _get_cost_optimized_models(
        self, task_type: str, context_size: int, budget_limit: Optional[float]
    ) -> List[str]:
        """Get models sorted by cost."""
        models = list(self.model_metrics.values())
        
        # Filter by budget
        if budget_limit:
            models = [
                m for m in models
                if (context_size / 1000) * m.cost_per_1k_tokens <= budget_limit
            ]
        
        # Sort by cost
        models.sort(key=lambda m: m.cost_per_1k_tokens)
        
        # Prefer models good at this task
        task_models = self._get_task_suitable_models(task_type, models)
        return [m.model_name for m in task_models[:3]]
    
    def _get_latency_optimized_models(
        self, task_type: str, latency_limit_ms: Optional[float]
    ) -> List[str]:
        """Get models sorted by latency."""
        models = list(self.model_metrics.values())
        
        # Filter by latency
        if latency_limit_ms:
            models = [m for m in models if m.avg_latency_ms <= latency_limit_ms]
        
        # Sort by latency
        models.sort(key=lambda m: m.avg_latency_ms)
        
        # Prefer models good at this task
        task_models = self._get_task_suitable_models(task_type, models)
        return [m.model_name for m in task_models[:3]]
    
    def _get_quality_optimized_models(self, task_type: str) -> List[str]:
        """Get models sorted by quality."""
        models = list(self.model_metrics.values())
        
        # Sort by quality
        models.sort(key=lambda m: m.quality_score, reverse=True)
        
        # Prefer models good at this task
        task_models = self._get_task_suitable_models(task_type, models)
        return [m.model_name for m in task_models[:3]]
    
    def _get_balanced_models(
        self,
        task_type: str,
        complexity: TaskComplexity,
        budget_limit: Optional[float],
        latency_limit_ms: Optional[float],
    ) -> List[str]:
        """Get models with balanced cost/quality/latency."""
        models = list(self.model_metrics.values())
        
        # Filter by constraints
        if budget_limit:
            models = [
                m for m in models
                if m.cost_per_1k_tokens <= budget_limit / 1000
            ]
        if latency_limit_ms:
            models = [m for m in models if m.avg_latency_ms <= latency_limit_ms]
        
        # Score models: quality - cost_factor - latency_factor
        def score_model(m: ModelMetrics) -> float:
            cost_factor = m.cost_per_1k_tokens * 100
            latency_factor = m.avg_latency_ms / 100
            return m.quality_score - cost_factor - latency_factor
        
        models.sort(key=score_model, reverse=True)
        
        # Prefer models good at this task
        task_models = self._get_task_suitable_models(task_type, models)
        return [m.model_name for m in task_models[:3]]
    
    def _get_ensemble_models(
        self, task_type: str, complexity: TaskComplexity
    ) -> List[str]:
        """Get diverse models for ensemble."""
        # Select one from each provider for diversity
        providers_map = {
            "gpt": [],
            "claude": [],
            "gemini": [],
            "ollama": [],
        }
        
        for model_name, metrics in self.model_metrics.items():
            if "gpt" in model_name:
                providers_map["gpt"].append(metrics)
            elif "claude" in model_name:
                providers_map["claude"].append(metrics)
            elif "gemini" in model_name:
                providers_map["gemini"].append(metrics)
            else:
                providers_map["ollama"].append(metrics)
        
        # Sort each provider by quality
        for provider_models in providers_map.values():
            provider_models.sort(key=lambda m: m.quality_score, reverse=True)
        
        # Select best from each provider
        ensemble = []
        for provider_models in providers_map.values():
            if provider_models:
                ensemble.append(provider_models[0].model_name)
        
        return ensemble
    
    def _get_task_suitable_models(
        self, task_type: str, models: List[ModelMetrics]
    ) -> List[ModelMetrics]:
        """Filter models suitable for the task."""
        task_keywords = {
            "performance": ["performance", "optimization", "latency"],
            "security": ["security", "safety"],
            "code": ["code", "refactor", "fix"],
            "analysis": ["analysis", "reasoning"],
        }
        
        # Find matching keyword
        matching_keyword = None
        for keyword, keywords in task_keywords.items():
            if any(k in task_type.lower() for k in keywords):
                matching_keyword = keyword
                break
        
        if not matching_keyword:
            return models
        
        # Score models by strength match
        def strength_score(m: ModelMetrics) -> int:
            return sum(
                1 for strength in m.strengths
                if matching_keyword in strength.lower()
            )
        
        models.sort(key=strength_score, reverse=True)
        return models
    
    def _generate_routing_reasoning(
        self,
        primary: str,
        strategy: RoutingStrategy,
        complexity: TaskComplexity,
        candidates: List[str],
    ) -> str:
        """Generate human-readable routing reasoning."""
        metrics = self.model_metrics[primary]
        
        reasoning = f"Selected {primary} for {complexity.value} task using {strategy.value} strategy. "
        reasoning += f"Strengths: {', '.join(metrics.strengths[:2])}. "
        
        if candidates:
            reasoning += f"Alternatives: {', '.join(candidates[1:])}"
        
        return reasoning
    
    def get_provider(self, model_name: str) -> LLMProvider:
        """Get LLM provider for a model."""
        if model_name in self.providers:
            return self.providers[model_name]
        
        # Determine provider type and create
        if "gpt" in model_name:
            provider = OpenAIProvider(model=model_name)
        elif "claude" in model_name:
            provider = AnthropicProvider(model=model_name)
        elif "gemini" in model_name:
            provider = GoogleGeminiProvider(model=model_name)
        else:
            provider = OllamaProvider(model=model_name)
        
        self.providers[model_name] = provider
        return provider


class ToolCallingExecutor:
    """
    Executes tool calls made by LLM.
    
    Allows LLM to call internal tools like:
    - get_callgraph_summary
    - run_anomaly_detector
    - run_auto_fixer
    """
    
    def __init__(self):
        """Initialize tool executor."""
        self.tools: Dict[str, callable] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default tools."""
        self.register_tool("get_callgraph_summary", self._get_callgraph_summary)
        self.register_tool("get_function_metrics", self._get_function_metrics)
        self.register_tool("detect_anomalies", self._detect_anomalies)
        self.register_tool("analyze_security", self._analyze_security)
    
    def register_tool(self, name: str, func: callable):
        """Register a tool that LLM can call."""
        self.tools[name] = func
    
    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool."""
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        return self.tools[tool_name](**kwargs)
    
    def _get_callgraph_summary(self, **kwargs) -> str:
        """Get call graph summary."""
        return "Call graph summary: [placeholder]"
    
    def _get_function_metrics(self, function_name: str, **kwargs) -> Dict[str, Any]:
        """Get metrics for a function."""
        return {"function": function_name, "metrics": "[placeholder]"}
    
    def _detect_anomalies(self, **kwargs) -> List[Dict[str, Any]]:
        """Detect anomalies in execution."""
        return [{"anomaly": "[placeholder]"}]
    
    def _analyze_security(self, code: str, **kwargs) -> List[Dict[str, Any]]:
        """Analyze code for security issues."""
        return [{"issue": "[placeholder]"}]


class ContextManager:
    """
    Manages context for LLM calls.
    
    Handles:
    - Automatic chunking of large traces
    - Summarization of call graphs
    - Focus windows around hot spots
    - Long-term caching
    """
    
    def __init__(self, max_context_tokens: int = 4000):
        """Initialize context manager."""
        self.max_context_tokens = max_context_tokens
        self.cache: Dict[str, str] = {}
    
    def prepare_context(
        self,
        trace_data: str,
        focus_on_hotspots: bool = True,
        use_cache: bool = True,
    ) -> str:
        """
        Prepare context for LLM call.
        
        Args:
            trace_data: Full execution trace
            focus_on_hotspots: Focus on hot spots only
            use_cache: Use cached summaries
            
        Returns:
            Prepared context within token limit
        """
        # Check cache
        cache_key = hash(trace_data)
        if use_cache and cache_key in self.cache:
            return self.cache[cache_key]
        
        # Estimate tokens (rough: 1 token ≈ 4 chars)
        estimated_tokens = len(trace_data) // 4
        
        if estimated_tokens <= self.max_context_tokens:
            context = trace_data
        elif focus_on_hotspots:
            context = self._extract_hotspots(trace_data)
        else:
            context = self._summarize_trace(trace_data)
        
        # Cache result
        self.cache[cache_key] = context
        
        return context
    
    def _extract_hotspots(self, trace_data: str) -> str:
        """Extract hot spots from trace."""
        # Placeholder: would parse trace and extract top functions
        lines = trace_data.split('\n')
        return '\n'.join(lines[:50])  # Return first 50 lines as placeholder
    
    def _summarize_trace(self, trace_data: str) -> str:
        """Summarize trace data."""
        # Placeholder: would create summary
        lines = trace_data.split('\n')
        return f"Summary of {len(lines)} trace lines: [placeholder]"
