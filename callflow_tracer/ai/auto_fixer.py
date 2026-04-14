"""
Auto-fix generation module for CallFlow Tracer.

Generates code fixes for detected performance issues.
Provides diffs and confidence scores for each suggested fix.

Example:
    from callflow_tracer.ai import generate_fixes

    fixes = generate_fixes(
        graph,
        root_cause_analysis=root_analysis,
        provider=OpenAIProvider(model='gpt-4o')
    )

    for fix in fixes:
        print(f"File:       {fix['file_path']}")
        print(f"Issue:      {fix['issue']}")
        print(f"Confidence: {fix['confidence']}")
        print(f"Diff:\\n{fix['diff']}")

        if fix['confidence'] > 0.8:
            apply_fix(fix)

Architecture:
    - IssueType / Severity          — enums (no more magic strings)
    - FixTemplate                   — separates content from logic
    - FixStrategy (ABC)             — Strategy: one class per issue type
    - BaseFixStrategy               — Template Method: shared generate() skeleton
    - FixStrategyRegistry           — O(1) dict dispatch (replaces if/elif chain)
    - AutoFixer                     — thin orchestrator: deduplicates, sorts, dispatches
"""

import difflib
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple

from .llm_provider import LLMProvider


# ---------------------------------------------------------------------------
# Enums — no more magic strings
# ---------------------------------------------------------------------------

class IssueType(str, Enum):
    N_PLUS_ONE          = "n_plus_one"
    INEFFICIENT_LOOP    = "inefficient_loop"
    MEMORY_LEAK         = "memory_leak"
    EXCESSIVE_RECURSION = "excessive_recursion"
    MISSING_CACHE       = "missing_cache"


class Severity(str, Enum):
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    CRITICAL = "critical"

    # Enables direct comparison: Severity.HIGH > Severity.LOW
    _ORDER = None  # populated below

    def __lt__(self, other: "Severity") -> bool:
        return _SEVERITY_RANK[self] < _SEVERITY_RANK[other]

    def __le__(self, other: "Severity") -> bool:
        return _SEVERITY_RANK[self] <= _SEVERITY_RANK[other]

    def __gt__(self, other: "Severity") -> bool:
        return _SEVERITY_RANK[self] > _SEVERITY_RANK[other]

    def __ge__(self, other: "Severity") -> bool:
        return _SEVERITY_RANK[self] >= _SEVERITY_RANK[other]


_SEVERITY_RANK: Dict[Severity, int] = {
    Severity.LOW:      0,
    Severity.MEDIUM:   1,
    Severity.HIGH:     2,
    Severity.CRITICAL: 3,
}


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------

@dataclass
class FixTemplate:
    """
    The content half of a fix — completely separate from dispatch logic.

    Keeping templates as data means they can be loaded from YAML/JSON in
    future without touching any strategy class.
    """
    before_code:          str
    after_code:           str
    issue_description:    str
    explanation:          str
    confidence:           float   # 0.0 – 1.0
    severity:             Severity
    estimated_improvement: float  # expected % speedup / memory saving


@dataclass
class CodeFix:
    """A fully-resolved fix ready for presentation or application."""

    file_path:             str
    function_name:         str
    issue:                 str
    issue_type:            str
    before_code:           str
    after_code:            str
    diff:                  str
    explanation:           str
    confidence:            float
    severity:              str    # str so asdict() is JSON-safe
    estimated_improvement: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Diff utility — replaces the broken zip-based implementation
# ---------------------------------------------------------------------------

def _unified_diff(before: str, after: str, fromfile: str = "before", tofile: str = "after") -> str:
    """
    Proper unified diff using difflib.

    Old implementation used zip() which silently dropped lines when before
    and after had different lengths — a correctness bug, not just a style issue.

    Time complexity: O(n·m) via LCS (difflib's SequenceMatcher)
    Space complexity: O(n + m)
    """
    before_lines = before.splitlines(keepends=True)
    after_lines  = after.splitlines(keepends=True)

    diff = difflib.unified_diff(
        before_lines,
        after_lines,
        fromfile=fromfile,
        tofile=tofile,
        lineterm="",
    )
    return "\n".join(diff)


