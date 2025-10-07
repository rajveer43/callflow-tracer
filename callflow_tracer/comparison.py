"""
Comparison mode for callflow-tracer.

This module provides side-by-side comparison of two call graphs,
useful for before/after optimization analysis.
"""

import json
from pathlib import Path
from typing import Union, Optional, Dict, List, Tuple
from .tracer import CallGraph


def compare_graphs(graph1: CallGraph, graph2: CallGraph, 
                   label1: str = "Before", label2: str = "After") -> dict:
    """
    Compare two call graphs and generate diff statistics.
    
    Args:
        graph1: First call graph (e.g., before optimization)
        graph2: Second call graph (e.g., after optimization)
        label1: Label for first graph
        label2: Label for second graph
    
    Returns:
        Dictionary with comparison statistics
    """
    data1 = graph1.to_dict()
    data2 = graph2.to_dict()
    
    # Compare nodes
    nodes1 = {n['full_name']: n for n in data1['nodes']}
    nodes2 = {n['full_name']: n for n in data2['nodes']}
    
    all_node_names = set(nodes1.keys()) | set(nodes2.keys())
    
    node_comparisons = []
    for name in all_node_names:
        n1 = nodes1.get(name)
        n2 = nodes2.get(name)
        
        if n1 and n2:
            # Both present - compare
            time_diff = n2['total_time'] - n1['total_time']
            time_diff_pct = (time_diff / n1['total_time'] * 100) if n1['total_time'] > 0 else 0
            call_diff = n2['call_count'] - n1['call_count']
            
            node_comparisons.append({
                'name': name,
                'status': 'modified',
                'time_before': n1['total_time'],
                'time_after': n2['total_time'],
                'time_diff': time_diff,
                'time_diff_pct': time_diff_pct,
                'calls_before': n1['call_count'],
                'calls_after': n2['call_count'],
                'calls_diff': call_diff,
                'improvement': time_diff < 0  # Negative diff = improvement
            })
        elif n1:
            # Only in first graph
            node_comparisons.append({
                'name': name,
                'status': 'removed',
                'time_before': n1['total_time'],
                'time_after': 0,
                'time_diff': -n1['total_time'],
                'time_diff_pct': -100,
                'calls_before': n1['call_count'],
                'calls_after': 0,
                'calls_diff': -n1['call_count'],
                'improvement': True
            })
        else:
            # Only in second graph
            node_comparisons.append({
                'name': name,
                'status': 'added',
                'time_before': 0,
                'time_after': n2['total_time'],
                'time_diff': n2['total_time'],
                'time_diff_pct': 100,
                'calls_before': 0,
                'calls_after': n2['call_count'],
                'calls_diff': n2['call_count'],
                'improvement': False
            })
    
    # Sort by absolute time difference
    node_comparisons.sort(key=lambda x: abs(x['time_diff']), reverse=True)
    
    # Calculate summary statistics
    total_time_before = data1['metadata']['duration']
    total_time_after = data2['metadata']['duration']
    time_saved = total_time_before - total_time_after
    time_saved_pct = (time_saved / total_time_before * 100) if total_time_before > 0 else 0
    
    improvements = [n for n in node_comparisons if n['improvement'] and n['status'] == 'modified']
    regressions = [n for n in node_comparisons if not n['improvement'] and n['status'] == 'modified']
    
    return {
        'label1': label1,
        'label2': label2,
        'summary': {
            'total_time_before': total_time_before,
            'total_time_after': total_time_after,
            'time_saved': time_saved,
            'time_saved_pct': time_saved_pct,
            'nodes_before': len(nodes1),
            'nodes_after': len(nodes2),
            'nodes_added': len([n for n in node_comparisons if n['status'] == 'added']),
            'nodes_removed': len([n for n in node_comparisons if n['status'] == 'removed']),
            'nodes_modified': len([n for n in node_comparisons if n['status'] == 'modified']),
            'improvements': len(improvements),
            'regressions': len(regressions)
        },
        'node_comparisons': node_comparisons,
        'top_improvements': improvements[:10],
        'top_regressions': regressions[:10],
        'graph1_data': data1,
        'graph2_data': data2
    }


