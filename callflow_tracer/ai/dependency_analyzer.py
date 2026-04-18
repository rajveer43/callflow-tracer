"""
Dependency analysis module for CallFlow Tracer.

Analyze function dependencies and coupling.
Detects circular dependencies, tight coupling, and dead code.

Example:
    from callflow_tracer.ai import analyze_dependencies

    result = analyze_dependencies(graph)
    print(result.circular_dependencies)
    print(result.tight_coupling)
    print(result.unused_functions)
    print(result.critical_path)
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


@dataclass
class DependencyAnalysis:
    """Dependency analysis results."""

    timestamp: str
    total_functions: int
    circular_dependencies: List[List[str]]
    tight_coupling: List[Dict[str, Any]]
    unused_functions: List[str]
    critical_path: List[str]
    dependency_graph: Dict[str, List[str]]
    reverse_dependency_graph: Dict[str, List[str]]
    function_depth: Dict[str, int]
    coupling_matrix: Dict[str, Dict[str, int]]


@dataclass
class AnalyzerConfig:
    """Configuration for DependencyAnalyzer behavior and thresholds."""

    # Coupling detection thresholds
    high_coupling_threshold: int = 5
    """Functions depending on > N others are flagged as high coupling."""

    severe_coupling_threshold: int = 10
    """Functions depending on > N others are marked 'high' severity (vs 'medium')."""

    # Entry point detection
    entry_point_patterns: List[str] = None
    """Heuristics for detecting entry points (not marked as unused)."""

    # Algorithm safety limits
    max_cycle_depth: int = 100
    """Maximum DFS depth to prevent stack overflow in cycle detection."""

    def __post_init__(self):
        """Initialize default entry point patterns if not provided."""
        if self.entry_point_patterns is None:
            self.entry_point_patterns = ["main", "__main__", "test_"]


class AnalysisPass(ABC):
    """Abstract base class for a single analysis pass over the dependency graph."""

    @abstractmethod
    def name(self) -> str:
        """Human-readable name for debugging and logging."""
        pass

    @abstractmethod
    def execute(
        self,
        nodes: Dict[str, Dict[str, Any]],
        edges: List[Tuple[str, str]],
        dep_graph: Dict[str, List[str]],
        rev_dep_graph: Dict[str, List[str]],
    ) -> Tuple[str, Any]:
        """
        Execute the analysis pass.

        Args:
            nodes: Dictionary of nodes
            edges: List of edges
            dep_graph: Forward dependency graph
            rev_dep_graph: Reverse dependency graph

        Returns:
            Tuple of (result_key, result_value) to include in output
        """
        pass


class AnalysisBuilder:
    """Builder for composing analysis passes."""

    def __init__(self, analyzer: "DependencyAnalyzer"):
        """
        Initialize the builder.

        Args:
            analyzer: DependencyAnalyzer instance to use for passes
        """
        self.analyzer = analyzer
        self.passes: List[AnalysisPass] = []
        logger.debug("Initialized AnalysisBuilder")

    def with_circular_deps(self) -> "AnalysisBuilder":
        """Add circular dependency detection pass."""
        self.passes.append(CircularDependencyPass(self.analyzer))
        return self

    def with_tight_coupling(self) -> "AnalysisBuilder":
        """Add tight coupling analysis pass."""
        self.passes.append(TightCouplingPass(self.analyzer))
        return self

    def with_unused_functions(self) -> "AnalysisBuilder":
        """Add unused functions detection pass."""
        self.passes.append(UnusedFunctionsPass(self.analyzer))
        return self

    def with_critical_path(self) -> "AnalysisBuilder":
        """Add critical path analysis pass."""
        self.passes.append(CriticalPathPass(self.analyzer))
        return self

    def with_function_depth(self) -> "AnalysisBuilder":
        """Add function depth computation pass."""
        self.passes.append(FunctionDepthPass(self.analyzer))
        return self

    def with_coupling_matrix(self) -> "AnalysisBuilder":
        """Add coupling matrix construction pass."""
        self.passes.append(CouplingMatrixPass(self.analyzer))
        return self

    def with_pass(self, analysis_pass: AnalysisPass) -> "AnalysisBuilder":
        """
        Add a custom analysis pass.

        Args:
            analysis_pass: AnalysisPass instance to add

        Returns:
            Self for chaining
        """
        self.passes.append(analysis_pass)
        logger.debug(f"Added analysis pass: {analysis_pass.name()}")
        return self

    def with_all_passes(self) -> "AnalysisBuilder":
        """
        Enable all standard analysis passes in order.

        Returns:
            Self for chaining
        """
        logger.debug("Enabling all standard analysis passes")
        return (
            self.with_circular_deps()
            .with_tight_coupling()
            .with_unused_functions()
            .with_critical_path()
            .with_function_depth()
            .with_coupling_matrix()
        )

    def build(self) -> List[AnalysisPass]:
        """
        Build and return the list of analysis passes.

        Returns:
            List of AnalysisPass instances to execute in order
        """
        logger.info(f"Built analysis pipeline with {len(self.passes)} passes")
        for i, pass_obj in enumerate(self.passes, 1):
            logger.debug(f"  {i}. {pass_obj.name()}")
        return self.passes


class GraphExtractor(ABC):
    """Abstract base class for extracting nodes and edges from different graph formats."""

    @abstractmethod
    def extract_nodes(self, graph: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Extract nodes from graph.

        Args:
            graph: Input graph structure

        Returns:
            Dictionary mapping node keys to node data

        Raises:
            ValueError: If graph structure is invalid
        """
        pass

    @abstractmethod
    def extract_edges(self, graph: Dict[str, Any]) -> List[Tuple[str, str]]:
        """
        Extract edges from graph.

        Args:
            graph: Input graph structure

        Returns:
            List of (source, target) edge tuples

        Raises:
            ValueError: If graph structure is invalid
        """
        pass

    @staticmethod
    def _build_node_key(node: Dict[str, Any]) -> str:
        """Build a unique key for a node from its metadata."""
        module = node.get("module", "unknown")
        name = node.get("name", "unknown")
        return f"{module}:{name}"


