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
                include_vis_js: bool = True,
                profiling_stats: Optional[dict] = None,
                layout: str = "hierarchical") -> None:
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
    html_content = _generate_html(graph_data, title, include_vis_js, profiling_stats, layout)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def export_html_3d(graph: CallGraph, output_path: Union[str, Path],
                   title: str = "Call Flow Graph 3D",
                   profiling_stats: Optional[dict] = None) -> None:
    """
    Export call graph to interactive 3D HTML format using Three.js.
    
    Args:
        graph: The CallGraph instance to export
        output_path: Path where to save the HTML file
        title: Title for the HTML page
        profiling_stats: Optional profiling statistics
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert graph to JSON
    graph_data = graph.to_dict()
    
    # Generate 3D HTML content
    html_content = _generate_html_3d(graph_data, title, profiling_stats)
    
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
    elif format == "html_3d":
        export_html_3d(graph, output_path, **kwargs)
    else:
        raise ValueError(f"Unsupported format: {format}. Supported formats: json, html, html_3d")


def _analyze_cpu_profile(cpu_profile_text: str) -> dict:
    """Analyze CPU profile data and extract key metrics with health indicators."""
    if not cpu_profile_text:
        return {
            'total_time': 0.0,
            'total_calls': 0,
            'top_functions': [],
            'health_indicators': {
                'execution_time': {'status': 'good', 'message': 'N/A'},
                'call_efficiency': {'status': 'good', 'message': 'N/A'},
                'hot_spots': {'status': 'good', 'message': 'N/A'}
            }
        }
    
    metrics = {
        'total_time': 0.0,
        'total_calls': 0,
        'primitive_calls': 0,
        'top_functions': [],
        'health_indicators': {}
    }
    
    try:
        lines = cpu_profile_text.strip().split('\n')
        
        # Parse the header line for summary stats
        for line in lines[:10]:  # Check first 10 lines for summary
            if 'function calls' in line and 'primitive calls' in line:
                # Example: "125 function calls (120 primitive calls) in 0.002 seconds"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'function':
                        metrics['total_calls'] = int(parts[i-1])
                    elif part == 'primitive':
                        metrics['primitive_calls'] = int(parts[i-1].strip('('))
                    elif part == 'in' and i+1 < len(parts):
                        try:
                            metrics['total_time'] = float(parts[i+1])
                        except ValueError:
                            pass
        
        # Parse function details (skip header lines)
        data_started = False
        function_count = 0
        
        for line in lines:
            if 'ncalls' in line and 'tottime' in line:
                data_started = True
                continue
            
            if data_started and line.strip() and not line.startswith(' ') and function_count < 5:
                # Parse function line: ncalls  tottime  percall  cumtime  percall filename:lineno(function)
                parts = line.split()
                if len(parts) >= 6:
                    try:
                        ncalls = parts[0]
                        tottime = float(parts[1])
                        percall_tot = float(parts[2]) if parts[2] != '0.000' else 0.0
                        cumtime = float(parts[3])
                        percall_cum = float(parts[4]) if parts[4] != '0.000' else 0.0
                        filename_func = ' '.join(parts[5:])
                        
                        metrics['top_functions'].append({
                            'ncalls': ncalls,
                            'tottime': tottime,
                            'percall_tot': percall_tot,
                            'cumtime': cumtime,
                            'percall_cum': percall_cum,
                            'function': filename_func
                        })
                        function_count += 1
                    except (ValueError, IndexError):
                        continue
        
        # Calculate health indicators
        metrics['health_indicators'] = _calculate_health_indicators(metrics)
        
    except Exception as e:
        # If parsing fails, return basic structure
        metrics['parse_error'] = str(e)
        metrics['health_indicators'] = {
            'execution_time': {'status': 'good', 'message': 'Parse Error'},
            'call_efficiency': {'status': 'good', 'message': 'Parse Error'},
            'hot_spots': {'status': 'good', 'message': 'Parse Error'}
        }
    
    return metrics


def _calculate_health_indicators(metrics: dict) -> dict:
    """Calculate health indicators based on CPU profiling metrics."""
    indicators = {}
    
    total_time = metrics.get('total_time', 0)
    total_calls = metrics.get('total_calls', 0)
    primitive_calls = metrics.get('primitive_calls', 0)
    top_functions = metrics.get('top_functions', [])
    
    # Total execution time health
    if total_time < 0.1:
        indicators['execution_time'] = {'status': 'excellent', 'message': '🟢 Very Fast'}
    elif total_time < 0.5:
        indicators['execution_time'] = {'status': 'good', 'message': '🔵 Good'}
    elif total_time < 2.0:
        indicators['execution_time'] = {'status': 'warning', 'message': '🟡 Moderate'}
    else:
        indicators['execution_time'] = {'status': 'poor', 'message': '🔴 Slow'}
    
    # Function call efficiency
    if total_calls > 0:
        recursive_ratio = (total_calls - primitive_calls) / total_calls
        if recursive_ratio < 0.1:
            indicators['call_efficiency'] = {'status': 'excellent', 'message': '🟢 Efficient'}
        elif recursive_ratio < 0.3:
            indicators['call_efficiency'] = {'status': 'good', 'message': '🔵 Good'}
        elif recursive_ratio < 0.6:
            indicators['call_efficiency'] = {'status': 'warning', 'message': '🟡 Some Recursion'}
        else:
            indicators['call_efficiency'] = {'status': 'poor', 'message': '🔴 High Recursion'}
    else:
        indicators['call_efficiency'] = {'status': 'good', 'message': '🔵 No Data'}
    
    # Hot spot analysis
    if top_functions:
        hottest_function = top_functions[0]
        hottest_time_ratio = hottest_function['tottime'] / total_time if total_time > 0 else 0
        
        if hottest_time_ratio < 0.2:
            indicators['hot_spots'] = {'status': 'excellent', 'message': '🟢 Well Distributed'}
        elif hottest_time_ratio < 0.4:
            indicators['hot_spots'] = {'status': 'good', 'message': '🔵 Balanced'}
        elif hottest_time_ratio < 0.7:
            indicators['hot_spots'] = {'status': 'warning', 'message': '🟡 Some Hot Spots'}
        else:
            indicators['hot_spots'] = {'status': 'poor', 'message': '🔴 Major Bottleneck'}
    else:
        indicators['hot_spots'] = {'status': 'good', 'message': '🔵 No Data'}
    
    return indicators


# def _generate_html(graph_data: dict, title: str, include_vis_js: bool, 
#                   profiling_stats: Optional[dict], layout: str = "hierarchical") -> str:
#     """Generate HTML content with embedded JavaScript for visualization.
    
#     This function uses Python's format() method with double braces for JavaScript code to avoid
#     conflicts between Python string formatting and JavaScript object literals.
#     """
    
#     # Prepare nodes and edges for vis.js
#     nodes = []
#     edges = []
    
#     # Process nodes
#     for node in graph_data['nodes']:
#         nodes.append({
#             'id': node['full_name'],
#             'label': node['name'],
#             'title': f"Module: {node['module']}\\nCalls: {node['call_count']}\\nTotal Time: {node['total_time']:.3f}s\\nAvg Time: {node['avg_time']:.3f}s",
#             'group': node['module'] or 'main',
#             'value': node['call_count'],
#             'color': _get_node_color(node['avg_time']),
#             'module': node['module'],  # Add module for JS filtering
#             'shape': 'circle',  # Make nodes circular
#             'total_time': node['total_time'],
#         })
    
#     # Process edges
#     for edge in graph_data['edges']:
#         edges.append({
#             'from': edge['caller'],
#             'to': edge['callee'],
#             'label': f"{edge['call_count']} calls",
#             'title': f"Calls: {edge['call_count']}\\nTotal Time: {edge['total_time']:.3f}s\\nAvg Time: {edge['avg_time']:.3f}s",
#             'width': min(max(1, edge['call_count'] / 5), 10),  # Scale width based on call count
#             'color': _get_edge_color(edge['avg_time'])
#         })
    
#     # Generate the HTML template
#     vis_js_cdn = "https://unpkg.com/vis-network/standalone/umd/vis-network.min.js" if include_vis_js else ""
#     # Prepare profiling stats display
#     profiling_present = profiling_stats is not None
#     memory_current = profiling_stats.get('memory', {}).get('current_mb', 0.0) if profiling_present else 0.0
#     memory_peak = profiling_stats.get('memory', {}).get('peak_mb', 0.0) if profiling_present else 0.0
#     io_wait = profiling_stats.get('io_wait', 0.0) if profiling_present else 0.0
#     cpu_profile_text = profiling_stats.get('cpu', {}).get('profile_data', '') if profiling_present else ''

#     # Analyze CPU profiling data if available
#     cpu_profile_metrics = _analyze_cpu_profile(cpu_profile_text) if cpu_profile_text else {
#         'total_time': 0.0,
#         'total_calls': 0,
#         'top_functions': [],
#         'health_indicators': {
#             'execution_time': {'status': 'good', 'message': 'N/A'},
#             'call_efficiency': {'status': 'good', 'message': 'N/A'},
#             'hot_spots': {'status': 'good', 'message': 'N/A'}
#         }
#     }

#     # Generate the HTML template with proper escaping
#     nodes_json = json.dumps(nodes, indent=2)
#     edges_json = json.dumps(edges, indent=2)
    
#     # To avoid f-string errors with curly braces in JS, use .format() for the outer template, and escape curly braces as needed
#     html_template = """<!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>{title}</title>
#     <style>
#         body {{
#             font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
#             margin: 0;
#             padding: 20px;
#             background-color: #f5f5f5;
#         }}
#         .container {{
#             max-width: 1200px;
#             margin: 0 auto;
#             background: white;
#             border-radius: 8px;
#             box-shadow: 0 2px 10px rgba(0,0,0,0.1);
#             overflow: hidden;
#         }}
#         .header {{
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#             color: white;
#             padding: 20px;
#             text-align: center;
#         }}
#         .header h1 {{
#             margin: 0;
#             font-size: 2em;
#         }}
#         .stats {{
#             display: flex;
#             justify-content: space-around;
#             padding: 15px;
#             background: #f8f9fa;
#             border-bottom: 1px solid #dee2e6;
#         }}
#         .stat {{
#             text-align: center;
#         }}
#         .stat-value {{
#             font-size: 1.5em;
#             font-weight: bold;
#             color: #667eea;
#         }}
#         .stat-label {{
#             font-size: 0.9em;
#             color: #6c757d;
#         }}
#         #mynetwork {{
#             width: 100%;
#             height: 700px;
#             border: 1px solid #444;
#             background-color: #fff;
#         }}
#         #timeline {{
#             width: 100%;
#             height: 200px;
#             border: 1px solid #444;
#             margin-top: 20px;
#             background-color: #fff;
#         }}
#         .controls {{
#             padding: 20px;
#             background: #ffffff;
#             border-top: 1px solid #e9ecef;
#             border-radius: 0 0 8px 8px;
#         }}
#         .control-panel {{
#             display: flex;
#             flex-wrap: wrap;
#             gap: 20px;
#             margin-bottom: 20px;
#             padding: 20px;
#             background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
#             border-radius: 12px;
#             border: 1px solid #dee2e6;
#             box-shadow: 0 2px 8px rgba(0,0,0,0.05);
#         }}
#         .control-group {{
#             display: flex;
#             flex-direction: column;
#             min-width: 150px;
#         }}
#         .control-group label {{
#             font-weight: 600;
#             color: #495057;
#             margin-bottom: 5px;
#             font-size: 14px;
#         }}
#         .control-group select {{
#             padding: 8px 12px;
#             border: 1px solid #ced4da;
#             border-radius: 4px;
#             background: white;
#             font-size: 14px;
#             color: #495057;
#             transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
#         }}
#         .control-group select:focus {{
#             outline: none;
#             border-color: #667eea;
#             box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.25);
#         }}
#         .control-group input[type="text"] {{
#             padding: 8px 12px;
#             border: 1px solid #ced4da;
#             border-radius: 4px;
#             background: white;
#             font-size: 14px;
#             color: #495057;
#             transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
#             width: 100%;
#             box-sizing: border-box;
#         }}
#         .control-group input[type="text"]:focus {{
#             outline: none;
#             border-color: #667eea;
#             box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.25);
#         }}
#         .export-buttons {{
#             display: flex;
#             gap: 10px;
#             align-items: center;
#         }}
#         .export-btn {{
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#             color: white;
#             border: none;
#             padding: 10px 20px;
#             border-radius: 6px;
#             font-size: 14px;
#             font-weight: 600;
#             cursor: pointer;
#             transition: all 0.3s ease;
#             box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
#             min-width: 140px;
#         }}
#         .export-btn:hover {{
#             transform: translateY(-2px);
#             box-shadow: 0 4px 8px rgba(102, 126, 234, 0.4);
#             background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
#         }}
#         .export-btn:active {{
#             transform: translateY(0);
#             box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
#         }}
#         .export-btn:disabled {{
#             background: #6c757d;
#             cursor: not-allowed;
#             transform: none;
#             box-shadow: none;
#         }}
#         .legend {{
#             display: flex;
#             flex-wrap: wrap;
#             gap: 20px;
#             margin-top: 15px;
#         }}
#         .legend-item {{
#             display: flex;
#             align-items: center;
#             gap: 8px;
#         }}
#         .legend-color {{
#             width: 16px;
#             height: 16px;
#             border-radius: 3px;
#             flex-shrink: 0;
#         }}
#         .legend-item span {{
#             font-size: 14px;
#             color: #495057;
#         }}
#         .select2-container--default .select2-selection--multiple {{
#             background-color: #444;
#             border: 1px solid #666;
#             color: #fff;
#         }}
#         .select2-container--default .select2-selection--multiple .select2-selection__choice {{
#             background-color: #666;
#             border: 1px solid #888;
#             color: #fff;
#         }}
#         .cpu-profile-section {{
#             margin: 20px 0;
#             background: #f8f9fa;
#             border-radius: 8px;
#             border: 1px solid #dee2e6;
#             overflow: hidden;
#         }}
#         .cpu-profile-header {{
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#             color: white;
#             padding: 15px 20px;
#             cursor: pointer;
#             display: flex;
#             align-items: center;
#             justify-content: space-between;
#             transition: background 0.3s ease;
#         }}
#         .cpu-profile-header:hover {{
#             background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
#         }}
#         .cpu-profile-title {{
#             font-weight: 600;
#             font-size: 16px;
#             display: flex;
#             align-items: center;
#             gap: 10px;
#         }}
#         .cpu-profile-icon {{
#             font-size: 18px;
#         }}
#         .cpu-profile-toggle {{
#             font-size: 14px;
#             transition: transform 0.3s ease;
#         }}
#         .cpu-profile-content {{
#             display: none;
#             padding: 20px;
#             background: white;
#             max-height: 400px;
#             overflow-y: auto;
#         }}
#         .cpu-profile-content.expanded {{
#             display: block;
#         }}
#         .cpu-profile-pre {{
#             background: #2d3748;
#             color: #e2e8f0;
#             padding: 15px;
#             border-radius: 6px;
#             font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
#             font-size: 12px;
#             line-height: 1.4;
#             white-space: pre-wrap;
#             word-wrap: break-word;
#             margin: 0;
#             border: 1px solid #4a5568;
#         }}
#         .cpu-profile-empty {{
#             text-align: center;
#             color: #6c757d;
#             font-style: italic;
#             padding: 20px;
#         }}
#         .cpu-metric {{
#             display: flex;
#             flex-direction: column;
#             align-items: center;
#             padding: 20px;
#             border-bottom: 1px solid #dee2e6;
#         }}
#         .cpu-metric-label {{
#             font-weight: 600;
#             font-size: 14px;
#             color: #495057;
#             margin-bottom: 5px;
#         }}
#         .cpu-metric-value {{
#             font-size: 1.5em;
#             font-weight: bold;
#             color: #667eea;
#         }}
#         .cpu-metric-health {{
#             font-size: 14px;
#             color: #495057;
#             margin-top: 5px;
#         }}
#         .health-good {{
#             color: #4ecdc4;
#         }}
#         .health-warning {{
#             color: #ff6b6b;
#         }}
#         .health-poor {{
#             color: #ff6b6b;
#         }}
#         .cpu-profile-explanation {{
#             padding: 20px;
#             background: #f8f9fa;
#             border-bottom: 1px solid #dee2e6;
#         }}
#         .cpu-profile-legend {{
#             padding: 20px;
#             background: #f8f9fa;
#             border-bottom: 1px solid #dee2e6;
#         }}
#         .legend-term {{
#             font-weight: 600;
#             color: #495057;
#             margin-right: 5px;
#         }}
#     </style>
#     {vis_js_script}
#     <link href="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.2/vis-network.min.css" rel="stylesheet" type="text/css" />
#     <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
#     <link href="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css" rel="stylesheet" />
#     <script src="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js"></script>
# </head>
# <body>
#     <div class="container">
#         <div class="header">
#             <h1>{title}</h1>
#             <p>Interactive Call Flow Visualization</p>
#         </div>
        
#         <div class="stats">
#             <div class="stat">
#                 <div class="stat-value">{total_nodes}</div>
#                 <div class="stat-label">Functions</div>
#             </div>
#             <div class="stat">
#                 <div class="stat-value">{total_edges}</div>
#                 <div class="stat-label">Call Relationships</div>
#             </div>
#             <div class="stat">
#                 <div class="stat-value">{duration:.3f}s</div>
#                 <div class="stat-label">Total Duration</div>
#             </div>
#             {memory_current_block}
#             {memory_peak_block}
#             {io_wait_block}
#         </div>
        
#         <div class="control-panel">
#             <div class="control-group">
#                 <label for="layout">Layout:</label>
#                 <select id="layout" onchange="changeLayout(this.value)">
#                     <option value="hierarchical">Hierarchical</option>
#                     <option value="force">Force-Directed</option>
#                     <option value="circular">Circular</option>
#                     <option value="timeline">Timeline</option>
#                 </select>
#             </div>
            
#             <div class="control-group">
#                 <label for="physics">Physics:</label>
#                 <select id="physics" onchange="togglePhysics(this.value === 'true')">
#                     <option value="true">Enabled</option>
#                     <option value="false">Disabled</option>
#                 </select>
#             </div>
            
#             <div class="control-group">
#                 <label for="filter">Filter by module:</label>
#                 <select id="filter">
#                     <option value="">All modules</option>
#                 </select>
#             </div>
            
#             <div class="control-group">
#                 <label>Export Options:</label>
#                 <div class="export-buttons">
#                     <button class="export-btn" onclick="exportToPng()" title="Download the current graph as a PNG image">
#                         📊 Export as PNG
#                     </button>
#                     <button class="export-btn" onclick="exportToJson()" title="Download the graph data as a JSON file">
#                         📄 Export as JSON
#                     </button>
#                 </div>
#             </div>
#         </div>
        
#         {cpu_profile_block}
        
#         <div id="mynetwork"></div>
#         <div id="timeline" style="display: none;"></div>
        
#         <div class="controls">
            
