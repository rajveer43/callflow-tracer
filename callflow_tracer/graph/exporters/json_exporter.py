"""JSON exporter — serialise the full unified graph."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Union

from .base_exporter import BaseExporter


class JSONExporter(BaseExporter):
    def __init__(self, indent: int = 2) -> None:
        self._indent = indent

    def export(
        self,
        unified_graph: "UnifiedCallGraph",  # noqa: F821
        output_path: Union[str, Path],
        *,
        knowledge_graph: Optional["KnowledgeGraph"] = None,  # noqa: F821
        communities: Optional[list] = None,
        god_nodes: Optional[list] = None,
    ) -> Path:
        out = Path(output_path)
        payload: dict = {"call_graph": unified_graph.to_dict()}
        if knowledge_graph is not None:
            payload["knowledge_graph"] = knowledge_graph.to_dict()
        if communities is not None:
            payload["communities"] = [c.to_dict() for c in communities]
        if god_nodes is not None:
            payload["god_nodes"] = [g.to_dict() for g in god_nodes]

        out.write_text(json.dumps(payload, indent=self._indent), encoding="utf-8")
        return out
