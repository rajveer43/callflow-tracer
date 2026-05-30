"""God-node detector — identify the highest-fanout nodes in a call graph.

A "god node" is a function with abnormally high degree (in + out edges),
suggesting it is doing too much and should be refactored.

DSA used:
  - Degree centrality (in-degree + out-degree dict)
  - Min-heap (heapq.nlargest) for top-k selection in O(n log k)
  - Z-score outlier detection (mean + std) with no external deps
"""

from __future__ import annotations

import heapq
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class GodNodeReport:
    full_name: str
    in_degree: int
    out_degree: int
    total_degree: int
    zscore: float
    is_god_node: bool
    call_count: int = 0
    total_time: float = 0.0

    def to_dict(self) -> dict:
        return {
            "full_name": self.full_name,
            "in_degree": self.in_degree,
            "out_degree": self.out_degree,
            "total_degree": self.total_degree,
            "zscore": round(self.zscore, 3),
            "is_god_node": self.is_god_node,
            "call_count": self.call_count,
            "total_time": round(self.total_time, 6),
        }


class GodNodeDetector:
    """Analyse a UnifiedCallGraph and return ranked god-node reports.

    Usage::

        detector = GodNodeDetector(threshold_zscore=2.0)
        reports = detector.analyse(unified_graph)
    """

    def __init__(self, threshold_zscore: float = 2.0, top_k: int = 20) -> None:
        self.threshold_zscore = threshold_zscore
        self.top_k = top_k

    def analyse(self, unified_graph: "UnifiedCallGraph") -> List[GodNodeReport]:  # noqa: F821
        # Count in/out degrees from edge list
        in_deg: Dict[str, int] = {n: 0 for n in unified_graph.nodes}
        out_deg: Dict[str, int] = {n: 0 for n in unified_graph.nodes}

        for edge in unified_graph.edges():
            out_deg[edge.caller] = out_deg.get(edge.caller, 0) + 1
            in_deg[edge.callee] = in_deg.get(edge.callee, 0) + 1

        all_nodes = set(unified_graph.nodes) | set(in_deg) | set(out_deg)
        total_degrees = {
            n: in_deg.get(n, 0) + out_deg.get(n, 0) for n in all_nodes
        }

        # Z-score computation
        values = list(total_degrees.values())
        mean = sum(values) / max(len(values), 1)
        variance = sum((v - mean) ** 2 for v in values) / max(len(values), 1)
        std = math.sqrt(variance) or 1.0

        reports: List[GodNodeReport] = []
        for name, total in total_degrees.items():
            z = (total - mean) / std
            node_data = unified_graph.nodes.get(name)
            report = GodNodeReport(
                full_name=name,
                in_degree=in_deg.get(name, 0),
                out_degree=out_deg.get(name, 0),
                total_degree=total,
                zscore=z,
                is_god_node=z >= self.threshold_zscore,
                call_count=node_data.call_count if node_data else 0,
                total_time=node_data.total_time if node_data else 0.0,
            )
            reports.append(report)

        # Top-k by total_degree — O(n log k)
        return heapq.nlargest(self.top_k, reports, key=lambda r: r.total_degree)

    def god_nodes_only(self, unified_graph: "UnifiedCallGraph") -> List[GodNodeReport]:  # noqa: F821
        return [r for r in self.analyse(unified_graph) if r.is_god_node]