def export_comparison_html(graph1: CallGraph, graph2: CallGraph,
                          output_path: Union[str, Path],
                          label1: str = "Before",
                          label2: str = "After",
                          title: str = "Call Graph Comparison") -> None:
    """
    Export side-by-side comparison of two call graphs to HTML.
    
    Args:
        graph1: First call graph (before)
        graph2: Second call graph (after)
        output_path: Path to save the HTML file
        label1: Label for first graph
        label2: Label for second graph
        title: Title for the HTML page
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Generate comparison data
    comparison = compare_graphs(graph1, graph2, label1, label2)
    
    # Generate HTML
    html_content = _generate_comparison_html(comparison, title)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def _generate_comparison_html(comparison: dict, title: str) -> str:
    """Generate HTML content for comparison view."""
    
    summary = comparison['summary']
    node_comparisons = comparison['node_comparisons']
    label1 = comparison['label1']
    label2 = comparison['label2']
    
    # Prepare data for visualization
    data1 = comparison['graph1_data']
    data2 = comparison['graph2_data']
    
    nodes1_json = json.dumps([{
        'id': n['full_name'],
        'label': n['name'],
        'title': f"Calls: {n['call_count']}\\nTime: {n['total_time']:.3f}s",
        'value': n['call_count'],
        'color': _get_comparison_color(n['avg_time']),
        'module': n['module']
    } for n in data1['nodes']], indent=2)
    
    nodes2_json = json.dumps([{
        'id': n['full_name'],
        'label': n['name'],
        'title': f"Calls: {n['call_count']}\\nTime: {n['total_time']:.3f}s",
        'value': n['call_count'],
        'color': _get_comparison_color(n['avg_time']),
        'module': n['module']
    } for n in data2['nodes']], indent=2)
    
    edges1_json = json.dumps([{
        'from': e['caller'],
        'to': e['callee'],
        'label': f"{e['call_count']}",
        'width': min(max(1, e['call_count'] / 5), 10)
    } for e in data1['edges']], indent=2)
    
    edges2_json = json.dumps([{
        'from': e['caller'],
        'to': e['callee'],
        'label': f"{e['call_count']}",
        'width': min(max(1, e['call_count'] / 5), 10)
    } for e in data2['edges']], indent=2)
    
    # Generate comparison table rows
    comparison_rows = ""
    for comp in node_comparisons[:50]:  # Limit to top 50
        status_class = comp['status']
        improvement_class = 'improvement' if comp['improvement'] else 'regression'
        
        if comp['status'] == 'modified':
            comparison_rows += f"""
            <tr class="{status_class} {improvement_class}">
                <td>{comp['name']}</td>
                <td class="status-badge status-{status_class}">{comp['status']}</td>
                <td>{comp['time_before']:.4f}s</td>
                <td>{comp['time_after']:.4f}s</td>
                <td class="{'positive' if comp['improvement'] else 'negative'}">
                    {comp['time_diff']:+.4f}s ({comp['time_diff_pct']:+.1f}%)
                </td>
                <td>{comp['calls_before']}</td>
                <td>{comp['calls_after']}</td>
                <td class="{'positive' if comp['calls_diff'] <= 0 else 'negative'}">
                    {comp['calls_diff']:+d}
                </td>
            </tr>
            """
        elif comp['status'] == 'removed':
            comparison_rows += f"""
            <tr class="{status_class}">
                <td>{comp['name']}</td>
                <td class="status-badge status-{status_class}">{comp['status']}</td>
                <td>{comp['time_before']:.4f}s</td>
                <td>-</td>
                <td class="positive">Removed</td>
                <td>{comp['calls_before']}</td>
                <td>-</td>
                <td class="positive">Removed</td>
            </tr>
            """
        else:  # added
            comparison_rows += f"""
            <tr class="{status_class}">
                <td>{comp['name']}</td>
                <td class="status-badge status-{status_class}">{comp['status']}</td>
                <td>-</td>
                <td>{comp['time_after']:.4f}s</td>
                <td class="negative">New</td>
                <td>-</td>
                <td>{comp['calls_after']}</td>
                <td class="negative">New</td>
            </tr>
            """
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.2/vis-network.min.css" rel="stylesheet" />
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1800px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 2px solid #dee2e6;
        }}
        
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.2s;
        }}
        
        .summary-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .summary-value {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .summary-value.positive {{
            color: #28a745;
        }}
        
        .summary-value.negative {{
            color: #dc3545;
        }}
        
        .summary-value.neutral {{
            color: #667eea;
        }}
        
        .summary-label {{
            font-size: 0.9em;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .graphs-container {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2px;
            background: #dee2e6;
        }}
        
        .graph-panel {{
            background: white;
            padding: 20px;
        }}
        
        .graph-title {{
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 15px;
            color: #495057;
            text-align: center;
            padding: 10px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 6px;
        }}
        
        .network {{
            width: 100%;
            height: 500px;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            background: #ffffff;
        }}
        
        .comparison-table {{
            padding: 30px;
        }}
        
        .table-title {{
            font-size: 1.8em;
            font-weight: bold;
            margin-bottom: 20px;
            color: #495057;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }}
        
        thead {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 1px;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #dee2e6;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .status-modified {{
            background: #ffc107;
            color: #000;
        }}
        
        .status-added {{
            background: #28a745;
            color: white;
        }}
        
        .status-removed {{
            background: #dc3545;
            color: white;
        }}
        
        .positive {{
            color: #28a745;
            font-weight: 600;
        }}
        
        .negative {{
            color: #dc3545;
            font-weight: 600;
        }}
        
        .improvement {{
            background: #d4edda;
        }}
        
        .regression {{
            background: #f8d7da;
        }}
        
        .legend {{
            padding: 20px 30px;
            background: #f8f9fa;
            border-top: 2px solid #dee2e6;
        }}
        
        .legend-title {{
            font-weight: bold;
            margin-bottom: 10px;
            color: #495057;
        }}
        
        .legend-items {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 {title}</h1>
            <p>Side-by-Side Performance Comparison</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <div class="summary-value {'positive' if summary['time_saved'] > 0 else 'negative' if summary['time_saved'] < 0 else 'neutral'}">
                    {summary['time_saved']:+.3f}s
                </div>
                <div class="summary-label">Time Saved</div>
            </div>
            
            <div class="summary-card">
                <div class="summary-value {'positive' if summary['time_saved_pct'] > 0 else 'negative' if summary['time_saved_pct'] < 0 else 'neutral'}">
                    {summary['time_saved_pct']:+.1f}%
                </div>
                <div class="summary-label">Performance Change</div>
            </div>
            
            <div class="summary-card">
                <div class="summary-value positive">
                    {summary['improvements']}
                </div>
                <div class="summary-label">Improvements</div>
            </div>
            
            <div class="summary-card">
                <div class="summary-value negative">
                    {summary['regressions']}
                </div>
                <div class="summary-label">Regressions</div>
            </div>
            
            <div class="summary-card">
                <div class="summary-value neutral">
                    {summary['nodes_added']}
                </div>
                <div class="summary-label">Functions Added</div>
            </div>
            
            <div class="summary-card">
                <div class="summary-value neutral">
                    {summary['nodes_removed']}
                </div>
                <div class="summary-label">Functions Removed</div>
            </div>
        </div>
        
        <div class="graphs-container">
            <div class="graph-panel">
                <div class="graph-title">🔴 {label1}</div>
                <div id="network1" class="network"></div>
                <div style="text-align: center; margin-top: 10px; color: #6c757d;">
                    <strong>Duration:</strong> {summary['total_time_before']:.3f}s | 
                    <strong>Functions:</strong> {summary['nodes_before']}
                </div>
            </div>
            
            <div class="graph-panel">
                <div class="graph-title">🟢 {label2}</div>
                <div id="network2" class="network"></div>
                <div style="text-align: center; margin-top: 10px; color: #6c757d;">
                    <strong>Duration:</strong> {summary['total_time_after']:.3f}s | 
                    <strong>Functions:</strong> {summary['nodes_after']}
                </div>
            </div>
        </div>
        
        <div class="comparison-table">
            <div class="table-title">📋 Detailed Comparison</div>
            <table>
                <thead>
                    <tr>
                        <th>Function</th>
                        <th>Status</th>
                        <th>{label1} Time</th>
                        <th>{label2} Time</th>
                        <th>Time Δ</th>
                        <th>{label1} Calls</th>
                        <th>{label2} Calls</th>
                        <th>Calls Δ</th>
                    </tr>
                </thead>
                <tbody>
                    {comparison_rows}
                </tbody>
            </table>
        </div>
        
        <div class="legend">
            <div class="legend-title">Legend</div>
            <div class="legend-items">
                <div class="legend-item">
                    <div class="legend-color" style="background: #d4edda;"></div>
                    <span>Performance Improvement</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #f8d7da;"></div>
                    <span>Performance Regression</span>
                </div>
                <div class="legend-item">
                    <span class="status-badge status-modified">Modified</span>
                    <span>Function exists in both</span>
                </div>
                <div class="legend-item">
                    <span class="status-badge status-added">Added</span>
                    <span>New function</span>
                </div>
                <div class="legend-item">
                    <span class="status-badge status-removed">Removed</span>
                    <span>Function removed</span>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Graph 1 data
        var nodes1 = {nodes1_json};
        var edges1 = {edges1_json};
        
        // Graph 2 data
        var nodes2 = {nodes2_json};
        var edges2 = {edges2_json};
        
        // Network options
        var options = {{
            nodes: {{
                shape: 'box',
                font: {{
                    size: 12,
                    color: '#ffffff'
                }},
                borderWidth: 2,
                shadow: true,
                margin: 10
            }},
            edges: {{
                arrows: {{
                    to: {{enabled: true, scaleFactor: 0.8}}
                }},
                smooth: {{
                    type: 'continuous'
                }},
                shadow: true
            }},
            physics: {{
                enabled: true,
                solver: 'forceAtlas2Based',
                stabilization: {{
                    iterations: 200
                }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 200
            }}
        }};
        
        // Create networks
        var container1 = document.getElementById('network1');
        var network1 = new vis.Network(container1, {{
            nodes: new vis.DataSet(nodes1),
            edges: new vis.DataSet(edges1)
        }}, options);
        
        var container2 = document.getElementById('network2');
        var network2 = new vis.Network(container2, {{
            nodes: new vis.DataSet(nodes2),
            edges: new vis.DataSet(edges2)
        }}, options);
        
        // Synchronize zoom and pan (optional)
        network1.on('zoom', function(params) {{
            // network2.moveTo({{scale: params.scale}});
        }});
        
        network2.on('zoom', function(params) {{
            // network1.moveTo({{scale: params.scale}});
        }});
    </script>
</body>
</html>"""
    
    return html_template


def _get_comparison_color(avg_time: float) -> str:
    """Get color for node based on average execution time."""
    if avg_time > 0.1:  # > 100ms
        return "#ff6b6b"  # Red
    elif avg_time > 0.01:  # 10-100ms
        return "#4ecdc4"  # Teal
    else:  # < 10ms
        return "#45b7d1"  # Blue
