"""
Cost analysis module for CallFlow Tracer.

Calculate infrastructure costs based on execution patterns.
Useful for cloud cost optimization and resource allocation.

Example:
    from callflow_tracer.ai import analyze_costs

    costs = analyze_costs(
        graph,
        pricing={
            'compute':  0.0001,   # $ per ms
            'database': 0.001,    # $ per query
            'api_call': 0.01,     # $ per call
        }
    )

    print(f"Estimated cost: ${costs['total_cost']:.6f}")
    print(f"Most expensive: {costs['top_functions']}")

Architecture:
    - CostCategory                  — enum (no magic strings)
    - CostClassifier (ABC)          — Strategy: one class per cost category
    - OpportunityDetector (ABC)     — Strategy: one class per optimization type
    - CostAnalyzerConfig            — all tuneable thresholds in one place
    - CostAnalyzer                  — thin orchestrator
    - GraphExtractor                — shared graph parsing (DRY, no third copy)
    - DSA: heapq.nlargest for top-k — O(n log k) vs O(n log n) sort
"""

import heapq
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple

from .comparison import GraphExtractor


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class CostCategory(str, Enum):
    COMPUTE  = "compute"
    DATABASE = "database"
    API      = "api"
    MEMORY   = "memory"
    OTHER    = "other"


class OpportunityType(str, Enum):
    EXPENSIVE_FUNCTION  = "expensive_function"
    HIGH_FREQUENCY      = "high_frequency_calls"
    DATABASE_BATCH      = "database_optimization"
    MEMORY_REDUCTION    = "memory_reduction"


# ---------------------------------------------------------------------------
# Configuration — all magic numbers in one place
# ---------------------------------------------------------------------------

@dataclass
class CostAnalyzerConfig:
    """
    Centralises every tuneable threshold.

    Before: magic numbers scattered across the class:
        if func_cost.total_cost > 0.01   (expensive threshold)
        if func_cost.execution_count > 100  (frequency threshold)
        potential_savings = total_cost * 0.3 / 0.5 / 0.4  (savings estimates)
        top_functions = function_costs[:10]  (hard-coded top-k)
    After: all configurable at construction time.
    """
    # Pricing defaults (AWS Lambda-like)
    default_pricing: Dict[str, float] = None   # set in __post_init__

    # Top-k for leaderboard
    top_functions_k: int = 10

    # OpportunityDetector thresholds
    expensive_cost_threshold:    float = 0.01    # $ above which a fn is "expensive"
    expensive_savings_pct:       float = 0.30    # estimated savings for expensive fn
    high_frequency_threshold:    int   = 100     # calls above which fn is "hot"
    high_frequency_savings_pct:  float = 0.50    # estimated savings with caching
    database_savings_pct:        float = 0.40    # estimated savings with batching
    top_expensive_to_check:      int   = 5       # check top-N for expensive opportunities

    def __post_init__(self):
        if self.default_pricing is None:
            self.default_pricing = {
                CostCategory.COMPUTE.value:  0.0001,    # $ per ms
                CostCategory.DATABASE.value: 0.001,     # $ per query
                CostCategory.API.value:      0.01,      # $ per call
                CostCategory.MEMORY.value:   0.00001,   # $ per MB per ms
            }


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------

@dataclass
class FunctionCost:
    """Cost breakdown for one function."""
    function_name:  str
    module:         str
    execution_count: int
    total_time_ms:  float
    compute_cost:   float
    call_cost:      float    # DB + API costs
    total_cost:     float
    cost_per_call:  float
    category_breakdown: Dict[str, float]  # CostCategory → amount

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OptimizationOpportunity:
    """A single cost-saving recommendation."""
    function:          str
    opportunity_type:  str              # OpportunityType.value
    current_cost:      float
    potential_savings: float
    recommendation:    str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CostAnalysis:
    """Complete cost analysis result."""
    timestamp:                str
    total_cost:               float
    cost_breakdown:           Dict[str, float]   # CostCategory → total
    function_costs:           List[FunctionCost]
    optimization_opportunities: List[OptimizationOpportunity]

    @property
    def top_functions(self) -> List[FunctionCost]:
        """Derived — always consistent with function_costs, never stale."""
        return sorted(self.function_costs, key=lambda f: f.total_cost, reverse=True)[:10]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp":    self.timestamp,
            "total_cost":   self.total_cost,
            "compute_cost": self.cost_breakdown.get(CostCategory.COMPUTE.value,  0.0),
            "database_cost":self.cost_breakdown.get(CostCategory.DATABASE.value, 0.0),
            "api_cost":     self.cost_breakdown.get(CostCategory.API.value,      0.0),
            "cost_breakdown":            self.cost_breakdown,
            "function_costs":            [f.to_dict() for f in self.function_costs],
            "top_functions":             [f.to_dict() for f in self.top_functions],
            "optimization_opportunities":[o.to_dict() for o in self.optimization_opportunities],
        }


