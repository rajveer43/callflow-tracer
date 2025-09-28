"""
Flame graph visualization for callflow-tracer.

This module provides functionality to generate flame graphs from call trace data,
which are useful for identifying performance bottlenecks in your code.
"""

import json
import os
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import tempfile
import webbrowser

from .tracer import CallGraph, CallNode


def generate_flamegraph(call_graph: Union[CallGraph, dict], 
                      output_file: Optional[Union[str, Path]] = None,
                      width: int = 1200,
                      height: int = 800) -> Optional[str]:
    """
    Generate an interactive flame graph from call trace data.
    
    Args:
        call_graph: A CallGraph instance or dictionary containing the call graph data
        output_file: Path to save the HTML output. If None, a temporary file will be created.
        width: Width of the flame graph in pixels
        height: Height of the flame graph in pixels
        
    Returns:
        Path to the generated HTML file if output_file is None, otherwise None
    """
    # Convert CallGraph to dict if needed
    if isinstance(call_graph, CallGraph):
        graph_data = call_graph.to_dict()
    else:
        graph_data = call_graph
    
    # Process the call graph data into a flame graph format
    flame_data = _process_for_flamegraph(graph_data)
    
    # Generate the HTML content
    html_content = _generate_flamegraph_html(flame_data, width, height)
    
    # Write to file or return the HTML content
    if output_file is None:
        # Create a temporary file
        fd, temp_path = tempfile.mkstemp(suffix='.html', prefix='flamegraph_')
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(html_content)
        output_path = temp_path
        # Open in default web browser
        webbrowser.open(f'file://{temp_path}')
        return temp_path
    else:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return None


def _process_for_flamegraph(graph_data: dict) -> List[dict]:
    """
    Process call graph data into a format suitable for flame graph visualization.
    
    Args:
        graph_data: The call graph data from CallGraph.to_dict()
        
    Returns:
        List of dictionaries representing the flame graph data
    """
    flame_data = []
    
    # Validate input data
    if not graph_data or 'nodes' not in graph_data or 'edges' not in graph_data:
        print("Warning: Invalid graph data for flamegraph")
        return flame_data
    
    nodes_list = graph_data.get('nodes', [])
    edges_list = graph_data.get('edges', [])
    
    if not nodes_list:
        print("Warning: No nodes found in graph data")
        return flame_data
    
    # Map of node ID to its data
    nodes = {node['full_name']: node for node in nodes_list if 'full_name' in node}
    
    # Find root nodes (nodes that are not called by anyone)
    called_nodes = set()
    for edge in edges_list:
        if 'callee' in edge:
            called_nodes.add(edge['callee'])
    
    root_nodes = [node for node in nodes_list 
                 if node.get('full_name') and node['full_name'] not in called_nodes]
    
    # If no root nodes found, treat all nodes as potential roots
    if not root_nodes:
        root_nodes = nodes_list[:1]  # Take the first node as root
        print("Warning: No root nodes found, using first node as root")
    
    # Process each root node and its call tree
    for root in root_nodes:
        root_name = root.get('full_name', 'Unknown')
        total_time = root.get('total_time', 0)
        
        root_data = {
            'name': root_name,
            'value': max(total_time * 1000, 1),  # Convert to milliseconds, minimum 1ms
            'children': [],
            'total_time': total_time,
            'call_count': root.get('call_count', 1)
        }
        
        # Recursively build the call tree
        _build_flame_children(root_data, nodes, edges_list)
        flame_data.append(root_data)
    
    return flame_data


def _build_flame_children(node_data: dict, nodes: dict, edges: list) -> None:
    """
    Recursively build the flame graph data structure.
    
    Args:
        node_data: Current node's data dictionary
        nodes: Dictionary of all nodes by ID
        edges: List of all edges in the call graph
    """
    node_name = node_data['name']
    
    # Find all calls made by this node
    calls = [e for e in edges if e.get('caller') == node_name]
    
    for call in calls:
        callee_name = call.get('callee')
        if not callee_name:
            continue
            
        callee_node = nodes.get(callee_name)
        
        # Even if we don't have the callee node details, we can still show the call
        total_time = call.get('total_time', 0)
        call_count = call.get('call_count', 1)
        avg_time = call.get('avg_time', total_time / call_count if call_count > 0 else 0)
            
        child_data = {
            'name': callee_name,
            'value': max(total_time * 1000, 1),  # Convert to milliseconds, minimum 1ms
            'children': [],
            'call_count': call_count,
            'total_time': total_time,
            'avg_time': avg_time
        }
        
        # Recursively process children (prevent infinite recursion)
        if callee_name != node_name:  # Avoid self-recursion
            _build_flame_children(child_data, nodes, edges)
        
        node_data['children'].append(child_data)


