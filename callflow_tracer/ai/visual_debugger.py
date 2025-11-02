"""
Visual debugging module for CallFlow Tracer.

Interactive visual debugging of execution traces.
Provides step-through debugging, variable inspection, and call stack visualization.

Example:
    from callflow_tracer.ai import VisualDebugger
    
    debugger = VisualDebugger(graph)
    
    # Get call stack at specific point
    stack = debugger.get_call_stack(function_name='process_data')
    
    # Get variable values
    variables = debugger.get_variables(function_name='process_data')
    
    # Get execution timeline
    timeline = debugger.get_execution_timeline()
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class DebugFrame:
    """A debug frame in the call stack."""
    function_name: str
    module: str
    line_number: Optional[int]
    local_variables: Dict[str, Any]
    execution_time: float
    call_depth: int


@dataclass
class ExecutionEvent:
    """An execution event."""
    timestamp: str
    event_type: str  # 'call', 'return', 'exception'
    function_name: str
    module: str
    duration: float
    arguments: Optional[Dict[str, Any]]
    return_value: Optional[Any]
    exception: Optional[str]


class VisualDebugger:
    """Visual debugging of execution traces."""
    
    def __init__(self, graph: Dict[str, Any]):
        """
        Initialize visual debugger.
        
        Args:
            graph: Execution trace graph
        """
        self.graph = graph
        self.nodes = self._extract_nodes(graph)
        self.edges = self._extract_edges(graph)
        self.events = self._build_execution_events()
    
    def get_call_stack(self, function_name: Optional[str] = None,
                      depth: int = 10) -> List[Dict[str, Any]]:
        """
        Get call stack.
        
        Args:
            function_name: Optional function to focus on
            depth: Stack depth
            
        Returns:
            Call stack frames
        """
        stack = []
        
        # Build call stack from edges
        for edge in self.edges[:depth]:
            source, target = edge
            source_node = self.nodes.get(source, {})
            target_node = self.nodes.get(target, {})
            
            frame = {
                'function': target_node.get('name', 'unknown'),
                'module': target_node.get('module', 'unknown'),
                'called_from': source_node.get('name', 'unknown'),
                'execution_time': target_node.get('total_time', 0),
                'call_count': target_node.get('call_count', 0)
            }
            stack.append(frame)
        
        return stack
    
    def get_variables(self, function_name: str) -> Dict[str, Any]:
        """
        Get variables for a function.
        
        Args:
            function_name: Function name
            
        Returns:
            Variable values
        """
        # Find matching node
        for node_key, node in self.nodes.items():
            if function_name in node_key:
                return {
                    'function': node.get('name', 'unknown'),
                    'module': node.get('module', 'unknown'),
                    'execution_time': node.get('total_time', 0),
                    'call_count': node.get('call_count', 0),
                    'metadata': node.get('metadata', {})
                }
        
        return {}
    
    def get_execution_timeline(self) -> List[Dict[str, Any]]:
        """
        Get execution timeline.
        
        Returns:
            Timeline of execution events
        """
        timeline = []
        
        for i, event in enumerate(self.events[:50]):
            timeline.append({
                'sequence': i + 1,
                'event_type': event.event_type,
                'function': event.function_name,
                'module': event.module,
                'duration': event.duration,
                'timestamp': event.timestamp
            })
        
        return timeline
    
    def get_function_details(self, function_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a function.
        
        Args:
            function_name: Function name
            
        Returns:
            Function details
        """
        for node_key, node in self.nodes.items():
            if function_name in node_key:
                # Find callers and callees
                callers = []
                callees = []
                
                for source, target in self.edges:
                    if target == node_key:
                        callers.append(source)
                    elif source == node_key:
                        callees.append(target)
                
                return {
                    'name': node.get('name', 'unknown'),
                    'module': node.get('module', 'unknown'),
                    'total_time': node.get('total_time', 0),
                    'call_count': node.get('call_count', 0),
                    'avg_time': node.get('total_time', 0) / node.get('call_count', 1),
                    'callers': callers[:5],
                    'callees': callees[:5],
                    'call_graph': self._build_call_graph(node_key)
                }
        
        return {}
    
    def get_performance_hotspots(self) -> List[Dict[str, Any]]:
        """
        Get performance hotspots.
        
        Returns:
            List of hotspots
        """
        hotspots = []
        
        sorted_nodes = sorted(
            self.nodes.items(),
            key=lambda x: x[1].get('total_time', 0),
            reverse=True
        )
        
        for node_key, node in sorted_nodes[:10]:
            hotspots.append({
                'function': node.get('name', 'unknown'),
                'module': node.get('module', 'unknown'),
                'time': node.get('total_time', 0),
                'calls': node.get('call_count', 0),
                'severity': self._calculate_severity(node)
            })
        
        return hotspots
    
    def get_call_graph_visualization(self) -> Dict[str, Any]:
        """
        Get call graph for visualization.
        
        Returns:
            Call graph data
        """
        return {
            'nodes': [
                {
                    'id': node_key,
                    'label': node.get('name', 'unknown'),
                    'title': f"{node.get('module', 'unknown')}:{node.get('name', 'unknown')}",
                    'value': node.get('total_time', 0),
                    'color': self._get_node_color(node)
                }
                for node_key, node in self.nodes.items()
            ],
            'edges': [
                {
                    'from': source,
                    'to': target,
                    'arrows': 'to'
                }
                for source, target in self.edges
            ]
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
    
    def _extract_edges(self, graph: Dict[str, Any]) -> List[tuple]:
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
    
    def _build_execution_events(self) -> List[ExecutionEvent]:
        """Build execution events from graph."""
        events = []
        
        for node_key, node in self.nodes.items():
            event = ExecutionEvent(
                timestamp=datetime.now().isoformat(),
                event_type='call',
                function_name=node.get('name', 'unknown'),
                module=node.get('module', 'unknown'),
                duration=node.get('total_time', 0),
                arguments=None,
                return_value=None,
                exception=None
            )
            events.append(event)
        
        return events
    
    def _build_call_graph(self, node_key: str) -> Dict[str, Any]:
        """Build call graph for a specific node."""
        graph = {
            'node': node_key,
            'callers': [],
            'callees': []
        }
        
        for source, target in self.edges:
            if target == node_key:
                graph['callers'].append(source)
            elif source == node_key:
                graph['callees'].append(target)
        
        return graph
    
    def _calculate_severity(self, node: Dict[str, Any]) -> str:
        """Calculate severity for a node."""
        total_time = node.get('total_time', 0)
        
        if total_time > 1.0:
            return 'critical'
        elif total_time > 0.5:
            return 'high'
        elif total_time > 0.1:
            return 'medium'
        else:
            return 'low'
    
    def _get_node_color(self, node: Dict[str, Any]) -> str:
        """Get color for node based on severity."""
        severity = self._calculate_severity(node)
        
        colors = {
            'critical': '#FF0000',
            'high': '#FF6600',
            'medium': '#FFCC00',
            'low': '#00CC00'
        }
        
        return colors.get(severity, '#808080')


def create_visual_debugger(graph: Dict[str, Any]) -> VisualDebugger:
    """
    Create visual debugger instance.
    
    Args:
        graph: Execution trace graph
        
    Returns:
        VisualDebugger instance
    """
    return VisualDebugger(graph)
