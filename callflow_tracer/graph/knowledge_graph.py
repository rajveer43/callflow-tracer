"""Semantic knowledge graph layered on top of the call graph.

Extracts higher-level relationships:
  - CALLS / CALLED_BY  (structural)
  - SHARES_DATA_WITH   (inferred from shared arg/return types via docstring)
  - IN_MODULE          (containment)
  - CO_CALLED_WITH     (frequently appear as siblings in the same parent)

DSA used:
  - Directed weighted multi-graph (dict of dicts, edge list per type)
  - PageRank (power iteration) for semantic node importance
  - Co-occurrence counting with Counter for CO_CALLED_WITH edges
"""

from __future__ import annotations

import collections
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Generator, List, Optional, Set, Tuple


class RelType(str, Enum):
    CALLS = "CALLS"
    CALLED_BY = "CALLED_BY"
    IN_MODULE = "IN_MODULE"
    CO_CALLED_WITH = "CO_CALLED_WITH"
    SHARES_MODULE = "SHARES_MODULE"


@dataclass
class KGEdge:
    source: str
    target: str
    rel_type: RelType
    weight: float = 1.0

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "rel": self.rel_type.value,
            "weight": round(self.weight, 4),
        }


@dataclass
class KGNode:
    name: str
    module: str = ""
    node_type: str = "function"  # "function" | "module" | "llm"
    pagerank: float = 0.0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "module": self.module,
            "type": self.node_type,
            "pagerank": round(self.pagerank, 6),
        }


class KnowledgeGraph:
    """Weighted directed multi-relational knowledge graph.

    Internal structure:
        _nodes: name → KGNode
        _edges: list[KGEdge]          (the edge store)
        _adj:   source → [KGEdge]     (fast forward-adjacency)
    """

    def __init__(self) -> None:
        self._nodes: Dict[str, KGNode] = {}
        self._edges: List[KGEdge] = []
        self._adj: Dict[str, List[KGEdge]] = collections.defaultdict(list)

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def add_node(self, name: str, module: str = "", node_type: str = "function") -> KGNode:
        if name not in self._nodes:
            self._nodes[name] = KGNode(name=name, module=module, node_type=node_type)
        return self._nodes[name]

    def add_edge(
        self,
        source: str,
        target: str,
        rel_type: RelType,
        weight: float = 1.0,
    ) -> None:
        self.add_node(source)
        self.add_node(target)
        edge = KGEdge(source=source, target=target, rel_type=rel_type, weight=weight)
        self._edges.append(edge)
        self._adj[source].append(edge)

    # ------------------------------------------------------------------
    # Build from a UnifiedCallGraph
    # ------------------------------------------------------------------

    @classmethod
    def from_unified_graph(cls, unified_graph: "UnifiedCallGraph") -> "KnowledgeGraph":  # noqa: F821
        kg = cls()
        # Module nodes and IN_MODULE edges
        for name, node in unified_graph.nodes.items():
            module = name.rsplit(".", 1)[0] if "." in name else ""
            kg.add_node(name, module=module)
            if module:
                kg.add_node(module, node_type="module")
                kg.add_edge(name, module, RelType.IN_MODULE)

        # CALLS / CALLED_BY
        for edge in unified_graph.edges():
            weight = float(edge.call_count or 1)
            kg.add_edge(edge.caller, edge.callee, RelType.CALLS, weight)
            kg.add_edge(edge.callee, edge.caller, RelType.CALLED_BY, weight)

        # CO_CALLED_WITH — siblings that share a common parent caller
        parent_children: Dict[str, List[str]] = collections.defaultdict(list)
        for edge in unified_graph.edges():
            parent_children[edge.caller].append(edge.callee)

        co_occurrence: Dict[Tuple[str, str], int] = collections.Counter()
        for children in parent_children.values():
            for i, a in enumerate(children):
                for b in children[i + 1:]:
                    pair = (min(a, b), max(a, b))
                    co_occurrence[pair] += 1

        for (a, b), count in co_occurrence.items():
            if count >= 2:
                kg.add_edge(a, b, RelType.CO_CALLED_WITH, float(count))
                kg.add_edge(b, a, RelType.CO_CALLED_WITH, float(count))

        kg.compute_pagerank()
        return kg

    # ------------------------------------------------------------------
    # PageRank (power iteration)
    # ------------------------------------------------------------------

    def compute_pagerank(self, damping: float = 0.85, iterations: int = 50) -> None:
        nodes = list(self._nodes.keys())
        if not nodes:
            return
        n = len(nodes)
        rank = {node: 1.0 / n for node in nodes}

        # Build forward adjacency for CALLS edges only (structural)
        out_weights: Dict[str, float] = collections.defaultdict(float)
        for edge in self._edges:
            if edge.rel_type == RelType.CALLS:
                out_weights[edge.source] += edge.weight

        for _ in range(iterations):
            new_rank: Dict[str, float] = {node: (1 - damping) / n for node in nodes}
            for edge in self._edges:
                if edge.rel_type != RelType.CALLS:
                    continue
                total_out = out_weights[edge.source]
                if total_out > 0:
                    new_rank[edge.target] += damping * rank[edge.source] * (edge.weight / total_out)
            rank = new_rank

        for name, score in rank.items():
            self._nodes[name].pagerank = score

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def neighbours(self, name: str, rel_type: Optional[RelType] = None) -> List[str]:
        edges = self._adj.get(name, [])
        if rel_type is not None:
            edges = [e for e in edges if e.rel_type == rel_type]
        return [e.target for e in edges]

    def top_by_pagerank(self, k: int = 10) -> List[KGNode]:
        import heapq
        return heapq.nlargest(k, self._nodes.values(), key=lambda n: n.pagerank)

    def to_dict(self) -> dict:
        return {
            "nodes": [n.to_dict() for n in self._nodes.values()],
            "edges": [e.to_dict() for e in self._edges],
        }
