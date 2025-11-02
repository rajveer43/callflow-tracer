"""
Smart instrumentation suggestions module for CallFlow Tracer.

Suggest where to add more instrumentation for better coverage.
Identifies high-value targets and missing coverage areas.

Example:
    from callflow_tracer.ai import suggest_instrumentation
    
    suggestions = suggest_instrumentation(graph)
    
    print(suggestions['missing_coverage'])
    print(suggestions['recommended_breakpoints'])
    print(suggestions['high_value_targets'])
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class InstrumentationSuggestion:
    """Instrumentation suggestion."""
    function_name: str
    module: str
    suggestion_type: str  # 'missing_coverage', 'high_value', 'bottleneck', etc
    reason: str
    priority: int  # 1-5
    estimated_impact: str  # 'high', 'medium', 'low'
    implementation_effort: str  # 'low', 'medium', 'high'


class InstrumentationSuggester:
    """Suggest instrumentation improvements."""
    
    def __init__(self):
        """Initialize instrumentation suggester."""
        pass
    
    def suggest(self, graph: Dict[str, Any],
               source_code: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Suggest instrumentation improvements.
        
        Args:
            graph: Execution trace graph
            source_code: Optional source code mapping
            
        Returns:
            Instrumentation suggestions
        """
        nodes = self._extract_nodes(graph)
        
        missing_coverage = []
        recommended_breakpoints = []
        high_value_targets = []
        
        # Analyze nodes
        for node_key, node in nodes.items():
            func_name = node.get('name', 'unknown')
            module = node.get('module', 'unknown')
            total_time = node.get('total_time', 0)
            call_count = node.get('call_count', 0)
            
            # High-value targets (slow or frequently called)
            if total_time > 0.5 or call_count > 50:
                suggestion = InstrumentationSuggestion(
                    function_name=func_name,
                    module=module,
                    suggestion_type='high_value',
                    reason=f"High impact: {total_time:.2f}s, {call_count} calls",
                    priority=5,
                    estimated_impact='high',
                    implementation_effort='low'
                )
                high_value_targets.append(suggestion)
            
            # Potential missing coverage (functions with no sub-calls)
            if call_count > 0 and total_time > 0.1:
                suggestion = InstrumentationSuggestion(
                    function_name=func_name,
                    module=module,
                    suggestion_type='missing_coverage',
                    reason=f"Complex function: {total_time:.2f}s execution time",
                    priority=3,
                    estimated_impact='medium',
                    implementation_effort='medium'
                )
                missing_coverage.append(suggestion)
        
        # Recommend breakpoints
        recommended_breakpoints = self._recommend_breakpoints(nodes)
        
        # Sort by priority
        high_value_targets.sort(key=lambda x: x.priority, reverse=True)
        missing_coverage.sort(key=lambda x: x.priority, reverse=True)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'missing_coverage': [asdict(s) for s in missing_coverage[:10]],
            'recommended_breakpoints': recommended_breakpoints,
            'high_value_targets': [asdict(s) for s in high_value_targets[:10]],
            'summary': {
                'total_functions': len(nodes),
                'high_value_targets_count': len(high_value_targets),
                'missing_coverage_count': len(missing_coverage),
                'recommended_breakpoints_count': len(recommended_breakpoints)
            }
        }
    
    def _recommend_breakpoints(self, nodes: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Recommend where to add breakpoints for debugging."""
        breakpoints = []
        
        # Find slow functions
        sorted_nodes = sorted(
            nodes.items(),
            key=lambda x: x[1].get('total_time', 0),
            reverse=True
        )
        
        for node_key, node in sorted_nodes[:5]:
            func_name = node.get('name', 'unknown')
            module = node.get('module', 'unknown')
            total_time = node.get('total_time', 0)
            
            breakpoints.append({
                'function': func_name,
                'module': module,
                'reason': f'Slow function: {total_time:.2f}s',
                'priority': 'high',
                'suggested_location': f'Entry and exit of {func_name}'
            })
        
        return breakpoints
    
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


def suggest_instrumentation(graph: Dict[str, Any],
                           source_code: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Suggest instrumentation improvements.
    
    Args:
        graph: Execution trace graph
        source_code: Optional source code
        
    Returns:
        Instrumentation suggestions
    """
    suggester = InstrumentationSuggester()
    return suggester.suggest(graph, source_code)
