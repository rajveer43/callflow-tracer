"""Facade that combines CallGraph + LLM spans + graph intelligence into
one JSON payload ready for the live dashboard WebSocket stream.

Observer Pattern: Renderer is the Subject; WebSocket clients are observers
that subscribe via DashboardServer.subscribe().
"""

from __future__ import annotations

import json
import time
from typing import Any, Callable, Dict, List, Optional


class DashboardRenderer:
    """Merges all data sources into a single JSON snapshot.

    The snapshot schema::

        {
          "ts": <unix float>,
          "call_graph": { "nodes": [...], "edges": [...] },
          "llm_spans":  [ { model, provider, cost_usd, ... } ],
          "hot_paths":  [ { frames, hit_count, fraction } ],
          "god_nodes":  [ { full_name, total_degree, zscore, is_god_node } ],
          "communities":[ { id, size, members } ],
        }
    """

    def __init__(
        self,
        call_graph: Optional[Any] = None,
        llm_registry: Optional[Any] = None,
        sampler: Optional[Any] = None,
        unified_graph: Optional[Any] = None,
        god_node_reports: Optional[list] = None,
        communities: Optional[list] = None,
    ) -> None:
        self.call_graph = call_graph
        self.llm_registry = llm_registry
        self.sampler = sampler
        self.unified_graph = unified_graph
        self.god_node_reports = god_node_reports or []
        self.communities = communities or []

    def snapshot(self) -> dict:
        payload: dict = {"ts": time.time()}

        # Runtime call graph
        if self.call_graph is not None:
            try:
                payload["call_graph"] = {
                    "nodes": [n.to_dict() for n in self.call_graph.nodes.values()],
                    "edges": [e.to_dict() for e in self.call_graph.edges.values()],
                }
            except Exception:
                payload["call_graph"] = {}

        # LLM spans
        if self.llm_registry is not None:
            try:
                payload["llm_spans"] = [
                    s.to_dict() for s in self.llm_registry.get_all().values()
                ]
            except Exception:
                payload["llm_spans"] = []

        # Sampling profiler hot paths
        if self.sampler is not None:
            try:
                payload["hot_paths"] = [
                    p.to_dict() for p in self.sampler.top_hot_paths(10)
                ]
            except Exception:
                payload["hot_paths"] = []

        # God nodes
        payload["god_nodes"] = [g.to_dict() for g in self.god_node_reports]

        # Communities
        payload["communities"] = [c.to_dict() for c in self.communities]

        return payload

    def snapshot_json(self) -> str:
        return json.dumps(self.snapshot())