# ---------------------------------------------------------------------------
# Strategy pattern — one class per issue type
# ---------------------------------------------------------------------------

class FixStrategy(ABC):
    """
    One fix strategy = one issue type.

    Implement this to support a new issue type without editing AutoFixer.
    Register via FixStrategyRegistry.register().
    """

    @property
    @abstractmethod
    def issue_type(self) -> IssueType: ...

    @abstractmethod
    def get_template(self, issue: Dict[str, Any], actual_source: str) -> FixTemplate:
        """
        Return the FixTemplate for this issue.

        Args:
            issue:         The issue dict from root_cause_analysis
            actual_source: The actual source code of the affected file (may be "")
                           Strategies MAY use this to produce context-aware fixes.
                           If empty, fall back to the canonical example template.
        """
        ...


class BaseFixStrategy(FixStrategy, ABC):
    """
    Template Method: defines the generate() skeleton.

    Subclasses only override get_template() — they never touch diff generation,
    CodeFix construction, or error handling.
    """

    def generate(self, issue: Dict[str, Any], actual_source: str) -> Optional[CodeFix]:
        """
        Full generate pipeline:
          1. get_template()  — provided by subclass
          2. _unified_diff() — shared utility
          3. CodeFix(...)    — shared construction

        Returns None only if get_template() itself returns None.
        """
        template = self.get_template(issue, actual_source)
        if template is None:
            return None

        diff = _unified_diff(template.before_code, template.after_code)

        return CodeFix(
            file_path             = issue.get("file", "unknown"),
            function_name         = issue.get("function", "unknown"),
            issue                 = template.issue_description,
            issue_type            = self.issue_type.value,
            before_code           = template.before_code,
            after_code            = template.after_code,
            diff                  = diff,
            explanation           = template.explanation,
            confidence            = template.confidence,
            severity              = template.severity.value,
            estimated_improvement = template.estimated_improvement,
        )


# ---------------------------------------------------------------------------
# Concrete strategies
# ---------------------------------------------------------------------------

class NPlusOneFixStrategy(BaseFixStrategy):
    """Fix: replace per-item queries inside a loop with a single batch query."""

    @property
    def issue_type(self) -> IssueType:
        return IssueType.N_PLUS_ONE

    def get_template(self, issue, actual_source) -> FixTemplate:
        return FixTemplate(
            before_code="""\
# Before — N+1 query problem
def get_user_orders(user_id):
    orders = []
    for order_id in get_order_ids(user_id):
        orders.append(get_order(order_id))  # N queries!
    return orders""",
            after_code="""\
# After — single batch query
def get_user_orders(user_id):
    order_ids = get_order_ids(user_id)
    return get_orders_batch(order_ids)  # 1 query""",
            issue_description = "N+1 Query Problem: multiple individual queries inside a loop",
            explanation       = (
                "Replace individual per-item queries with a single batch call. "
                "Reduces database round-trips from O(n) to O(1)."
            ),
            confidence            = 0.95,
            severity              = Severity.HIGH,
            estimated_improvement = 80.0,
        )


class InefficientLoopFixStrategy(BaseFixStrategy):
    """Fix: replace O(n) list membership test with O(1) set lookup."""

    @property
    def issue_type(self) -> IssueType:
        return IssueType.INEFFICIENT_LOOP

    def get_template(self, issue, actual_source) -> FixTemplate:
        return FixTemplate(
            before_code="""\
# Before — O(n²): list membership inside a loop
def deduplicate(items):
    result = []
    for item in items:
        if item in result:   # O(n) scan each iteration → O(n²) total
            continue
        result.append(item)
    return result""",
            after_code="""\
# After — O(n): set for O(1) membership test
def deduplicate(items):
    seen   = set()
    result = []
    for item in items:
        if item in seen:     # O(1) hash lookup → O(n) total
            continue
        seen.add(item)
        result.append(item)
    return result""",
            issue_description = "Inefficient Loop: O(n) list search should be O(1) set lookup",
            explanation       = (
                "Use a set for membership testing instead of a list. "
                "Reduces loop from O(n²) to O(n) time complexity."
            ),
            confidence            = 0.90,
            severity              = Severity.HIGH,
            estimated_improvement = 60.0,
        )


