"""
Context extraction pipeline for `callflow context` command.

DSA used:
  - heapq (priority queue)  : O(N log K) top-N ranking
  - frozenset               : O(1) prefix/marker membership test
  - defaultdict + deque     : O(V+E) BFS for depth computation
  - dict[str, int]          : O(1) depth lookup

Patterns:
  Strategy → RankingStrategy hierarchy  (swap scoring without touching caller)
  Builder  → ContextBuilder             (step-by-step Markdown assembly)
"""

from __future__ import annotations

import heapq
import inspect
import sys
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.tracer import CallGraph, CallNode

# ── Constants ──────────────────────────────────────────────────────────────────

_STDLIB_ROOT_MODULES: frozenset[str] = frozenset({
    "_", "__", "abc", "argparse", "ast", "asyncio", "builtins", "codecs",
    "collections", "concurrent", "contextlib", "copy", "csv", "dataclasses",
    "datetime", "difflib", "email", "enum", "errno", "fnmatch", "fractions",
    "ftplib", "functools", "gc", "getpass", "glob", "hashlib", "heapq",
    "hmac", "html", "http", "idlelib", "importlib", "inspect", "io",
    "itertools", "json", "keyword", "linecache", "locale", "logging",
    "math", "mimetypes", "multiprocessing", "numbers", "operator", "os",
    "pathlib", "pickle", "platform", "pprint", "queue", "random", "re",
    "runpy", "shutil", "signal", "site", "socket", "sqlite3", "ssl",
    "stat", "string", "struct", "subprocess", "sys", "tempfile", "textwrap",
    "threading", "time", "timeit", "tokenize", "traceback", "types",
    "typing", "unicodedata", "unittest", "urllib", "uuid", "warnings",
    "weakref", "xml", "xmlrpc", "zipfile", "zipimport",
})

# Substrings that mark a name as belonging to vendored / framework code.
_VENDOR_MARKERS: frozenset[str] = frozenset({
    "site-packages",
    "dist-packages",
    "callflow_tracer",   # exclude our own tracer from output
})


# ── User-code predicate ────────────────────────────────────────────────────────

def is_user_code(full_name: str) -> bool:
    """
    Return True only if *full_name* belongs to user-authored code.

    Checks (in order, short-circuit):
      1. Synthetic / anonymous names     — <module>, <lambda>, <listcomp>, etc.
      2. Root module not in stdlib set   — O(1) frozenset lookup
      3. No vendor marker substring      — O(M) where M = |_VENDOR_MARKERS| (tiny)
    """
    # Synthetic Python execution names
    if full_name.startswith("<") or full_name.endswith(">"):
        return False

    root_module = full_name.split(".")[0].lstrip("_")
    if root_module in _STDLIB_ROOT_MODULES:
        return False

    lower = full_name.lower()
    for marker in _VENDOR_MARKERS:
        if marker in lower:
            return False
    return True


# ── Depth computation ──────────────────────────────────────────────────────────

def compute_node_depths(graph: "CallGraph") -> dict[str, int]:
    """
    BFS from root nodes (in-degree == 0) to assign a call-depth to every node.

    Builds a forward adjacency list + in-degree map in a single O(E) pass,
    then runs BFS in O(V+E). Unreachable nodes default to depth 0.

    Returns: dict[full_name → depth]
    """
    # --- O(E) pass: forward adjacency + in-degree --------------------------
    forward: dict[str, list[str]] = defaultdict(list)
    in_degree: dict[str, int] = {name: 0 for name in graph.nodes}

    for (caller, callee) in graph.edges:          # keys are (caller, callee) tuples
        forward[caller].append(callee)
        if callee in in_degree:
            in_degree[callee] += 1

    # --- BFS from roots ----------------------------------------------------
    depths: dict[str, int] = {}
    queue: deque[str] = deque()

    for name, deg in in_degree.items():
        if deg == 0:
            depths[name] = 0
            queue.append(name)

    while queue:
        current = queue.popleft()
        current_depth = depths[current]
        for callee in forward[current]:
            if callee not in depths:
                depths[callee] = current_depth + 1
                queue.append(callee)

    # Disconnected nodes (cycles or orphans) default to 0
    for name in graph.nodes:
        depths.setdefault(name, 0)

    return depths


