"""
Call-graph analysis utilities for `callflow why` command.

DSA used:
  - defaultdict(list)         : O(E) reverse adjacency list construction
  - deque                     : O(1) FIFO for BFS
  - frozenset per BFS state   : O(1) cycle detection per hop
  - set[str]                  : O(1) candidate lookup for fuzzy name matching

All graph algorithms are O(V + E) or better.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.tracer import CallGraph

# ── Reverse adjacency list ─────────────────────────────────────────────────────

def build_reverse_graph(graph: "CallGraph") -> dict[str, list[str]]:
    """
    Build a reverse adjacency list: callee → list[caller].

    graph.edges is a dict keyed by (caller, callee) tuples, so one O(E)
    iteration is all we need — no second pass required.

    Returns a plain dict (not defaultdict) so callers can use .get(k, [])
    without accidentally inserting empty lists.
    """
    reverse: dict[str, list[str]] = defaultdict(list)

    for (caller, callee) in graph.edges:
        reverse[callee].append(caller)

    return dict(reverse)


# ── Fuzzy name resolution ──────────────────────────────────────────────────────

def resolve_target_names(graph: "CallGraph", partial_name: str) -> list[str]:
    """
    Return all full_names in *graph* that match *partial_name*.

    Matching rules (checked in order, union of results):
      1. Exact match          — full_name == partial_name
      2. Suffix match         — full_name ends with ".{partial_name}"
      3. Substring match      — partial_name appears anywhere in full_name

    Returns a deduplicated list preserving discovery order.
    Uses a set for O(1) dedup — O(V) total.
    """
    seen: set[str] = set()
    ordered: list[str] = []

    def _add(name: str) -> None:
        if name not in seen:
            seen.add(name)
            ordered.append(name)

    suffix = f".{partial_name}"
    for full_name in graph.nodes:
        if full_name == partial_name:
            _add(full_name)
        elif full_name.endswith(suffix):
            _add(full_name)
        elif partial_name in full_name:
            _add(full_name)

    return ordered


# ── BFS path finder ────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class CallChain:
    """
    One complete call chain leading to the target function.

    path    : ordered list from root caller → target  (e.g. ["a", "b", "c"])
    target  : the function being investigated
    depth   : len(path) - 1  (number of hops)
    """

    path: tuple[str, ...]
    target: str

    @property
    def depth(self) -> int:
        return len(self.path) - 1

    @property
    def root(self) -> str:
        return self.path[0]


def find_call_chains(
    reverse_graph: dict[str, list[str]],
    target: str,
    max_chains: int = 25,
    max_depth: int = 15,
) -> list[CallChain]:
    """
    BFS backwards from *target* through the reverse adjacency list to discover
    every unique call chain that leads to it.

    BFS (not DFS) is used so shorter chains are returned before deeper ones —
    the developer sees the most direct callers first.

    Cycle safety:
        Each BFS state carries a frozenset of nodes already in the current path.
        Before enqueuing a caller, we check membership in O(1).  Because we
        create a new frozenset per state (immutable), there is no shared mutable
        state between paths — safe across all branches.

    Args:
        reverse_graph : callee → list[caller]  (from build_reverse_graph)
        target        : full_name of the function to investigate
        max_chains    : cap on total results (prevents explosion on fan-in graphs)
        max_depth     : maximum chain length (prevents very deep traversal)

    Returns:
        List of CallChain objects, shortest chains first.
    """
    # BFS state: (current_node, path_so_far, path_as_frozenset)
    # path_so_far is stored reversed (target first) for O(1) append;
    # we reverse it when building the final CallChain.
    BFSState = tuple[str, tuple[str, ...], frozenset[str]]

    initial_path: tuple[str, ...] = (target,)
    initial_seen: frozenset[str] = frozenset({target})

    queue: deque[BFSState] = deque()
    queue.append((target, initial_path, initial_seen))

    completed: list[CallChain] = []

    while queue and len(completed) < max_chains:
        current, path_reversed, path_set = queue.popleft()

        callers = reverse_graph.get(current, [])

        if not callers:
            # Reached a root node — this is a complete chain
            completed.append(
                CallChain(path=tuple(reversed(path_reversed)), target=target)
            )
            continue

        if len(path_reversed) > max_depth:
            # Chain too deep — treat current node as root
            completed.append(
                CallChain(path=tuple(reversed(path_reversed)), target=target)
            )
            continue

        for caller in callers:
            if caller not in path_set:          # O(1) frozenset lookup
                new_path = path_reversed + (caller,)
                new_seen = path_set | {caller}  # new frozenset — no mutation
                queue.append((caller, new_path, new_seen))

    return completed


# ── Edge frequency lookup ──────────────────────────────────────────────────────

def get_edge_call_count(graph: "CallGraph", caller: str, callee: str) -> int:
    """
    Return the call count for a specific caller→callee edge, or 0 if missing.
    O(1) — graph.edges is a dict keyed by (caller, callee) tuples.
    """
    edge = graph.edges.get((caller, callee))
    return edge.call_count if edge is not None else 0


# ── Formatting helpers ─────────────────────────────────────────────────────────

def format_chain_as_tree(
    chain: CallChain,
    graph: "CallGraph",
    chain_index: int,
) -> str:
    """
    Render a single CallChain as an indented tree with call counts.

    Example output:
        [1] api.routes.post_purchase (12×)
            └─ payment.cart.checkout (12×)
                └─ payment.processor.charge_customer  ← TARGET
    """
    lines: list[str] = []
    root_count = get_edge_call_count(graph, chain.path[0], chain.path[1]) if len(chain.path) > 1 else 0
    root_label = f"{chain.path[0]}"
    if root_count:
        root_label += f" ({root_count}×)"
    lines.append(f"[{chain_index}] {root_label}")

    for i in range(1, len(chain.path)):
        indent = "    " * i
        node = chain.path[i]
        if i < len(chain.path) - 1:
            count = get_edge_call_count(graph, chain.path[i], chain.path[i + 1])
            label = f"{node} ({count}×)" if count else node
        else:
            label = f"{node}  ← TARGET"
        lines.append(f"{indent}└─ {label}")

    return "\n".join(lines)


def group_chains_by_root(chains: list[CallChain]) -> dict[str, list[CallChain]]:
    """
    Group chains by their root node for organised display.
    Uses a dict to preserve insertion order — O(N).
    """
    groups: dict[str, list[CallChain]] = {}
    for chain in chains:
        root = chain.root
        if root not in groups:
            groups[root] = []
        groups[root].append(chain)
    return groups