#             <div class="legend">
#                 <div class="legend-item">
#                     <div class="legend-color" style="background-color: #ff6b6b;"></div>
#                     <span>Slow functions (>100ms avg)</span>
#                 </div>
#                 <div class="legend-item">
#                     <div class="legend-color" style="background-color: #4ecdc4;"></div>
#                     <span>Medium functions (10-100ms avg)</span>
#                 </div>
#                 <div class="legend-item">
#                     <div class="legend-color" style="background-color: #45b7d1;"></div>
#                     <span>Fast functions (<10ms avg)</span>
#                 </div>
#             </div>
#         </div>
#     </div>

#     <script type="text/javascript">
#         // Graph data
#         var nodes = {nodes_json};
#         var edges = {edges_json};

#         // Wait for vis to be loaded
#         function ensureVisLoaded(callback) {{
#             if (typeof vis !== "undefined" && vis.Network) {{
#                 callback();
#             }} else {{
#                 setTimeout(function() {{ ensureVisLoaded(callback); }}, 100);
#             }}
#         }}

#         ensureVisLoaded(function() {{
#             // Initialize network
#             var container = document.getElementById('mynetwork');
#             var data = {{
#                 nodes: new vis.DataSet(nodes),
#                 edges: new vis.DataSet(edges)
#             }};

#             // Store node and edge data for filtering
#             window.allNodes = new vis.DataSet(nodes);
#             window.allEdges = new vis.DataSet(edges);
            
#             // Store network reference globally for export functions
#             window.network = network;

#             // Network options
#             var options = {{
#                 nodes: {{
#                     shape: 'box',
#                     font: {{
#                         size: 12,
#                         color: '#ffffff',
#                         strokeWidth: 0,
#                         strokeColor: '#000000'
#                     }},
#                     borderWidth: 1,
#                     shadow: true,
#                     margin: 10,
#                     widthConstraint: {{
#                         minimum: 100,
#                         maximum: 200
#                     }}
#                 }},
#                 edges: {{
#                     width: 1,
#                     shadow: true,
#                     smooth: {{
#                         type: 'continuous'
#                     }},
#                     arrows: {{
#                         to: {{enabled: true, scaleFactor: 0.8}}
#                     }},
#                     color: {{
#                         inherit: 'both',
#                         opacity: 0.8
#                     }}
#                 }},
#                 layout: {{
#                     hierarchical: {{
#                         enabled: false
#                     }}
#                 }},
#                 physics: {{
#                     enabled: true,
#                     solver: "forceAtlas2Based"
#                 }},
#                 interaction: {{
#                     hover: true,
#                     tooltipDelay: 200
#                 }}
#             }};

#             var network = new vis.Network(container, data, options);

#             // Set initial layout and physics for footer controls
#             document.getElementById('physics').value = "true";
#             document.getElementById('layout').value = "force";

#             // Layout change handler
#             window.changeLayout = function(layoutType) {{
#                 if (layoutType === "hierarchical") {{
#                     // Reset node positions for hierarchical layout
#                     var resetNodes = nodes.map(function(node) {{
#                         return {{
#                             ...node,
#                             x: undefined,
#                             y: undefined,
#                             fixed: {{x: false, y: false}}
#                         }};
#                     }});
                    
#                     data.nodes.clear();
#                     data.nodes.add(resetNodes);
                    
#                     network.setOptions({{
#                         layout: {{
#                             hierarchical: {{
#                                 enabled: true,
#                                 direction: 'UD',
#                                 sortMethod: 'directed'
#                             }}
#                         }},
#                         physics: {{enabled: false}}
#                     }});
#                     document.getElementById('layout').value = "hierarchical";
#                     document.getElementById('physics').value = "false";
#                 }} else if (layoutType === "force") {{
#                     // Reset node positions for force-directed layout
#                     var resetNodes = nodes.map(function(node) {{
#                         return {{
#                             ...node,
#                             x: undefined,
#                             y: undefined,
#                             fixed: {{x: false, y: false}}
#                         }};
#                     }});
                    
#                     data.nodes.clear();
#                     data.nodes.add(resetNodes);
                    
#                     network.setOptions({{
#                         layout: {{hierarchical: false}},
#                         physics: {{enabled: true, solver: "forceAtlas2Based"}}
#                     }});
#                     document.getElementById('layout').value = "force";
#                     document.getElementById('physics').value = "true";
#                 }} else if (layoutType === "circular") {{
#                     // Create circular layout by updating node positions
#                     var radius = 300;
#                     var centerX = 400;
#                     var centerY = 300;
#                     var angleStep = 2 * Math.PI / nodes.length;
                    
#                     var updatedNodes = nodes.map(function(node, i) {{
#                         var angle = i * angleStep;
#                         return {{
#                             ...node,
#                             x: centerX + radius * Math.cos(angle),
#                             y: centerY + radius * Math.sin(angle),
#                             fixed: {{x: true, y: true}}
#                         }};
#                     }});
                    
#                     data.nodes.clear();
#                     data.nodes.add(updatedNodes);
                    
#                     network.setOptions({{
#                         layout: {{hierarchical: false}},
#                         physics: {{enabled: false}}
#                     }});
#                     document.getElementById('layout').value = "circular";
#                     document.getElementById('physics').value = "false";
                    
#                     // Fit the view after layout
#                     setTimeout(() => network.fit(), 100);
                    
#                 }} else if (layoutType === "timeline") {{
#                     // Create timeline layout sorted by execution time
#                     var sorted = nodes.slice().sort(function(a, b) {{
#                         return a.total_time - b.total_time;
#                     }});
                    
#                     var startX = 100;
#                     var spacing = Math.max(150, (window.innerWidth - 200) / sorted.length);
#                     var timelineY = 300;
                    
#                     var updatedNodes = sorted.map(function(node, i) {{
#                         return {{
#                             ...node,
#                             x: startX + i * spacing,
#                             y: timelineY,
#                             fixed: {{x: true, y: true}}
#                         }};
#                     }});
                    
#                     data.nodes.clear();
#                     data.nodes.add(updatedNodes);
                    
#                     network.setOptions({{
#                         layout: {{hierarchical: false}},
#                         physics: {{enabled: false}}
#                     }});
#                     document.getElementById('layout').value = "timeline";
#                     document.getElementById('physics').value = "false";
                    
#                     // Fit the view after layout
#                     setTimeout(() => network.fit(), 100);
#                 }}
#             }};

#         // Set initial layout and physics for footer controls
#         document.getElementById('physics').value = "true";
#         document.getElementById('layout').value = "force";

#         // Make changeLayout available globally
#         window.changeLayout = changeLayout;

#         // Export as PNG
#         window.exportToPng = function() {{
#             try {{
#                 // Wait for network to be ready
#                 if (!network) {{
#                     throw new Error('Network not initialized');
#                 }}
                
#                 // Get the canvas from the network
#                 var canvas = network.canvas.frame.canvas;
#                 if (!canvas) {{
#                     throw new Error('Canvas not found. Please wait for the graph to load completely.');
#                 }}
                
#                 // Create a temporary canvas with higher resolution
#                 var tempCanvas = document.createElement('canvas');
#                 var ctx = tempCanvas.getContext('2d');
#                 var scale = 2; // Higher resolution
                
#                 // Set the temporary canvas dimensions
#                 tempCanvas.width = canvas.width * scale;
#                 tempCanvas.height = canvas.height * scale;
                
#                 // Scale and draw the original canvas
#                 ctx.scale(scale, scale);
#                 ctx.drawImage(canvas, 0, 0);
                
#                 // Create download link
#                 var link = document.createElement('a');
#                 link.href = tempCanvas.toDataURL('image/png');
#                 link.download = 'callflow-graph-' + new Date().toISOString().slice(0, 10) + '.png';
#                 document.body.appendChild(link);
#                 link.click();
#                 document.body.removeChild(link);
                
#                 // Clean up
#                 tempCanvas = null;
#             }} catch (error) {{
#                 console.error('PNG export error:', error);
#                 alert('Error exporting PNG: ' + (error.message || 'Unknown error occurred'));
#             }}
#         }};

#         // Export as JSON
#         window.exportToJson = function() {{
#             try {{
#                 // Use the original nodes and edges data instead of network.getData()
#                 if (!nodes || !edges) {{
#                     throw new Error('Graph data not available');
#                 }}
                
#                 var exportData = {{
#                     metadata: {{
#                         total_nodes: nodes.length,
#                         total_edges: edges.length,
#                         duration: Number('{duration}'),
#                         export_timestamp: new Date().toISOString(),
#                         version: "callflow-tracer",
#                         title: "{title}"
#                     }},
#                     nodes: nodes,
#                     edges: edges
#                 }};
                
#                 // Create a Blob with the JSON data
#                 var dataStr = JSON.stringify(exportData, null, 2);
#                 var dataBlob = new Blob([dataStr], {{type: 'application/json'}});
                
#                 // Create download link
#                 var link = document.createElement('a');
#                 var url = URL.createObjectURL(dataBlob);
                
#                 link.href = url;
#                 link.download = 'callflow-graph-' + new Date().toISOString().slice(0, 10) + '.json';
                
#                 // Add to document, trigger download, then clean up
#                 document.body.appendChild(link);
#                 link.click();
                
#                 // Show success message
#                 console.log('JSON export successful:', exportData.metadata);
                
#                 // Clean up
#                 setTimeout(function() {{
#                     document.body.removeChild(link);
#                     URL.revokeObjectURL(url);
#                 }}, 100);
                
#             }} catch (error) {{
#                 console.error('JSON export error:', error);
#                 console.error('Nodes available:', !!nodes, 'Edges available:', !!edges);
#                 console.error('Nodes length:', nodes ? nodes.length : 'undefined');
#                 console.error('Edges length:', edges ? edges.length : 'undefined');
#                 alert('Error exporting JSON: ' + (error.message || 'Unknown error occurred') + 
#                       '\\n\\nPlease check the browser console for more details.');
#             }}
#         }};

#         // --- Footer Controls ---

#         // Physics toggle (footer)
#         document.getElementById('physics').addEventListener('change', function() {{
#             var enabled = this.value === 'true';
#             network.setOptions({{ physics: {{ enabled: enabled }} }});
#         }});

#             // Layout select (footer)
#             document.getElementById('layout').addEventListener('change', function() {{
#                 if (this.value === 'hierarchical') {{
#                     network.setOptions({{
#                         layout: {{
#                             hierarchical: {{
#                                 enabled: true,
#                                 direction: 'UD',
#                                 sortMethod: 'directed'
#                             }}
#                         }},
#                         physics: {{ enabled: false }}
#                     }});
#                     document.getElementById('layout').value = "hierarchical";
#                     document.getElementById('physics').value = "false";
#                 }} else {{
#                     network.setOptions({{
#                         layout: {{ hierarchical: false }},
#                         physics: {{ enabled: true, solver: "forceAtlas2Based" }}
#                     }});
#                     document.getElementById('layout').value = "force";
#                     document.getElementById('physics').value = "true";
#                 }}
#             }});

#             // Populate module filter dropdown
#             const modulesSet = new Set();
#             nodes.forEach(n => {{
#                 if (n.module) {{
#                     modulesSet.add(n.module);
#                 }} else {{
#                     modulesSet.add('__main__');  // Handle nodes without module
#                 }}
#             }});
            
#             const modulesArr = Array.from(modulesSet).sort();
#             const filterSelect = document.getElementById('filter');
            
#             // Remove all existing options except "All modules"
#             while (filterSelect.options.length > 1) {{
#                 filterSelect.remove(1);
#             }}
            
#             // Add sorted module options
#             modulesArr.forEach(module => {{
#                 const option = document.createElement('option');
#                 option.value = module;
#                 option.textContent = module === '__main__' ? 'Main Module' : module;
#                 filterSelect.appendChild(option);
#             }});

#             // Add module filter functionality
#             filterSelect.addEventListener('change', function() {{
#                 const selectedModule = this.value;
                
#                 if (selectedModule === '') {{
#                     // Show all nodes and edges
#                     data.nodes.clear();
#                     data.edges.clear();
#                     data.nodes.add(window.allNodes.get());
#                     data.edges.add(window.allEdges.get());
#                     console.log('Filter: Showing all modules');
#                 }} else {{
#                     // Filter nodes by selected module
#                     const filteredNodes = window.allNodes.get().filter(node => {{
#                         if (selectedModule === '__main__') {{
#                             return !node.module || node.module === '' || node.module === '__main__';
#                         }}
#                         return node.module === selectedModule;
#                     }});
                    
#                     // Get IDs of filtered nodes
#                     const filteredNodeIds = new Set(filteredNodes.map(node => node.id));
                    
#                     // Filter edges that connect filtered nodes
#                     const filteredEdges = window.allEdges.get().filter(edge => 
#                         filteredNodeIds.has(edge.from) && filteredNodeIds.has(edge.to)
#                     );
                    
#                     // Update the network data
#                     data.nodes.clear();
#                     data.edges.clear();
#                     data.nodes.add(filteredNodes);
#                     data.edges.add(filteredEdges);
                    
#                     console.log(`Filter: Showing module '${{selectedModule}}' - ${{filteredNodes.length}} nodes, ${{filteredEdges.length}} edges`);
#                 }}
                
#                 // Fit the network to show all visible nodes
#                 setTimeout(() => {{
#                     network.fit({{
#                         animation: {{
#                             duration: 500,
#                             easingFunction: 'easeInOutQuad'
#                         }}
#                     }});
#                 }}, 100);
#             }});

#             // Add some styling on load
#             network.on("stabilizationIterationsDone", function() {{
#                 // Keep physics enabled for force-directed by default
#                 // network.setOptions({{ physics: false }});
#             }});

#             // Set initial layout and physics to force-directed and enabled
#             network.setOptions({{
#                 layout: {{hierarchical: false}},
#                 physics: {{enabled: true, solver: "forceAtlas2Based"}}
#             }});
#             document.getElementById('layout-select').value = "force";
#             document.getElementById('layout').value = "force";
#             document.getElementById('physics').value = "true";

#         }});

#         // CPU Profile Toggle Function
#         function toggleCpuProfile() {{
#             const content = document.getElementById('cpu-content');
#             const toggle = document.getElementById('cpu-toggle');
            
#             if (content && toggle) {{
#                 if (content.classList.contains('expanded')) {{
#                     content.classList.remove('expanded');
#                     toggle.textContent = '▼';
#                     toggle.style.transform = 'rotate(0deg)';
#                 }} else {{
#                     content.classList.add('expanded');
#                     toggle.textContent = '▲';
#                     toggle.style.transform = 'rotate(180deg)';
#                 }}
#             }}
#         }}
#     </script>
# </body>
# </html>"""
    
#     # Prepare blocks for optional profiling stats
#     memory_current_block = (
#         f'<div class="stat"><div class="stat-value">{memory_current:.2f}MB</div><div class="stat-label">Memory (current)</div></div>'
#         if profiling_present else ''
#     )
#     memory_peak_block = (
#         f'<div class="stat"><div class="stat-value">{memory_peak:.2f}MB</div><div class="stat-label">Memory (peak)</div></div>'
#         if profiling_present else ''
#     )
#     io_wait_block = (
#         f'<div class="stat"><div class="stat-value">{io_wait:.3f}s</div><div class="stat-label">I/O wait</div></div>'
#         if profiling_present else ''
#     )
#     # Extract CPU metrics for easier template formatting
#     cpu_total_time = cpu_profile_metrics.get('total_time', 0.0)
#     cpu_total_calls = cpu_profile_metrics.get('total_calls', 0)
#     cpu_hot_spots_count = len(cpu_profile_metrics.get('top_functions', []))
    
#     health_indicators = cpu_profile_metrics.get('health_indicators', {})
#     exec_time_status = health_indicators.get('execution_time', {}).get('status', 'good')
#     exec_time_message = health_indicators.get('execution_time', {}).get('message', 'N/A')
#     call_eff_status = health_indicators.get('call_efficiency', {}).get('status', 'good')
#     call_eff_message = health_indicators.get('call_efficiency', {}).get('message', 'N/A')
#     hot_spots_status = health_indicators.get('hot_spots', {}).get('status', 'good')
#     hot_spots_message = health_indicators.get('hot_spots', {}).get('message', 'N/A')
    
#     cpu_profile_block = (
#         f'''<div class="cpu-profile-section">
#             <div class="cpu-profile-header" onclick="toggleCpuProfile()">
#                 <div class="cpu-profile-title">
#                     <span class="cpu-profile-icon">🔥</span>
#                     CPU Profile Analysis (cProfile)
#                 </div>
#                 <span class="cpu-profile-toggle" id="cpu-toggle">▼</span>
#             </div>
#             <div class="cpu-profile-content" id="cpu-content">
#                 <div class="cpu-profile-explanation">
#                     <h4>📊 What This Data Means</h4>
#                     <p><strong>CPU Profiling</strong> shows how much time your program spends in each function, helping identify performance bottlenecks.</p>
#                     <p><strong>Key Terms:</strong></p>
#                     <p>• <strong>ncalls:</strong> Number of calls to the function</p>
#                     <p>• <strong>tottime:</strong> Total time spent in the function (excluding sub-calls)</p>
#                     <p>• <strong>cumtime:</strong> Cumulative time (including sub-calls)</p>
#                     <p>• <strong>percall:</strong> Time per call (tottime/ncalls or cumtime/ncalls)</p>
#                 </div>
                
#                 <div class="cpu-metrics">
#                     <div class="cpu-metric">
#                         <div class="cpu-metric-label">Total Execution Time</div>
#                         <div class="cpu-metric-value">{cpu_total_time:.3f}s</div>
#                         <div class="cpu-metric-health health-{exec_time_status}">
#                             {exec_time_message}
#                         </div>
#                     </div>
#                     <div class="cpu-metric">
#                         <div class="cpu-metric-label">Function Calls</div>
#                         <div class="cpu-metric-value">{cpu_total_calls:,}</div>
#                         <div class="cpu-metric-health health-{call_eff_status}">
#                             {call_eff_message}
#                         </div>
#                     </div>
#                     <div class="cpu-metric">
#                         <div class="cpu-metric-label">Performance Distribution</div>
#                         <div class="cpu-metric-value">{cpu_hot_spots_count} Hot Spots</div>
#                         <div class="cpu-metric-health health-{hot_spots_status}">
#                             {hot_spots_message}
#                         </div>
#                     </div>
#                 </div>
                
#                 <div class="cpu-profile-legend">
#                     <h5>🎯 Performance Health Guide</h5>
#                     <div class="legend-item">
#                         <span class="legend-term">🟢 Excellent:</span>
#                         <span>Optimal performance, no action needed</span>
#                     </div>
#                     <div class="legend-item">
#                         <span class="legend-term">🔵 Good:</span>
#                         <span>Good performance, minor optimizations possible</span>
#                     </div>
#                     <div class="legend-item">
#                         <span class="legend-term">🟡 Warning:</span>
#                         <span>Moderate performance, consider optimization</span>
#                     </div>
#                     <div class="legend-item">
#                         <span class="legend-term">🔴 Poor:</span>
#                         <span>Performance issues detected, optimization recommended</span>
#                     </div>
#                 </div>
                
#                 <h4>📋 Detailed Profile Data</h4>
#                 <pre class="cpu-profile-pre">{cpu_profile_text}</pre>
#             </div>
#         </div>'''
#         if profiling_present and cpu_profile_text else ''
#     )
#     vis_js_script = f'<script type="text/javascript" src="{vis_js_cdn}"></script>' if include_vis_js else ''