class MemoryLeakFixStrategy(BaseFixStrategy):
    """Fix: add a bounded LRU eviction policy to an unbounded cache dict."""

    @property
    def issue_type(self) -> IssueType:
        return IssueType.MEMORY_LEAK

    def get_template(self, issue, actual_source) -> FixTemplate:
        return FixTemplate(
            before_code="""\
# Before — unbounded cache growth (memory leak)
class DataProcessor:
    def __init__(self):
        self.cache = {}                 # grows forever

    def process(self, key, data):
        self.cache[key] = data
        return self.cache[key]""",
            after_code="""\
# After — bounded LRU cache via collections.OrderedDict
from collections import OrderedDict

class DataProcessor:
    def __init__(self, max_cache: int = 1000):
        self._cache:     OrderedDict = OrderedDict()
        self._max_cache: int         = max_cache

    def process(self, key, data):
        if key in self._cache:
            self._cache.move_to_end(key)   # mark as recently used
            return self._cache[key]
        if len(self._cache) >= self._max_cache:
            self._cache.popitem(last=False) # evict LRU entry — O(1)
        self._cache[key] = data
        return data""",
            issue_description = "Memory Leak: unbounded dict cache with no eviction policy",
            explanation       = (
                "Replace the unbounded dict with an OrderedDict-backed LRU cache. "
                "Eviction is O(1). Memory is bounded by max_cache entries."
            ),
            confidence            = 0.85,
            severity              = Severity.CRITICAL,
            estimated_improvement = 100.0,
        )


class ExcessiveRecursionFixStrategy(BaseFixStrategy):
    """Fix: add memoization to eliminate redundant recursive calls."""

    @property
    def issue_type(self) -> IssueType:
        return IssueType.EXCESSIVE_RECURSION

    def get_template(self, issue, actual_source) -> FixTemplate:
        return FixTemplate(
            before_code="""\
# Before — exponential recursion: O(2ⁿ) time, O(n) stack
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)""",
            after_code="""\
# After — memoized: O(n) time, O(n) space
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)""",
            issue_description = "Excessive Recursion: exponential time due to repeated subproblems",
            explanation       = (
                "Add @lru_cache to memoize results of repeated subproblems. "
                "Reduces time from O(2ⁿ) to O(n) with O(n) additional space."
            ),
            confidence            = 0.92,
            severity              = Severity.CRITICAL,
            estimated_improvement = 99.0,
        )


class MissingCacheFixStrategy(BaseFixStrategy):
    """Fix: cache the result of an expensive repeated computation."""

    @property
    def issue_type(self) -> IssueType:
        return IssueType.MISSING_CACHE

    def get_template(self, issue, actual_source) -> FixTemplate:
        return FixTemplate(
            before_code="""\
# Before — repeated expensive query, no caching
def get_user_profile(user_id: int):
    return database.query(
        "SELECT * FROM users WHERE id = %s", (user_id,)
    )""",
            after_code="""\
# After — cache up to 1000 results in memory
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_user_profile(user_id: int):
    return database.query(
        "SELECT * FROM users WHERE id = %s", (user_id,)
    )""",
            issue_description = "Missing Cache: expensive operation repeated with identical inputs",
            explanation       = (
                "Add @lru_cache to avoid redundant work. "
                "Each unique user_id is fetched once; subsequent calls are O(1)."
            ),
            confidence            = 0.88,
            severity              = Severity.HIGH,
            estimated_improvement = 70.0,
        )


# ---------------------------------------------------------------------------
# FixStrategyRegistry — O(1) dispatch (replaces the if/elif chain)
# ---------------------------------------------------------------------------

class FixStrategyRegistry:
    """
    Maps IssueType → FixStrategy in O(1).

    Before: if/elif chain, O(k) per lookup, requires editing AutoFixer to extend.
    After:  dict lookup, O(1) per lookup, extend by calling register().
    """

    def __init__(self) -> None:
        # Dict[IssueType, BaseFixStrategy] — hash map, O(1) get/set
        self._registry: Dict[IssueType, BaseFixStrategy] = {}

    def register(self, strategy: BaseFixStrategy) -> None:
        """Add or replace a strategy for its issue_type."""
        self._registry[strategy.issue_type] = strategy

    def get(self, issue_type: str) -> Optional[BaseFixStrategy]:
        """O(1) lookup. Returns None for unknown issue types."""
        try:
            return self._registry.get(IssueType(issue_type))
        except ValueError:
            return None

    @classmethod
    def default(cls) -> "FixStrategyRegistry":
        """Factory: registry pre-loaded with all built-in strategies."""
        registry = cls()
        for strategy in [
            NPlusOneFixStrategy(),
            InefficientLoopFixStrategy(),
            MemoryLeakFixStrategy(),
            ExcessiveRecursionFixStrategy(),
            MissingCacheFixStrategy(),
        ]:
            registry.register(strategy)
        return registry


