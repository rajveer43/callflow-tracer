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
            'title': f"Module: {node['module']}\\nCalls: {node['call_count']}\\nTotal Time: {node['total_time']:.3f}s\\nAvg Time: {node['avg_time']:.3f}s",
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
                    <option value="timeline">Timeline</option>
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
            
            // Store network reference globally for export functions
            window.network = network;

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
                    var radius = 300;
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
                    var spacing = Math.max(150, (window.innerWidth - 200) / sorted.length);
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
                }}
            }};

        // Set initial layout and physics for footer controls
        document.getElementById('physics').value = "true";
        document.getElementById('layout').value = "force";

        // Make changeLayout available globally
        window.changeLayout = changeLayout;

        // Export as PNG
        window.exportToPng = function() {{
            try {{
                // Wait for network to be ready
                if (!network) {{
                    throw new Error('Network not initialized');
                }}
                
                // Get the canvas from the network
                var canvas = network.canvas.frame.canvas;
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
            network.setOptions({{ physics: {{ enabled: enabled }} }});
        }});

            // Layout select (footer)
            document.getElementById('layout').addEventListener('change', function() {{
                if (this.value === 'hierarchical') {{
                    network.setOptions({{
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
                    network.setOptions({{
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
                    network.fit({{
                        animation: {{
                            duration: 500,
                            easingFunction: 'easeInOutQuad'
                        }}
                    }});
                }}, 100);
            }});

            // Add some styling on load
            network.on("stabilizationIterationsDone", function() {{
                // Keep physics enabled for force-directed by default
                // network.setOptions({{ physics: false }});
            }});

            // Set initial layout and physics to force-directed and enabled
            network.setOptions({{
                layout: {{hierarchical: false}},
                physics: {{enabled: true, solver: "forceAtlas2Based"}}
            }});
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