#     # Format the template with the JSON data and blocks
#     return html_template.format(
#         title=title,
#         nodes_json=nodes_json,
#         edges_json=edges_json,
#         total_nodes=graph_data['metadata']['total_nodes'],
#         total_edges=graph_data['metadata']['total_edges'],
#         duration=graph_data['metadata']['duration'],
#         memory_current_block=memory_current_block,
#         memory_peak_block=memory_peak_block,
#         io_wait_block=io_wait_block,
#         cpu_profile_block=cpu_profile_block,
#         vis_js_script=vis_js_script
#     )

def _generate_html(graph_data: dict, title: str, include_vis_js: bool, 
                  profiling_stats: Optional[dict], layout: str = "hierarchical") -> str:
    """Generate HTML content with embedded JavaScript for visualization.
    
    This function uses Python's format() method with double braces for JavaScript code to avoid
    conflicts between Python string formatting and JavaScript object literals.
    """
    
    # Prepare nodes and edges for vis.js
    nodes = []
    edges = []
    
    # Process nodes
    for node in graph_data['nodes']:
        nodes.append({
            'id': node['full_name'],
            'label': node['name'],
            'title': f"Module: {node['module']}\nCalls: {node['call_count']}\nTotal Time: {node['total_time']:.3f}s\nAvg Time: {node['avg_time']:.3f}s",
            'group': node['module'] or 'main',
            'value': node['call_count'],
            'color': _get_node_color(node['avg_time']),
            'module': node['module'],  # Add module for JS filtering
            'shape': 'circle',  # Make nodes circular
            'total_time': node['total_time'],
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
    # Prepare profiling stats display
    profiling_present = profiling_stats is not None
    memory_current = profiling_stats.get('memory', {}).get('current_mb', 0.0) if profiling_present else 0.0
    memory_peak = profiling_stats.get('memory', {}).get('peak_mb', 0.0) if profiling_present else 0.0
    io_wait = profiling_stats.get('io_wait', 0.0) if profiling_present else 0.0
    cpu_profile_text = profiling_stats.get('cpu', {}).get('profile_data', '') if profiling_present else ''

    # Analyze CPU profiling data if available
    cpu_profile_metrics = _analyze_cpu_profile(cpu_profile_text) if cpu_profile_text else {
        'total_time': 0.0,
        'total_calls': 0,
        'top_functions': [],
        'health_indicators': {
            'execution_time': {'status': 'good', 'message': 'N/A'},
            'call_efficiency': {'status': 'good', 'message': 'N/A'},
            'hot_spots': {'status': 'good', 'message': 'N/A'}
        }
    }

    # Generate the HTML template with proper escaping
    nodes_json = json.dumps(nodes, indent=2)
    edges_json = json.dumps(edges, indent=2)
    
    # To avoid f-string errors with curly braces in JS, use .format() for the outer template, and escape curly braces as needed
    html_template = """<!DOCTYPE html>
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
        #mynetwork {{
            width: 100%;
            height: 700px;
            border: 1px solid #444;
            background-color: #fff;
        }}
        #timeline {{
            width: 100%;
            height: 200px;
            border: 1px solid #444;
            margin-top: 20px;
            background-color: #fff;
        }}
        .controls {{
            padding: 20px;
            background: #ffffff;
            border-top: 1px solid #e9ecef;
            border-radius: 0 0 8px 8px;
        }}
        .control-panel {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 20px;
            padding: 20px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 12px;
            border: 1px solid #dee2e6;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        .control-group {{
            display: flex;
            flex-direction: column;
            min-width: 150px;
        }}
        .control-group label {{
            font-weight: 600;
            color: #495057;
            margin-bottom: 5px;
            font-size: 14px;
        }}
        .control-group select {{
            padding: 8px 12px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            background: white;
            font-size: 14px;
            color: #495057;
            transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
        }}
        .control-group select:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.25);
        }}
        .control-group input[type="text"] {{
            padding: 8px 12px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            background: white;
            font-size: 14px;
            color: #495057;
            transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
            width: 100%;
            box-sizing: border-box;
        }}
        .control-group input[type="text"]:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.25);
        }}
        .export-buttons {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        .export-btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
            min-width: 140px;
        }}
        .export-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(102, 126, 234, 0.4);
            background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        }}
        .export-btn:active {{
            transform: translateY(0);
            box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
        }}
        .export-btn:disabled {{
            background: #6c757d;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }}
        .legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-top: 15px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 3px;
            flex-shrink: 0;
        }}
        .legend-item span {{
            font-size: 14px;
            color: #495057;
        }}
        .select2-container--default .select2-selection--multiple {{
            background-color: #444;
            border: 1px solid #666;
            color: #fff;
        }}
        .select2-container--default .select2-selection--multiple .select2-selection__choice {{
            background-color: #666;
            border: 1px solid #888;
            color: #fff;
        }}
        .cpu-profile-section {{
            margin: 20px 0;
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #dee2e6;
            overflow: hidden;
        }}
        .cpu-profile-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: background 0.3s ease;
        }}
        .cpu-profile-header:hover {{
            background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        }}
        .cpu-profile-title {{
            font-weight: 600;
            font-size: 16px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .cpu-profile-icon {{
            font-size: 18px;
        }}
        .cpu-profile-toggle {{
            font-size: 14px;
            transition: transform 0.3s ease;
        }}
        .cpu-profile-content {{
            display: none;
            padding: 20px;
            background: white;
            max-height: 400px;
            overflow-y: auto;
        }}
        .cpu-profile-content.expanded {{
            display: block;
        }}
        .cpu-profile-pre {{
            background: #2d3748;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 6px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 12px;
            line-height: 1.4;
            white-space: pre-wrap;
            word-wrap: break-word;
            margin: 0;
            border: 1px solid #4a5568;
        }}
        .cpu-profile-empty {{
            text-align: center;
            color: #6c757d;
            font-style: italic;
            padding: 20px;
        }}
        .cpu-metric {{
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
            border-bottom: 1px solid #dee2e6;
        }}
        .cpu-metric-label {{
            font-weight: 600;
            font-size: 14px;
            color: #495057;
            margin-bottom: 5px;
        }}
        .cpu-metric-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
        }}
        .cpu-metric-health {{
            font-size: 14px;
            color: #495057;
            margin-top: 5px;
        }}
        .health-good {{
            color: #4ecdc4;
        }}
        .health-warning {{
            color: #ff6b6b;
        }}
        .health-poor {{
            color: #ff6b6b;
        }}
        .cpu-profile-explanation {{
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }}
        .cpu-profile-legend {{
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }}
        .legend-term {{
            font-weight: 600;
            color: #495057;
            margin-right: 5px;
        }}
    </style>
    {vis_js_script}
    <link href="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.2/vis-network.min.css" rel="stylesheet" type="text/css" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css" rel="stylesheet" />
    <script src="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <p>Interactive Call Flow Visualization</p>
        </div>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{total_nodes}</div>
                <div class="stat-label">Functions</div>
            </div>
            <div class="stat">
                <div class="stat-value">{total_edges}</div>
                <div class="stat-label">Call Relationships</div>
            </div>
            <div class="stat">
                <div class="stat-value">{duration:.3f}s</div>
                <div class="stat-label">Total Duration</div>
            </div>
            {memory_current_block}
            {memory_peak_block}
            {io_wait_block}
        </div>
        
        <div class="control-panel">
            <div class="control-group">
                <label for="layout">Layout:</label>
                <select id="layout" onchange="changeLayout(this.value)">
                    <option value="hierarchical">Hierarchical</option>
                    <option value="force">Force-Directed</option>
                    <option value="circular">Circular</option>
                    <option value="radial">Radial Tree</option>
                    <option value="grid">Grid</option>
                    <option value="tree">Tree (Vertical)</option>
                    <option value="tree-horizontal">Tree (Horizontal)</option>
                    <option value="timeline">Timeline</option>
                    <option value="organic">Organic (Spring)</option>
                </select>
            </div>
            
            <div class="control-group">
                <label for="physics">Physics:</label>
                <select id="physics" onchange="togglePhysics(this.value === 'true')">
                    <option value="true">Enabled</option>
                    <option value="false">Disabled</option>
                </select>
            </div>
            
            <div class="control-group">
                <label for="filter">Filter by module:</label>
                <select id="filter">
                    <option value="">All modules</option>
                </select>
            </div>
            
            <div class="control-group">
                <label for="node-spacing">Node Spacing:</label>
                <select id="node-spacing" onchange="updateLayoutSpacing(this.value)">
                    <option value="100">Compact</option>
                    <option value="150" selected>Normal</option>
                    <option value="200">Relaxed</option>
                    <option value="300">Wide</option>
                </select>
            </div>
            
            <div class="control-group">
                <label>Export Options:</label>
                <div class="export-buttons">
                    <button class="export-btn" onclick="exportToPng()" title="Download the current graph as a PNG image">
                        📊 Export as PNG
                    </button>
                    <button class="export-btn" onclick="exportToJson()" title="Download the graph data as a JSON file">
                        📄 Export as JSON
                    </button>
                </div>
            </div>
        </div>
        
        {cpu_profile_block}
        
        <div id="mynetwork"></div>
        <div id="timeline" style="display: none;"></div>
        
        <div class="controls">
            
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
        var nodes = {nodes_json};
        var edges = {edges_json};

        // Wait for vis to be loaded
        function ensureVisLoaded(callback) {{
            if (typeof vis !== "undefined" && vis.Network) {{
                callback();
            }} else {{
                setTimeout(function() {{ ensureVisLoaded(callback); }}, 100);
            }}
        }}

        ensureVisLoaded(function() {{
            // Initialize network
            var container = document.getElementById('mynetwork');
            var data = {{
                nodes: new vis.DataSet(nodes),
                edges: new vis.DataSet(edges)
            }};

            // Store node and edge data for filtering
            window.allNodes = new vis.DataSet(nodes);
            window.allEdges = new vis.DataSet(edges);

            // Network options
            var options = {{
                nodes: {{
                    shape: 'box',
                    font: {{
                        size: 12,
                        color: '#ffffff',
                        strokeWidth: 0,
                        strokeColor: '#000000'
                    }},
                    borderWidth: 1,
                    shadow: true,
                    margin: 10,
                    widthConstraint: {{
                        minimum: 100,
                        maximum: 200
                    }}
                }},
                edges: {{
                    width: 1,
                    shadow: true,
                    smooth: {{
                        type: 'continuous'
                    }},
                    arrows: {{
                        to: {{enabled: true, scaleFactor: 0.8}}
                    }},
                    color: {{
                        inherit: 'both',
                        opacity: 0.8
                    }}
                }},
                layout: {{
                    hierarchical: {{
                        enabled: false
                    }}
                }},
                physics: {{
                    enabled: true,
                    solver: "forceAtlas2Based"
                }},
                interaction: {{
                    hover: true,
                    tooltipDelay: 200
                }}
            }};

            var network = new vis.Network(container, data, options);
            
            // Store network reference globally for export and control functions
            window.network = network;

            // Set initial layout and physics for footer controls
            document.getElementById('physics').value = "true";
            document.getElementById('layout').value = "force";

            // Layout change handler
            window.changeLayout = function(layoutType) {{
                if (layoutType === "hierarchical") {{
                    // Reset node positions for hierarchical layout
                    var resetNodes = nodes.map(function(node) {{
                        return {{
                            ...node,
                            x: undefined,
                            y: undefined,
                            fixed: {{x: false, y: false}}
                        }};
                    }});
                    
                    data.nodes.clear();
                    data.nodes.add(resetNodes);
                    
                    network.setOptions({{
                        layout: {{
                            hierarchical: {{
                                enabled: true,
                                direction: 'UD',
                                sortMethod: 'directed'
                            }}
                        }},
                        physics: {{enabled: false}}
                    }});
                    document.getElementById('layout').value = "hierarchical";
                    document.getElementById('physics').value = "false";
                }} else if (layoutType === "force") {{
                    // Reset node positions for force-directed layout
                    var resetNodes = nodes.map(function(node) {{
                        return {{
                            ...node,
                            x: undefined,
                            y: undefined,
                            fixed: {{x: false, y: false}}
                        }};
                    }});
                    
                    data.nodes.clear();
                    data.nodes.add(resetNodes);
                    
                    network.setOptions({{
                        layout: {{hierarchical: false}},
                        physics: {{enabled: true, solver: "forceAtlas2Based"}}
                    }});
                    document.getElementById('layout').value = "force";
                    document.getElementById('physics').value = "true";
                }} else if (layoutType === "circular") {{
                    // Create circular layout by updating node positions
                    var spacing = window.currentSpacing || 150;
                    var radius = spacing * 2; // Radius scales with spacing
                    var centerX = 400;
                    var centerY = 300;
                    var angleStep = 2 * Math.PI / nodes.length;
                    
                    var updatedNodes = nodes.map(function(node, i) {{
                        var angle = i * angleStep;
                        return {{
                            ...node,
                            x: centerX + radius * Math.cos(angle),
                            y: centerY + radius * Math.sin(angle),
                            fixed: {{x: true, y: true}}
                        }};
                    }});
                    
                    data.nodes.clear();
                    data.nodes.add(updatedNodes);
                    
                    network.setOptions({{
                        layout: {{hierarchical: false}},
                        physics: {{enabled: false}}
                    }});
                    document.getElementById('layout').value = "circular";
                    document.getElementById('physics').value = "false";
                    
                    // Fit the view after layout
                    setTimeout(() => network.fit(), 100);
                    
                }} else if (layoutType === "timeline") {{
                    // Create timeline layout sorted by execution time
                    var sorted = nodes.slice().sort(function(a, b) {{
                        return a.total_time - b.total_time;
                    }});
                    
                    var startX = 100;
                    var customSpacing = window.currentSpacing || 150;
                    var spacing = Math.max(customSpacing, (window.innerWidth - 200) / sorted.length);
                    var timelineY = 300;
                    
                    var updatedNodes = sorted.map(function(node, i) {{
                        return {{
                            ...node,
                            x: startX + i * spacing,
                            y: timelineY,
                            fixed: {{x: true, y: true}}
                        }};
                    }});
                    
                    data.nodes.clear();
                    data.nodes.add(updatedNodes);
                    
                    network.setOptions({{
                        layout: {{hierarchical: false}},
                        physics: {{enabled: false}}
                    }});
                    document.getElementById('layout').value = "timeline";
                    document.getElementById('physics').value = "false";
                    
                    // Fit the view after layout
                    setTimeout(() => network.fit(), 100);
                    
                }} else if (layoutType === "radial") {{
                    // Radial tree layout - nodes arranged in concentric circles by depth
                    var nodeMap = {{}};
                    nodes.forEach(n => nodeMap[n.id] = n);
                    
                    // Build adjacency list
                    var adjacency = {{}};
                    nodes.forEach(n => adjacency[n.id] = []);
                    edges.forEach(e => {{
                        if (!adjacency[e.from]) adjacency[e.from] = [];
                        adjacency[e.from].push(e.to);
                    }});
                    
                    // Find root nodes (nodes with no incoming edges)
                    var inDegree = {{}};
                    nodes.forEach(n => inDegree[n.id] = 0);
                    edges.forEach(e => inDegree[e.to] = (inDegree[e.to] || 0) + 1);
                    var roots = nodes.filter(n => inDegree[n.id] === 0).map(n => n.id);
                    if (roots.length === 0 && nodes.length > 0) roots = [nodes[0].id];
                    
                    // BFS to assign levels
                    var levels = {{}};
                    var queue = roots.map(r => [r, 0]);
                    var visited = new Set();
                    
                    while (queue.length > 0) {{
                        var [nodeId, level] = queue.shift();
                        if (visited.has(nodeId)) continue;
                        visited.add(nodeId);
                        levels[nodeId] = level;
                        
                        (adjacency[nodeId] || []).forEach(child => {{
                            if (!visited.has(child)) {{
                                queue.push([child, level + 1]);
                            }}
                        }});
                    }}
                    
                    // Assign unvisited nodes to level 0
                    nodes.forEach(n => {{
                        if (!(n.id in levels)) levels[n.id] = 0;
                    }});
                    
                    // Group nodes by level
                    var levelGroups = {{}};
                    Object.keys(levels).forEach(id => {{
                        var level = levels[id];
                        if (!levelGroups[level]) levelGroups[level] = [];
                        levelGroups[level].push(id);
                    }});
                    
                    // Calculate radial positions with custom spacing
                    var centerX = 400, centerY = 300;
                    var radiusStep = window.currentSpacing || 150;
                    var updatedNodes = [];
                    
                    Object.keys(levelGroups).forEach(level => {{
                        var levelNodes = levelGroups[level];
                        var radius = level * radiusStep + 50;
                        var angleStep = (2 * Math.PI) / levelNodes.length;
                        
                        levelNodes.forEach((nodeId, i) => {{
                            var angle = i * angleStep;
                            var node = nodeMap[nodeId];
                            updatedNodes.push({{
                                ...node,
                                x: centerX + radius * Math.cos(angle),
                                y: centerY + radius * Math.sin(angle),
                                fixed: {{x: true, y: true}}
                            }});
                        }});
                    }});
                    
                    data.nodes.clear();
                    data.nodes.add(updatedNodes);
                    
                    network.setOptions({{
                        layout: {{hierarchical: false}},
                        physics: {{enabled: false}}
                    }});
                    document.getElementById('layout').value = "radial";
                    document.getElementById('physics').value = "false";
                    setTimeout(() => network.fit(), 100);
                    
                }} else if (layoutType === "grid") {{
                    // Grid layout - arrange nodes in a grid pattern
                    var cols = Math.ceil(Math.sqrt(nodes.length));
                    var spacing = window.currentSpacing || 200;
                    var startX = 100, startY = 100;
                    
                    var updatedNodes = nodes.map(function(node, i) {{
                        var row = Math.floor(i / cols);
                        var col = i % cols;
                        return {{
                            ...node,
                            x: startX + col * spacing,
                            y: startY + row * spacing,
                            fixed: {{x: true, y: true}}
                        }};
                    }});
                    
                    data.nodes.clear();
                    data.nodes.add(updatedNodes);
                    
                    network.setOptions({{
                        layout: {{hierarchical: false}},
                        physics: {{enabled: false}}
                    }});
                    document.getElementById('layout').value = "grid";
                    document.getElementById('physics').value = "false";
                    setTimeout(() => network.fit(), 100);
                    
                }} else if (layoutType === "tree") {{
                    // Vertical tree layout using hierarchical
                    var resetNodes = nodes.map(function(node) {{
                        return {{
                            ...node,
                            x: undefined,
                            y: undefined,
                            fixed: {{x: false, y: false}}
                        }};
                    }});
                    
                    data.nodes.clear();
                    data.nodes.add(resetNodes);
                    
                    var spacing = window.currentSpacing || 150;
                    network.setOptions({{
                        layout: {{
                            hierarchical: {{
                                enabled: true,
                                direction: 'UD',
                                sortMethod: 'directed',
                                nodeSpacing: spacing,
                                levelSeparation: spacing * 1.3,
                                treeSpacing: spacing * 1.3
                            }}
                        }},
                        physics: {{enabled: false}}
                    }});
                    document.getElementById('layout').value = "tree";
                    document.getElementById('physics').value = "false";
                    
                }} else if (layoutType === "tree-horizontal") {{
                    // Horizontal tree layout
                    var resetNodes = nodes.map(function(node) {{
                        return {{
                            ...node,
                            x: undefined,
                            y: undefined,
                            fixed: {{x: false, y: false}}
                        }};
                    }});
                    
                    data.nodes.clear();
                    data.nodes.add(resetNodes);
                    
                    var spacing = window.currentSpacing || 150;
                    network.setOptions({{
                        layout: {{
                            hierarchical: {{
                                enabled: true,
                                direction: 'LR',
                                sortMethod: 'directed',
                                nodeSpacing: spacing,
                                levelSeparation: spacing * 1.7,
                                treeSpacing: spacing * 1.3
                            }}
                        }},
                        physics: {{enabled: false}}
                    }});
                    document.getElementById('layout').value = "tree-horizontal";
                    document.getElementById('physics').value = "false";
                    
                }} else if (layoutType === "organic") {{
                    // Organic spring layout with custom physics
                    var resetNodes = nodes.map(function(node) {{
                        return {{
                            ...node,
                            x: undefined,
                            y: undefined,
                            fixed: {{x: false, y: false}}
                        }};
                    }});
                    
                    data.nodes.clear();
                    data.nodes.add(resetNodes);
                    
                    var spacing = window.currentSpacing || 150;
                    network.setOptions({{
                        layout: {{hierarchical: false}},
                        physics: {{
                            enabled: true,
                            solver: 'barnesHut',
                            barnesHut: {{
                                gravitationalConstant: -8000,
                                centralGravity: 0.3,
                                springLength: spacing,
                                springConstant: 0.04,
                                damping: 0.09,
                                avoidOverlap: 0.5
                            }},
                            stabilization: {{
                                iterations: 200,
                                fit: true
                            }}
                        }}
                    }});
                    document.getElementById('layout').value = "organic";
                    document.getElementById('physics').value = "true";
                }}
            }};

        // Set initial layout and physics for footer controls
        document.getElementById('physics').value = "true";
        document.getElementById('layout').value = "force";

        // Make changeLayout available globally
        window.changeLayout = changeLayout;
        
        // Store current layout spacing
        window.currentSpacing = 150;
        
        // Update layout spacing
        window.updateLayoutSpacing = function(spacing) {{
            window.currentSpacing = parseInt(spacing);
            // Re-apply current layout with new spacing
            var currentLayout = document.getElementById('layout').value;
            changeLayout(currentLayout);
        }};
        
        // Toggle physics
        window.togglePhysics = function(enabled) {{
            if (window.network) {{
                window.network.setOptions({{ physics: {{ enabled: enabled }} }});
            }}
        }};

        // Export as PNG
        window.exportToPng = function() {{
            try {{
                // Wait for network to be ready
                if (!window.network) {{
                    throw new Error('Network not initialized');
                }}
                
                // Get the canvas from the network
                var canvas = window.network.canvas.frame.canvas;
                if (!canvas) {{
                    throw new Error('Canvas not found. Please wait for the graph to load completely.');
                }}
                
                // Create a temporary canvas with higher resolution
                var tempCanvas = document.createElement('canvas');
                var ctx = tempCanvas.getContext('2d');
                var scale = 2; // Higher resolution
                
                // Set the temporary canvas dimensions
                tempCanvas.width = canvas.width * scale;
                tempCanvas.height = canvas.height * scale;
                
                // Scale and draw the original canvas
                ctx.scale(scale, scale);
                ctx.drawImage(canvas, 0, 0);
                
                // Create download link
                var link = document.createElement('a');
                link.href = tempCanvas.toDataURL('image/png');
                link.download = 'callflow-graph-' + new Date().toISOString().slice(0, 10) + '.png';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                // Clean up
                tempCanvas = null;
            }} catch (error) {{
                console.error('PNG export error:', error);
                alert('Error exporting PNG: ' + (error.message || 'Unknown error occurred'));
            }}
        }};

        // Export as JSON
        window.exportToJson = function() {{
            try {{
                // Use the original nodes and edges data instead of network.getData()
                if (!nodes || !edges) {{
                    throw new Error('Graph data not available');
                }}
                
                var exportData = {{
                    metadata: {{
                        total_nodes: nodes.length,
                        total_edges: edges.length,
                        duration: Number('{duration}'),
                        export_timestamp: new Date().toISOString(),
                        version: "callflow-tracer",
                        title: "{title}"
                    }},
                    nodes: nodes,
                    edges: edges
                }};
                
                // Create a Blob with the JSON data
                var dataStr = JSON.stringify(exportData, null, 2);
                var dataBlob = new Blob([dataStr], {{type: 'application/json'}});
                
                // Create download link
                var link = document.createElement('a');
                var url = URL.createObjectURL(dataBlob);
                
                link.href = url;
                link.download = 'callflow-graph-' + new Date().toISOString().slice(0, 10) + '.json';
                
                // Add to document, trigger download, then clean up
                document.body.appendChild(link);
                link.click();
                
                // Show success message
                console.log('JSON export successful:', exportData.metadata);
                
                // Clean up
                setTimeout(function() {{
                    document.body.removeChild(link);
                    URL.revokeObjectURL(url);
                }}, 100);
                
            }} catch (error) {{
                console.error('JSON export error:', error);
                console.error('Nodes available:', !!nodes, 'Edges available:', !!edges);
                console.error('Nodes length:', nodes ? nodes.length : 'undefined');
                console.error('Edges length:', edges ? edges.length : 'undefined');
                alert('Error exporting JSON: ' + (error.message || 'Unknown error occurred') + 
                      '\\n\\nPlease check the browser console for more details.');
            }}
        }};

        // --- Footer Controls ---

        // Physics toggle (footer)
        document.getElementById('physics').addEventListener('change', function() {{
            var enabled = this.value === 'true';
            if (window.network) {{
                window.network.setOptions({{ physics: {{ enabled: enabled }} }});
            }}
        }});

            // Layout select (footer)
            document.getElementById('layout').addEventListener('change', function() {{
                if (!window.network) return;
                if (this.value === 'hierarchical') {{
                    window.network.setOptions({{
                        layout: {{
                            hierarchical: {{
                                enabled: true,
                                direction: 'UD',
                                sortMethod: 'directed'
                            }}
                        }},
                        physics: {{ enabled: false }}
                    }});
                    document.getElementById('layout').value = "hierarchical";
                    document.getElementById('physics').value = "false";
                }} else {{
                    window.network.setOptions({{
                        layout: {{ hierarchical: false }},
                        physics: {{ enabled: true, solver: "forceAtlas2Based" }}
                    }});
                    document.getElementById('layout').value = "force";
                    document.getElementById('physics').value = "true";
                }}
            }});

            // Populate module filter dropdown
            const modulesSet = new Set();
            nodes.forEach(n => {{
                if (n.module) {{
                    modulesSet.add(n.module);
                }} else {{
                    modulesSet.add('__main__');  // Handle nodes without module
                }}
            }});
            
            const modulesArr = Array.from(modulesSet).sort();
            const filterSelect = document.getElementById('filter');
            
            // Remove all existing options except "All modules"
            while (filterSelect.options.length > 1) {{
                filterSelect.remove(1);
            }}
            
            // Add sorted module options
            modulesArr.forEach(module => {{
                const option = document.createElement('option');
                option.value = module;
                option.textContent = module === '__main__' ? 'Main Module' : module;
                filterSelect.appendChild(option);
            }});

            // Add module filter functionality
            filterSelect.addEventListener('change', function() {{
                const selectedModule = this.value;
                
                if (selectedModule === '') {{
                    // Show all nodes and edges
                    data.nodes.clear();
                    data.edges.clear();
                    data.nodes.add(window.allNodes.get());
                    data.edges.add(window.allEdges.get());
                    console.log('Filter: Showing all modules');
                }} else {{
                    // Filter nodes by selected module
                    const filteredNodes = window.allNodes.get().filter(node => {{
                        if (selectedModule === '__main__') {{
                            return !node.module || node.module === '' || node.module === '__main__';
                        }}
                        return node.module === selectedModule;
                    }});
                    
                    // Get IDs of filtered nodes
                    const filteredNodeIds = new Set(filteredNodes.map(node => node.id));
                    
                    // Filter edges that connect filtered nodes
                    const filteredEdges = window.allEdges.get().filter(edge => 
                        filteredNodeIds.has(edge.from) && filteredNodeIds.has(edge.to)
                    );
                    
                    // Update the network data
                    data.nodes.clear();
                    data.edges.clear();
                    data.nodes.add(filteredNodes);
                    data.edges.add(filteredEdges);
                    
                    console.log(`Filter: Showing module '${{selectedModule}}' - ${{filteredNodes.length}} nodes, ${{filteredEdges.length}} edges`);
                }}
                
                // Fit the network to show all visible nodes
                setTimeout(() => {{
                    if (window.network) {{
                        window.network.fit({{
                            animation: {{
                                duration: 500,
                                easingFunction: 'easeInOutQuad'
                            }}
                        }});
                    }}
                }}, 100);
            }});

            // Add some styling on load
            if (window.network) {{
                window.network.on("stabilizationIterationsDone", function() {{
                    // Keep physics enabled for force-directed by default
                    // window.network.setOptions({{ physics: false }});
                }});

                // Set initial layout and physics to force-directed and enabled
                window.network.setOptions({{
                    layout: {{hierarchical: false}},
                    physics: {{enabled: true, solver: "forceAtlas2Based"}}
                }});
            }}
            document.getElementById('layout-select').value = "force";
            document.getElementById('layout').value = "force";
            document.getElementById('physics').value = "true";

        }});

        // CPU Profile Toggle Function
        function toggleCpuProfile() {{
            const content = document.getElementById('cpu-content');
            const toggle = document.getElementById('cpu-toggle');
            
            if (content && toggle) {{
                if (content.classList.contains('expanded')) {{
                    content.classList.remove('expanded');
                    toggle.textContent = '▼';
                    toggle.style.transform = 'rotate(0deg)';
                }} else {{
                    content.classList.add('expanded');
                    toggle.textContent = '▲';
                    toggle.style.transform = 'rotate(180deg)';
                }}
            }}
        }}
    </script>
</body>
</html>"""
    
    # Prepare blocks for optional profiling stats
    memory_current_block = (
        f'<div class="stat"><div class="stat-value">{memory_current:.2f}MB</div><div class="stat-label">Memory (current)</div></div>'
        if profiling_present else ''
    )
    memory_peak_block = (
        f'<div class="stat"><div class="stat-value">{memory_peak:.2f}MB</div><div class="stat-label">Memory (peak)</div></div>'
        if profiling_present else ''
    )
    io_wait_block = (
        f'<div class="stat"><div class="stat-value">{io_wait:.3f}s</div><div class="stat-label">I/O wait</div></div>'
        if profiling_present else ''
    )
    # Extract CPU metrics for easier template formatting
    cpu_total_time = cpu_profile_metrics.get('total_time', 0.0)
    cpu_total_calls = cpu_profile_metrics.get('total_calls', 0)
    cpu_hot_spots_count = len(cpu_profile_metrics.get('top_functions', []))
    
    health_indicators = cpu_profile_metrics.get('health_indicators', {})
    exec_time_status = health_indicators.get('execution_time', {}).get('status', 'good')
    exec_time_message = health_indicators.get('execution_time', {}).get('message', 'N/A')
    call_eff_status = health_indicators.get('call_efficiency', {}).get('status', 'good')
    call_eff_message = health_indicators.get('call_efficiency', {}).get('message', 'N/A')
    hot_spots_status = health_indicators.get('hot_spots', {}).get('status', 'good')
    hot_spots_message = health_indicators.get('hot_spots', {}).get('message', 'N/A')
    
    cpu_profile_block = (
        f'''<div class="cpu-profile-section">
            <div class="cpu-profile-header" onclick="toggleCpuProfile()">
                <div class="cpu-profile-title">
                    <span class="cpu-profile-icon">🔥</span>
                    CPU Profile Analysis (cProfile)
                </div>
                <span class="cpu-profile-toggle" id="cpu-toggle">▼</span>
            </div>
            <div class="cpu-profile-content" id="cpu-content">
                <div class="cpu-profile-explanation">
                    <h4>📊 What This Data Means</h4>
                    <p><strong>CPU Profiling</strong> shows how much time your program spends in each function, helping identify performance bottlenecks.</p>
                    <p><strong>Key Terms:</strong></p>
                    <p>• <strong>ncalls:</strong> Number of calls to the function</p>
                    <p>• <strong>tottime:</strong> Total time spent in the function (excluding sub-calls)</p>
                    <p>• <strong>cumtime:</strong> Cumulative time (including sub-calls)</p>
                    <p>• <strong>percall:</strong> Time per call (tottime/ncalls or cumtime/ncalls)</p>
                </div>
                
                <div class="cpu-metrics">
                    <div class="cpu-metric">
                        <div class="cpu-metric-label">Total Execution Time</div>
                        <div class="cpu-metric-value">{cpu_total_time:.3f}s</div>
                        <div class="cpu-metric-health health-{exec_time_status}">
                            {exec_time_message}
                        </div>
                    </div>
                    <div class="cpu-metric">
                        <div class="cpu-metric-label">Function Calls</div>
                        <div class="cpu-metric-value">{cpu_total_calls:,}</div>
                        <div class="cpu-metric-health health-{call_eff_status}">
                            {call_eff_message}
                        </div>
                    </div>
                    <div class="cpu-metric">
                        <div class="cpu-metric-label">Performance Distribution</div>
                        <div class="cpu-metric-value">{cpu_hot_spots_count} Hot Spots</div>
                        <div class="cpu-metric-health health-{hot_spots_status}">
                            {hot_spots_message}
                        </div>
                    </div>
                </div>
                
                <div class="cpu-profile-legend">
                    <h5>🎯 Performance Health Guide</h5>
                    <div class="legend-item">
                        <span class="legend-term">🟢 Excellent:</span>
                        <span>Optimal performance, no action needed</span>
                    </div>
                    <div class="legend-item">
                        <span class="legend-term">🔵 Good:</span>
                        <span>Good performance, minor optimizations possible</span>
                    </div>
                    <div class="legend-item">
                        <span class="legend-term">🟡 Warning:</span>
                        <span>Moderate performance, consider optimization</span>
                    </div>
                    <div class="legend-item">
                        <span class="legend-term">🔴 Poor:</span>
                        <span>Performance issues detected, optimization recommended</span>
                    </div>
                </div>
                
                <h4>📋 Detailed Profile Data</h4>
                <pre class="cpu-profile-pre">{cpu_profile_text}</pre>
            </div>
        </div>'''
        if profiling_present and cpu_profile_text else ''
    )
    vis_js_script = f'<script type="text/javascript" src="{vis_js_cdn}"></script>' if include_vis_js else ''

    # Format the template with the JSON data and blocks
    return html_template.format(
        title=title,
        nodes_json=nodes_json,
        edges_json=edges_json,
        total_nodes=graph_data['metadata']['total_nodes'],
        total_edges=graph_data['metadata']['total_edges'],
        duration=graph_data['metadata']['duration'],
        memory_current_block=memory_current_block,
        memory_peak_block=memory_peak_block,
        io_wait_block=io_wait_block,
        cpu_profile_block=cpu_profile_block,
        vis_js_script=vis_js_script
    )



def _generate_html_3d(graph_data: dict, title: str, profiling_stats: Optional[dict] = None) -> str:
    """
    Generate 3D interactive HTML visualization using Three.js.
    
    Args:
        graph_data: Dictionary containing graph data
        title: Title for the page
        profiling_stats: Optional profiling statistics
        
    Returns:
        Complete HTML string with 3D visualization
    """
    nodes = graph_data['nodes']
    edges = graph_data['edges']
    
    # Prepare node data for 3D
    nodes_3d = []
    for node in nodes:
        nodes_3d.append({
            'id': node['full_name'],
            'label': node['name'],
            'module': node.get('module', ''),
            'call_count': node['call_count'],
            'total_time': node['total_time'],
            'avg_time': node['avg_time']
        })
    
    # Prepare edge data for 3D
    edges_3d = []
    for edge in edges:
        edges_3d.append({
            'source': edge['caller'],
            'target': edge['callee'],
            'call_count': edge['call_count'],
            'total_time': edge['total_time']
        })
    
    nodes_json = json.dumps(nodes_3d)
    edges_json = json.dumps(edges_3d)
    
    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
{{ ... }}
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a0a0a;
            color: #ffffff;
            overflow: hidden;
        }}
        #container {{
            width: 100vw;
            height: 100vh;
            position: relative;
        }}
        #controls {{
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(0, 0, 0, 0.9);
            padding: 20px;
            border-radius: 10px;
            z-index: 100;
            max-width: 320px;
            max-height: calc(100vh - 40px);
            overflow-y: auto;
            overflow-x: hidden;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        }}
        #controls::-webkit-scrollbar {{
            width: 8px;
        }}
        #controls::-webkit-scrollbar-track {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        }}
        #controls::-webkit-scrollbar-thumb {{
            background: #4fc3f7;
            border-radius: 4px;
        }}
        #controls::-webkit-scrollbar-thumb:hover {{
            background: #29b6f6;
        }}
        #stats {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.8);
            padding: 20px;
            border-radius: 10px;
            z-index: 100;
            max-height: calc(100vh - 40px);
            overflow-y: auto;
        }}
        #minimap {{
            position: absolute;
            bottom: 20px;
            right: 20px;
            width: 200px;
            height: 150px;
            background: rgba(0, 0, 0, 0.8);
            border: 2px solid #4fc3f7;
            border-radius: 5px;
            z-index: 100;
        }}
        #timeline {{
            position: absolute;
            bottom: 20px;
            left: 20px;
            right: 230px;
            background: rgba(0, 0, 0, 0.9);
            padding: 15px;
            border-radius: 10px;
            z-index: 100;
            display: none;
        }}
        #timeline-controls {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }}
        #timeline-slider {{
            flex: 1;
            height: 8px;
        }}
        .timeline-btn {{
            padding: 5px 10px;
            background: #4fc3f7;
            border: none;
            border-radius: 3px;
            color: #000;
            cursor: pointer;
            font-size: 12px;
        }}
        #filterPanel {{
            position: absolute;
            top: 20px;
            left: 350px;
            background: rgba(0, 0, 0, 0.9);
            padding: 15px;
            border-radius: 10px;
            z-index: 100;
            display: none;
            max-width: 300px;
        }}
        .filter-item {{
            margin-bottom: 10px;
        }}
        .filter-item label {{
            font-size: 11px;
            color: #aaa;
        }}
        .filter-item input {{
            width: 100%;
            padding: 5px;
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 3px;
            color: #fff;
        }}
        #heatmapLegend {{
            position: absolute;
            top: 50%;
            right: 20px;
            transform: translateY(-50%);
            background: rgba(0, 0, 0, 0.8);
            padding: 15px;
            border-radius: 10px;
            z-index: 100;
            display: none;
        }}
        .heatmap-gradient {{
            width: 30px;
            height: 200px;
            background: linear-gradient(to top, #00ff00, #ffff00, #ff0000);
            border-radius: 3px;
            margin: 10px auto;
        }}
        #info {{
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: rgba(0, 0, 0, 0.8);
            padding: 15px;
            border-radius: 10px;
            z-index: 100;
            max-width: 400px;
            display: none;
        }}
        h2 {{
            font-size: 18px;
            margin-bottom: 15px;
            color: #4fc3f7;
        }}
        .control-group {{
            margin-bottom: 15px;
        }}
        label {{
            display: block;
            margin-bottom: 5px;
            font-size: 12px;
            color: #aaa;
        }}
        select, input[type="range"] {{
            width: 100%;
            padding: 8px;
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 5px;
            color: #fff;
            font-size: 14px;
        }}
        button {{
            width: 100%;
            padding: 10px;
            margin-top: 8px;
            background: #4fc3f7;
            border: none;
            border-radius: 5px;
            color: #000;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.3s;
            font-size: 13px;
        }}
        button:hover {{
            background: #29b6f6;
        }}
        button:active {{
            transform: scale(0.98);
        }}
        .section-header {{
            color: #4fc3f7;
            font-size: 14px;
            font-weight: bold;
            margin: 15px 0 10px 0;
            padding-bottom: 5px;
            border-bottom: 1px solid #333;
        }}
        .stat-item {{
            margin-bottom: 10px;
            font-size: 14px;
        }}
        .stat-label {{
            color: #aaa;
            font-size: 12px;
        }}
        .stat-value {{
            color: #4fc3f7;
            font-size: 18px;
            font-weight: bold;
        }}
        .legend {{
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #333;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 8px;
            font-size: 12px;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 3px;
            margin-right: 10px;
        }}
        #loading {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 24px;
            color: #4fc3f7;
            z-index: 200;
        }}
        .checkbox-group {{
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }}
        .checkbox-group input[type="checkbox"] {{
            width: auto;
            margin-right: 8px;
        }}
        .checkbox-group label {{
            margin: 0;
            cursor: pointer;
        }}
        #tooltip {{
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 10px;
            border-radius: 5px;
            pointer-events: none;
            display: none;
            z-index: 1000;
            font-size: 12px;
            max-width: 300px;
        }}
        #codePreview {{
            position: absolute;
            background: rgba(10, 10, 10, 0.95);
            color: #e0e0e0;
            padding: 15px;
            border-radius: 8px;
            border: 2px solid #4fc3f7;
            display: none;
            z-index: 1001;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            max-width: 600px;
            max-height: 400px;
            overflow-y: auto;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.8);
        }}
        #codePreview::-webkit-scrollbar {{
            width: 6px;
        }}
        #codePreview::-webkit-scrollbar-thumb {{
            background: #4fc3f7;
            border-radius: 3px;
        }}
        .code-header {{
            color: #4fc3f7;
            font-weight: bold;
            margin-bottom: 10px;
            padding-bottom: 5px;
            border-bottom: 1px solid #333;
        }}
        .code-line {{
            display: flex;
            padding: 2px 0;
        }}
        .line-number {{
            color: #666;
            margin-right: 15px;
            min-width: 30px;
            text-align: right;
            user-select: none;
        }}
        .line-content {{
            color: #e0e0e0;
            white-space: pre;
        }}
        .keyword {{
            color: #c678dd;
            font-weight: bold;
        }}
        .string {{
            color: #98c379;
        }}
        .comment {{
            color: #5c6370;
            font-style: italic;
        }}
        .function {{
            color: #61afef;
        }}
        .number {{
            color: #d19a66;
        }}
        .docstring {{
            color: #98c379;
            font-style: italic;
        }}
        .code-footer {{
            margin-top: 10px;
            padding-top: 5px;
            border-top: 1px solid #333;
            font-size: 10px;
            color: #888;
        }}
        .perf-indicator {{
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 5px;
        }}
    </style>