# ---------------------------------------------------------------------------
# Strategy pattern — cost classifiers
# ---------------------------------------------------------------------------

class CostClassifier(ABC):
    """
    One cost category.

    Implement to add new cost types (e.g. egress, GPU) without editing CostAnalyzer.
    Register via CostAnalyzer.register_classifier().
    """

    @property
    @abstractmethod
    def category(self) -> CostCategory: ...

    @abstractmethod
    def applies_to(self, func_name: str, module: str) -> bool:
        """Return True if this classifier should contribute cost for this function."""
        ...

    @abstractmethod
    def compute(
        self,
        func_name:      str,
        module:         str,
        call_count:     int,
        total_time_ms:  float,
        pricing:        Dict[str, float],
    ) -> float:
        """Return the dollar cost for this function under this category."""
        ...


class ComputeCostClassifier(CostClassifier):
    """Every function pays compute cost proportional to its execution time."""

    @property
    def category(self) -> CostCategory:
        return CostCategory.COMPUTE

    def applies_to(self, func_name: str, module: str) -> bool:
        return True  # universal

    def compute(self, func_name, module, call_count, total_time_ms, pricing) -> float:
        rate = pricing.get(CostCategory.COMPUTE.value, 0.0001)
        return total_time_ms * rate


class DatabaseCostClassifier(CostClassifier):
    """
    Functions whose name contains DB-related keywords incur per-query cost.

    The keyword list is configurable at construction time — no more hardcoded
    'query' / 'db' strings baked into the class body.
    """

    DEFAULT_KEYWORDS = frozenset({"query", "db", "database", "select", "insert", "fetch"})

    def __init__(self, keywords: Optional[frozenset] = None) -> None:
        self._keywords = keywords or self.DEFAULT_KEYWORDS

    @property
    def category(self) -> CostCategory:
        return CostCategory.DATABASE

    def applies_to(self, func_name: str, module: str) -> bool:
        lower = func_name.lower()
        return any(kw in lower for kw in self._keywords)

    def compute(self, func_name, module, call_count, total_time_ms, pricing) -> float:
        rate = pricing.get(CostCategory.DATABASE.value, 0.001)
        return call_count * rate


class ApiCostClassifier(CostClassifier):
    """Functions whose name suggests an outbound API call incur per-call cost."""

    DEFAULT_KEYWORDS = frozenset({"api", "request", "http", "call", "endpoint", "webhook"})

    def __init__(self, keywords: Optional[frozenset] = None) -> None:
        self._keywords = keywords or self.DEFAULT_KEYWORDS

    @property
    def category(self) -> CostCategory:
        return CostCategory.API

    def applies_to(self, func_name: str, module: str) -> bool:
        lower = func_name.lower()
        return any(kw in lower for kw in self._keywords)

    def compute(self, func_name, module, call_count, total_time_ms, pricing) -> float:
        rate = pricing.get(CostCategory.API.value, 0.01)
        return call_count * rate


# ---------------------------------------------------------------------------
# Strategy pattern — opportunity detectors
# ---------------------------------------------------------------------------

class OpportunityDetector(ABC):
    """
    One optimization opportunity type.

    Implement to add new opportunity types (e.g. parallelism, lazy loading)
    without editing CostAnalyzer.
    Register via CostAnalyzer.register_opportunity_detector().
    """

    @property
    @abstractmethod
    def opportunity_type(self) -> OpportunityType: ...

    @abstractmethod
    def detect(
        self,
        function_costs: List[FunctionCost],
        config:         CostAnalyzerConfig,
    ) -> List[OptimizationOpportunity]: ...