def _generate_flamegraph_html(flame_data: List[dict], width: int, height: int) -> str:
    """
    Generate the HTML content for the flame graph.
    
    Args:
        flame_data: Processed flame graph data
        width: Width of the visualization in pixels
        height: Height of the visualization in pixels
        
    Returns:
        HTML content as a string
    """
    # Handle empty flame data
    if not flame_data:
        flame_data = [{
            'name': 'No Data',
            'value': 1,
            'children': []
        }]
    
    # Convert the data to JSON for the JavaScript
    json_data = json.dumps(flame_data, indent=2)
    chart_width = width - 40
    chart_height = height - 40
    
    # HTML template with embedded JavaScript
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>CallFlow Flame Graph</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        #chart {{
            width: {width}px;
            height: {height}px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        .tooltip {{
            position: absolute;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 14px;
            pointer-events: none;
            z-index: 1000;
        }}
        .controls {{
            margin: 20px auto;
            text-align: center;
        }}
        button {{
            background: #4CAF50;
            color: white;
            border: none;
            padding: 8px 16px;
            margin: 0 5px;
            border-radius: 4px;
            cursor: pointer;
        }}
        button:hover {{
            background: #45a049;
        }}
        .error-message {{
            text-align: center;
            color: #666;
            margin: 20px;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <h1 style="text-align: center;">CallFlow Flame Graph</h1>
    <div class="controls">
        <button onclick="zoomToFit()">Zoom to Fit</button>
        <button onclick="resetZoom()">Reset Zoom</button>
    </div>
    <div id="chart"></div>
    <div id="tooltip" class="tooltip" style="display: none;"></div>
    
    <!-- Load D3.js and D3 flame graph plugin -->
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/d3-flame-graph@4.1.3/dist/d3-flamegraph.min.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/d3-flame-graph@4.1.3/dist/d3-flamegraph.css">
    
    <script>
        try {{
            // Initialize flame graph
            const data = {json_data};
            
            // Check if we have valid data
            if (!data || data.length === 0) {{
                document.getElementById('chart').innerHTML = '<div class="error-message">No flame graph data available</div>';
                throw new Error('No flame graph data');
            }}
            
            const chart = flamegraph()
                .width({chart_width})
                .height({chart_height})
                .tooltip(function(d) {{
                    var tooltip = '<strong>' + (d.data.name || 'Unknown') + '</strong><br/>';
                    tooltip += 'Total Time: ' + (d.data.total_time ? d.data.total_time.toFixed(4) + 's' : 'N/A') + '<br/>';
                    tooltip += 'Avg Time: ' + (d.data.avg_time ? d.data.avg_time.toFixed(4) + 's' : 'N/A') + '<br/>';
                    tooltip += 'Calls: ' + (d.data.call_count || 1);
                    return tooltip;
                }})
                .sort((a, b) => b.value - a.value);
                
            // Create the chart
            var container = d3.select("#chart");
            
            // Use the first root node or create a wrapper if multiple roots
            var rootData = data.length === 1 ? data[0] : {{
                name: 'Root',
                value: data.reduce((sum, d) => sum + (d.value || 0), 0),
                children: data
            }};
            
            container.datum(rootData).call(chart);
            
            // Zoom to fit the entire graph
            window.zoomToFit = function() {{
                chart.resetZoom();
            }};
            
            // Reset zoom
            window.resetZoom = function() {{
                chart.resetZoom();
            }};
            
            // Handle window resize
            window.addEventListener('resize', function() {{
                var newWidth = document.getElementById('chart').clientWidth - 40;
                chart.width(newWidth);
                d3.select("#chart svg")
                    .attr("width", newWidth)
                    .attr("height", {chart_height});
                chart.resetZoom();
            }});
            
        }} catch (error) {{
            console.error('Error creating flame graph:', error);
            document.getElementById('chart').innerHTML = '<div class="error-message">Error creating flame graph: ' + error.message + '</div>';
        }}
    </script>
</body>
</html>"""
    
    return html
