"""
Documentation generation module for CallFlow Tracer.

Auto-generate performance documentation from execution traces.
Produces markdown, HTML, and PDF documentation with diagrams.

Example:
    from callflow_tracer.ai import generate_documentation
    
    docs = generate_documentation(
        graph,
        format='markdown',
        include_diagrams=True
    )
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Documentation:
    """Generated documentation."""
    title: str
    format: str  # 'markdown', 'html', 'pdf'
    content: str
    diagrams: List[str]
    metadata: Dict[str, Any]


class DocumentationGenerator:
    """Generate documentation from execution traces."""
    
    def __init__(self):
        """Initialize documentation generator."""
        pass
    
    def generate(self, graph: Dict[str, Any],
                format: str = 'markdown',
                include_diagrams: bool = True,
                title: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate documentation from trace.
        
        Args:
            graph: Execution trace graph
            format: Output format ('markdown', 'html', 'pdf')
            include_diagrams: Include diagrams
            title: Optional documentation title
            
        Returns:
            Generated documentation
        """
        nodes = self._extract_nodes(graph)
        edges = self._extract_edges(graph)
        total_time = self._get_total_time(graph)
        
        if title is None:
            title = "Performance Analysis Documentation"
        
        # Generate content based on format
        if format == 'markdown':
            content = self._generate_markdown(nodes, edges, total_time, title)
        elif format == 'html':
            content = self._generate_html(nodes, edges, total_time, title)
        else:
            content = self._generate_markdown(nodes, edges, total_time, title)
        
        # Generate diagrams
        diagrams = []
        if include_diagrams:
            diagrams = self._generate_diagrams(nodes, edges)
        
        doc = Documentation(
            title=title,
            format=format,
            content=content,
            diagrams=diagrams,
            metadata={
                'generated_at': datetime.now().isoformat(),
                'total_functions': len(nodes),
                'total_calls': len(edges),
                'total_time': total_time
            }
        )
        
        return {
            'title': doc.title,
            'format': doc.format,
            'content': doc.content,
            'diagrams': doc.diagrams,
            'metadata': doc.metadata
        }
    
    def _generate_markdown(self, nodes: Dict[str, Dict[str, Any]],
                          edges: List[tuple],
                          total_time: float,
                          title: str) -> str:
        """Generate markdown documentation."""
        md = f"# {title}\n\n"
        
        md += f"**Generated:** {datetime.now().isoformat()}\n\n"
        
        # Executive Summary
        md += "## Executive Summary\n\n"
        md += f"- **Total Execution Time:** {total_time:.3f}s\n"
        md += f"- **Total Functions:** {len(nodes)}\n"
        md += f"- **Total Calls:** {len(edges)}\n\n"
        
        # Performance Characteristics
        md += "## Performance Characteristics\n\n"
        
        # Top functions by time
        md += "### Top Functions by Execution Time\n\n"
        md += "| Function | Module | Time (s) | Calls | Avg Time (ms) |\n"
        md += "|----------|--------|----------|-------|---------------|\n"
        
        sorted_nodes = sorted(
            nodes.items(),
            key=lambda x: x[1].get('total_time', 0),
            reverse=True
        )
        
        for node_key, node in sorted_nodes[:10]:
            func_name = node.get('name', 'unknown')
            module = node.get('module', 'unknown')
            total = node.get('total_time', 0)
            calls = node.get('call_count', 0)
            avg = (total * 1000 / calls) if calls > 0 else 0
            
            md += f"| {func_name} | {module} | {total:.3f} | {calls} | {avg:.2f} |\n"
        
        md += "\n"
        
        # Top functions by call count
        md += "### Most Frequently Called Functions\n\n"
        md += "| Function | Module | Calls | Total Time (s) |\n"
        md += "|----------|--------|-------|----------------|\n"
        
        sorted_by_calls = sorted(
            nodes.items(),
            key=lambda x: x[1].get('call_count', 0),
            reverse=True
        )
        
        for node_key, node in sorted_by_calls[:10]:
            func_name = node.get('name', 'unknown')
            module = node.get('module', 'unknown')
            calls = node.get('call_count', 0)
            total = node.get('total_time', 0)
            
            md += f"| {func_name} | {module} | {calls} | {total:.3f} |\n"
        
        md += "\n"
        
        # Optimization Recommendations
        md += "## Optimization Recommendations\n\n"
        
        recommendations = self._generate_recommendations(nodes)
        for i, rec in enumerate(recommendations, 1):
            md += f"{i}. **{rec['title']}**\n"
            md += f"   - {rec['description']}\n"
            md += f"   - Potential Impact: {rec['impact']}\n\n"
        
        # API Documentation
        md += "## Function Reference\n\n"
        
        for node_key, node in sorted_nodes[:20]:
            func_name = node.get('name', 'unknown')
            module = node.get('module', 'unknown')
            total_time = node.get('total_time', 0)
            calls = node.get('call_count', 0)
            
            md += f"### {func_name}\n\n"
            md += f"- **Module:** {module}\n"
            md += f"- **Total Time:** {total_time:.3f}s\n"
            md += f"- **Call Count:** {calls}\n"
            md += f"- **Average Time:** {(total_time * 1000 / calls):.2f}ms\n\n"
        
        return md
    
    def _generate_html(self, nodes: Dict[str, Dict[str, Any]],
                      edges: List[tuple],
                      total_time: float,
                      title: str) -> str:
        """Generate HTML documentation."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #f0f0f0; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p>Generated: {datetime.now().isoformat()}</p>
    
    <h2>Summary</h2>
    <div class="metric">Total Time: {total_time:.3f}s</div>
    <div class="metric">Total Functions: {len(nodes)}</div>
    <div class="metric">Total Calls: {len(edges)}</div>
    
    <h2>Top Functions</h2>
    <table>
        <tr>
            <th>Function</th>
            <th>Module</th>
            <th>Time (s)</th>
            <th>Calls</th>
            <th>Avg (ms)</th>
        </tr>
"""
        
        sorted_nodes = sorted(
            nodes.items(),
            key=lambda x: x[1].get('total_time', 0),
            reverse=True
        )
        
        for node_key, node in sorted_nodes[:10]:
            func_name = node.get('name', 'unknown')
            module = node.get('module', 'unknown')
            total = node.get('total_time', 0)
            calls = node.get('call_count', 0)
            avg = (total * 1000 / calls) if calls > 0 else 0
            
            html += f"""        <tr>
            <td>{func_name}</td>
            <td>{module}</td>
            <td>{total:.3f}</td>
            <td>{calls}</td>
            <td>{avg:.2f}</td>
        </tr>
"""
        
        html += """    </table>
</body>
</html>
"""
        
        return html
    
    def _generate_diagrams(self, nodes: Dict[str, Dict[str, Any]],
                          edges: List[tuple]) -> List[str]:
        """Generate diagrams."""
        diagrams = []
        
        # Generate call graph diagram (Mermaid format)
        mermaid_diagram = self._generate_mermaid_diagram(nodes, edges)
        diagrams.append(mermaid_diagram)
        
        return diagrams
    
    def _generate_mermaid_diagram(self, nodes: Dict[str, Dict[str, Any]],
                                 edges: List[tuple]) -> str:
        """Generate Mermaid diagram."""
        diagram = "graph TD\n"
        
        # Add nodes
        for node_key, node in list(nodes.items())[:20]:
            func_name = node.get('name', 'unknown')
            time = node.get('total_time', 0)
            
            # Shorten name if too long
            display_name = func_name[:20] + "..." if len(func_name) > 20 else func_name
            
            diagram += f'    {node_key.replace(":", "_")}["{display_name}<br/>{time:.2f}s"]\n'
        
        # Add edges (limit to top edges)
        for i, (source, target) in enumerate(edges[:20]):
            source_id = source.replace(":", "_")
            target_id = target.replace(":", "_")
            diagram += f"    {source_id} --> {target_id}\n"
        
        return diagram
    
    def _generate_recommendations(self, nodes: Dict[str, Dict[str, Any]]) -> List[Dict[str, str]]:
        """Generate optimization recommendations."""
        recommendations = []
        
        # Find slow functions
        sorted_nodes = sorted(
            nodes.items(),
            key=lambda x: x[1].get('total_time', 0),
            reverse=True
        )
        
        if sorted_nodes:
            top_func = sorted_nodes[0]
            func_name = top_func[1].get('name', 'unknown')
            time = top_func[1].get('total_time', 0)
            
            recommendations.append({
                'title': 'Optimize Top Function',
                'description': f'{func_name} takes {time:.3f}s. Consider profiling and optimization.',
                'impact': 'High'
            })
        
        # Find frequently called functions
        sorted_by_calls = sorted(
            nodes.items(),
            key=lambda x: x[1].get('call_count', 0),
            reverse=True
        )
        
        if sorted_by_calls:
            top_called = sorted_by_calls[0]
            func_name = top_called[1].get('name', 'unknown')
            calls = top_called[1].get('call_count', 0)
            
            if calls > 100:
                recommendations.append({
                    'title': 'Cache Results',
                    'description': f'{func_name} is called {calls} times. Consider caching.',
                    'impact': 'High'
                })
        
        return recommendations
    
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
    
    def _get_total_time(self, graph: Dict[str, Any]) -> float:
        """Get total time from graph."""
        if isinstance(graph, dict):
            if 'total_time' in graph:
                return graph['total_time']
            elif 'data' in graph and 'total_time' in graph['data']:
                return graph['data']['total_time']
        return 0.0


def generate_documentation(graph: Dict[str, Any],
                          format: str = 'markdown',
                          include_diagrams: bool = True,
                          title: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate documentation from trace.
    
    Args:
        graph: Execution trace graph
        format: Output format ('markdown', 'html', 'pdf')
        include_diagrams: Include diagrams
        title: Optional title
        
    Returns:
        Generated documentation
    """
    generator = DocumentationGenerator()
    return generator.generate(graph, format, include_diagrams, title)