class FlatGraphExtractor(GraphExtractor):
    """Handles graphs with top-level 'nodes' and 'edges' keys."""

    def extract_nodes(self, graph: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Extract nodes from flat graph structure."""
        if "nodes" not in graph:
            raise ValueError(
                "Graph missing 'nodes' key. Expected format: {'nodes': [...], 'edges': [...]}"
            )

        nodes = {}
        try:
            for node in graph["nodes"]:
                if not isinstance(node, dict):
                    logger.warning(f"Skipping non-dict node: {node}")
                    continue
                key = self._build_node_key(node)
                nodes[key] = node
        except Exception as e:
            logger.error(f"Error processing nodes in flat graph: {e}")
            raise ValueError(f"Failed to extract nodes: {e}") from e

        return nodes

    def extract_edges(self, graph: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Extract edges from flat graph structure."""
        if "edges" not in graph:
            raise ValueError(
                "Graph missing 'edges' key. Expected format: {'nodes': [...], 'edges': [...]}"
            )

        edges = []
        try:
            for i, edge in enumerate(graph["edges"]):
                if not isinstance(edge, dict):
                    logger.warning(f"Skipping non-dict edge at index {i}: {edge}")
                    continue

                source = edge.get("from")
                target = edge.get("to")

                if not source or not target:
                    logger.warning(
                        f"Skipping edge at index {i} with missing 'from' or 'to': {edge}"
                    )
                    continue

                edges.append((source, target))
        except Exception as e:
            logger.error(f"Error processing edges in flat graph: {e}")
            raise ValueError(f"Failed to extract edges: {e}") from e

        return edges


class NestedGraphExtractor(GraphExtractor):
    """Handles graphs with nested 'data.nodes' and 'data.edges' structure."""

    def extract_nodes(self, graph: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Extract nodes from nested graph structure."""
        if "data" not in graph:
            raise ValueError(
                "Graph missing 'data' key. Expected format: {'data': {'nodes': [...], 'edges': [...]}}"
            )

        if "nodes" not in graph.get("data", {}):
            raise ValueError(
                "Graph missing 'data.nodes' key. Expected format: {'data': {'nodes': [...], 'edges': [...]}}"
            )

        # Delegate to flat extractor on nested data
        flat_extractor = FlatGraphExtractor()
        return flat_extractor.extract_nodes(graph["data"])

    def extract_edges(self, graph: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Extract edges from nested graph structure."""
        if "data" not in graph:
            raise ValueError("Graph missing 'data' key")

        if "edges" not in graph.get("data", {}):
            raise ValueError("Graph missing 'data.edges' key")

        # Delegate to flat extractor on nested data
        flat_extractor = FlatGraphExtractor()
        return flat_extractor.extract_edges(graph["data"])


class GraphExtractorFactory:
    """Factory to detect and instantiate the appropriate graph extractor."""

    @staticmethod
    def create(graph: Dict[str, Any]) -> GraphExtractor:
        """
        Create the appropriate extractor for the given graph format.

        Args:
            graph: Input graph to detect format from

        Returns:
            GraphExtractor instance for the detected format

        Raises:
            ValueError: If graph format is not recognized
        """
        if not isinstance(graph, dict):
            raise ValueError(f"Expected dict, got {type(graph).__name__}")

        # Try nested format first (more specific)
        if "data" in graph and isinstance(graph.get("data"), dict):
            if "nodes" in graph["data"] or "edges" in graph["data"]:
                logger.debug("Detected nested graph format (data.nodes/edges)")
                return NestedGraphExtractor()

        # Try flat format
        if "nodes" in graph or "edges" in graph:
            logger.debug("Detected flat graph format (top-level nodes/edges)")
            return FlatGraphExtractor()

        raise ValueError(
            "Unknown graph format. Expected either:\n"
            "  - Flat format: {'nodes': [...], 'edges': [...]}\n"
            "  - Nested format: {'data': {'nodes': [...], 'edges': [...]}}"
        )


class DependencyAnalyzer:
    """Analyze function dependencies with configurable behavior."""

    def __init__(self, config: Optional[AnalyzerConfig] = None):
        """
        Initialize dependency analyzer.

        Args:
            config: Configuration for thresholds and behavior. Defaults to AnalyzerConfig()
        """
        self.config = config or AnalyzerConfig()
        logger.debug(
            f"Initialized DependencyAnalyzer with config: "
            f"high_coupling_threshold={self.config.high_coupling_threshold}, "
            f"severe_coupling_threshold={self.config.severe_coupling_threshold}"
        )

    def analyze_with_builder(
        self,
        nodes: Dict[str, Dict[str, Any]],
        edges: List[Tuple[str, str]],
        dep_graph: Dict[str, List[str]],
        rev_dep_graph: Dict[str, List[str]],
        builder: Optional[AnalysisBuilder] = None,
    ) -> DependencyAnalysis:
        """
        Run analysis passes using a builder and collect results.

        Args:
            nodes: Dictionary of nodes
            edges: List of edges
            dep_graph: Forward dependency graph
            rev_dep_graph: Reverse dependency graph
            builder: Optional AnalysisBuilder. If None, uses all passes.

        Returns:
            DependencyAnalysis with results from all executed passes
        """
        if builder is None:
            builder = AnalysisBuilder(self).with_all_passes()

        passes = builder.build()
        results = {}

        # Execute each pass and collect results
        for pass_obj in passes:
            try:
                logger.debug(f"Executing pass: {pass_obj.name()}")
                key, value = pass_obj.execute(nodes, edges, dep_graph, rev_dep_graph)
                results[key] = value
                logger.debug(f"Completed pass: {pass_obj.name()}")
            except Exception:
                logger.exception(f"Error executing pass: {pass_obj.name()}")
                raise

        # Build and return DependencyAnalysis
        analysis = DependencyAnalysis(
            timestamp=datetime.now().isoformat(),
            total_functions=len(nodes),
            circular_dependencies=results.get("circular_dependencies", []),
            tight_coupling=results.get("tight_coupling", []),
            unused_functions=results.get("unused_functions", []),
            critical_path=results.get("critical_path", []),
            dependency_graph=dep_graph,
            reverse_dependency_graph=rev_dep_graph,
            function_depth=results.get("function_depth", {}),
            coupling_matrix=results.get("coupling_matrix", {}),
        )

        return analysis

    def analyze(self, graph: Dict[str, Any]) -> DependencyAnalysis:
        """
        Analyze dependencies from execution trace.

        Args:
            graph: Execution trace graph with 'nodes' and 'edges' keys,
                   or nested structure with 'data.nodes' and 'data.edges'

        Returns:
            DependencyAnalysis dataclass with all analysis results

        Raises:
            TypeError: If graph is not a dict
            ValueError: If graph structure is invalid or missing required keys
        """
        logger.info("Starting dependency analysis")

        # Validate input
        if not isinstance(graph, dict):
            msg = f"Expected dict for graph, got {type(graph).__name__}"
            logger.error(msg)
            raise TypeError(msg)

        try:
            logger.debug(f"Input graph top-level keys: {list(graph.keys())}")

            # Extract nodes and edges
            try:
                nodes = self._extract_nodes(graph)
                logger.info(f"Extracted {len(nodes)} nodes")
            except Exception as e:
                logger.error(f"Failed to extract nodes from graph: {e}", exc_info=True)
                raise

            try:
                edges = self._extract_edges(graph)
                logger.info(f"Extracted {len(edges)} edges")
            except Exception as e:
                logger.error(f"Failed to extract edges from graph: {e}", exc_info=True)
                raise

            # Validate graph structure
            orphaned_edges = [
                (source, target) for source, target in edges
                if source not in nodes or target not in nodes
            ]
            if orphaned_edges:
                logger.warning(
                    f"Found {len(orphaned_edges)} edges with missing source/target nodes. "
                    f"Examples: {orphaned_edges[:3]}"
                )

            # Build dependency graphs
            logger.debug("Building dependency graphs")
            dep_graph = self._build_dependency_graph(nodes, edges)
            rev_dep_graph = self._build_reverse_dependency_graph(dep_graph)

            # Run all analysis passes using builder pattern
            analysis_results = self.analyze_with_builder(
                nodes, edges, dep_graph, rev_dep_graph
            )

            logger.info("Dependency analysis completed successfully")
            return analysis_results

        except Exception:
            logger.exception("Unexpected error during dependency analysis")
            raise

    def _extract_nodes(self, graph: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Extract nodes from graph using appropriate adapter.

        Args:
            graph: Input graph structure

        Returns:
            Dictionary mapping node keys to node data
        """
        extractor = GraphExtractorFactory.create(graph)
        return extractor.extract_nodes(graph)

    def _extract_edges(self, graph: Dict[str, Any]) -> List[Tuple[str, str]]:
        """
        Extract edges from graph using appropriate adapter.

        Args:
            graph: Input graph structure

        Returns:
            List of (source, target) edge tuples
        """
        extractor = GraphExtractorFactory.create(graph)
        return extractor.extract_edges(graph)

    def _build_dependency_graph(
        self, nodes: Dict[str, Dict[str, Any]], edges: List[Tuple[str, str]]
    ) -> Dict[str, List[str]]:
        """Build dependency graph."""
        graph = {node_key: [] for node_key in nodes.keys()}

        for source, target in edges:
            if source in graph:
                if target not in graph[source]:
                    graph[source].append(target)

        return graph

    def _build_reverse_dependency_graph(
        self, dep_graph: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """Build reverse dependency graph."""
        rev_graph = defaultdict(list)

        for source, targets in dep_graph.items():
            for target in targets:
                if target not in rev_graph:
                    rev_graph[target] = []
                rev_graph[target].append(source)

        return dict(rev_graph)

    def _find_circular_dependencies(
        self, dep_graph: Dict[str, List[str]]
    ) -> List[List[str]]:
        """
        Find circular dependencies using optimized DFS.

        Uses a dictionary to track node positions in current path for O(1) lookups
        instead of O(n) list.index() operations. Time complexity: O(V + E) instead of O(V² + E).
        """
        circular = []
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: List[str], path_indices: Dict[str, int], depth: int):
            """
            Recursively search for cycles using optimized path tracking.

            Args:
                node: Current node being visited
                path: Current DFS path
                path_indices: Maps node -> index in path for O(1) cycle detection
                depth: Current recursion depth (safety check)
            """
            if depth > self.config.max_cycle_depth:
                logger.warning(
                    f"Circular dependency search exceeded max depth {self.config.max_cycle_depth}"
                )
                return

            visited.add(node)
            rec_stack.add(node)
            path_indices[node] = len(path)
            path.append(node)

            for neighbor in dep_graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path, path_indices, depth + 1)
                elif neighbor in rec_stack:
                    # Found cycle using O(1) dictionary lookup instead of list.index()
                    cycle_start = path_indices[neighbor]
                    cycle = path[cycle_start:] + [neighbor]
                    if cycle not in circular:
                        circular.append(cycle)
                        logger.debug(f"Found cycle: {' -> '.join(cycle)}")

            # Clean up recursion stack
            rec_stack.discard(node)
            del path_indices[node]
            path.pop()

        # Start DFS from each unvisited node
        for node in dep_graph:
            if node not in visited:
                dfs(node, [], {}, depth=0)

        return circular

    def _find_tight_coupling(
        self, dep_graph: Dict[str, List[str]], rev_dep_graph: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """
        Find tightly coupled functions using configured thresholds.

        Functions are flagged if they depend on or are depended upon by more
        than config.high_coupling_threshold other functions.
        """
        tight_couplings = []

        # Find functions that depend on many others (high outgoing coupling)
        for func, dependencies in dep_graph.items():
            if len(dependencies) > self.config.high_coupling_threshold:
                severity = (
                    "high"
                    if len(dependencies) > self.config.severe_coupling_threshold
                    else "medium"
                )
                tight_couplings.append(
                    {
                        "function": func,
                        "type": "high_outgoing_coupling",
                        "coupled_with": dependencies[: self.config.high_coupling_threshold],
                        "coupling_count": len(dependencies),
                        "severity": severity,
                    }
                )

        # Find functions that are depended on by many others (high incoming coupling)
        for func, dependents in rev_dep_graph.items():
            if len(dependents) > self.config.high_coupling_threshold:
                severity = (
                    "high"
                    if len(dependents) > self.config.severe_coupling_threshold
                    else "medium"
                )
                tight_couplings.append(
                    {
                        "function": func,
                        "type": "high_incoming_coupling",
                        "depended_by": dependents[: self.config.high_coupling_threshold],
                        "coupling_count": len(dependents),
                        "severity": severity,
                    }
                )

        return tight_couplings

    def _find_unused_functions(
        self, nodes: Dict[str, Dict[str, Any]], rev_dep_graph: Dict[str, List[str]]
    ) -> List[str]:
        """Find unused functions."""
        unused = []

        for node_key in nodes.keys():
            if node_key not in rev_dep_graph or len(rev_dep_graph[node_key]) == 0:
                # Check if it's a root function (entry point)
                if not self._is_entry_point(node_key):
                    unused.append(node_key)

        return unused

    def _is_entry_point(self, func_key: str) -> bool:
        """
        Check if function is an entry point using configured patterns.

        Entry points are not marked as unused, even if nothing depends on them.

        Args:
            func_key: Function key in format "module:name"

        Returns:
            True if function matches any entry point pattern
        """
        func_lower = func_key.lower()
        return any(pattern in func_lower for pattern in self.config.entry_point_patterns)

    def _find_critical_path(
        self, nodes: Dict[str, Dict[str, Any]], edges: List[Tuple[str, str]]
    ) -> List[str]:
        """Find critical path (longest execution path)."""
        # Build graph with weights
        weighted_graph = defaultdict(list)

        for source, target in edges:
            weight = nodes.get(target, {}).get("total_time", 0)
            weighted_graph[source].append((target, weight))

        # Find longest path using DFS
        max_path = []
        max_weight = 0

        def dfs(node, path, weight):
            nonlocal max_path, max_weight

            if weight > max_weight:
                max_weight = weight
                max_path = path.copy()

            for neighbor, edge_weight in weighted_graph.get(node, []):
                if neighbor not in path:
                    path.append(neighbor)
                    dfs(neighbor, path, weight + edge_weight)
                    path.pop()

        # Start from all nodes
        for start_node in nodes.keys():
            dfs(
                start_node, [start_node], nodes.get(start_node, {}).get("total_time", 0)
            )

        return max_path

    def _compute_function_depth(
        self, dep_graph: Dict[str, List[str]]
    ) -> Dict[str, int]:
        """Compute depth of each function in dependency tree."""
        depth = {}

        def compute_depth(node, visited=None):
            if visited is None:
                visited = set()

            if node in depth:
                return depth[node]

            if node in visited:
                return 0  # Circular dependency

            visited.add(node)

            if not dep_graph.get(node):
                depth[node] = 0
            else:
                max_depth = 0
                for dependency in dep_graph[node]:
                    max_depth = max(
                        max_depth, compute_depth(dependency, visited.copy())
                    )
                depth[node] = max_depth + 1

            return depth[node]

        for node in dep_graph:
            compute_depth(node)

        return depth

    def _build_coupling_matrix(
        self, dep_graph: Dict[str, List[str]]
    ) -> Dict[str, Dict[str, int]]:
        """Build coupling matrix showing dependencies between functions."""
        matrix = {}

        for func in dep_graph:
            matrix[func] = {}
            for other_func in dep_graph:
                if func != other_func:
                    # Count direct dependencies
                    if other_func in dep_graph.get(func, []):
                        matrix[func][other_func] = 1
                    else:
                        matrix[func][other_func] = 0

        return matrix


# ============================================================================
# Concrete Analysis Pass Implementations
# ============================================================================


class CircularDependencyPass(AnalysisPass):
    """Analysis pass for detecting circular dependencies."""

    def __init__(self, analyzer: "DependencyAnalyzer"):
        """Initialize with reference to analyzer."""
        self.analyzer = analyzer

    def name(self) -> str:
        """Return pass name."""
        return "Circular Dependency Detection"

    def execute(
        self,
        nodes: Dict[str, Dict[str, Any]],
        edges: List[Tuple[str, str]],
        dep_graph: Dict[str, List[str]],
        rev_dep_graph: Dict[str, List[str]],
    ) -> Tuple[str, Any]:
        """Execute circular dependency analysis."""
        result = self.analyzer._find_circular_dependencies(dep_graph)
        return "circular_dependencies", result


class TightCouplingPass(AnalysisPass):
    """Analysis pass for detecting tight coupling."""

    def __init__(self, analyzer: "DependencyAnalyzer"):
        """Initialize with reference to analyzer."""
        self.analyzer = analyzer

    def name(self) -> str:
        """Return pass name."""
        return "Tight Coupling Analysis"

    def execute(
        self,
        nodes: Dict[str, Dict[str, Any]],
        edges: List[Tuple[str, str]],
        dep_graph: Dict[str, List[str]],
        rev_dep_graph: Dict[str, List[str]],
    ) -> Tuple[str, Any]:
        """Execute tight coupling analysis."""
        result = self.analyzer._find_tight_coupling(dep_graph, rev_dep_graph)
        return "tight_coupling", result


class UnusedFunctionsPass(AnalysisPass):
    """Analysis pass for detecting unused functions."""

    def __init__(self, analyzer: "DependencyAnalyzer"):
        """Initialize with reference to analyzer."""
        self.analyzer = analyzer

    def name(self) -> str:
        """Return pass name."""
        return "Unused Functions Detection"

    def execute(
        self,
        nodes: Dict[str, Dict[str, Any]],
        edges: List[Tuple[str, str]],
        dep_graph: Dict[str, List[str]],
        rev_dep_graph: Dict[str, List[str]],
    ) -> Tuple[str, Any]:
        """Execute unused functions analysis."""
        result = self.analyzer._find_unused_functions(nodes, rev_dep_graph)
        return "unused_functions", result


class CriticalPathPass(AnalysisPass):
    """Analysis pass for finding critical path."""

    def __init__(self, analyzer: "DependencyAnalyzer"):
        """Initialize with reference to analyzer."""
        self.analyzer = analyzer

    def name(self) -> str:
        """Return pass name."""
        return "Critical Path Analysis"

    def execute(
        self,
        nodes: Dict[str, Dict[str, Any]],
        edges: List[Tuple[str, str]],
        dep_graph: Dict[str, List[str]],
        rev_dep_graph: Dict[str, List[str]],
    ) -> Tuple[str, Any]:
        """Execute critical path analysis."""
        result = self.analyzer._find_critical_path(nodes, edges)
        return "critical_path", result


class FunctionDepthPass(AnalysisPass):
    """Analysis pass for computing function depths."""

    def __init__(self, analyzer: "DependencyAnalyzer"):
        """Initialize with reference to analyzer."""
        self.analyzer = analyzer

    def name(self) -> str:
        """Return pass name."""
        return "Function Depth Computation"

    def execute(
        self,
        nodes: Dict[str, Dict[str, Any]],
        edges: List[Tuple[str, str]],
        dep_graph: Dict[str, List[str]],
        rev_dep_graph: Dict[str, List[str]],
    ) -> Tuple[str, Any]:
        """Execute function depth computation."""
        result = self.analyzer._compute_function_depth(dep_graph)
        return "function_depth", result


class CouplingMatrixPass(AnalysisPass):
    """Analysis pass for building coupling matrix."""

    def __init__(self, analyzer: "DependencyAnalyzer"):
        """Initialize with reference to analyzer."""
        self.analyzer = analyzer

    def name(self) -> str:
        """Return pass name."""
        return "Coupling Matrix Construction"

    def execute(
        self,
        nodes: Dict[str, Dict[str, Any]],
        edges: List[Tuple[str, str]],
        dep_graph: Dict[str, List[str]],
        rev_dep_graph: Dict[str, List[str]],
    ) -> Tuple[str, Any]:
        """Execute coupling matrix construction."""
        result = self.analyzer._build_coupling_matrix(dep_graph)
        return "coupling_matrix", result


def analyze_dependencies(
    graph: Dict[str, Any], config: Optional[AnalyzerConfig] = None
) -> DependencyAnalysis:
    """
    Analyze function dependencies.

    Args:
        graph: Execution trace graph with 'nodes' and 'edges' keys,
               or nested structure with 'data.nodes' and 'data.edges'
        config: Optional AnalyzerConfig for tuning behavior. Defaults to AnalyzerConfig()

    Returns:
        DependencyAnalysis dataclass with comprehensive dependency information

    Raises:
        TypeError: If graph is not a dict
        ValueError: If graph structure is invalid

    Example:
        >>> config = AnalyzerConfig(high_coupling_threshold=7)
        >>> result = analyze_dependencies(graph, config)
        >>> print(f"Found {len(result.circular_dependencies)} cycles")
    """
    analyzer = DependencyAnalyzer(config)
    return analyzer.analyze(graph)