# ── Token similarity (no external deps) ───────────────────────────────────────

def _jaccard_token_similarity(name: str, query: str) -> float:
    """
    Compute Jaccard similarity between the token-sets of *name* and *query*.
    Tokens are lower-cased words split on '.', '_', and whitespace.
    Returns 0.0 if query is empty.
    """
    if not query:
        return 0.0

    def tokenise(text: str) -> set[str]:
        for ch in (".", "_"):
            text = text.replace(ch, " ")
        return {t.lower() for t in text.split() if t}

    name_tokens = tokenise(name)
    query_tokens = tokenise(query)
    union = name_tokens | query_tokens
    return len(name_tokens & query_tokens) / len(union) if union else 0.0


# ── Strategy Pattern: RankingStrategy hierarchy ────────────────────────────────

class RankingStrategy(ABC):
    """
    Abstract ranking strategy.
    Concrete strategies can be swapped without touching rank_nodes().
    """

    @abstractmethod
    def score(self, node: "CallNode", depth: int, query: str) -> float:
        """Return a non-negative relevance score. Higher = more relevant."""


class WeightedRankingStrategy(RankingStrategy):
    """
    Default strategy:
      score = (call_count  × CALL_WEIGHT)
            + (1/(depth+1) × DEPTH_WEIGHT × 10)
            + (jaccard_sim  × QUERY_WEIGHT × 10)

    Weights are class-level constants so subclasses can override them cheaply.
    """

    CALL_WEIGHT: float = 1.0
    DEPTH_WEIGHT: float = 0.5
    QUERY_WEIGHT: float = 2.0

    def score(self, node: "CallNode", depth: int, query: str) -> float:
        call_score  = node.call_count * self.CALL_WEIGHT
        depth_score = (1.0 / (depth + 1)) * self.DEPTH_WEIGHT * 10.0
        query_score = _jaccard_token_similarity(node.full_name, query) * self.QUERY_WEIGHT * 10.0
        return call_score + depth_score + query_score


# ── Heap item (used by heapq) ──────────────────────────────────────────────────

@dataclass(order=True)
class _RankedNode:
    """
    Heap entry for top-N selection.
    neg_score is negative so Python's min-heap acts as a max-heap.
    full_name is the secondary sort key (stable tie-breaker, O(1) compare).
    node/depth/score are payload — excluded from ordering via field(compare=False).
    """

    neg_score: float
    full_name: str
    node: "CallNode" = field(compare=False)
    depth: int       = field(compare=False, default=0)
    score: float     = field(compare=False, default=0.0)


# ── Source extraction ──────────────────────────────────────────────────────────

def extract_source(full_name: str) -> str | None:
    """
    Resolve *full_name* to a live Python object and return its source via inspect.
    Returns None for built-ins, dynamic functions, or anything inspect can't reach.

    Walk sys.modules once per call — only called for the top-N nodes so the
    O(modules) cost is paid at most top_n times.
    """
    parts = full_name.rsplit(".", 1)
    module_path = parts[0] if len(parts) == 2 else "__main__"
    func_name   = parts[-1]

    obj = None
    for mod_name, mod in sys.modules.items():
        if mod is None:
            continue
        if mod_name == module_path or mod_name.endswith(f".{module_path}"):
            obj = getattr(mod, func_name, None)
            if callable(obj):
                break

    if obj is None:
        return None

    try:
        return inspect.getsource(obj)
    except (OSError, TypeError):
        return None


# ── Public ranking API ─────────────────────────────────────────────────────────