</head>
<body>
    <div id="loading">Loading 3D Visualization...</div>
    <div id="container"></div>
    
    <div id="controls">
        <h2 style="margin-bottom: 15px;">🎮 Controls</h2>
        
        <div class="section-header">📐 Layout</div>
        <div class="control-group">
            <label>Algorithm</label>
            <select id="layout">
                <option value="force">Force-Directed 3D</option>
                <option value="sphere">Sphere</option>
                <option value="helix">Helix</option>
                <option value="grid">Grid 3D</option>
                <option value="tree">Tree 3D</option>
            </select>
        </div>
        <div class="control-group">
            <label>Spread: <span id="spreadValue">500</span></label>
            <input type="range" id="spread" min="100" max="1000" value="500">
        </div>
        
        <div class="section-header">🎨 Appearance</div>
        <div class="control-group">
            <label>Node Size: <span id="nodeSizeValue">15</span></label>
            <input type="range" id="nodeSize" min="5" max="30" value="15">
        </div>
        <div class="control-group">
            <label>Edge Thickness: <span id="edgeThicknessValue">2</span></label>
            <input type="range" id="edgeThickness" min="1" max="5" value="2">
        </div>
        <div class="control-group">
            <label>Node Opacity: <span id="nodeOpacityValue">100</span>%</label>
            <input type="range" id="nodeOpacity" min="10" max="100" value="100">
        </div>
        <div class="control-group">
            <label>Background Color</label>
            <select id="bgColor">
                <option value="0x0a0a0a">Dark (Default)</option>
                <option value="0x1a1a2e">Deep Blue</option>
                <option value="0x0f0f23">Midnight</option>
                <option value="0x1a0a1a">Purple Dark</option>
                <option value="0xffffff">White</option>
            </select>
        </div>
        
        <div class="section-header">✨ Effects</div>
        <div class="checkbox-group">
            <input type="checkbox" id="showLabels" checked>
            <label for="showLabels">Show Labels</label>
        </div>
        <div class="checkbox-group">
            <input type="checkbox" id="showEdges" checked>
            <label for="showEdges">Show Connections</label>
        </div>
        <div class="checkbox-group">
            <input type="checkbox" id="pulseNodes" checked>
            <label for="pulseNodes">Pulse Animation</label>
        </div>
        <div class="checkbox-group">
            <input type="checkbox" id="particleEffect">
            <label for="particleEffect">Particle Effects</label>
        </div>
        <div class="checkbox-group">
            <input type="checkbox" id="showCallPath">
            <label for="showCallPath">Highlight Paths</label>
        </div>
        <div class="checkbox-group">
            <input type="checkbox" id="showGrid">
            <label for="showGrid">Show Grid</label>
        </div>
        <div class="checkbox-group">
            <input type="checkbox" id="showStats" checked>
            <label for="showStats">Show Stats Panel</label>
        </div>
        <div class="checkbox-group">
            <input type="checkbox" id="enableCodePreview" checked>
            <label for="enableCodePreview">Code Preview on Hover</label>
        </div>
        
        <div class="section-header">🎬 Animation</div>
        <div class="control-group">
            <label>Rotation Speed: <span id="rotationSpeedValue">0</span></label>
            <input type="range" id="rotationSpeed" min="0" max="100" value="0">
        </div>
        <div class="control-group">
            <label>Flow Speed: <span id="animSpeedValue">5</span>x</label>
            <input type="range" id="animSpeed" min="1" max="10" value="5">
        </div>
        <button onclick="playAnimation()">▶️ Play Flow Animation</button>
        <button onclick="toggleAnimation()">⏸️ Pause/Resume</button>
        <button onclick="toggleTimeline()">⏱️ Timeline Playback</button>
        
        <div class="section-header">🎯 Navigation</div>
        <button onclick="resetView()">🔄 Reset View</button>
        <button onclick="focusOnSlowest()">🐌 Focus Slowest</button>
        <button onclick="focusOnFastest()">⚡ Focus Fastest</button>
        <button onclick="fitToView()">📏 Fit All Nodes</button>
        <button onclick="topView()">⬆️ Top View</button>
        <button onclick="sideView()">↔️ Side View</button>
        
        <div class="section-header">🔍 Analysis</div>
        <button onclick="showCallChain()">🔗 Show Call Chain</button>
        <button onclick="highlightModule()">📦 Filter by Module</button>
        <button onclick="findNode()">🔎 Search Function</button>
        <button onclick="showHotspots()">🔥 Show Hotspots</button>
        <button onclick="compareNodes()">⚖️ Compare Selected</button>
        <button onclick="toggleFilters()">🎛️ Advanced Filters</button>
        <button onclick="toggleHeatmap()">🔥 Heatmap Mode</button>
        <button onclick="showCriticalPath()">🛤️ Critical Path</button>
        <button onclick="clusterByModule()">📦 Auto-Cluster</button>
        
        <div class="section-header">💾 Export & Share</div>
        <button onclick="takeScreenshot()">📸 Screenshot</button>
        <button onclick="exportData()">💾 Export JSON</button>
        <button onclick="copyToClipboard()">📋 Copy Stats</button>
        <button onclick="generateShareableURL()">🔗 Generate Share Link</button>
        <button onclick="saveToLocalStorage()">💾 Save State</button>
        <button onclick="loadFromLocalStorage()">📂 Load State</button>
        
        <div class="legend">
            <h5 style="margin-bottom: 10px; color: #4fc3f7;">Performance</h5>
            <div class="legend-item">
                <div class="legend-color" style="background: #00ff00;"></div>
                <span>Fast (&lt;10ms)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #ffff00;"></div>
                <span>Medium (10-100ms)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #ff0000;"></div>
                <span>Slow (&gt;100ms)</span>
            </div>
            <h5 style="margin: 15px 0 10px 0; color: #4fc3f7;">Connections</h5>
            <div class="legend-item">
                <div class="legend-color" style="background: #00d4ff;"></div>
                <span>Call Flow Lines</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #ff9800;"></div>
                <span>Direction Arrows</span>
            </div>
        </div>
    </div>
    
    <div id="stats">
        <h2>📊 Statistics</h2>
        <div class="stat-item">
            <div class="stat-label">Functions</div>
            <div class="stat-value">{graph_data['metadata']['total_nodes']}</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Relationships</div>
            <div class="stat-value">{graph_data['metadata']['total_edges']}</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Duration</div>
            <div class="stat-value">{graph_data['metadata']['duration']:.3f}s</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">FPS</div>
            <div class="stat-value" id="fpsCounter">60</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Complexity</div>
            <div class="stat-value" id="complexityScore">-</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Max Depth</div>
            <div class="stat-value" id="maxDepth">-</div>
        </div>
        
        <button onclick="toggleCharts()" style="width: 100%; margin-top: 15px; padding: 8px; background: #4fc3f7; border: none; border-radius: 5px; color: #000; font-weight: bold; cursor: pointer;">
            📊 Show Charts
        </button>
    </div>
    
    <!-- Charts Panel -->
    <div id="chartsPanel" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(0, 0, 0, 0.95); padding: 30px; border-radius: 15px; z-index: 200; display: none; max-width: 900px; max-height: 80vh; overflow-y: auto; border: 2px solid #4fc3f7;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h2 style="color: #4fc3f7; margin: 0;">📊 Performance Analytics</h2>
            <button onclick="toggleCharts()" style="background: #ff5252; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-weight: bold;">✕ Close</button>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px;">
                <h3 style="color: #4fc3f7; margin-bottom: 10px; font-size: 14px;">Performance Distribution</h3>
                <canvas id="perfChart" width="400" height="300"></canvas>
            </div>
            
            <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px;">
                <h3 style="color: #4fc3f7; margin-bottom: 10px; font-size: 14px;">Call Depth Histogram</h3>
                <canvas id="depthChart" width="400" height="300"></canvas>
            </div>
            
            <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px;">
                <h3 style="color: #4fc3f7; margin-bottom: 10px; font-size: 14px;">Top Functions by Time</h3>
                <canvas id="topFunctionsChart" width="400" height="300"></canvas>
            </div>
            
            <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px;">
                <h3 style="color: #4fc3f7; margin-bottom: 10px; font-size: 14px;">Call Frequency</h3>
                <canvas id="callFreqChart" width="400" height="300"></canvas>
            </div>
        </div>
    </div>
    
    <div id="info">
        <h2>ℹ️ Node Information</h2>
        <div id="infoContent"></div>
    </div>
    
    <div id="tooltip"></div>
    
    <!-- Code Preview Panel -->
    <div id="codePreview">
        <div class="code-header" id="codeHeader">Function Code</div>
        <div id="codeContent"></div>
        <div class="code-footer" id="codeFooter">
            Press 'C' to toggle code preview | Right-click to copy
        </div>
    </div>
    
    <!-- Minimap -->
    <canvas id="minimap"></canvas>
    
    <!-- Timeline Playback -->
    <div id="timeline">
        <div id="timeline-controls">
            <button class="timeline-btn" onclick="timelinePlay()">▶️</button>
            <button class="timeline-btn" onclick="timelinePause()">⏸️</button>
            <button class="timeline-btn" onclick="timelineReset()">⏮️</button>
            <input type="range" id="timeline-slider" min="0" max="100" value="0">
            <span id="timeline-time" style="color: #4fc3f7; font-size: 12px;">0.00s</span>
            <select id="timeline-speed" style="background: #1a1a1a; color: #fff; border: 1px solid #333; padding: 3px;">
                <option value="0.5">0.5x</option>
                <option value="1" selected>1x</option>
                <option value="2">2x</option>
                <option value="5">5x</option>
                <option value="10">10x</option>
            </select>
        </div>
        <div style="font-size: 11px; color: #aaa;">Timeline: Replay execution chronologically</div>
    </div>
    
    <!-- Advanced Filters -->
    <div id="filterPanel">
        <h3 style="color: #4fc3f7; margin-bottom: 10px;">🎛️ Advanced Filters</h3>
        <div class="filter-item">
            <label>Min Execution Time (ms)</label>
            <input type="number" id="filter-min-time" value="0" min="0">
        </div>
        <div class="filter-item">
            <label>Max Execution Time (ms)</label>
            <input type="number" id="filter-max-time" value="10000" min="0">
        </div>
        <div class="filter-item">
            <label>Min Call Count</label>
            <input type="number" id="filter-min-calls" value="0" min="0">
        </div>
        <div class="filter-item">
            <label>Function Name Contains</label>
            <input type="text" id="filter-name" placeholder="Enter text...">
        </div>
        <button onclick="applyFilters()" style="width: 100%; margin-top: 10px;">Apply Filters</button>
        <button onclick="clearFilters()" style="width: 100%; margin-top: 5px; background: #666;">Clear Filters</button>
    </div>
    
    <!-- Heatmap Legend -->
    <div id="heatmapLegend">
        <h4 style="color: #4fc3f7; margin-bottom: 10px;">🔥 Heatmap</h4>
        <div class="heatmap-gradient"></div>
        <div style="font-size: 11px; color: #aaa; text-align: center;">
            <div>Slow</div>
            <div style="margin: 60px 0;">Medium</div>
            <div>Fast</div>
        </div>
        <select id="heatmap-metric" style="width: 100%; background: #1a1a1a; color: #fff; border: 1px solid #333; padding: 5px; margin-top: 10px;">
            <option value="time">Execution Time</option>
            <option value="calls">Call Frequency</option>
            <option value="total">Total Time</option>
        </select>
    </div>

    <script>
        const nodes = {nodes_json};
        const edges = {edges_json};
        
        let scene, camera, renderer, controls;
        let nodeMeshes = [];
        let nodeSprites = [];
        let edgeLines = [];
        let particles = [];
        let animationId;
        let isAnimating = true;
        let rotationSpeed = 0;
        let raycaster = new THREE.Raycaster();
        let mouse = new THREE.Vector2();
        let selectedNode = null;
        let hoveredNode = null;
        
        function init() {{
            // Scene
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0a0a0a);
            scene.fog = new THREE.Fog(0x0a0a0a, 1000, 3000);
            
            // Camera
            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 1, 5000);
            camera.position.z = 1000;
            
            // Renderer
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.getElementById('container').appendChild(renderer.domElement);
            
            // Controls
            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            
            // Lights
            const ambientLight = new THREE.AmbientLight(0x404040, 2);
            scene.add(ambientLight);
            
            const pointLight = new THREE.PointLight(0xffffff, 1, 2000);
            pointLight.position.set(500, 500, 500);
            scene.add(pointLight);
            
            // Create graph
            createGraph('force');
            
            // Event listeners
            document.getElementById('layout').addEventListener('change', (e) => {{
                createGraph(e.target.value);
            }});
            
            document.getElementById('nodeSize').addEventListener('input', (e) => {{
                const value = parseInt(e.target.value);
                document.getElementById('nodeSizeValue').textContent = value;
                updateNodeSize(value);
            }});
            
            document.getElementById('spread').addEventListener('input', (e) => {{
                const value = parseInt(e.target.value);
                document.getElementById('spreadValue').textContent = value;
                createGraph(document.getElementById('layout').value);
            }});
            
            document.getElementById('rotationSpeed').addEventListener('input', (e) => {{
                const value = parseInt(e.target.value);
                document.getElementById('rotationSpeedValue').textContent = value;
                rotationSpeed = value / 1000;
            }});
            
            document.getElementById('nodeOpacity').addEventListener('input', (e) => {{
                const value = parseInt(e.target.value);
                document.getElementById('nodeOpacityValue').textContent = value;
                updateNodeOpacity(value / 100);
            }});
            
            document.getElementById('bgColor').addEventListener('change', (e) => {{
                scene.background = new THREE.Color(parseInt(e.target.value));
            }});
            
            document.getElementById('showGrid').addEventListener('change', (e) => {{
                toggleGrid(e.target.checked);
            }});
            
            document.getElementById('showStats').addEventListener('change', (e) => {{
                document.getElementById('stats').style.display = e.target.checked ? 'block' : 'none';
            }});
            
            // New feature event listeners
            document.getElementById('showLabels').addEventListener('change', (e) => {{
                toggleLabels(e.target.checked);
            }});
            
            document.getElementById('showEdges').addEventListener('change', (e) => {{
                toggleEdges(e.target.checked);
            }});
            
            document.getElementById('pulseNodes').addEventListener('change', (e) => {{
                // Pulse animation handled in animate loop
            }});
            
            document.getElementById('particleEffect').addEventListener('change', (e) => {{
                if (e.target.checked) {{
                    createParticles();
                }} else {{
                    removeParticles();
                }}
            }});
            
            // New control event listeners
            document.getElementById('showCallPath').addEventListener('change', (e) => {{
                // Call path highlighting handled in showCallChain
            }});
            
            document.getElementById('edgeThickness').addEventListener('input', (e) => {{
                const value = parseInt(e.target.value);
                document.getElementById('edgeThicknessValue').textContent = value;
                updateEdgeThickness(value);
            }});
            
            document.getElementById('animSpeed').addEventListener('input', (e) => {{
                const value = parseInt(e.target.value);
                document.getElementById('animSpeedValue').textContent = value;
            }});
            
            // Mouse events for interaction
            renderer.domElement.addEventListener('mousemove', onMouseMove);
            renderer.domElement.addEventListener('click', onMouseClick);
            
            // Keyboard shortcuts
            document.addEventListener('keydown', onKeyDown);
            
            window.addEventListener('resize', onWindowResize);
            
            // Hide loading
            document.getElementById('loading').style.display = 'none';
            
            // Start animation
            animate();
        }}
        
        function createGraph(layoutType) {{
            // Clear existing
            nodeMeshes.forEach(mesh => scene.remove(mesh));
            nodeSprites.forEach(sprite => scene.remove(sprite));
            edgeLines.forEach(line => scene.remove(line));
            nodeMeshes = [];
            nodeSprites = [];
            edgeLines = [];
            
            const spread = parseInt(document.getElementById('spread').value);
            const positions = calculatePositions(layoutType, nodes.length, spread);
            
            // Create node map
            const nodeMap = {{}};
            nodes.forEach((node, i) => {{
                nodeMap[node.id] = i;
            }});
            
            // Create nodes
            nodes.forEach((node, i) => {{
                const pos = positions[i];
                const color = getNodeColor(node.avg_time);
                const size = Math.max(5, Math.min(30, node.call_count * 2));
                
                const geometry = new THREE.SphereGeometry(size, 32, 32);
                const material = new THREE.MeshPhongMaterial({{
                    color: color,
                    emissive: color,
                    emissiveIntensity: 0.3,
                    shininess: 100
                }});
                
                const mesh = new THREE.Mesh(geometry, material);
                mesh.position.set(pos.x, pos.y, pos.z);
                mesh.userData = node;
                
                scene.add(mesh);
                nodeMeshes.push(mesh);
                
                // Add label sprite
                const sprite = createTextSprite(node.label);
                sprite.position.set(pos.x, pos.y + size + 10, pos.z);
                scene.add(sprite);
                nodeSprites.push(sprite);
            }});
            
            // Create edges with arrows
            edges.forEach(edge => {{
                const sourceIdx = nodeMap[edge.source];
                const targetIdx = nodeMap[edge.target];
                
                if (sourceIdx !== undefined && targetIdx !== undefined) {{
                    const sourcePos = nodeMeshes[sourceIdx].position;
                    const targetPos = nodeMeshes[targetIdx].position;
                    
                    // Create line
                    const geometry = new THREE.BufferGeometry().setFromPoints([
                        sourcePos,
                        targetPos
                    ]);
                    
                    // Brighter, more visible color
                    const material = new THREE.LineBasicMaterial({{
                        color: 0x00d4ff,  // Bright cyan
                        opacity: 0.7,
                        transparent: true,
                        linewidth: 2
                    }});
                    
                    const line = new THREE.Line(geometry, material);
                    scene.add(line);
                    edgeLines.push(line);
                    
                    // Create arrow head at target
                    const direction = new THREE.Vector3().subVectors(targetPos, sourcePos);
                    const length = direction.length();
                    direction.normalize();
                    
                    // Position arrow slightly before target node
                    const arrowPos = targetPos.clone().sub(direction.multiplyScalar(20));
                    
                    // Create cone for arrow head
                    const arrowGeometry = new THREE.ConeGeometry(5, 15, 8);
                    const arrowMaterial = new THREE.MeshBasicMaterial({{
                        color: 0xff9800,  // Orange for visibility
                        transparent: true,
                        opacity: 0.9
                    }});
                    const arrow = new THREE.Mesh(arrowGeometry, arrowMaterial);
                    
                    // Position and orient arrow
                    arrow.position.copy(arrowPos);
                    arrow.lookAt(targetPos);
                    arrow.rotateX(Math.PI / 2);  // Align cone tip with direction
                    
                    scene.add(arrow);
                    edgeLines.push(arrow);  // Store for toggling
                }}
            }});
        }}
        
        function calculatePositions(layoutType, count, spread) {{
            const positions = [];
            
            if (layoutType === 'force') {{
                // Force-directed 3D
                for (let i = 0; i < count; i++) {{
                    positions.push({{
                        x: (Math.random() - 0.5) * spread,
                        y: (Math.random() - 0.5) * spread,
                        z: (Math.random() - 0.5) * spread
                    }});
                }}
            }} else if (layoutType === 'sphere') {{
                // Sphere layout
                const radius = spread / 2;
                for (let i = 0; i < count; i++) {{
                    const phi = Math.acos(-1 + (2 * i) / count);
                    const theta = Math.sqrt(count * Math.PI) * phi;
                    
                    positions.push({{
                        x: radius * Math.cos(theta) * Math.sin(phi),
                        y: radius * Math.sin(theta) * Math.sin(phi),
                        z: radius * Math.cos(phi)
                    }});
                }}
            }} else if (layoutType === 'helix') {{
                // Helix layout
                const radius = spread / 3;
                const height = spread;
                for (let i = 0; i < count; i++) {{
                    const angle = (i / count) * Math.PI * 4;
                    const y = (i / count) * height - height / 2;
                    
                    positions.push({{
                        x: radius * Math.cos(angle),
                        y: y,
                        z: radius * Math.sin(angle)
                    }});
                }}
            }} else if (layoutType === 'grid') {{
                // 3D Grid
                const size = Math.ceil(Math.pow(count, 1/3));
                const spacing = spread / size;
                let idx = 0;
                
                for (let x = 0; x < size && idx < count; x++) {{
                    for (let y = 0; y < size && idx < count; y++) {{
                        for (let z = 0; z < size && idx < count; z++) {{
                            positions.push({{
                                x: (x - size/2) * spacing,
                                y: (y - size/2) * spacing,
                                z: (z - size/2) * spacing
                            }});
                            idx++;
                        }}
                    }}
                }}
            }} else if (layoutType === 'tree') {{
                // 3D Tree
                const levels = Math.ceil(Math.log2(count + 1));
                const levelHeight = spread / levels;
                let idx = 0;
                
                for (let level = 0; level < levels && idx < count; level++) {{
                    const nodesInLevel = Math.pow(2, level);
                    const radius = spread / (level + 2);
                    
                    for (let i = 0; i < nodesInLevel && idx < count; i++) {{
                        const angle = (i / nodesInLevel) * Math.PI * 2;
                        positions.push({{
                            x: radius * Math.cos(angle),
                            y: level * levelHeight - spread/2,
                            z: radius * Math.sin(angle)
                        }});
                        idx++;
                    }}
                }}
            }}
            
            return positions;
        }}
        
        function getNodeColor(avgTime) {{
            if (avgTime > 0.1) return 0xff0000; // Red - slow
            if (avgTime > 0.01) return 0xffff00; // Yellow - medium
            return 0x00ff00; // Green - fast
        }}
        
        function createTextSprite(text) {{
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            canvas.width = 256;
            canvas.height = 64;
            
            context.fillStyle = 'rgba(0, 0, 0, 0.8)';
            context.fillRect(0, 0, canvas.width, canvas.height);
            
            context.font = 'Bold 20px Arial';
            context.fillStyle = 'white';
            context.textAlign = 'center';
            context.fillText(text, canvas.width / 2, canvas.height / 2 + 7);
            
            const texture = new THREE.CanvasTexture(canvas);
            const material = new THREE.SpriteMaterial({{ map: texture }});
            const sprite = new THREE.Sprite(material);
            sprite.scale.set(100, 25, 1);
            
            return sprite;
        }}
        
        function updateNodeSize(size) {{
            nodeMeshes.forEach(mesh => {{
                mesh.geometry.dispose();
                mesh.geometry = new THREE.SphereGeometry(size, 32, 32);
            }});
        }}
        
        function resetView() {{
            camera.position.set(0, 0, 1000);
            controls.reset();
        }}
        
        function toggleAnimation() {{
            isAnimating = !isAnimating;
        }}
        
        function animate() {{
            animationId = requestAnimationFrame(animate);
            
            const time = Date.now() * 0.001;
            
            // Rotation animation
            if (isAnimating && rotationSpeed > 0) {{
                nodeMeshes.forEach(mesh => {{
                    mesh.rotation.y += rotationSpeed;
                }});
            }}
            
            // Pulse animation
            if (document.getElementById('pulseNodes').checked) {{
                nodeMeshes.forEach((mesh, i) => {{
                    const scale = 1 + Math.sin(time * 2 + i * 0.5) * 0.1;
                    mesh.scale.set(scale, scale, scale);
                }});
            }}
            
            // Animate particles
            if (particles.length > 0) {{
                particles.forEach(particle => {{
                    particle.position.y += particle.velocity;
                    particle.material.opacity -= 0.01;
                    if (particle.material.opacity <= 0) {{
                        scene.remove(particle);
                        particles = particles.filter(p => p !== particle);
                    }}
                }});
            }}
            
            controls.update();
            renderer.render(scene, camera);
        }}
        
        function onWindowResize() {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }}
        
        function toggleLabels(show) {{
            nodeSprites.forEach(sprite => {{
                sprite.visible = show;
            }});
        }}
        
        function toggleEdges(show) {{
            edgeLines.forEach(line => {{
                line.visible = show;
            }});
        }}
        
        function createParticles() {{
            // Create particle system around nodes
            nodeMeshes.forEach(mesh => {{
                for (let i = 0; i < 5; i++) {{
                    const geometry = new THREE.SphereGeometry(2, 8, 8);
                    const material = new THREE.MeshBasicMaterial({{
                        color: 0x4fc3f7,
                        transparent: true,
                        opacity: 0.8
                    }});
                    const particle = new THREE.Mesh(geometry, material);
                    particle.position.copy(mesh.position);
                    particle.position.x += (Math.random() - 0.5) * 50;
                    particle.position.z += (Math.random() - 0.5) * 50;
                    particle.velocity = Math.random() * 2 + 1;
                    scene.add(particle);
                    particles.push(particle);
                }}
            }});
        }}
        
        function removeParticles() {{
            particles.forEach(particle => {{
                scene.remove(particle);
            }});
            particles = [];
        }}
        
        function onMouseMove(event) {{
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
            
            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(nodeMeshes);
            
            const tooltip = document.getElementById('tooltip');
            
            if (intersects.length > 0) {{
                const mesh = intersects[0].object;
                const node = mesh.userData;
                hoveredNode = mesh;
                
                // Show tooltip
                tooltip.style.display = 'block';
                tooltip.style.left = event.clientX + 10 + 'px';
                tooltip.style.top = event.clientY + 10 + 'px';
                tooltip.innerHTML = `
                    <strong>${{node.label}}</strong><br>
                    Module: ${{node.module || 'N/A'}}<br>
                    Calls: ${{node.call_count}}<br>
                    Avg Time: ${{node.avg_time.toFixed(4)}}s<br>
                    Total Time: ${{node.total_time.toFixed(4)}}s
                `;
                
                // Show code preview
                showCodePreview(node, event.clientX, event.clientY);
                
                // Highlight hovered node
                mesh.material.emissiveIntensity = 0.8;
                document.body.style.cursor = 'pointer';
            }} else {{
                tooltip.style.display = 'none';
                hideCodePreview();
                if (hoveredNode && hoveredNode !== selectedNode) {{
                    hoveredNode.material.emissiveIntensity = 0.3;
                }}
                hoveredNode = null;
                document.body.style.cursor = 'default';
            }}
        }}
        
        function onMouseClick(event) {{
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
            
            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(nodeMeshes);
            
            // Deselect previous
            if (selectedNode) {{
                selectedNode.material.emissiveIntensity = 0.3;
            }}
            
            if (intersects.length > 0) {{
                const mesh = intersects[0].object;
                const node = mesh.userData;
                selectedNode = mesh;
                
                // Highlight selected node
                mesh.material.emissiveIntensity = 1.0;
                
                // Show info panel
                const info = document.getElementById('info');
                const infoContent = document.getElementById('infoContent');
                info.style.display = 'block';
                
                const perfColor = node.avg_time > 0.1 ? '#ff0000' : 
                                 node.avg_time > 0.01 ? '#ffff00' : '#00ff00';
                
                infoContent.innerHTML = `
                    <div style="margin-bottom: 10px;">
                        <strong style="font-size: 16px;">${{node.label}}</strong>
                    </div>
                    <div style="margin-bottom: 5px;">
                        <span class="perf-indicator" style="background: ${{perfColor}};"></span>
                        <strong>Performance:</strong> ${{node.avg_time > 0.1 ? 'Slow' : node.avg_time > 0.01 ? 'Medium' : 'Fast'}}
                    </div>
                    <div><strong>Module:</strong> ${{node.module || 'N/A'}}</div>
                    <div><strong>Call Count:</strong> ${{node.call_count}}</div>
                    <div><strong>Average Time:</strong> ${{node.avg_time.toFixed(4)}}s</div>
                    <div><strong>Total Time:</strong> ${{node.total_time.toFixed(4)}}s</div>
                `;
            }} else {{
                selectedNode = null;
                document.getElementById('info').style.display = 'none';
            }}
        }}
        
        function focusOnSlowest() {{
            // Find slowest node
            let slowest = null;
            let maxTime = 0;
            
            nodeMeshes.forEach(mesh => {{
                if (mesh.userData.avg_time > maxTime) {{
                    maxTime = mesh.userData.avg_time;
                    slowest = mesh;
                }}
            }});
            
            if (slowest) {{
                // Animate camera to slowest node
                const targetPos = slowest.position.clone();
                const distance = 300;
                
                const newPos = {{
                    x: targetPos.x,
                    y: targetPos.y,
                    z: targetPos.z + distance
                }};
                
                // Simple camera animation
                const startPos = camera.position.clone();
                const duration = 1000; // ms
                const startTime = Date.now();
                
                function animateCamera() {{
                    const elapsed = Date.now() - startTime;
                    const progress = Math.min(elapsed / duration, 1);
                    const eased = 1 - Math.pow(1 - progress, 3); // ease out cubic
                    
                    camera.position.x = startPos.x + (newPos.x - startPos.x) * eased;
                    camera.position.y = startPos.y + (newPos.y - startPos.y) * eased;
                    camera.position.z = startPos.z + (newPos.z - startPos.z) * eased;
                    
                    controls.target.copy(targetPos);
                    
                    if (progress < 1) {{
                        requestAnimationFrame(animateCamera);
                    }}
                }}
                
                animateCamera();
                
                // Select the node
                if (selectedNode) {{
                    selectedNode.material.emissiveIntensity = 0.3;
                }}
                selectedNode = slowest;
                slowest.material.emissiveIntensity = 1.0;
            }}
        }}
        
        function takeScreenshot() {{
            renderer.render(scene, camera);
            const dataURL = renderer.domElement.toDataURL('image/png');
            const link = document.createElement('a');
            link.download = 'callflow-3d-screenshot.png';
            link.href = dataURL;
            link.click();
        }}
        
        function focusOnFastest() {{
            let fastest = null;
            let minTime = Infinity;
            
            nodeMeshes.forEach(mesh => {{
                if (mesh.userData.avg_time < minTime) {{
                    minTime = mesh.userData.avg_time;
                    fastest = mesh;
                }}
            }});
            
            if (fastest) {{
                animateCameraToNode(fastest);
            }}
        }}
        
        function animateCameraToNode(targetMesh) {{
            const targetPos = targetMesh.position.clone();
            const distance = 300;
            const newPos = {{
                x: targetPos.x,
                y: targetPos.y,
                z: targetPos.z + distance
            }};
            
            const startPos = camera.position.clone();
            const duration = 1000;
            const startTime = Date.now();
            
            function animateCamera() {{
                const elapsed = Date.now() - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const eased = 1 - Math.pow(1 - progress, 3);
                
                camera.position.x = startPos.x + (newPos.x - startPos.x) * eased;
                camera.position.y = startPos.y + (newPos.y - startPos.y) * eased;
                camera.position.z = startPos.z + (newPos.z - startPos.z) * eased;
                controls.target.copy(targetPos);
                
                if (progress < 1) requestAnimationFrame(animateCamera);
            }}
            
            animateCamera();
            
            if (selectedNode) selectedNode.material.emissiveIntensity = 0.3;
            selectedNode = targetMesh;
            targetMesh.material.emissiveIntensity = 1.0;
        }}
        
        function showCallChain() {{
            if (!selectedNode) {{
                alert('Please select a node first by clicking on it');
                return;
            }}
            
            // Highlight all nodes in call chain
            const chainNodes = new Set();
            const chainEdges = new Set();
            
            function findCallChain(nodeId, visited = new Set()) {{
                if (visited.has(nodeId)) return;
                visited.add(nodeId);
                chainNodes.add(nodeId);
                
                edges.forEach(edge => {{
                    if (edge.source === nodeId) {{
                        chainEdges.add(edge);
                        findCallChain(edge.target, visited);
                    }}
                }});
            }}
            
            findCallChain(selectedNode.userData.id);
            
            // Dim non-chain nodes
            nodeMeshes.forEach(mesh => {{
                if (chainNodes.has(mesh.userData.id)) {{
                    mesh.material.emissiveIntensity = 0.8;
                }} else {{
                    mesh.material.opacity = 0.2;
                }}
            }});
            
            // Highlight chain edges
            edgeLines.forEach((line, idx) => {{
                const edgeIdx = Math.floor(idx / 2);
                if (edgeIdx < edges.length && chainEdges.has(edges[edgeIdx])) {{
                    line.material.opacity = 1.0;
                }} else {{
                    line.material.opacity = 0.1;
                }}
            }});
        }}
        
        function highlightModule() {{
            const modules = [...new Set(nodes.map(n => n.module).filter(m => m))];
            if (modules.length === 0) {{
                alert('No module information available');
                return;
            }}
            
            const module = prompt('Enter module name to highlight:\\n' + modules.join('\\n'));
            if (!module) return;
            
            nodeMeshes.forEach(mesh => {{
                if (mesh.userData.module === module) {{
                    mesh.material.emissiveIntensity = 1.0;
                    mesh.scale.set(1.5, 1.5, 1.5);
                }} else {{
                    mesh.material.opacity = 0.3;
                }}
            }});
        }}
        
        function playAnimation() {{
            let currentIndex = 0;
            const animSpeed = parseInt(document.getElementById('animSpeed').value);
            const delay = 1000 / animSpeed;
            
            function animateNext() {{
                if (currentIndex > 0) {{
                    nodeMeshes[currentIndex - 1].material.emissiveIntensity = 0.3;
                }}
                
                if (currentIndex < nodeMeshes.length) {{
                    const mesh = nodeMeshes[currentIndex];
                    mesh.material.emissiveIntensity = 1.0;
                    animateCameraToNode(mesh);
                    currentIndex++;
                    setTimeout(animateNext, delay);
                }} else {{
                    nodeMeshes.forEach(m => m.material.emissiveIntensity = 0.3);
                }}
            }}
            
            animateNext();
        }}
        
        function exportData() {{
            const data = {{
                nodes: nodes,
                edges: edges,
                metadata: {{
                    exported: new Date().toISOString(),
                    layout: document.getElementById('layout').value,
                    nodeCount: nodes.length,
                    edgeCount: edges.length
                }}
            }};
            
            const blob = new Blob([JSON.stringify(data, null, 2)], {{ type: 'application/json' }});
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.download = 'callflow-3d-data.json';
            link.href = url;
            link.click();
            URL.revokeObjectURL(url);
        }}
        
        function updateEdgeThickness(thickness) {{
            // Update line thickness (note: linewidth may not work in all browsers)
            edgeLines.forEach(line => {{
                if (line.type === 'Line') {{
                    line.material.linewidth = thickness;
                }}
            }});
        }}
        
        function onKeyDown(event) {{
            switch(event.key) {{
                case 'r':
                case 'R':
                    resetView();
                    break;
                case 's':
                case 'S':
                    if (event.ctrlKey || event.metaKey) {{
                        event.preventDefault();
                        takeScreenshot();
                    }}
                    break;
                case 'f':
                case 'F':
                    focusOnSlowest();
                    break;
                case 'h':
                case 'H':
                    document.getElementById('controls').style.display = 
                        document.getElementById('controls').style.display === 'none' ? 'block' : 'none';
                    break;
                case 'p':
                case 'P':
                    playAnimation();
                    break;
                case 'c':
                case 'C':
                    // Toggle code preview
                    const checkbox = document.getElementById('enableCodePreview');
                    checkbox.checked = !checkbox.checked;
                    codePreviewEnabled = checkbox.checked;
                    if (!codePreviewEnabled) {{
                        hideCodePreview();
                    }}
                    break;
                case 'Escape':
                    // Reset all highlighting
                    hideCodePreview();
                    nodeMeshes.forEach(mesh => {{
                        mesh.material.opacity = 1.0;
                        mesh.material.emissiveIntensity = 0.3;
                        mesh.scale.set(1, 1, 1);
                    }});
                    edgeLines.forEach(line => {{
                        line.material.opacity = line.type === 'Line' ? 0.7 : 0.9;
                    }});
                    break;
            }}
        }}
        
        // NEW FEATURES
        let gridHelper = null;
        let comparedNodes = [];
        let heatmapEnabled = false;
        let timelineData = [];
        let timelineIndex = 0;
        let timelinePlaying = false;
        let codePreviewEnabled = true;
        let codePreviewTimeout = null;
        
        function updateNodeOpacity(opacity) {{
            nodeMeshes.forEach(mesh => {{
                mesh.material.opacity = opacity;
            }});
        }}
        
        function toggleGrid(show) {{
            if (show && !gridHelper) {{
                gridHelper = new THREE.GridHelper(1000, 20, 0x444444, 0x222222);
                scene.add(gridHelper);
            }} else if (!show && gridHelper) {{
                scene.remove(gridHelper);
                gridHelper = null;
            }}
        }}
        
        function fitToView() {{
            if (nodeMeshes.length === 0) return;
            
            const box = new THREE.Box3();
            nodeMeshes.forEach(mesh => box.expandByObject(mesh));
            
            const center = box.getCenter(new THREE.Vector3());
            const size = box.getSize(new THREE.Vector3());
            const maxDim = Math.max(size.x, size.y, size.z);
            const fov = camera.fov * (Math.PI / 180);
            let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));
            cameraZ *= 1.5; // Add padding
            
            camera.position.set(center.x, center.y, center.z + cameraZ);
            controls.target.copy(center);
            controls.update();
        }}
        
        function topView() {{
            const target = controls.target.clone();
            camera.position.set(target.x, target.y + 800, target.z);
            camera.lookAt(target);
            controls.update();
        }}
        
        function sideView() {{
            const target = controls.target.clone();
            camera.position.set(target.x + 800, target.y, target.z);
            camera.lookAt(target);
            controls.update();
        }}
        
        function findNode() {{
            const searchTerm = prompt('Enter function name to search:');
            if (!searchTerm) return;
            
            const found = nodeMeshes.filter(mesh => 
                mesh.userData.label.toLowerCase().includes(searchTerm.toLowerCase())
            );
            
            if (found.length === 0) {{
                alert('No functions found matching: ' + searchTerm);
                return;
            }}
            
            // Highlight all found nodes
            nodeMeshes.forEach(mesh => {{
                if (found.includes(mesh)) {{
                    mesh.material.emissiveIntensity = 1.0;
                    mesh.scale.set(1.3, 1.3, 1.3);
                }} else {{
                    mesh.material.opacity = 0.2;
                }}
            }});
            
            // Focus on first result
            if (found.length > 0) {{
                animateCameraToNode(found[0]);
                alert(`Found ${{found.length}} function(s) matching "${{searchTerm}}"`);
            }}
        }}
        
        function showHotspots() {{
            // Find top 3 slowest functions
            const sorted = [...nodeMeshes].sort((a, b) => 
                b.userData.total_time - a.userData.total_time
            );
            const hotspots = sorted.slice(0, Math.min(3, sorted.length));
            
            // Highlight hotspots
            nodeMeshes.forEach(mesh => {{
                if (hotspots.includes(mesh)) {{
                    mesh.material.emissiveIntensity = 1.0;
                    mesh.scale.set(1.5, 1.5, 1.5);
                }} else {{
                    mesh.material.opacity = 0.3;
                }}
            }});
            
            // Show info
            const info = hotspots.map((m, i) => 
                `${{i+1}}. ${{m.userData.label}}: ${{m.userData.total_time.toFixed(4)}}s`
            ).join('\\n');
            alert('🔥 Performance Hotspots:\\n\\n' + info);
        }}
        
        function compareNodes() {{
            if (comparedNodes.length === 0) {{
                alert('Click on nodes to select them for comparison, then click this button again.');
                return;
            }}
            
            if (comparedNodes.length < 2) {{
                alert('Please select at least 2 nodes to compare.');
                return;
            }}
            
            const comparison = comparedNodes.map(mesh => {{
                const node = mesh.userData;
                return `${{node.label}}:\\n` +
                       `  Calls: ${{node.call_count}}\\n` +
                       `  Avg Time: ${{node.avg_time.toFixed(4)}}s\\n` +
                       `  Total Time: ${{node.total_time.toFixed(4)}}s`;
            }}).join('\\n\\n');
            
            alert('⚖️ Node Comparison:\\n\\n' + comparison);
            comparedNodes = [];
        }}
        
        function copyToClipboard() {{
            const stats = `CallFlow 3D Visualization Stats\\n` +
                         `================================\\n` +
                         `Functions: ${{nodes.length}}\\n` +
                         `Relationships: ${{edges.length}}\\n` +
                         `Layout: ${{document.getElementById('layout').value}}\\n` +
                         `Exported: ${{new Date().toLocaleString()}}`;
            
            navigator.clipboard.writeText(stats).then(() => {{
                alert('✅ Stats copied to clipboard!');
            }}).catch(() => {{
                alert('❌ Failed to copy to clipboard');
            }});
        }}
        
        // HEATMAP MODE
        function toggleHeatmap() {{
            heatmapEnabled = !heatmapEnabled;
            const legend = document.getElementById('heatmapLegend');
            legend.style.display = heatmapEnabled ? 'block' : 'none';
            
            if (heatmapEnabled) {{
                applyHeatmap();
            }} else {{
                // Reset to default colors
                nodeMeshes.forEach(mesh => {{
                    const color = getNodeColor(mesh.userData.avg_time);
                    mesh.material.color.setHex(color);
                }});
            }}
        }}
        
        function applyHeatmap() {{
            const metric = document.getElementById('heatmap-metric').value;
            
            // Find min and max values for normalization
            let minVal = Infinity;
            let maxVal = -Infinity;
            
            nodeMeshes.forEach(mesh => {{
                let value;
                if (metric === 'time') {{
                    value = mesh.userData.avg_time;
                }} else if (metric === 'calls') {{
                    value = mesh.userData.call_count;
                }} else {{
                    value = mesh.userData.total_time;
                }}
                minVal = Math.min(minVal, value);
                maxVal = Math.max(maxVal, value);
            }});
            
            // Apply heatmap colors
            nodeMeshes.forEach(mesh => {{
                let value;
                if (metric === 'time') {{
                    value = mesh.userData.avg_time;
                }} else if (metric === 'calls') {{
                    value = mesh.userData.call_count;
                }} else {{
                    value = mesh.userData.total_time;
                }}
                
                // Normalize to 0-1
                const normalized = (value - minVal) / (maxVal - minVal || 1);
                
                // Create gradient color (green -> yellow -> red)
                let color;
                if (normalized < 0.5) {{
                    // Green to Yellow
                    const t = normalized * 2;
                    color = new THREE.Color(t, 1, 0);
                }} else {{
                    // Yellow to Red
                    const t = (normalized - 0.5) * 2;
                    color = new THREE.Color(1, 1 - t, 0);
                }}
                
                mesh.material.color = color;
                mesh.material.emissive = color;
                mesh.material.emissiveIntensity = 0.3;
            }});
        }}
        
        // Listen for heatmap metric changes
        document.getElementById('heatmap-metric').addEventListener('change', () => {{
            if (heatmapEnabled) {{
                applyHeatmap();
            }}
        }});
        
        // CRITICAL PATH
        function showCriticalPath() {{
            // Build adjacency list
            const adjacency = {{}};
            nodes.forEach(n => adjacency[n.id] = []);
            edges.forEach(e => {{
                if (!adjacency[e.source]) adjacency[e.source] = [];
                adjacency[e.source].push({{ target: e.target, time: e.total_time }});
            }});
            
            // Find longest path using DFS with memoization
            const memo = {{}};
            
            function dfs(nodeId) {{
                if (memo[nodeId]) return memo[nodeId];
                
                let maxPath = {{ length: 0, time: 0, path: [nodeId] }};
                
                if (adjacency[nodeId]) {{
                    adjacency[nodeId].forEach(edge => {{
                        const subPath = dfs(edge.target);
                        const totalTime = edge.time + subPath.time;
                        
                        if (totalTime > maxPath.time) {{
                            maxPath = {{
                                length: subPath.length + 1,
                                time: totalTime,
                                path: [nodeId, ...subPath.path]
                            }};
                        }}
                    }});
                }}
                
                memo[nodeId] = maxPath;
                return maxPath;
            }}
            
            // Find critical path from all root nodes
            let criticalPath = {{ length: 0, time: 0, path: [] }};
            nodes.forEach(node => {{
                const path = dfs(node.id);
                if (path.time > criticalPath.time) {{
                    criticalPath = path;
                }}
            }});
            
            if (criticalPath.path.length === 0) {{
                alert('No critical path found');
                return;
            }}
            
            // Highlight critical path
            const pathSet = new Set(criticalPath.path);
            
            nodeMeshes.forEach(mesh => {{
                if (pathSet.has(mesh.userData.id)) {{
                    mesh.material.emissiveIntensity = 1.0;
                    mesh.material.color.setHex(0xff0000); // Red for critical path
                    mesh.scale.set(1.3, 1.3, 1.3);
                }} else {{
                    mesh.material.opacity = 0.2;
                }}
            }});
            
            // Highlight critical edges
            edgeLines.forEach((line, idx) => {{
                const edgeIdx = Math.floor(idx / 2);
                if (edgeIdx < edges.length) {{
                    const edge = edges[edgeIdx];
                    const inPath = pathSet.has(edge.source) && pathSet.has(edge.target);
                    line.material.opacity = inPath ? 1.0 : 0.1;
                    if (inPath && line.type === 'Line') {{
                        line.material.color.setHex(0xff0000);
                    }}
                }}
            }});
            
            alert(`🛤️ Critical Path Found!\\n\\nLength: ${{criticalPath.length}} functions\\nTotal Time: ${{criticalPath.time.toFixed(4)}}s\\n\\nPath: ${{criticalPath.path.slice(0, 5).join(' → ')}}${{criticalPath.path.length > 5 ? '...' : ''}}`);
        }}
        
        // AUTO-CLUSTER BY MODULE
        function clusterByModule() {{
            // Group nodes by module
            const modules = {{}};
            nodeMeshes.forEach(mesh => {{
                const module = mesh.userData.module || 'unknown';
                if (!modules[module]) modules[module] = [];
                modules[module].push(mesh);
            }});
            
            const moduleNames = Object.keys(modules);
            if (moduleNames.length === 0) {{
                alert('No module information available');
                return;
            }}
            
            // Position clusters in a circle
            const angleStep = (2 * Math.PI) / moduleNames.length;
            const clusterRadius = 500;
            
            moduleNames.forEach((moduleName, i) => {{
                const angle = i * angleStep;
                const clusterX = Math.cos(angle) * clusterRadius;
                const clusterZ = Math.sin(angle) * clusterRadius;
                
                const moduleNodes = modules[moduleName];
                const innerRadius = Math.sqrt(moduleNodes.length) * 30;
                
                // Arrange nodes within cluster in a circle
                moduleNodes.forEach((mesh, j) => {{
                    const innerAngle = (j / moduleNodes.length) * Math.PI * 2;
                    mesh.position.x = clusterX + Math.cos(innerAngle) * innerRadius;
                    mesh.position.y = 0;
                    mesh.position.z = clusterZ + Math.sin(innerAngle) * innerRadius;
                    
                    // Color by module
                    const hue = (i / moduleNames.length) * 360;
                    mesh.material.color.setHSL(hue / 360, 0.7, 0.5);
                }});
                
                // Create cluster boundary (optional visual)
                const boundaryGeometry = new THREE.RingGeometry(innerRadius + 20, innerRadius + 25, 32);
                const boundaryMaterial = new THREE.MeshBasicMaterial({{ 
                    color: 0x4fc3f7, 
                    side: THREE.DoubleSide,
                    transparent: true,
                    opacity: 0.3
                }});
                const boundary = new THREE.Mesh(boundaryGeometry, boundaryMaterial);
                boundary.position.set(clusterX, 0, clusterZ);
                boundary.rotation.x = Math.PI / 2;
                scene.add(boundary);
            }});
            
            // Fit view to see all clusters
            setTimeout(() => fitToView(), 100);
            
            alert(`📦 Clustered into ${{moduleNames.length}} modules:\\n\\n${{moduleNames.join('\\n')}}`);
        }}
        
        // TIMELINE FUNCTIONS
        function toggleTimeline() {{
            const panel = document.getElementById('timeline');
            panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
        }}
        
        function timelinePlay() {{
            timelinePlaying = true;
            playTimelineAnimation();
        }}
        
        function timelinePause() {{
            timelinePlaying = false;
        }}
        
        function timelineReset() {{
            timelineIndex = 0;
            timelinePlaying = false;
            document.getElementById('timeline-slider').value = 0;
            document.getElementById('timeline-time').textContent = '0.00s';
        }}
        
        function playTimelineAnimation() {{
            if (!timelinePlaying) return;
            
            const speed = parseFloat(document.getElementById('timeline-speed').value);
            const maxIndex = nodeMeshes.length - 1;
            
            if (timelineIndex <= maxIndex) {{
                // Highlight current node
                nodeMeshes.forEach((mesh, i) => {{
                    if (i === timelineIndex) {{
                        mesh.material.emissiveIntensity = 1.0;
                        animateCameraToNode(mesh);
                    }} else if (i < timelineIndex) {{
                        mesh.material.emissiveIntensity = 0.5;
                    }} else {{
                        mesh.material.opacity = 0.2;
                    }}
                }});
                
                // Update slider and time
                const progress = (timelineIndex / maxIndex) * 100;
                document.getElementById('timeline-slider').value = progress;
                
                const currentTime = nodeMeshes[timelineIndex].userData.total_time;
                document.getElementById('timeline-time').textContent = currentTime.toFixed(2) + 's';
                
                timelineIndex++;
                setTimeout(() => playTimelineAnimation(), 1000 / speed);
            }} else {{
                timelinePause();
                timelineReset();
            }}
        }}
        
        // FILTER FUNCTIONS
        function toggleFilters() {{
            const panel = document.getElementById('filterPanel');
            panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
        }}
        
        function applyFilters() {{
            const minTime = parseFloat(document.getElementById('filter-min-time').value) / 1000;
            const maxTime = parseFloat(document.getElementById('filter-max-time').value) / 1000;
            const minCalls = parseInt(document.getElementById('filter-min-calls').value);
            const nameFilter = document.getElementById('filter-name').value.toLowerCase();
            
            let visibleCount = 0;
            nodeMeshes.forEach(mesh => {{
                const node = mesh.userData;
                const visible = node.avg_time >= minTime && 
                               node.avg_time <= maxTime &&
                               node.call_count >= minCalls &&
                               (nameFilter === '' || node.label.toLowerCase().includes(nameFilter));
                mesh.visible = visible;
                if (visible) visibleCount++;
            }});
            
            // Also filter sprites
            nodeSprites.forEach((sprite, i) => {{
                sprite.visible = nodeMeshes[i].visible;
            }});
            
            alert(`🎛️ Filter Applied\\n\\nShowing ${{visibleCount}} of ${{nodeMeshes.length}} functions`);
        }}
        
        function clearFilters() {{
            document.getElementById('filter-min-time').value = 0;
            document.getElementById('filter-max-time').value = 10000;
            document.getElementById('filter-min-calls').value = 0;
            document.getElementById('filter-name').value = '';
            
            nodeMeshes.forEach(mesh => {{
                mesh.visible = true;
                mesh.material.opacity = 1.0;
            }});
            nodeSprites.forEach(sprite => sprite.visible = true);
            
            alert('✅ Filters cleared');
        }}
        
        // CODE PREVIEW FUNCTIONS
        function generateMockCode(node) {{
            // Generate realistic Python code based on node data
            const funcName = node.label;
            const module = node.module || 'unknown';
            
            // Create a realistic function signature
            let code = 'def ' + funcName + '(';
            
            // Add some parameters based on function name
            if (funcName.includes('get') || funcName.includes('fetch')) {{
                code += 'id: int';
            }} else if (funcName.includes('process') || funcName.includes('handle')) {{
                code += 'data: dict';
            }} else if (funcName.includes('save') || funcName.includes('update')) {{
                code += 'obj: object, **kwargs';
            }} else {{
                code += '*args, **kwargs';
            }}
            code += '):\\n';
            
            // Add docstring
            code += '    ' + String.fromCharCode(34, 34, 34) + '\\n';
            code += '    ' + funcName.replace(/_/g, ' ').replace(/([A-Z])/g, ' $1').trim() + '\\n';
            code += '    \\n';
            code += '    Module: ' + module + '\\n';
            code += '    Calls: ' + node.call_count + '\\n';
            code += '    Avg Time: ' + node.avg_time.toFixed(4) + 's\\n';
            code += '    Total Time: ' + node.total_time.toFixed(4) + 's\\n';
            code += '    ' + String.fromCharCode(34, 34, 34) + '\\n';
            
            // Add some realistic function body
            if (funcName.includes('get') || funcName.includes('fetch')) {{
                code += '    # Fetch data from source\\n';
                code += '    result = database.query(id)\\n';
                code += '    if not result:\\n';
                code += '        return None\\n';
                code += '    return result\\n';
            }} else if (funcName.includes('process')) {{
                code += '    # Process the data\\n';
                code += '    try:\\n';
                code += '        validated = validate(data)\\n';
                code += '        transformed = transform(validated)\\n';
                code += '        return transformed\\n';
                code += '    except Exception as e:\\n';
                code += '        logger.error(f"Error: {{e}}")\\n';
                code += '        raise\\n';
            }} else if (funcName.includes('save') || funcName.includes('update')) {{
                code += '    # Save to database\\n';
                code += '    obj.updated_at = datetime.now()\\n';
                code += '    database.save(obj)\\n';
                code += '    return obj.id\\n';
            }} else {{
                code += '    # Function implementation\\n';
                code += '    result = perform_operation()\\n';
                code += '    return result\\n';
            }}
            
            return code;
        }}
        
        function syntaxHighlight(code) {{
            const lines = code.split('\\n');
            let inDocstring = false;
            
            return lines.map((line, i) => {{
                let highlighted = line;
                
                // Check for docstring
                const tripleQuote = String.fromCharCode(34, 34, 34);
                const tripleSingle = String.fromCharCode(39, 39, 39);
                if (line.trim().startsWith(tripleQuote) || line.trim().startsWith(tripleSingle)) {{
                    inDocstring = !inDocstring;
                    highlighted = '<span class="docstring">' + escapeHtml(line) + '</span>';
                }} else if (inDocstring) {{
                    highlighted = '<span class="docstring">' + escapeHtml(line) + '</span>';
                }} else {{
                    // Escape HTML first
                    highlighted = escapeHtml(line);
                    
                    // Highlight comments
                    highlighted = highlighted.replace(/(#.*$)/g, '<span class="comment">$1</span>');
                    
                    // Highlight keywords
                    highlighted = highlighted.replace(/\\b(def|class|if|else|elif|return|import|from|try|except|finally|with|as|for|while|in|not|and|or|is|None|True|False|raise|pass|break|continue|yield|lambda)\\b/g, '<span class="keyword">$1</span>');
                    
                    // Highlight strings (before function names to avoid conflicts)
                    highlighted = highlighted.replace(/(".*?"|'.*?')/g, '<span class="string">$1</span>');
                    
                    // Highlight numbers
                    highlighted = highlighted.replace(/\\b(\\d+\\.?\\d*)\\b/g, '<span class="number">$1</span>');
                    
                    // Highlight function calls
                    highlighted = highlighted.replace(/\\b([a-zA-Z_][a-zA-Z0-9_]*)\\s*\\(/g, '<span class="function">$1</span>(');
                }}
                
                return '<div class="code-line">' +
                    '<span class="line-number">' + (i + 1) + '</span>' +
                    '<span class="line-content">' + highlighted + '</span>' +
                '</div>';
            }}).join('');
        }}
        
        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}
        
        function showCodePreview(node, x, y) {{
            if (!codePreviewEnabled) return;
            
            // Clear any existing timeout
            if (codePreviewTimeout) {{
                clearTimeout(codePreviewTimeout);
            }}
            
            // Delay showing to avoid flicker
            codePreviewTimeout = setTimeout(() => {{
                const preview = document.getElementById('codePreview');
                const header = document.getElementById('codeHeader');
                const content = document.getElementById('codeContent');
                const footer = document.getElementById('codeFooter');
                
                // Set header
                header.innerHTML = `📄 ${{node.label}} <span style="color: #888; font-size: 10px;">(${{node.module || 'unknown'}})</span>`;
                
                // Generate and highlight code
                const code = generateMockCode(node);
                content.innerHTML = syntaxHighlight(code);
                
                // Update footer with file info
                footer.innerHTML = `
                    <div>Module: ${{node.module || 'N/A'}} | Calls: ${{node.call_count}} | Avg: ${{node.avg_time.toFixed(4)}}s</div>
                    <div style="margin-top: 3px;">Press 'C' to toggle | Right-click to copy code</div>
                `;
                
                // Position near cursor but ensure it stays on screen
                let left = x + 20;
                let top = y;
                
                // Adjust if too far right
                if (left + 620 > window.innerWidth) {{
                    left = x - 620;
                }}
                
                // Adjust if too far down
                if (top + 420 > window.innerHeight) {{
                    top = window.innerHeight - 420;
                }}
                
                preview.style.left = Math.max(10, left) + 'px';
                preview.style.top = Math.max(10, top) + 'px';
                preview.style.display = 'block';
            }}, 300); // 300ms delay
        }}
        
        function hideCodePreview() {{
            if (codePreviewTimeout) {{
                clearTimeout(codePreviewTimeout);
                codePreviewTimeout = null;
            }}
            document.getElementById('codePreview').style.display = 'none';
        }}
        
        // Listen for code preview toggle
        document.getElementById('enableCodePreview').addEventListener('change', (e) => {{
            codePreviewEnabled = e.target.checked;
            if (!codePreviewEnabled) {{
                hideCodePreview();
            }}
        }});
        
        // Add right-click to copy code
        document.getElementById('codePreview').addEventListener('contextmenu', (e) => {{
            e.preventDefault();
            const codeContent = document.getElementById('codeContent').innerText;
            navigator.clipboard.writeText(codeContent).then(() => {{
                alert('✅ Code copied to clipboard!');
            }}).catch(() => {{
                alert('❌ Failed to copy code');
            }});
        }});
        
        // ADVANCED STATISTICS
        let fpsHistory = [];
        let lastFrameTime = Date.now();
        let charts = {{}};
        
        function updateFPS() {{
            const now = Date.now();
            const delta = now - lastFrameTime;
            const fps = Math.round(1000 / delta);
            lastFrameTime = now;
            
            fpsHistory.push(fps);
            if (fpsHistory.length > 60) fpsHistory.shift();
            
            const avgFps = Math.round(fpsHistory.reduce((a, b) => a + b, 0) / fpsHistory.length);
            document.getElementById('fpsCounter').textContent = avgFps;
        }}
        
        function calculateComplexity() {{
            // Graph complexity score based on nodes, edges, and depth
            const nodeCount = nodes.length;
            const edgeCount = edges.length;
            const avgDegree = edgeCount / nodeCount;
            const depth = calculateMaxDepth();
            
            // Complexity formula: weighted combination
            const complexity = Math.round((nodeCount * 0.3) + (edgeCount * 0.4) + (avgDegree * 10) + (depth * 5));
            
            document.getElementById('complexityScore').textContent = complexity;
            document.getElementById('maxDepth').textContent = depth;
        }}
        
        function calculateMaxDepth() {{
            // BFS to find maximum depth
            const adjacency = {{}};
            nodes.forEach(n => adjacency[n.id] = []);
            edges.forEach(e => {{
                if (!adjacency[e.source]) adjacency[e.source] = [];
                adjacency[e.source].push(e.target);
            }});
            
            // Find root nodes (no incoming edges)
            const hasIncoming = new Set();
            edges.forEach(e => hasIncoming.add(e.target));
            const roots = nodes.filter(n => !hasIncoming.has(n.id)).map(n => n.id);
            
            if (roots.length === 0) return 0;
            
            let maxDepth = 0;
            roots.forEach(root => {{
                const queue = [[root, 0]];
                const visited = new Set();
                
                while (queue.length > 0) {{
                    const [node, depth] = queue.shift();
                    if (visited.has(node)) continue;
                    visited.add(node);
                    maxDepth = Math.max(maxDepth, depth);
                    
                    if (adjacency[node]) {{
                        adjacency[node].forEach(child => {{
                            if (!visited.has(child)) {{
                                queue.push([child, depth + 1]);
                            }}
                        }});
                    }}
                }}
            }});
            
            return maxDepth;
        }}
        
        function toggleCharts() {{
            const panel = document.getElementById('chartsPanel');
            const isVisible = panel.style.display !== 'none';
            
            if (isVisible) {{
                panel.style.display = 'none';
            }} else {{
                panel.style.display = 'block';
                createCharts();
            }}
        }}
        
        function createCharts() {{
            // Destroy existing charts
            Object.values(charts).forEach(chart => {{
                if (chart) chart.destroy();
            }});
            
            createPerformanceChart();
            createDepthChart();
            createTopFunctionsChart();
            createCallFrequencyChart();
        }}
        
        function createPerformanceChart() {{
            const ctx = document.getElementById('perfChart').getContext('2d');
            
            // Categorize by performance
            const fast = nodes.filter(n => n.avg_time < 0.01).length;
            const medium = nodes.filter(n => n.avg_time >= 0.01 && n.avg_time < 0.1).length;
            const slow = nodes.filter(n => n.avg_time >= 0.1).length;
            
            charts.perf = new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: ['Fast (<10ms)', 'Medium (10-100ms)', 'Slow (>100ms)'],
                    datasets: [{{
                        data: [fast, medium, slow],
                        backgroundColor: ['#00ff00', '#ffff00', '#ff0000'],
                        borderColor: '#000',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            labels: {{ color: '#fff' }}
                        }}
                    }}
                }}
            }});
        }}
        
        function createDepthChart() {{
            const ctx = document.getElementById('depthChart').getContext('2d');
            
            // Calculate depth for each node
            const depths = nodes.map(() => 0);
            const adjacency = {{}};
            const nodeIndexMap = {{}};
            
            nodes.forEach((n, i) => {{
                adjacency[n.id] = [];
                nodeIndexMap[n.id] = i;
            }});
            
            edges.forEach(e => {{
                if (adjacency[e.source]) {{
                    adjacency[e.source].push(e.target);
                }}
            }});
            
            // BFS from roots
            const hasIncoming = new Set();
            edges.forEach(e => hasIncoming.add(e.target));
            const roots = nodes.filter(n => !hasIncoming.has(n.id));
            
            roots.forEach(root => {{
                const queue = [[root.id, 0]];
                const visited = new Set();
                
                while (queue.length > 0) {{
                    const [nodeId, depth] = queue.shift();
                    if (visited.has(nodeId)) continue;
                    visited.add(nodeId);
                    
                    const idx = nodeIndexMap[nodeId];
                    depths[idx] = Math.max(depths[idx], depth);
                    
                    if (adjacency[nodeId]) {{
                        adjacency[nodeId].forEach(child => {{
                            queue.push([child, depth + 1]);
                        }});
                    }}
                }}
            }});
            
            // Count nodes at each depth
            const depthCounts = {{}};
            depths.forEach(d => {{
                depthCounts[d] = (depthCounts[d] || 0) + 1;
            }});
            
            const labels = Object.keys(depthCounts).sort((a, b) => a - b);
            const data = labels.map(l => depthCounts[l]);
            
            charts.depth = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: labels.map(l => 'Depth ' + l),
                    datasets: [{{
                        label: 'Function Count',
                        data: data,
                        backgroundColor: '#4fc3f7',
                        borderColor: '#29b6f6',
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            ticks: {{ color: '#fff' }}
                        }},
                        x: {{
                            ticks: {{ color: '#fff' }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            labels: {{ color: '#fff' }}
                        }}
                    }}
                }}
            }});
        }}
        
        function createTopFunctionsChart() {{
            const ctx = document.getElementById('topFunctionsChart').getContext('2d');
            
            // Get top 10 slowest functions
            const sorted = [...nodes].sort((a, b) => b.total_time - a.total_time).slice(0, 10);
            
            charts.topFuncs = new Chart(ctx, {{
                type: 'horizontalBar',
                data: {{
                    labels: sorted.map(n => n.label.substring(0, 20)),
                    datasets: [{{
                        label: 'Total Time (s)',
                        data: sorted.map(n => n.total_time),
                        backgroundColor: sorted.map(n => 
                            n.avg_time > 0.1 ? '#ff0000' : 
                            n.avg_time > 0.01 ? '#ffff00' : '#00ff00'
                        ),
                        borderColor: '#000',
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    indexAxis: 'y',
                    responsive: true,
                    scales: {{
                        x: {{
                            beginAtZero: true,
                            ticks: {{ color: '#fff' }}
                        }},
                        y: {{
                            ticks: {{ color: '#fff' }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            labels: {{ color: '#fff' }}
                        }}
                    }}
                }}
            }});
        }}
        
        function createCallFrequencyChart() {{
            const ctx = document.getElementById('callFreqChart').getContext('2d');
            
            // Group by call count ranges
            const ranges = {{
                '1-5': 0,
                '6-10': 0,
                '11-20': 0,
                '21-50': 0,
                '51+': 0
            }};
            
            nodes.forEach(n => {{
                const count = n.call_count;
                if (count <= 5) ranges['1-5']++;
                else if (count <= 10) ranges['6-10']++;
                else if (count <= 20) ranges['11-20']++;
                else if (count <= 50) ranges['21-50']++;
                else ranges['51+']++;
            }});
            
            charts.callFreq = new Chart(ctx, {{
                type: 'pie',
                data: {{
                    labels: Object.keys(ranges),
                    datasets: [{{
                        data: Object.values(ranges),
                        backgroundColor: [
                            '#00ff00',
                            '#7fff00',
                            '#ffff00',
                            '#ff7f00',
                            '#ff0000'
                        ],
                        borderColor: '#000',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            labels: {{ color: '#fff' }}
                        }}
                    }}
                }}
            }});
        }}
        
        // Initialize
        init();
        
        // Calculate initial metrics
        calculateComplexity();
        
        // Update FPS in animation loop
        setInterval(updateFPS, 100);
        
        // SHAREABLE URL & STATE MANAGEMENT
        function generateShareableURL() {{
            const state = {{
                layout: document.getElementById('layout').value,
                nodeSize: document.getElementById('nodeSize').value,
                spread: document.getElementById('spread').value,
                showLabels: document.getElementById('showLabels').checked,
                showEdges: document.getElementById('showEdges').checked,
                pulseNodes: document.getElementById('pulseNodes').checked,
                bgColor: document.getElementById('bgColor').value,
                cameraPosition: {{
                    x: camera.position.x,
                    y: camera.position.y,
                    z: camera.position.z
                }},
                cameraTarget: {{
                    x: controls.target.x,
                    y: controls.target.y,
                    z: controls.target.z
                }}
            }};
            
            // Encode state to base64
            const stateStr = JSON.stringify(state);
            const encoded = btoa(stateStr);
            
            // Create shareable URL
            const baseUrl = window.location.href.split('?')[0];
            const shareUrl = baseUrl + '?state=' + encoded;
            
            // Copy to clipboard
            navigator.clipboard.writeText(shareUrl).then(() => {{
                alert('🔗 Shareable URL copied to clipboard!\\n\\nShare this link to show your exact view configuration.\\n\\nURL length: ' + shareUrl.length + ' characters');
            }}).catch(() => {{
                // Fallback: show in prompt
                prompt('🔗 Shareable URL (copy this):', shareUrl);
            }});
        }}
        
        function loadStateFromURL() {{
            const urlParams = new URLSearchParams(window.location.search);
            const stateParam = urlParams.get('state');
            
            if (stateParam) {{
                try {{
                    const stateStr = atob(stateParam);
                    const state = JSON.parse(stateStr);
                    
                    // Apply state
                    document.getElementById('layout').value = state.layout || 'force';
                    document.getElementById('nodeSize').value = state.nodeSize || 15;
                    document.getElementById('spread').value = state.spread || 500;
                    document.getElementById('showLabels').checked = state.showLabels !== false;
                    document.getElementById('showEdges').checked = state.showEdges !== false;
                    document.getElementById('pulseNodes').checked = state.pulseNodes !== false;
                    document.getElementById('bgColor').value = state.bgColor || '0x0a0a0a';
                    
                    // Update displays
                    document.getElementById('nodeSizeValue').textContent = state.nodeSize || 15;
                    document.getElementById('spreadValue').textContent = state.spread || 500;
                    
                    // Apply layout
                    createGraph(state.layout || 'force');
                    
                    // Restore camera position
                    if (state.cameraPosition) {{
                        camera.position.set(
                            state.cameraPosition.x,
                            state.cameraPosition.y,
                            state.cameraPosition.z
                        );
                    }}
                    
                    if (state.cameraTarget) {{
                        controls.target.set(
                            state.cameraTarget.x,
                            state.cameraTarget.y,
                            state.cameraTarget.z
                        );
                    }}
                    
                    // Apply background color
                    scene.background = new THREE.Color(parseInt(state.bgColor));
                    
                    console.log('✅ State loaded from URL');
                }} catch (e) {{
                    console.error('Failed to load state from URL:', e);
                }}
            }}
        }}
        
        function saveToLocalStorage() {{
            const state = {{
                layout: document.getElementById('layout').value,
                nodeSize: document.getElementById('nodeSize').value,
                spread: document.getElementById('spread').value,
                rotationSpeed: document.getElementById('rotationSpeed').value,
                showLabels: document.getElementById('showLabels').checked,
                showEdges: document.getElementById('showEdges').checked,
                pulseNodes: document.getElementById('pulseNodes').checked,
                particleEffect: document.getElementById('particleEffect').checked,
                showGrid: document.getElementById('showGrid').checked,
                bgColor: document.getElementById('bgColor').value,
                nodeOpacity: document.getElementById('nodeOpacity').value,
                edgeThickness: document.getElementById('edgeThickness').value,
                cameraPosition: {{
                    x: camera.position.x,
                    y: camera.position.y,
                    z: camera.position.z
                }},
                cameraTarget: {{
                    x: controls.target.x,
                    y: controls.target.y,
                    z: controls.target.z
                }},
                timestamp: new Date().toISOString()
            }};
            
            localStorage.setItem('callflow3d_state', JSON.stringify(state));
            alert('💾 State saved to browser storage!\\n\\nYou can reload this page and click "Load State" to restore this view.');
        }}
        
        function loadFromLocalStorage() {{
            const stateStr = localStorage.getItem('callflow3d_state');
            
            if (!stateStr) {{
                alert('❌ No saved state found');
                return;
            }}
            
            try {{
                const state = JSON.parse(stateStr);
                
                // Apply all settings
                document.getElementById('layout').value = state.layout;
                document.getElementById('nodeSize').value = state.nodeSize;
                document.getElementById('spread').value = state.spread;
                document.getElementById('rotationSpeed').value = state.rotationSpeed || 0;
                document.getElementById('showLabels').checked = state.showLabels;
                document.getElementById('showEdges').checked = state.showEdges;
                document.getElementById('pulseNodes').checked = state.pulseNodes;
                document.getElementById('particleEffect').checked = state.particleEffect;
                document.getElementById('showGrid').checked = state.showGrid;
                document.getElementById('bgColor').value = state.bgColor;
                document.getElementById('nodeOpacity').value = state.nodeOpacity;
                document.getElementById('edgeThickness').value = state.edgeThickness;
                
                // Update value displays
                document.getElementById('nodeSizeValue').textContent = state.nodeSize;
                document.getElementById('spreadValue').textContent = state.spread;
                document.getElementById('rotationSpeedValue').textContent = state.rotationSpeed || 0;
                document.getElementById('nodeOpacityValue').textContent = state.nodeOpacity;
                document.getElementById('edgeThicknessValue').textContent = state.edgeThickness;
                
                // Apply layout
                createGraph(state.layout);
                
                // Restore camera
                camera.position.set(
                    state.cameraPosition.x,
                    state.cameraPosition.y,
                    state.cameraPosition.z
                );
                controls.target.set(
                    state.cameraTarget.x,
                    state.cameraTarget.y,
                    state.cameraTarget.z
                );
                
                // Apply other settings
                scene.background = new THREE.Color(parseInt(state.bgColor));
                updateNodeOpacity(state.nodeOpacity / 100);
                updateEdgeThickness(state.edgeThickness);
                toggleLabels(state.showLabels);
                toggleEdges(state.showEdges);
                toggleGrid(state.showGrid);
                
                if (state.particleEffect) {{
                    createParticles();
                }}
                
                const savedDate = new Date(state.timestamp).toLocaleString();
                alert('✅ State loaded successfully!\\n\\nSaved on: ' + savedDate);
            }} catch (e) {{
                alert('❌ Failed to load state: ' + e.message);
            }}
        }}
        
        // Load state from URL on init
        setTimeout(() => loadStateFromURL(), 100);
    </script>
</body>
</html>'''
    
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