# ---------------------------------------------------------------------------
# AutoFixer — thin orchestrator
# ---------------------------------------------------------------------------

class AutoFixer:
    """
    Orchestrates fix generation across a list of detected issues.

    Responsibilities:
      1. Deduplicate issues by (file, issue_type, function) — avoids duplicate fixes
      2. Dispatch each unique issue to the correct FixStrategy — O(1) per lookup
      3. Sort fixes by (severity DESC, confidence DESC) — correct 4-level ordering
    """

    def __init__(
        self,
        llm_provider: LLMProvider,
        registry: Optional[FixStrategyRegistry] = None,
    ) -> None:
        self.llm_provider = llm_provider
        self._registry    = registry or FixStrategyRegistry.default()

    def generate_fixes(
        self,
        graph: Dict[str, Any],  # reserved for future graph-aware fix strategies
        root_cause_analysis: Optional[Dict[str, Any]] = None,
        source_code: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate and return deduplicated, sorted code fixes.

        Deduplication key: (file_path, issue_type, function_name)
        Sort order:        severity DESC → confidence DESC

        Time complexity:  O(n log n) where n = number of unique issues
        Space complexity: O(n) for the seen-set and output list
        """
        if not root_cause_analysis:
            return []

        issues = root_cause_analysis.get("issues", [])

        # Deduplication — O(1) per insert/lookup via hash set
        # Without this, the same issue appearing twice yields duplicate fixes.
        seen: set = set()
        fixes: List[Dict[str, Any]] = []

        for issue in issues:
            dedup_key: Tuple[str, str, str] = (
                issue.get("file", ""),
                issue.get("type", ""),
                issue.get("function", ""),
            )
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            actual_source = (source_code or {}).get(issue.get("file", ""), "")
            fix = self._dispatch(issue, actual_source)
            if fix:
                fixes.append(fix.to_dict())

        # Sort: severity DESC (4 levels), then confidence DESC
        # Old code used `severity != "critical"` which collapsed HIGH/MEDIUM/LOW together.
        fixes.sort(
            key=lambda x: (
                _SEVERITY_RANK.get(Severity(x["severity"]), 0),  # 0–3
                x["confidence"],                                   # 0.0–1.0
            ),
            reverse=True,
        )

        return fixes

    def _dispatch(self, issue: Dict[str, Any], actual_source: str) -> Optional[CodeFix]:
        """
        O(1) dispatch to the correct strategy via registry dict lookup.

        Old code: if/elif chain — O(k), must edit AutoFixer to add a new type.
        New code: dict.get()    — O(1), add new types via registry.register().
        """
        strategy = self._registry.get(issue.get("type", ""))
        if strategy is None:
            return None
        return strategy.generate(issue, actual_source)


# ---------------------------------------------------------------------------
# Convenience function (public API unchanged)
# ---------------------------------------------------------------------------

def generate_fixes(
    graph: Dict[str, Any],
    root_cause_analysis: Optional[Dict[str, Any]] = None,
    provider: Optional[LLMProvider] = None,
    source_code: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """
    Generate code fixes for detected issues.

    Args:
        graph:                Execution trace graph
        root_cause_analysis:  Output from root cause analyser
        provider:             LLM provider (used for future LLM-assisted fixes)
        source_code:          Dict mapping file paths to source strings

    Returns:
        Deduplicated, severity-sorted list of fix dicts
    """
    if not provider:
        from .llm_provider import OpenAIProvider
        provider = OpenAIProvider()

    fixer = AutoFixer(provider)
    return fixer.generate_fixes(graph, root_cause_analysis, source_code)