def rank_nodes(
    graph: "CallGraph",
    query: str,
    top_n: int,
    strategy: RankingStrategy,
) -> list[_RankedNode]:
    """
    Filter graph to user-code nodes, score each one, and return the top-N
    using a heap so we never sort the full list — O(N log top_n).

    Args:
        graph    : CallGraph produced by the tracer
        query    : optional freeform query string (empty → no query boost)
        top_n    : maximum results to return
        strategy : RankingStrategy instance (injected)

    Returns:
        List of _RankedNode sorted best-first (highest score first).
    """
    depths = compute_node_depths(graph)
    heap: list[_RankedNode] = []

    for full_name, node in graph.nodes.items():
        if not is_user_code(full_name):
            continue
        depth = depths.get(full_name, 0)
        s = strategy.score(node, depth, query)
        entry = _RankedNode(
            neg_score=-s,
            full_name=full_name,
            node=node,
            depth=depth,
            score=s,
        )
        heapq.heappush(heap, entry)

    # nsmallest on neg_score == nlargest on score — O(N log top_n)
    return heapq.nsmallest(top_n, heap)


# ── Builder Pattern: ContextBuilder ───────────────────────────────────────────

class ContextBuilder:
    """
    Assembles the context.md document section by section.

    Intended call order:
        builder.set_header(...)
        for each function:
            builder.add_function(...)
        builder.set_footer()
        markdown = builder.build()

    Each method returns self so calls can be chained if preferred.
    """

    def __init__(self) -> None:
        self._sections: list[str] = []
        self._char_count: int = 0
        self._function_count: int = 0

    # ── Header ─────────────────────────────────────────────────────────────

    def set_header(
        self,
        query: str,
        script: str,
        total_calls: int,
        total_files: int,
        top_n: int,
    ) -> "ContextBuilder":
        query_line = f'**Query:** "{query}"' if query else "_No query specified — showing by call frequency + depth_"
        self._sections.append(
            f"# Execution Context\n\n"
            f"{query_line}  \n"
            f"**Script:** `{script}`  \n"
            f"**Traced:** {total_calls:,} calls across ~{total_files} modules  \n"
            f"**Showing:** top {top_n} most relevant functions\n\n"
            f"---\n"
        )
        return self

    # ── Per-function section ────────────────────────────────────────────────

    def add_function(
        self,
        node: "CallNode",
        source: str | None,
        score: float,
        depth: int,
        rank: int,
    ) -> "ContextBuilder":
        avg_ms = round((node.total_time / max(node.call_count, 1)) * 1000, 2)
        meta = (
            f"\n## {rank}. `{node.full_name}`\n\n"
            f"- **Called:** {node.call_count}×  "
            f"| **Avg time:** {avg_ms} ms  "
            f"| **Depth:** {depth}  "
            f"| **Score:** {score:.1f}\n"
        )
        if source:
            code_block = f"\n```python\n{source.rstrip()}\n```\n"
            self._char_count += len(source)
        else:
            code_block = "\n> _Source unavailable (built-in, lambda, or dynamically defined)_\n"
            self._char_count += 80

        self._sections.append(meta + code_block)
        self._function_count += 1
        return self

    # ── Footer ──────────────────────────────────────────────────────────────

    def set_footer(self) -> "ContextBuilder":
        token_estimate = self._char_count // 4   # 1 token ≈ 4 chars
        self._sections.append(
            f"\n---\n\n"
            f"_**{self._function_count} functions shown** — "
            f"≈ {token_estimate:,} tokens (estimated at 4 chars/token)_\n"
        )
        return self

    # ── Finalise ────────────────────────────────────────────────────────────

    def build(self) -> str:
        """Return the complete Markdown document as a single string."""
        return "".join(self._sections)

    @property
    def estimated_tokens(self) -> int:
        """Rough token count (char_count / 4) available before build()."""
        return self._char_count // 4
