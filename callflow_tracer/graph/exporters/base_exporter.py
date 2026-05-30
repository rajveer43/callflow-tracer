"""Abstract base exporter — Strategy Pattern interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Union


class BaseExporter(ABC):
    """All graph exporters implement this interface."""

    @abstractmethod
    def export(
        self,
        unified_graph: "UnifiedCallGraph",  # noqa: F821
        output_path: Union[str, Path],
        *,
        knowledge_graph: Optional["KnowledgeGraph"] = None,  # noqa: F821
        communities: Optional[list] = None,
        god_nodes: Optional[list] = None,
    ) -> Path:
        """Write the graph to *output_path* and return the resolved path."""