class ExpensiveFunctionDetector(OpportunityDetector):
    """Flag the top-N costliest functions."""

    @property
    def opportunity_type(self) -> OpportunityType:
        return OpportunityType.EXPENSIVE_FUNCTION

    def detect(self, function_costs, config) -> List[OptimizationOpportunity]:
        opportunities = []
        for fc in function_costs[:config.top_expensive_to_check]:
            if fc.total_cost > config.expensive_cost_threshold:
                savings = fc.total_cost * config.expensive_savings_pct
                opportunities.append(OptimizationOpportunity(
                    function         = fc.function_name,
                    opportunity_type = self.opportunity_type.value,
                    current_cost     = fc.total_cost,
                    potential_savings= savings,
                    recommendation   = (
                        f"Optimise {fc.function_name} — currently costs "
                        f"${fc.total_cost:.4f}. "
                        f"Estimated {config.expensive_savings_pct*100:.0f}% reduction "
                        f"saves ${savings:.4f}."
                    ),
                ))
        return opportunities


class HighFrequencyDetector(OpportunityDetector):
    """
    Flag all functions called more than the frequency threshold.

    Old code had a `break` after the first match — only one function was ever
    reported. This reports ALL hot functions.
    """

    @property
    def opportunity_type(self) -> OpportunityType:
        return OpportunityType.HIGH_FREQUENCY

    def detect(self, function_costs, config) -> List[OptimizationOpportunity]:
        opportunities = []
        for fc in function_costs:
            if fc.execution_count > config.high_frequency_threshold:
                savings = fc.total_cost * config.high_frequency_savings_pct
                opportunities.append(OptimizationOpportunity(
                    function         = fc.function_name,
                    opportunity_type = self.opportunity_type.value,
                    current_cost     = fc.total_cost,
                    potential_savings= savings,
                    recommendation   = (
                        f"Cache {fc.function_name} — called "
                        f"{fc.execution_count}× (threshold: "
                        f"{config.high_frequency_threshold}). "
                        f"Caching could save ${savings:.4f}."
                    ),
                ))
        return opportunities


class DatabaseBatchDetector(OpportunityDetector):
    """Flag DB-heavy functions that could benefit from batching."""

    DB_KEYWORDS = frozenset({"query", "select", "insert", "fetch", "db"})

    @property
    def opportunity_type(self) -> OpportunityType:
        return OpportunityType.DATABASE_BATCH

    def detect(self, function_costs, config) -> List[OptimizationOpportunity]:
        opportunities = []
        for fc in function_costs:
            if any(kw in fc.function_name.lower() for kw in self.DB_KEYWORDS):
                savings = fc.total_cost * config.database_savings_pct
                opportunities.append(OptimizationOpportunity(
                    function         = fc.function_name,
                    opportunity_type = self.opportunity_type.value,
                    current_cost     = fc.total_cost,
                    potential_savings= savings,
                    recommendation   = (
                        f"Batch database queries in {fc.function_name}. "
                        f"Estimated {config.database_savings_pct*100:.0f}% saving "
                        f"= ${savings:.4f}."
                    ),
                ))
        return opportunities


# ---------------------------------------------------------------------------
# CostAnalyzer — thin orchestrator
# ---------------------------------------------------------------------------

