"""Community / cluster detection on the call graph.

Implements a pure-Python greedy modularity maximisation algorithm (Louvain-style
Phase-1 only) so there are zero extra dependencies.

DSA used:
  - Union-Find (disjoint set with path compression + union by rank) for
    merging clusters in O(α(n)) amortized
  - Adjacency dict with edge weight accumulation
  - Modularity Q = (1/2m) Σ [A_ij - k_i*k_j/2m] δ(c_i, c_j)
"""

from __future__ import annotations

import collections
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# Union-Find with path compression + union by rank
# ---------------------------------------------------------------------------

class UnionFind:
    def __init__(self, nodes: list[str]) -> None:
        self.parent: Dict[str, str] = {n: n for n in nodes}
        self.rank: Dict[str, int] = {n: 0 for n in nodes}

    def find(self, x: str) -> str:
        # Path compression
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x: str, y: str) -> None:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1


# ---------------------------------------------------------------------------
# Community data model
# ---------------------------------------------------------------------------

@dataclass
class Community:
    id: int
    members: Set[str] = field(default_factory=set)
    internal_edges: int = 0
    total_degree: float = 0.0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "size": len(self.members),
            "members": sorted(self.members),
            "internal_edges": self.internal_edges,
        }


# ---------------------------------------------------------------------------
# Detector
# ---------------------------------------------------------------------------

class CommunityDetector:
    """Greedy modularity community detection.

    Works on the undirected projection of the (directed) call graph:
    edge weight = call_count (bidirectional average).

    Usage::

        detector = CommunityDetector(min_community_size=2)
        communities = detector.detect(unified_graph)
    """

    def __init__(self, min_community_size: int = 2, max_iterations: int = 10) -> None:
        self.min_community_size = min_community_size
        self.max_iterations = max_iterations

    def detect(self, unified_graph: "UnifiedCallGraph") -> List[Community]:  # noqa: F821
        nodes = list(unified_graph.nodes.keys())
        if not nodes:
            return []

        # Build undirected weighted adjacency dict
        weights: Dict[str, Dict[str, float]] = collections.defaultdict(lambda: collections.defaultdict(float))
        total_weight = 0.0
        for edge in unified_graph.edges():
            w = float(max(edge.call_count, 1))
            weights[edge.caller][edge.callee] += w
            weights[edge.callee][edge.caller] += w
            total_weight += w

        if total_weight == 0:
            # No edges — every node is its own community
            return [Community(i, {n}) for i, n in enumerate(nodes)]

        degree: Dict[str, float] = {
            n: sum(weights[n].values()) for n in nodes
        }

        # Start: each node is its own community
        uf = UnionFind(nodes)

        def _modularity_gain(u: str, v: str) -> float:
            # ΔQ for merging communities of u and v
            a_uv = weights[u].get(v, 0.0)
            two_m = total_weight
            k_u = degree[u]
            k_v = degree[v]
            return a_uv / two_m - (k_u * k_v) / (two_m ** 2)

        for _ in range(self.max_iterations):
            improved = False
            for u in nodes:
                best_gain = 0.0
                best_v: Optional[str] = None
                for v, w in weights[u].items():
                    if uf.find(u) != uf.find(v):
                        gain = _modularity_gain(u, v)
                        if gain > best_gain:
                            best_gain = gain
                            best_v = v
                if best_v is not None:
                    uf.union(u, best_v)
                    improved = True
            if not improved:
                break

        # Collect communities from Union-Find
        community_map: Dict[str, Set[str]] = collections.defaultdict(set)
        for n in nodes:
            root = uf.find(n)
            community_map[root].add(n)

        communities: List[Community] = []
        for idx, (root, members) in enumerate(community_map.items()):
            if len(members) < self.min_community_size:
                continue
            # Count internal edges
            internal = sum(
                1 for u in members for v in weights[u] if v in members and u < v
            )
            total_deg = sum(degree.get(m, 0.0) for m in members)
            communities.append(Community(idx, members, internal, total_deg))

        communities.sort(key=lambda c: len(c.members), reverse=True)
        return communities
