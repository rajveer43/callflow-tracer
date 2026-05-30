"""Merge static AST call graph with runtime CallGraph into one unified view.

Builder Pattern: UnifiedGraphBuilder accumulates both sources and produces
a single UnifiedCallGraph that downstream exporters and analysers can consume.

DSA used:
  - Adjacency list with edge-weight dict for O(1) edge lookup and merging
  - BFS for reachability queries
  - topological sort (Kahn's algorithm) for critical-path ordering
"""

from __future__ import annotations

import collections
from dataclasses import dataclass, field
from typing import Dict, Generator, List, Optional, Set, Tuple


@dataclass
class UnifiedEdge:
    caller: str
    callee: str
    call_count: int = 0
    total_time: float = 0.0
    is_static_only: bool = False   # seen in AST but not at runtime
    is_runtime_only: bool = False  # seen at runtime but not in AST

    @property
    def avg_time(self) -> float:
        return self.total_time / max(self.call_count, 1)

    def to_dict(self) -> dict:
        return {
            "caller": self.caller,
            "callee": self.callee,
            "call_count": self.call_count,
            "total_time": round(self.total_time, 6),
            "avg_time": round(self.avg_time, 6),
            "is_static_only": self.is_static_only,
            "is_runtime_only": self.is_runtime_only,
        }


@dataclass
class UnifiedNode:
    full_name: str
    call_count: int = 0
    total_time: float = 0.0
    in_static: bool = False
    in_runtime: bool = False

    def to_dict(self) -> dict:
        return {
            "full_name": self.full_name,
            "call_count": self.call_count,
            "total_time": round(self.total_time, 6),
            "avg_time": round(self.total_time / max(self.call_count, 1), 6),
            "in_static": self.in_static,
            "in_runtime": self.in_runtime,
        }


class UnifiedCallGraph:
    """The merged static+runtime call graph.

    Adjacency list stored as:
        _adj[caller] = {callee: UnifiedEdge}
    """

    def __init__(self) -> None:
        self.nodes: Dict[str, UnifiedNode] = {}
        # adjacency list: caller → (callee → edge)
        self._adj: Dict[str, Dict[str, UnifiedEdge]] = collections.defaultdict(dict)

    def _get_or_create_node(self, name: str) -> UnifiedNode:
        if name not in self.nodes:
            self.nodes[name] = UnifiedNode(full_name=name)
        return self.nodes[name]

    def add_static_edge(self, caller: str, callee: str) -> None:
        self._get_or_create_node(caller).in_static = True
        self._get_or_create_node(callee).in_static = True
        edge = self._adj[caller].get(callee)
        if edge is None:
            self._adj[caller][callee] = UnifiedEdge(
                caller=caller, callee=callee, is_static_only=True
            )

    def add_runtime_edge(
        self, caller: str, callee: str, call_count: int, total_time: float
    ) -> None:
        node_c = self._get_or_create_node(caller)
        node_e = self._get_or_create_node(callee)
        node_c.in_runtime = True
        node_e.in_runtime = True
        node_e.call_count += call_count
        node_e.total_time += total_time

        edge = self._adj[caller].get(callee)
        if edge is None:
            self._adj[caller][callee] = UnifiedEdge(
                caller=caller,
                callee=callee,
                call_count=call_count,
                total_time=total_time,
                is_runtime_only=True,
            )
        else:
            edge.call_count += call_count
            edge.total_time += total_time
            edge.is_static_only = False
            edge.is_runtime_only = not edge.is_static_only

    def edges(self) -> Generator[UnifiedEdge, None, None]:
        for callee_map in self._adj.values():
            yield from callee_map.values()

    def successors(self, node: str) -> List[str]:
        return list(self._adj.get(node, {}).keys())

    def predecessors(self, node: str) -> List[str]:
        return [c for c, callees in self._adj.items() if node in callees]

    # ------------------------------------------------------------------
    # BFS reachability
    # ------------------------------------------------------------------

    def reachable_from(self, start: str) -> Set[str]:
        visited: Set[str] = set()
        queue = collections.deque([start])
        while queue:
            cur = queue.popleft()
            if cur in visited:
                continue
            visited.add(cur)
            queue.extend(self.successors(cur))
        return visited

    # ------------------------------------------------------------------
    # Kahn topological sort (handles cycles — skips back-edges)
    # ------------------------------------------------------------------

    def topological_order(self) -> List[str]:
        in_degree: Dict[str, int] = {n: 0 for n in self.nodes}
        for edge in self.edges():
            in_degree[edge.callee] = in_degree.get(edge.callee, 0) + 1

        queue = collections.deque(
            [n for n, d in in_degree.items() if d == 0]
        )
        order: List[str] = []
        while queue:
            node = queue.popleft()
            order.append(node)
            for succ in self.successors(node):
                in_degree[succ] -= 1
                if in_degree[succ] == 0:
                    queue.append(succ)
        # append remaining (cycle members) in arbitrary order
        remaining = set(self.nodes) - set(order)
        order.extend(sorted(remaining))
        return order

    def to_dict(self) -> dict:
        return {
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges()],
        }


class UnifiedGraphBuilder:
    """Builder Pattern — fluent API for merging static + runtime data."""

    def __init__(self) -> None:
        self._graph = UnifiedCallGraph()

    def add_static_graph(self, static_graph: "StaticCallGraph") -> "UnifiedGraphBuilder":  # noqa: F821
        for caller, callees in static_graph.edges.items():
            for callee in callees:
                self._graph.add_static_edge(caller, callee)
        return self

    def add_runtime_graph(self, call_graph: Any) -> "UnifiedGraphBuilder":  # noqa: F821
        """Accept a callflow_tracer.core.tracer.CallGraph instance."""
        for (caller, callee), edge in call_graph.edges.items():
            self._graph.add_runtime_edge(
                caller, callee, edge.call_count, edge.total_time
            )
        return self

    def build(self) -> UnifiedCallGraph:
        return self._graph


# Keep the Any import for the type hint above
from typing import Any  # noqa: E402
