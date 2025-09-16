"""
Export functionality for callflow-tracer.

This module handles exporting call graphs to various formats including JSON and HTML.
"""

import json
import os
from pathlib import Path
from typing import Union, Optional
from .tracer import CallGraph


def export_json(graph: CallGraph, output_path: Union[str, Path]) -> None:
    """
    Export call graph to JSON format.
    
    Args:
        graph: The CallGraph instance to export
        output_path: Path where to save the JSON file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(graph.to_dict(), f, indent=2, ensure_ascii=False)


def export_html(graph: CallGraph, output_path: Union[str, Path], 
                title: str = "Call Flow Graph", 
                include_vis_js: bool = True) -> None:
    """
    Export call graph to interactive HTML format.
    
    Args:
        graph: The CallGraph instance to export
        output_path: Path where to save the HTML file
        title: Title for the HTML page
        include_vis_js: Whether to include vis.js from CDN (requires internet)
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert graph to JSON
    graph_data = graph.to_dict()
    
    # Generate HTML content
    html_content = _generate_html(graph_data, title, include_vis_js)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def export_graph(graph: CallGraph, output_path: Union[str, Path], 
                format: str = "auto", **kwargs) -> None:
    """
    Export call graph to specified format.
    
    Args:
        graph: The CallGraph instance to export
        output_path: Path where to save the file
        format: Export format ("json", "html", or "auto" to detect from extension)
        **kwargs: Additional arguments passed to specific exporters
    """
    output_path = Path(output_path)
    
    if format == "auto":
        format = output_path.suffix.lower().lstrip('.')
    
    if format == "json":
        export_json(graph, output_path)
    elif format == "html":
        export_html(graph, output_path, **kwargs)
    else:
        raise ValueError(f"Unsupported format: {format}. Supported formats: json, html")