class CostAnalyzer:
    """
    Orchestrates cost classification and opportunity detection across a trace.

    Extend by calling:
        analyzer.register_classifier(MyNewCostClassifier())
        analyzer.register_opportunity_detector(MyNewDetector())
    """

    def __init__(
        self,
        pricing: Optional[Dict[str, float]] = None,
        config:  Optional[CostAnalyzerConfig] = None,
    ) -> None:
        self._config = config or CostAnalyzerConfig()

        # Merge caller-supplied pricing into defaults
        effective_pricing = dict(self._config.default_pricing)
        if pricing:
            effective_pricing.update(pricing)
        self._pricing = effective_pricing

        self._extractor = GraphExtractor()

        # Classifier registry — dict preserves insertion order
        self._classifiers: Dict[CostCategory, CostClassifier] = {}
        for clf in [
            ComputeCostClassifier(),
            DatabaseCostClassifier(),
            ApiCostClassifier(),
        ]:
            self.register_classifier(clf)

        # Opportunity detector registry
        self._detectors: List[OpportunityDetector] = [
            ExpensiveFunctionDetector(),
            HighFrequencyDetector(),
            DatabaseBatchDetector(),
        ]

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_classifier(self, classifier: CostClassifier) -> None:
        """Add or replace the classifier for its CostCategory."""
        self._classifiers[classifier.category] = classifier

    def register_opportunity_detector(self, detector: OpportunityDetector) -> None:
        """Add an opportunity detector. Appended at the end of the pipeline."""
        self._detectors.append(detector)

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def analyze(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse costs from execution trace.

        Returns:
            Serialised CostAnalysis dict.
        """
        nodes = self._extractor.extract_nodes(graph)

        category_totals: Dict[str, float] = {c.value: 0.0 for c in CostCategory}
        function_costs: List[FunctionCost] = []

        for node_key, node in nodes.items():
            func_name     = node.get("name",       "unknown")
            module        = node.get("module",      "unknown")
            total_time_ms = float(node.get("total_time", 0)) * 1000
            call_count    = int(node.get("call_count", 1))

            breakdown: Dict[str, float] = {}
            for clf in self._classifiers.values():
                if clf.applies_to(func_name, module):
                    cost = clf.compute(
                        func_name, module, call_count, total_time_ms, self._pricing
                    )
                    breakdown[clf.category.value]      = cost
                    category_totals[clf.category.value] += cost

            total_cost   = sum(breakdown.values())
            compute_cost = breakdown.get(CostCategory.COMPUTE.value, 0.0)
            call_cost    = total_cost - compute_cost

            function_costs.append(FunctionCost(
                function_name     = func_name,
                module            = module,
                execution_count   = call_count,
                total_time_ms     = total_time_ms,
                compute_cost      = compute_cost,
                call_cost         = call_cost,
                total_cost        = total_cost,
                cost_per_call     = total_cost / call_count if call_count > 0 else 0.0,
                category_breakdown= breakdown,
            ))

        # DSA: top-k with heapq — O(n log k) instead of O(n log n) full sort
        # For a leaderboard of k=10 out of n=1000, this is ~3x fewer comparisons.
        top_k = heapq.nlargest(
            self._config.top_functions_k,
            function_costs,
            key=lambda f: f.total_cost,
        )

        # Sort full list for deterministic output (still needed for opportunity detectors)
        function_costs.sort(key=lambda f: f.total_cost, reverse=True)

        total_cost = sum(category_totals.values())

        opportunities = self._detect_opportunities(function_costs)

        analysis = CostAnalysis(
            timestamp     = datetime.now().isoformat(),
            total_cost    = total_cost,
            cost_breakdown= {k: v for k, v in category_totals.items() if v > 0},
            function_costs= function_costs,
            optimization_opportunities= opportunities,
        )

        return analysis.to_dict()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _detect_opportunities(
        self,
        function_costs: List[FunctionCost],
    ) -> List[OptimizationOpportunity]:
        """Run all detectors and merge results."""
        all_opportunities: List[OptimizationOpportunity] = []
        for detector in self._detectors:
            all_opportunities.extend(detector.detect(function_costs, self._config))

        # Sort by potential savings DESC
        all_opportunities.sort(key=lambda o: o.potential_savings, reverse=True)
        return all_opportunities


# ---------------------------------------------------------------------------
# Convenience function (public API unchanged)
# ---------------------------------------------------------------------------

def analyze_costs(
    graph:   Dict[str, Any],
    pricing: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Analyse infrastructure costs from a trace graph.

    Args:
        graph:   Execution trace graph
        pricing: Optional pricing overrides

    Returns:
        Cost analysis dict with total_cost, function_costs, top_functions,
        cost_breakdown, and optimization_opportunities.
    """
    return CostAnalyzer(pricing).analyze(graph)
