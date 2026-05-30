"""callflow_tracer.graph — static + runtime call graph intelligence.

Quick start::

    from callflow_tracer.graph import build_graph, GodNodeDetector, HTMLExporter

    graph = build_graph(runtime_call_graph=tracer_graph, source_root="src/")
    reports = GodNodeDetector().analyse(graph)
    HTMLExporter().export(graph, "call_graph.html", god_nodes=reports)
"""

from .ast_parser import ASTParser, StaticCallGraph
from .community_detector import Community, CommunityDetector
from .exporters import BaseExporter, HTMLExporter, JSONExporter, Neo4jExporter
from .god_nodes import GodNodeDetector, GodNodeReport
from .knowledge_graph import KnowledgeGraph, RelType
from .runtime_graph import UnifiedCallGraph, UnifiedGraphBuilder


def build_graph(
    runtime_call_graph=None,
    source_root: str | None = None,
    package: str = "",
) -> UnifiedCallGraph:
    """Convenience factory: parse source + merge runtime data."""
    builder = UnifiedGraphBuilder()
    if source_root is not None:
        parser = ASTParser()
        parser.parse_directory(source_root, package=package)
        builder.add_static_graph(parser.graph)
    if runtime_call_graph is not None:
        builder.add_runtime_graph(runtime_call_graph)
    return builder.build()


__all__ = [
    "build_graph",
    "ASTParser",
    "StaticCallGraph",
    "UnifiedCallGraph",
    "UnifiedGraphBuilder",
    "KnowledgeGraph",
    "RelType",
    "GodNodeDetector",
    "GodNodeReport",
    "CommunityDetector",
    "Community",
    "BaseExporter",
    "HTMLExporter",
    "JSONExporter",
    "Neo4jExporter",
]