def _generate_html(graph_data: dict, title: str, include_vis_js: bool) -> str:
    """Generate HTML content with embedded JavaScript for visualization."""
    
    # Prepare nodes and edges for vis.js
    nodes = []
    edges = []
    
    # Process nodes
    for node in graph_data['nodes']:
        nodes.append({
            'id': node['full_name'],
            'label': node['name'],
            'title': f"Module: {node['module']}\\nCalls: {node['call_count']}\\nTotal Time: {node['total_time']:.3f}s\\nAvg Time: {node['avg_time']:.3f}s",
            'group': node['module'] or 'main',
            'value': node['call_count'],
            'color': _get_node_color(node['avg_time'])
        })
    
    # Process edges
    for edge in graph_data['edges']:
        edges.append({
            'from': edge['caller'],
            'to': edge['callee'],
            'label': f"{edge['call_count']} calls",
            'title': f"Calls: {edge['call_count']}\\nTotal Time: {edge['total_time']:.3f}s\\nAvg Time: {edge['avg_time']:.3f}s",
            'width': min(max(1, edge['call_count'] / 5), 10),  # Scale width based on call count
            'color': _get_edge_color(edge['avg_time'])
        })
    
    # Generate the HTML template
    vis_js_cdn = "https://unpkg.com/vis-network/standalone/umd/vis-network.min.js" if include_vis_js else ""
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2em;
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            padding: 15px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }}
        .stat {{
            text-align: center;
        }}
        .stat-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            font-size: 0.9em;
            color: #6c757d;
        }}
        #network {{
            height: 600px;
            border: 1px solid #dee2e6;
        }}
        .controls {{
            padding: 15px;
            background: #f8f9fa;
            border-top: 1px solid #dee2e6;
        }}
        .control-group {{
            margin: 10px 0;
        }}
        .control-group label {{
            display: inline-block;
            width: 120px;
            font-weight: bold;
        }}
        .control-group select, .control-group input {{
            padding: 5px;
            border: 1px solid #ced4da;
            border-radius: 4px;
        }}
        .legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-top: 10px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 3px;
        }}
    </style>
    {f'<script type="text/javascript" src="{vis_js_cdn}"></script>' if include_vis_js else ''}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <p>Interactive Call Flow Visualization</p>
        </div>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{graph_data['metadata']['total_nodes']}</div>
                <div class="stat-label">Functions</div>
            </div>
            <div class="stat">
                <div class="stat-value">{graph_data['metadata']['total_edges']}</div>
                <div class="stat-label">Call Relationships</div>
            </div>
            <div class="stat">
                <div class="stat-value">{graph_data['metadata']['duration']:.3f}s</div>
                <div class="stat-label">Total Duration</div>
            </div>
        </div>
        
        <div id="network"></div>
        
        <div class="controls">
            <div class="control-group">
                <label for="physics">Physics:</label>
                <select id="physics">
                    <option value="true">Enabled</option>
                    <option value="false">Disabled</option>
                </select>
            </div>
            <div class="control-group">
                <label for="layout">Layout:</label>
                <select id="layout">
                    <option value="hierarchical">Hierarchical</option>
                    <option value="force">Force-directed</option>
                </select>
            </div>
            <div class="control-group">
                <label for="filter">Filter by module:</label>
                <select id="filter">
                    <option value="">All modules</option>
                </select>
            </div>
            
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-color" style="background-color: #ff6b6b;"></div>
                    <span>Slow functions (>100ms avg)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: #4ecdc4;"></div>
                    <span>Medium functions (10-100ms avg)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: #45b7d1;"></div>
                    <span>Fast functions (<10ms avg)</span>
                </div>
            </div>
        </div>
    </div>

    <script type="text/javascript">
        // Graph data
        const nodes = {json.dumps(nodes, indent=2)};
        const edges = {json.dumps(edges, indent=2)};
        
        // Create network
        const container = document.getElementById('network');
        const data = {{ nodes: nodes, edges: edges }};
        
        const options = {{
            nodes: {{
                shape: 'dot',
                font: {{ size: 12, color: '#333' }},
                borderWidth: 2,
                shadow: true
            }},
            edges: {{
                font: {{ size: 10, color: '#666' }},
                arrows: {{ to: {{ enabled: true, scaleFactor: 0.5 }} }},
                smooth: {{ type: 'continuous' }}
            }},
            physics: {{
                enabled: true,
                stabilization: {{ iterations: 100 }},
                barnesHut: {{
                    gravitationalConstant: -2000,
                    centralGravity: 0.1,
                    springLength: 100,
                    springConstant: 0.04
                }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 200
            }}
        }};
        
        const network = new vis.Network(container, data, options);
        
        // Control handlers
        document.getElementById('physics').addEventListener('change', function() {{
            options.physics.enabled = this.value === 'true';
            network.setOptions(options);
        }});
        
        document.getElementById('layout').addEventListener('change', function() {{
            if (this.value === 'hierarchical') {{
                options.layout = {{
                    hierarchical: {{
                        direction: 'UD',
                        sortMethod: 'directed'
                    }}
                }};
            }} else {{
                options.layout = {{}};
            }}
            network.setOptions(options);
        }});
        
        // Populate module filter
        const modules = [...new Set(nodes.map(n => n.group))].filter(m => m);
        const filterSelect = document.getElementById('filter');
        modules.forEach(module => {{
            const option = document.createElement('option');
            option.value = module;
            option.textContent = module;
            filterSelect.appendChild(option);
        }});
        
        // Module filter handler
        document.getElementById('filter').addEventListener('change', function() {{
            const selectedModule = this.value;
            const filteredNodes = nodes.filter(node => 
                !selectedModule || node.group === selectedModule
            );
            const filteredEdges = edges.filter(edge => {{
                const fromNode = nodes.find(n => n.id === edge.from);
                const toNode = nodes.find(n => n.id === edge.to);
                return (!selectedModule || (fromNode && fromNode.group === selectedModule)) &&
                       (!selectedModule || (toNode && toNode.group === selectedModule));
            }});
            
            const filteredData = {{ nodes: filteredNodes, edges: filteredEdges }};
            network.setData(filteredData);
        }});
        
        // Add some styling on load
        network.on("stabilizationIterationsDone", function() {{
            network.setOptions({{ physics: false }});
        }});
    </script>
</body>
</html>"""
    
    return html_template


def _get_node_color(avg_time: float) -> str:
    """Get color for node based on average execution time."""
    if avg_time > 0.1:  # > 100ms
        return "#ff6b6b"  # Red
    elif avg_time > 0.01:  # 10-100ms
        return "#4ecdc4"  # Teal
    else:  # < 10ms
        return "#45b7d1"  # Blue


def _get_edge_color(avg_time: float) -> str:
    """Get color for edge based on average execution time."""
    if avg_time > 0.1:  # > 100ms
        return "#ff6b6b"  # Red
    elif avg_time > 0.01:  # 10-100ms
        return "#4ecdc4"  # Teal
    else:  # < 10ms
        return "#45b7d1"  # Blue
