"""
Dependency analysis module for CallFlow Tracer.

Analyze function dependencies and coupling.
Detects circular dependencies, tight coupling, and dead code.

Example:
    from callflow_tracer.ai import analyze_dependencies
    
    deps = analyze_dependencies(graph)
    
    print(deps['circular_dependencies'])
    print(deps['tight_coupling'])
    print(deps['unused_functions'])
    print(deps['critical_path'])
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict, deque


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


class DependencyAnalyzer:
    """Analyze function dependencies."""
    
    def __init__(self):
        """Initialize dependency analyzer."""
        pass
    
    def analyze(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze dependencies from execution trace.
        
        Args:
            graph: Execution trace graph
            
        Returns:
            Dependency analysis results
        """
        nodes = self._extract_nodes(graph)
        edges = self._extract_edges(graph)
        
        # Build dependency graphs
        dep_graph = self._build_dependency_graph(nodes, edges)
        rev_dep_graph = self._build_reverse_dependency_graph(dep_graph)
        
        # Analyze
        circular_deps = self._find_circular_dependencies(dep_graph)
        tight_coupling = self._find_tight_coupling(dep_graph, rev_dep_graph)
        unused_funcs = self._find_unused_functions(nodes, rev_dep_graph)
        critical_path = self._find_critical_path(nodes, edges)
        function_depth = self._compute_function_depth(dep_graph)
        coupling_matrix = self._build_coupling_matrix(dep_graph)
        
        analysis = DependencyAnalysis(
            timestamp=datetime.now().isoformat(),
            total_functions=len(nodes),
            circular_dependencies=circular_deps,
            tight_coupling=tight_coupling,
            unused_functions=unused_funcs,
            critical_path=critical_path,
            dependency_graph=dep_graph,
            reverse_dependency_graph=rev_dep_graph,
            function_depth=function_depth,
            coupling_matrix=coupling_matrix
        )
        
        return {
            'timestamp': analysis.timestamp,
            'total_functions': analysis.total_functions,
            'circular_dependencies': analysis.circular_dependencies,
            'tight_coupling': analysis.tight_coupling,
            'unused_functions': analysis.unused_functions,
            'critical_path': analysis.critical_path,
            'dependency_graph': analysis.dependency_graph,
            'reverse_dependency_graph': analysis.reverse_dependency_graph,
            'function_depth': analysis.function_depth,
            'coupling_matrix': analysis.coupling_matrix
        }
    
    def _extract_nodes(self, graph: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Extract nodes from graph."""
        nodes = {}
        
        if isinstance(graph, dict):
            if 'nodes' in graph:
                for node in graph['nodes']:
                    key = f"{node.get('module', 'unknown')}:{node.get('name', 'unknown')}"
                    nodes[key] = node
            elif 'data' in graph and 'nodes' in graph['data']:
                for node in graph['data']['nodes']:
                    key = f"{node.get('module', 'unknown')}:{node.get('name', 'unknown')}"
                    nodes[key] = node
        
        return nodes
    
    def _extract_edges(self, graph: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Extract edges from graph."""
        edges = []
        
        if isinstance(graph, dict):
            if 'edges' in graph:
                for edge in graph['edges']:
                    source = edge.get('from', '')
                    target = edge.get('to', '')
                    if source and target:
                        edges.append((source, target))
            elif 'data' in graph and 'edges' in graph['data']:
                for edge in graph['data']['edges']:
                    source = edge.get('from', '')
                    target = edge.get('to', '')
                    if source and target:
                        edges.append((source, target))
        
        return edges
    
    def _build_dependency_graph(self, nodes: Dict[str, Dict[str, Any]],
                               edges: List[Tuple[str, str]]) -> Dict[str, List[str]]:
        """Build dependency graph."""
        graph = {node_key: [] for node_key in nodes.keys()}
        
        for source, target in edges:
            if source in graph:
                if target not in graph[source]:
                    graph[source].append(target)
        
        return graph
    
    def _build_reverse_dependency_graph(self, dep_graph: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Build reverse dependency graph."""
        rev_graph = defaultdict(list)
        
        for source, targets in dep_graph.items():
            for target in targets:
                if target not in rev_graph:
                    rev_graph[target] = []
                rev_graph[target].append(source)
        
        return dict(rev_graph)
    
    def _find_circular_dependencies(self, dep_graph: Dict[str, List[str]]) -> List[List[str]]:
        """Find circular dependencies using DFS."""
        circular = []
        visited = set()
        rec_stack = set()
        
        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in dep_graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path.copy())
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    if cycle not in circular:
                        circular.append(cycle)
            
            rec_stack.remove(node)
        
        for node in dep_graph:
            if node not in visited:
                dfs(node, [])
        
        return circular
    
    def _find_tight_coupling(self, dep_graph: Dict[str, List[str]],
                            rev_dep_graph: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Find tightly coupled functions."""
        tight_couplings = []
        
        # Find functions that depend on many others
        for func, dependencies in dep_graph.items():
            if len(dependencies) > 5:
                tight_couplings.append({
                    'function': func,
                    'type': 'high_outgoing_coupling',
                    'coupled_with': dependencies[:5],
                    'coupling_count': len(dependencies),
                    'severity': 'high' if len(dependencies) > 10 else 'medium'
                })
        
        # Find functions that are depended on by many others
        for func, dependents in rev_dep_graph.items():
            if len(dependents) > 5:
                tight_couplings.append({
                    'function': func,
                    'type': 'high_incoming_coupling',
                    'depended_by': dependents[:5],
                    'coupling_count': len(dependents),
                    'severity': 'high' if len(dependents) > 10 else 'medium'
                })
        
        return tight_couplings
    
    def _find_unused_functions(self, nodes: Dict[str, Dict[str, Any]],
                              rev_dep_graph: Dict[str, List[str]]) -> List[str]:
        """Find unused functions."""
        unused = []
        
        for node_key in nodes.keys():
            if node_key not in rev_dep_graph or len(rev_dep_graph[node_key]) == 0:
                # Check if it's a root function (entry point)
                if not self._is_entry_point(node_key):
                    unused.append(node_key)
        
        return unused
    
    def _is_entry_point(self, func_key: str) -> bool:
        """Check if function is an entry point."""
        # Heuristic: main, __main__, test_, or functions in __main__ module
        return (
            'main' in func_key.lower() or
            'test_' in func_key.lower() or
            '__main__' in func_key
        )
    
    def _find_critical_path(self, nodes: Dict[str, Dict[str, Any]],
                           edges: List[Tuple[str, str]]) -> List[str]:
        """Find critical path (longest execution path)."""
        # Build graph with weights
        weighted_graph = defaultdict(list)
        
        for source, target in edges:
            weight = nodes.get(target, {}).get('total_time', 0)
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
            dfs(start_node, [start_node], nodes.get(start_node, {}).get('total_time', 0))
        
        return max_path
    
    def _compute_function_depth(self, dep_graph: Dict[str, List[str]]) -> Dict[str, int]:
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
                    max_depth = max(max_depth, compute_depth(dependency, visited.copy()))
                depth[node] = max_depth + 1
            
            return depth[node]
        
        for node in dep_graph:
            compute_depth(node)
        
        return depth
    
    def _build_coupling_matrix(self, dep_graph: Dict[str, List[str]]) -> Dict[str, Dict[str, int]]:
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


def analyze_dependencies(graph: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze function dependencies.
    
    Args:
        graph: Execution trace graph
        
    Returns:
        Dependency analysis results
    """
    analyzer = DependencyAnalyzer()
    return analyzer.analyze(graph)
