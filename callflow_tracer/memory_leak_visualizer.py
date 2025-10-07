"""
Memory Leak Visualization for callflow-tracer.

This module provides HTML visualization for memory leak detection results.
"""

import json
from pathlib import Path
from typing import Union, Dict, Any


def export_leak_report(detector, output_path: Union[str, Path]) -> None:
    """
    Export memory leak detection report to HTML.
    
    Args:
        detector: MemoryLeakDetector instance
        output_path: Path to save the HTML report
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    report = detector.get_report()
    html_content = _generate_leak_report_html(report)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def _generate_leak_report_html(report: Dict[str, Any]) -> str:
    """Generate HTML content for leak report."""
    
    obj_stats = report['object_stats']
    suspected_leaks = report['suspected_leaks']
    growth_patterns = report['growth_patterns']
    
    # Generate leak severity
    leak_count = len(suspected_leaks)
    if leak_count == 0:
        severity = 'good'
        severity_text = '✅ No Leaks Detected'
        severity_color = '#28a745'
    elif leak_count <= 2:
        severity = 'warning'
        severity_text = '⚠️ Potential Leaks'
        severity_color = '#ffc107'
    else:
        severity = 'critical'
        severity_text = '🔴 Critical Leaks'
        severity_color = '#dc3545'
    
    # Generate leak details HTML
    leak_details_html = ""
    for i, leak in enumerate(suspected_leaks):
        leak_type = leak['type'].replace('_', ' ').title()
        
        if leak['type'] == 'unreleased_objects':
            details = f"""
                <div class="leak-detail">
                    <strong>Count:</strong> {leak['count']} objects<br>
                    <strong>Types:</strong>
                    <ul>
                        {''.join(f'<li>{t}: {c}</li>' for t, c in list(leak['details'].items())[:10])}
                    </ul>
                </div>
            """
        elif leak['type'] == 'continuous_growth':
            details = f"""
                <div class="leak-detail">
                    <strong>Growth Rate:</strong> {leak['avg_growth_rate']:.2f} bytes/sec<br>
                    <strong>Patterns:</strong> {len(leak['patterns'])} growth events detected
                </div>
            """
        elif leak['type'] == 'reference_cycles':
            details = f"""
                <div class="leak-detail">
                    <strong>Cycles Found:</strong> {leak['count']}<br>
                    <strong>Object Types:</strong> {', '.join(leak['objects'])}
                </div>
            """
        else:
            details = f"<div class='leak-detail'>{json.dumps(leak, indent=2)}</div>"
        
        leak_details_html += f"""
        <div class="leak-card leak-{severity}">
            <div class="leak-header">
                <span class="leak-number">#{i+1}</span>
                <span class="leak-type">{leak_type}</span>
            </div>
            {details}
        </div>
        """
    
    # Generate growth pattern chart data
    growth_chart_data = []
    if growth_patterns:
        for pattern in growth_patterns:
            growth_chart_data.append({
                'label': pattern['to_snapshot'],
                'memory': pattern['memory_growth'],
                'objects': pattern['object_growth']
            })
    
    growth_chart_json = json.dumps(growth_chart_data)
    
    # Generate snapshot comparison table
    snapshot_rows = ""
    if len(report.get('snapshot_comparisons', [])) > 0:
        for i, comp in enumerate(report['snapshot_comparisons']):
            memory_change = comp['memory_diff']
            memory_class = 'positive' if memory_change > 0 else 'negative' if memory_change < 0 else 'neutral'
            
            snapshot_rows += f"""
            <tr>
                <td>{i}</td>
                <td>{comp['time_diff']:.3f}s</td>
                <td class="{memory_class}">{memory_change:+,} bytes</td>
                <td class="{memory_class}">{comp['objects_diff']:+,}</td>
                <td>{len(comp.get('type_changes', {}))}</td>
            </tr>
            """
    
    # Generate type distribution
    type_dist_html = ""
    if obj_stats.get('type_distribution'):
        sorted_types = sorted(
            obj_stats['type_distribution'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:15]
        
        for obj_type, count in sorted_types:
            percentage = (count / obj_stats['currently_live'] * 100) if obj_stats['currently_live'] > 0 else 0
            type_dist_html += f"""
            <div class="type-bar">
                <div class="type-label">{obj_type}</div>
                <div class="type-bar-container">
                    <div class="type-bar-fill" style="width: {percentage}%"></div>
                    <div class="type-count">{count}</div>
                </div>
            </div>
            """
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Memory Leak Detection Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
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
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .severity-badge {{
            display: inline-block;
            padding: 10px 30px;
            border-radius: 25px;
            font-size: 1.2em;
            font-weight: bold;
            margin-top: 20px;
            background: {severity_color};
            color: white;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 2px solid #dee2e6;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.2s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .stat-value.good {{
            color: #28a745;
        }}
        
        .stat-value.warning {{
            color: #ffc107;
        }}
        
        .stat-value.critical {{
            color: #dc3545;
        }}
        
        .stat-label {{
            font-size: 0.9em;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .section {{
            padding: 30px;
        }}
        
        .section-title {{
            font-size: 1.8em;
            font-weight: bold;
            margin-bottom: 20px;
            color: #495057;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .leak-card {{
            background: white;
            border-left: 5px solid;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .leak-card.leak-good {{
            border-color: #28a745;
            background: #d4edda;
        }}
        
        .leak-card.leak-warning {{
            border-color: #ffc107;
            background: #fff3cd;
        }}
        
        .leak-card.leak-critical {{
            border-color: #dc3545;
            background: #f8d7da;
        }}
        
        .leak-header {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
        }}
        
        .leak-number {{
            background: #667eea;
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }}
        
        .leak-type {{
            font-size: 1.3em;
            font-weight: bold;
            color: #495057;
        }}
        
        .leak-detail {{
            padding: 15px;
            background: white;
            border-radius: 6px;
            line-height: 1.8;
        }}
        
        .leak-detail ul {{
            margin-left: 20px;
            margin-top: 10px;
        }}
        
        .chart-container {{
            position: relative;
            height: 400px;
            margin: 20px 0;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
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
        
        .positive {{
            color: #dc3545;
            font-weight: 600;
        }}
        
        .negative {{
            color: #28a745;
            font-weight: 600;
        }}
        
        .neutral {{
            color: #6c757d;
        }}
        
        .type-bar {{
            margin-bottom: 15px;
        }}
        
        .type-label {{
            font-weight: 600;
            margin-bottom: 5px;
            color: #495057;
        }}
        
        .type-bar-container {{
            position: relative;
            background: #e9ecef;
            height: 30px;
            border-radius: 15px;
            overflow: hidden;
        }}
        
        .type-bar-fill {{
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            height: 100%;
            transition: width 0.3s ease;
        }}
        
        .type-count {{
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            font-weight: bold;
            color: #495057;
        }}
        
        .no-leaks {{
            text-align: center;
            padding: 60px;
            background: #d4edda;
            border-radius: 8px;
            color: #155724;
        }}
        
        .no-leaks h2 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        
        .recommendations {{
            background: #e7f3ff;
            border-left: 5px solid #0066cc;
            padding: 20px;
            margin-top: 20px;
            border-radius: 8px;
        }}
        
        .recommendations h3 {{
            color: #0066cc;
            margin-bottom: 15px;
        }}
        
        .recommendations ul {{
            margin-left: 20px;
            line-height: 2;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💾 Memory Leak Detection Report</h1>
            <p class="subtitle">Comprehensive Memory Analysis & Leak Detection</p>
            <div class="severity-badge">{severity_text}</div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value neutral">{report['duration']:.2f}s</div>
                <div class="stat-label">Analysis Duration</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value neutral">{report['snapshots']}</div>
                <div class="stat-label">Snapshots Taken</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value neutral">{obj_stats['total_tracked']:,}</div>
                <div class="stat-label">Objects Tracked</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value {severity}">{obj_stats['leaked_count']}</div>
                <div class="stat-label">Potential Leaks</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">🔍 Detected Issues</div>
            
            {leak_details_html if leak_details_html else '<div class="no-leaks"><h2>✅ No Memory Leaks Detected!</h2><p>Your code appears to be managing memory properly.</p></div>'}
        </div>
        
        {f'''
        <div class="section">
            <div class="section-title">📈 Memory Growth Pattern</div>
            <div class="chart-container">
                <canvas id="growthChart"></canvas>
            </div>
        </div>
        ''' if growth_patterns else ''}
        
        <div class="section">
            <div class="section-title">📊 Object Type Distribution</div>
            {type_dist_html if type_dist_html else '<p>No object data available.</p>'}
        </div>
        
        {f'''
        <div class="section">
            <div class="section-title">📸 Snapshot Comparisons</div>
            <table>
                <thead>
                    <tr>
                        <th>Snapshot</th>
                        <th>Time Elapsed</th>
                        <th>Memory Change</th>
                        <th>Object Change</th>
                        <th>Type Changes</th>
                    </tr>
                </thead>
                <tbody>
                    {snapshot_rows}
                </tbody>
            </table>
        </div>
        ''' if snapshot_rows else ''}
        
        <div class="section">
            <div class="recommendations">
                <h3>💡 Recommendations</h3>
                <ul>
                    <li><strong>Regular Monitoring:</strong> Run leak detection periodically during development</li>
                    <li><strong>Profile Production:</strong> Use sampling to minimize overhead in production</li>
                    <li><strong>Fix Cycles:</strong> Break reference cycles with weak references</li>
                    <li><strong>Clean Resources:</strong> Always close files, connections, and other resources</li>
                    <li><strong>Use Context Managers:</strong> Prefer 'with' statements for automatic cleanup</li>
                    <li><strong>Monitor Growth:</strong> Watch for continuous memory growth patterns</li>
                </ul>
            </div>
        </div>
    </div>
    
    <script>
        // Growth chart
        var growthData = {growth_chart_json};
        
        if (growthData.length > 0) {{
            var ctx = document.getElementById('growthChart').getContext('2d');
            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: growthData.map(d => d.label),
                    datasets: [{{
                        label: 'Memory Growth (bytes)',
                        data: growthData.map(d => d.memory),
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4,
                        fill: true
                    }}, {{
                        label: 'Object Growth',
                        data: growthData.map(d => d.objects),
                        borderColor: '#764ba2',
                        backgroundColor: 'rgba(118, 75, 162, 0.1)',
                        tension: 0.4,
                        fill: true,
                        yAxisID: 'y1'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            display: true,
                            position: 'top'
                        }},
                        title: {{
                            display: true,
                            text: 'Memory and Object Growth Over Time'
                        }}
                    }},
                    scales: {{
                        y: {{
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: {{
                                display: true,
                                text: 'Memory (bytes)'
                            }}
                        }},
                        y1: {{
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: {{
                                display: true,
                                text: 'Objects'
                            }},
                            grid: {{
                                drawOnChartArea: false
                            }}
                        }}
                    }}
                }}
            }});
        }}
    </script>
</body>
</html>"""
    
    return html_template
