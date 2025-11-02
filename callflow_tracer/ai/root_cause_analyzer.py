"""
Root Cause Analysis for CallFlow Tracer.

Uses graph algorithms + LLM to identify root causes of performance issues,
errors, and bottlenecks. Helps debug faster by tracing issues to their source.
"""

from typing import Dict, List, Optional, Any, Tuple, Set
from collections import defaultdict, deque
import statistics


class RootCauseAnalyzer:
    """
    Analyzes execution traces to identify root causes of issues.
    
    Uses graph algorithms to trace dependencies and LLM for intelligent analysis.
    """
    
    def __init__(self, provider=None):
        """
        Initialize root cause analyzer.
        
        Args:
            provider: Optional LLM provider for enhanced analysis
        """
        from .llm_provider import get_default_provider
        
        if provider is None:
            try:
                provider = get_default_provider()
            except ValueError:
                provider = None
        
        self.provider = provider
    
    def analyze(self, graph, issue_type: str = "performance", 
                threshold: Optional[float] = None) -> Dict[str, Any]:
        """
        Perform root cause analysis on a call graph.
        
        Args:
            graph: CallGraph to analyze
            issue_type: Type of issue ('performance', 'error', 'bottleneck')
            threshold: Performance threshold (e.g., time in seconds)
        
        Returns:
            Dict with root causes, impact analysis, and recommendations
        """
        # Extract graph data
        nodes = self._extract_nodes(graph)
        edges = self._extract_edges(graph)
        
        # Build dependency graph
        dependencies = self._build_dependency_graph(nodes, edges)
        
        # Identify problematic nodes
        if issue_type == "performance":
            problematic = self._identify_slow_nodes(nodes, threshold)
        elif issue_type == "error":
            problematic = self._identify_error_nodes(nodes)
        else:
            problematic = self._identify_bottleneck_nodes(nodes)
        
        # Trace root causes using graph algorithms
        root_causes = self._trace_root_causes(problematic, dependencies, nodes)
        
        # Calculate impact
        impact_analysis = self._analyze_impact(root_causes, dependencies, nodes)
        
        # Get LLM insights if available
        llm_insights = None
        if self.provider:
            llm_insights = self._get_llm_insights(root_causes, impact_analysis, nodes, issue_type)
        
        return {
            'issue_type': issue_type,
            'root_causes': root_causes,
            'impact_analysis': impact_analysis,
            'llm_insights': llm_insights,
            'total_issues': len(problematic),
            'total_root_causes': len(root_causes)
        }
    
    def _extract_nodes(self, graph) -> Dict[str, Dict[str, Any]]:
        """Extract node information from graph."""
        nodes = {}
        for node_id, node in graph.nodes.items():
            nodes[node_id] = {
                'id': node_id,
                'function': node.name,
                'module': node.module,
                'total_time': node.total_time,
                'self_time': node.total_time,  # CallNode doesn't have self_time, use total_time
                'call_count': node.call_count,
                'avg_time': node.total_time / node.call_count if node.call_count > 0 else 0,
                'has_error': hasattr(node, 'error') and node.error is not None
            }
        return nodes
    
    def _extract_edges(self, graph) -> List[Tuple[str, str]]:
        """Extract edges (caller -> callee relationships)."""
        edges = []
        for (caller, callee), edge in graph.edges.items():
            edges.append((caller, callee))
        return edges
    
    def _build_dependency_graph(self, nodes: Dict, edges: List[Tuple]) -> Dict[str, Dict]:
        """Build dependency graph with callers and callees."""
        dependencies = defaultdict(lambda: {'callers': set(), 'callees': set()})
        
        for caller_id, callee_id in edges:
            dependencies[callee_id]['callers'].add(caller_id)
            dependencies[caller_id]['callees'].add(callee_id)
        
        return dependencies
    
    def _identify_slow_nodes(self, nodes: Dict, threshold: Optional[float]) -> List[str]:
        """Identify slow nodes based on execution time."""
        if threshold is None:
            # Auto-calculate threshold (mean + 1 std dev)
            times = [n['total_time'] for n in nodes.values()]
            if len(times) > 1:
                mean = statistics.mean(times)
                stdev = statistics.stdev(times)
                threshold = mean + stdev
            else:
                threshold = 0.1  # Default 100ms
        
        slow_nodes = []
        for node_id, node in nodes.items():
            if node['total_time'] > threshold:
                slow_nodes.append(node_id)
        
        return slow_nodes
    
    def _identify_error_nodes(self, nodes: Dict) -> List[str]:
        """Identify nodes with errors."""
        return [node_id for node_id, node in nodes.items() if node['has_error']]
    
    def _identify_bottleneck_nodes(self, nodes: Dict) -> List[str]:
        """Identify bottleneck nodes (high self time or call count)."""
        bottlenecks = []
        
        # High self time
        times = [n['self_time'] for n in nodes.values()]
        if times:
            time_threshold = statistics.mean(times) + statistics.stdev(times) if len(times) > 1 else 0
            
            for node_id, node in nodes.items():
                if node['self_time'] > time_threshold:
                    bottlenecks.append(node_id)
        
        return bottlenecks
    
    def _trace_root_causes(self, problematic: List[str], dependencies: Dict, 
                          nodes: Dict) -> List[Dict[str, Any]]:
        """
        Trace root causes using graph traversal.
        
        A root cause is a node that:
        1. Is problematic itself OR causes problematic nodes
        2. Has no problematic callers (or minimal upstream issues)
        3. Has significant impact on downstream nodes
        """
        root_causes = []
        visited = set()
        
        for problem_node in problematic:
            if problem_node in visited:
                continue
            
            # Traverse up the call chain
            upstream_path = self._traverse_upstream(problem_node, dependencies, nodes, problematic)
            
            # Find the root (topmost problematic node in the chain)
            root = upstream_path[0] if upstream_path else problem_node
            
            if root not in visited:
                visited.add(root)
                
                # Calculate impact
                downstream_impact = self._calculate_downstream_impact(root, dependencies, nodes)
                
                root_causes.append({
                    'node_id': root,
                    'function': nodes[root]['function'],
                    'module': nodes[root]['module'],
                    'total_time': nodes[root]['total_time'],
                    'self_time': nodes[root]['self_time'],
                    'call_count': nodes[root]['call_count'],
                    'affected_nodes': downstream_impact['affected_count'],
                    'total_impact_time': downstream_impact['total_time'],
                    'upstream_path': upstream_path,
                    'confidence': self._calculate_confidence(root, upstream_path, downstream_impact)
                })
        
        # Sort by impact and confidence
        root_causes.sort(key=lambda x: (x['confidence'], x['total_impact_time']), reverse=True)
        
        return root_causes
    
    def _traverse_upstream(self, node_id: str, dependencies: Dict, 
                          nodes: Dict, problematic: List[str]) -> List[str]:
        """Traverse upstream to find root cause path."""
        path = []
        current = node_id
        visited = set()
        
        while current and current not in visited:
            visited.add(current)
            callers = dependencies[current]['callers']
            
            # Find problematic callers
            problematic_callers = [c for c in callers if c in problematic]
            
            if not problematic_callers:
                # No problematic callers, this is the root
                path.insert(0, current)
                break
            
            # Choose the slowest caller
            slowest_caller = max(problematic_callers, 
                               key=lambda c: nodes[c]['total_time'])
            path.insert(0, current)
            current = slowest_caller
        
        return path
    
    def _calculate_downstream_impact(self, node_id: str, dependencies: Dict, 
                                    nodes: Dict) -> Dict[str, Any]:
        """Calculate impact on downstream nodes using BFS."""
        affected = set()
        total_time = 0
        queue = deque([node_id])
        visited = set()
        
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            
            visited.add(current)
            affected.add(current)
            total_time += nodes[current]['total_time']
            
            # Add callees to queue
            for callee in dependencies[current]['callees']:
                if callee not in visited:
                    queue.append(callee)
        
        return {
            'affected_count': len(affected),
            'total_time': total_time,
            'affected_nodes': list(affected)
        }
    
    def _calculate_confidence(self, root: str, path: List[str], 
                             impact: Dict) -> float:
        """Calculate confidence score for root cause (0-1)."""
        confidence = 0.5  # Base confidence
        
        # Higher confidence if path is short (closer to root)
        if len(path) <= 2:
            confidence += 0.2
        
        # Higher confidence if impact is large
        if impact['affected_count'] > 5:
            confidence += 0.2
        
        # Higher confidence if it's at the top of call chain
        if len(path) == 1:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _analyze_impact(self, root_causes: List[Dict], dependencies: Dict, 
                       nodes: Dict) -> Dict[str, Any]:
        """Analyze overall impact of root causes."""
        total_affected = set()
        total_time_impact = 0
        
        for root in root_causes:
            impact = self._calculate_downstream_impact(root['node_id'], dependencies, nodes)
            total_affected.update(impact['affected_nodes'])
            total_time_impact += impact['total_time']
        
        return {
            'total_affected_functions': len(total_affected),
            'total_time_impact': total_time_impact,
            'affected_functions': list(total_affected),
            'impact_percentage': (len(total_affected) / len(nodes) * 100) if nodes else 0
        }
    
    def _get_llm_insights(self, root_causes: List[Dict], impact: Dict, 
                         nodes: Dict, issue_type: str) -> Optional[str]:
        """Get LLM insights about root causes."""
        if not self.provider:
            return None
        
        # Prepare context
        context = self._prepare_llm_context(root_causes, impact, nodes, issue_type)
        
        system_prompt = """You are an expert performance analyst helping developers debug their code.
Analyze the root cause analysis results and provide actionable insights."""
        
        prompt = f"""Root Cause Analysis Results:

Issue Type: {issue_type}

Top Root Causes:
{context['root_causes_text']}

Impact Analysis:
- Total affected functions: {impact['total_affected_functions']}
- Total time impact: {impact['total_time_impact']:.3f}s
- Impact percentage: {impact['impact_percentage']:.1f}%

Please provide:
1. A clear explanation of the root causes
2. Why these are the primary issues
3. Specific recommendations to fix each root cause
4. Priority order for addressing these issues

Be concise and actionable."""
        
        try:
            response = self.provider.generate(prompt, system_prompt, temperature=0.3)
            return response
        except Exception as e:
            return f"LLM analysis failed: {str(e)}"
    
    def _prepare_llm_context(self, root_causes: List[Dict], impact: Dict, 
                            nodes: Dict, issue_type: str) -> Dict[str, str]:
        """Prepare context for LLM analysis."""
        root_causes_text = ""
        for i, root in enumerate(root_causes[:5], 1):  # Top 5
            root_causes_text += f"\n{i}. {root['function']} (module: {root['module']})\n"
            root_causes_text += f"   - Total time: {root['total_time']:.3f}s\n"
            root_causes_text += f"   - Self time: {root['self_time']:.3f}s\n"
            root_causes_text += f"   - Call count: {root['call_count']}\n"
            root_causes_text += f"   - Affected nodes: {root['affected_nodes']}\n"
            root_causes_text += f"   - Confidence: {root['confidence']:.2f}\n"
        
        return {
            'root_causes_text': root_causes_text
        }


def analyze_root_cause(graph, issue_type: str = "performance", 
                       threshold: Optional[float] = None, 
                       provider=None) -> Dict[str, Any]:
    """
    Convenience function for root cause analysis.
    
    Args:
        graph: CallGraph to analyze
        issue_type: Type of issue ('performance', 'error', 'bottleneck')
        threshold: Optional threshold for identifying issues
        provider: Optional LLM provider
    
    Returns:
        Dict with root cause analysis results
    
    Example:
        >>> with trace_scope() as graph:
        ...     my_slow_function()
        >>> analysis = analyze_root_cause(graph, issue_type='performance')
        >>> print(analysis['llm_insights'])
    """
    analyzer = RootCauseAnalyzer(provider=provider)
    return analyzer.analyze(graph, issue_type=issue_type, threshold=threshold)
