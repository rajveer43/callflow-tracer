"""
Enhanced flamegraph HTML generation with advanced features.

This module contains the enhanced HTML template for flamegraphs with:
- Statistics panel
- Search functionality
- Color schemes
- Performance metrics
- Export options
- Comparison mode
"""

def generate_enhanced_html_template(flame_data_json, width, height, title, 
                                   color_scheme, stats, min_width, search_enabled):
    """Generate enhanced HTML with all new features."""
    
    # Prepare statistics HTML
    stats_html = ""
    if stats:
        stats_html = f"""
        <div class="stats-panel">
            <h3>📊 Statistics</h3>
            <div class="stat-grid">
                <div class="stat-item">
                    <div class="stat-label">Total Functions</div>
                    <div class="stat-value">{stats['total_functions']}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Total Calls</div>
                    <div class="stat-value">{stats['total_calls']:,}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Total Time</div>
                    <div class="stat-value">{stats['total_time']:.4f}s</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Avg Time/Call</div>
                    <div class="stat-value">{stats['avg_time_per_call']:.4f}s</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Call Depth</div>
                    <div class="stat-value">{stats['call_depth']}</div>
                </div>
                <div class="stat-item highlight">
                    <div class="stat-label">🔥 Slowest Function</div>
                    <div class="stat-value-small">{stats['slowest_function']['name']}</div>
                    <div class="stat-subvalue">{stats['slowest_function']['time']:.4f}s</div>
                </div>
                <div class="stat-item highlight">
                    <div class="stat-label">📞 Most Called</div>
                    <div class="stat-value-small">{stats['most_called_function']['name']}</div>
                    <div class="stat-subvalue">{stats['most_called_function']['count']:,} calls</div>
                </div>
            </div>
        </div>
        """
    
    # Search HTML
    search_html = ""
    if search_enabled:
        search_html = """
        <div class="search-container">
            <input type="text" id="searchBox" placeholder="🔍 Search functions..." />
            <button onclick="clearSearch()">Clear</button>
        </div>
        """
    
    # Color scheme options
    color_schemes = {
        'default': 'Default',
        'hot': 'Hot (Red-Orange)',
        'cool': 'Cool (Blue-Green)',
        'rainbow': 'Rainbow',
        'performance': 'Performance (Fast=Green, Slow=Red)'
    }
    
    color_options = ''.join([
        f'<option value="{key}" {"selected" if key == color_scheme else ""}>{value}</option>'
        for key, value in color_schemes.items()
    ])
    
    chart_width = width - 40
    chart_height = height - 40
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
        * {{
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: {width + 100}px;
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
            margin: 0 0 10px 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        
        .header p {{
            margin: 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        
        .stats-panel {{
            padding: 20px 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .stats-panel h3 {{
            margin: 0 0 15px 0;
            color: #495057;
            font-size: 1.3em;
        }}
        
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }}
        
        .stat-item {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #e9ecef;
            text-align: center;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .stat-item:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        
        .stat-item.highlight {{
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
            border-color: #667eea;
        }}
        
        .stat-label {{
            font-size: 0.85em;
            color: #6c757d;
            margin-bottom: 5px;
            font-weight: 600;
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-value-small {{
            font-size: 1.1em;
            font-weight: 600;
            color: #495057;
            margin: 5px 0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        
        .stat-subvalue {{
            font-size: 1.3em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .controls {{
            padding: 20px 30px;
            background: white;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            align-items: center;
            justify-content: space-between;
        }}
        
        .control-group {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        
        .search-container {{
            flex: 1;
            min-width: 250px;
            display: flex;
            gap: 10px;
        }}
        
        #searchBox {{
            flex: 1;
            padding: 10px 15px;
            border: 2px solid #e9ecef;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.3s;
        }}
        
        #searchBox:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        button, select {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
            box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
        }}
        
        button:hover, select:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(102, 126, 234, 0.4);
        }}
        
        button:active {{
            transform: translateY(0);
        }}
        
        select {{
            padding-right: 30px;
            appearance: none;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='white' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 10px center;
        }}
        
        #chart {{
            width: {width}px;
            height: {height}px;
            margin: 0 auto;
            background: white;
            position: relative;
        }}
        
        .tooltip {{
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 12px 16px;
            border-radius: 6px;
            font-size: 13px;
            pointer-events: none;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            max-width: 300px;
        }}
        
        .tooltip strong {{
            font-size: 14px;
            display: block;
            margin-bottom: 5px;
            color: #4ecdc4;
        }}
        
        .error-message {{
            text-align: center;
            color: #666;
            margin: 40px;
            font-style: italic;
            font-size: 1.1em;
        }}
        
        .legend {{
            padding: 20px 30px;
            background: #f8f9fa;
            border-top: 1px solid #e9ecef;
        }}
        
        .legend h4 {{
            margin: 0 0 15px 0;
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
            font-size: 14px;
            color: #495057;
        }}
        
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }}
        
        .info-panel {{
            padding: 20px 30px;
            background: white;
            border-top: 1px solid #e9ecef;
        }}
        
        .info-panel h4 {{
            margin: 0 0 10px 0;
            color: #495057;
        }}
        
        .info-panel ul {{
            margin: 0;
            padding-left: 20px;
            color: #6c757d;
        }}
        
        .info-panel li {{
            margin: 5px 0;
        }}
        
        @media (max-width: 768px) {{
            .controls {{
                flex-direction: column;
                align-items: stretch;
            }}
            
            .control-group {{
                flex-direction: column;
            }}
            
            .stat-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 {title}</h1>
            <p>Interactive Performance Visualization</p>
        </div>
        
        {stats_html}
        
        <div class="controls">
            {search_html}
            
            <div class="control-group">
                <label style="color: #495057; font-weight: 600;">Color Scheme:</label>
                <select id="colorScheme" onchange="changeColorScheme(this.value)">
                    {color_options}
                </select>
            </div>
            
            <div class="control-group">
                <button onclick="zoomToFit()">🔍 Zoom to Fit</button>
                <button onclick="resetZoom()">↺ Reset</button>
                <button onclick="exportSVG()">💾 Export SVG</button>
            </div>
        </div>
        
        <div id="chart"></div>
        <div id="tooltip" class="tooltip" style="display: none;"></div>
        
        <div class="legend">
            <h4>📖 How to Read This Flamegraph</h4>
            <div class="legend-items">
                <div class="legend-item">
                    <div class="legend-color" style="background: linear-gradient(90deg, #4ecdc4, #ff6b6b);"></div>
                    <span><strong>Width</strong> = Time spent (wider = slower)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: linear-gradient(0deg, #4ecdc4, #667eea);"></div>
                    <span><strong>Height</strong> = Call stack depth</span>
                </div>
                <div class="legend-item">
                    <span>🖱️ <strong>Click</strong> to zoom in</span>
                </div>
                <div class="legend-item">
                    <span>👆 <strong>Hover</strong> for details</span>
                </div>
            </div>
        </div>
        
        <div class="info-panel">
            <h4>💡 Tips for Performance Optimization</h4>
            <ul>
                <li><strong>Wide bars</strong> indicate functions where most time is spent - these are your optimization targets</li>
                <li><strong>Tall stacks</strong> show deep call chains - consider flattening if excessive</li>
                <li><strong>Repeated patterns</strong> suggest loops or recursion - check for optimization opportunities</li>
                <li>Use the search box to quickly find specific functions</li>
                <li>Try different color schemes to highlight different aspects</li>
            </ul>
        </div>
    </div>
    
    <!-- Load D3.js and D3 flame graph plugin -->
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/d3-flame-graph@4.1.3/dist/d3-flamegraph.min.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/d3-flame-graph@4.1.3/dist/d3-flamegraph.css">
    
    <script>
        let chart;
        let currentData;
        let currentColorScheme = '{color_scheme}';
        const minWidthThreshold = {min_width};
        
        // Color scheme definitions
        const colorSchemes = {{
            default: (d) => d3.interpolateRdYlGn(1 - (d.data.value / 1000)),
            hot: (d) => d3.interpolateYlOrRd(d.data.value / 1000),
            cool: (d) => d3.interpolateCool(d.data.value / 1000),
            rainbow: (d) => d3.interpolateRainbow(d.data.value / 1000),
            performance: (d) => {{
                const time = d.data.total_time || 0;
                if (time < 0.01) return '#4ecdc4'; // Fast - cyan
                if (time < 0.1) return '#45b7d1';  // Medium - blue
                if (time < 0.5) return '#f7b731';  // Slow - yellow
                return '#ff6b6b';                   // Very slow - red
            }}
        }};
        
        try {{
            // Initialize flame graph
            const data = {flame_data_json};
            
            // Check if we have valid data
            if (!data || data.length === 0) {{
                document.getElementById('chart').innerHTML = '<div class="error-message">No flame graph data available</div>';
                throw new Error('No flame graph data');
            }}
            
            // Store current data
            currentData = data;
            
            // Create the chart
            initializeChart(data);
            
        }} catch (error) {{
            console.error('Error creating flame graph:', error);
            document.getElementById('chart').innerHTML = '<div class="error-message">Error creating flame graph: ' + error.message + '</div>';
        }}
        
        function initializeChart(data) {{
            const container = d3.select("#chart");
            container.selectAll("*").remove(); // Clear existing
            
            chart = flamegraph()
                .width({chart_width})
                .height({chart_height})
                .cellHeight(18)
                .transitionDuration(750)
                .minFrameSize(5)
                .transitionEase(d3.easeCubic)
                .tooltip(function(d) {{
                    let tooltip = '<strong>' + (d.data.name || 'Unknown') + '</strong><br/>';
                    tooltip += 'Total Time: ' + (d.data.total_time ? d.data.total_time.toFixed(4) + 's' : 'N/A') + '<br/>';
                    tooltip += 'Avg Time: ' + (d.data.avg_time ? d.data.avg_time.toFixed(4) + 's' : 'N/A') + '<br/>';
                    tooltip += 'Calls: ' + (d.data.call_count || 1) + '<br/>';
                    
                    // Calculate percentage
                    const totalTime = {stats['total_time'] if stats else 0};
                    if (totalTime > 0 && d.data.total_time) {{
                        const percentage = (d.data.total_time / totalTime * 100).toFixed(2);
                        tooltip += 'Percentage: ' + percentage + '%';
                    }}
                    
                    return tooltip;
                }})
                .sort((a, b) => b.value - a.value)
                .color(colorSchemes[currentColorScheme]);
                
            // Use the first root node or create a wrapper if multiple roots
            const rootData = data.length === 1 ? data[0] : {{
                name: 'Root',
                value: data.reduce((sum, d) => sum + (d.value || 0), 0),
                children: data
            }};
            
            container.datum(rootData).call(chart);
        }}
        
        // Zoom to fit the entire graph
        window.zoomToFit = function() {{
            if (chart) chart.resetZoom();
        }};
        
        // Reset zoom
        window.resetZoom = function() {{
            if (chart) chart.resetZoom();
        }};
        
        // Change color scheme
        window.changeColorScheme = function(scheme) {{
            currentColorScheme = scheme;
            if (chart && currentData) {{
                initializeChart(currentData);
            }}
        }};
        
        // Search functionality
        window.searchFunction = function() {{
            const searchTerm = document.getElementById('searchBox').value.toLowerCase();
            if (!searchTerm) {{
                clearSearch();
                return;
            }}
            
            if (chart) {{
                chart.search(searchTerm);
            }}
        }};
        
        window.clearSearch = function() {{
            document.getElementById('searchBox').value = '';
            if (chart) {{
                chart.clear();
            }}
        }};
        
        // Export SVG
        window.exportSVG = function() {{
            try {{
                const svg = document.querySelector('#chart svg');
                if (!svg) {{
                    alert('No SVG found to export');
                    return;
                }}
                
                const serializer = new XMLSerializer();
                const svgString = serializer.serializeToString(svg);
                const blob = new Blob([svgString], {{type: 'image/svg+xml'}});
                const url = URL.createObjectURL(blob);
                
                const link = document.createElement('a');
                link.href = url;
                link.download = 'flamegraph-' + new Date().toISOString().slice(0, 10) + '.svg';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                URL.revokeObjectURL(url);
                
                console.log('SVG exported successfully');
            }} catch (error) {{
                console.error('Error exporting SVG:', error);
                alert('Error exporting SVG: ' + error.message);
            }}
        }};
        
        // Add search on Enter key
        if (document.getElementById('searchBox')) {{
            document.getElementById('searchBox').addEventListener('keyup', function(event) {{
                if (event.key === 'Enter') {{
                    searchFunction();
                }} else if (this.value === '') {{
                    clearSearch();
                }}
            }});
        }}
        
        // Handle window resize
        window.addEventListener('resize', function() {{
            if (chart && currentData) {{
                const newWidth = Math.min(document.getElementById('chart').clientWidth - 40, {chart_width});
                chart.width(newWidth);
                d3.select("#chart svg")
                    .attr("width", newWidth)
                    .attr("height", {chart_height});
            }}
        }});
        
    </script>
</body>
</html>"""
    
    return html
