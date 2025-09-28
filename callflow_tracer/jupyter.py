"""
Jupyter notebook integration for callflow-tracer.

This module provides IPython magic commands and display functions for using
callflow-tracer within Jupyter notebooks.
"""

from IPython.core.magic import register_line_magic, register_cell_magic
from IPython.display import HTML, display
import tempfile
import os
import webbrowser
from pathlib import Path
from typing import Optional, Dict, Any

from .tracer import trace_scope, get_current_graph, clear_trace
from .exporter import export_html


def init_jupyter():
    """Initialize Jupyter notebook integration."""
    # Register magic commands
    register_line_magic(callflow_trace)
    register_cell_magic(callflow_cell_trace)
    
    print("Callflow Tracer Jupyter integration loaded. Use %callflow_trace or %%callflow_cell_trace")


def display_callgraph(graph_data: Dict[str, Any], 
                     width: str = "100%", 
                     height: str = "600px",
                     layout: str = "hierarchical") -> None:
    """
    Display an interactive call graph in a Jupyter notebook.
    
    Args:
        graph_data: The call graph data to display
        width: Width of the visualization (CSS string)
        height: Height of the visualization (CSS string)
        layout: Initial layout to use ('hierarchical', 'force', 'circular', 'timeline')
    """
    # Generate a unique ID for this visualization
    import uuid
    div_id = f"callflow-viz-{uuid.uuid4().hex}"
    
    # Prepare the HTML/JS for the visualization
    html = f"""
    <div id="{div_id}" style="width:{width}; height:{height}; border:1px solid #ddd;"></div>
    <script>
    require.config({{ 
        paths: {{ 
            'vis': 'https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min',
            'jquery': 'https://code.jquery.com/jquery-3.6.0.min',
            'select2': 'https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min'
        }},
        map: {{
            '*': {{
                'css': 'https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.css',
                'select2css': 'https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css'
            }}
        }}
    }});
    
    require(['vis', 'jquery', 'select2', 'css!', 'select2css!'], function(vis, $) {{
        // Initialize network
        var container = document.getElementById('{div_id}');
        var data = {{
            nodes: new vis.DataSet({nodes}),
            edges: new vis.DataSet({edges})
        }};
        
        // Network options
        var options = {{
            nodes: {{
                shape: 'box',
                font: {{
                    size: 12,
                    color: '#333',
                    strokeWidth: 0
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
                }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 200
            }}
        }};
        
        // Create the network
        var network = new vis.Network(container, data, options);
        
        // Set initial layout
        changeLayout('{layout}');
        
        // Layout management
        function changeLayout(layoutType) {{
            var options = network.getOptions();
            
            switch(layoutType) {{
                case 'hierarchical':
                    options.layout = {{
                        hierarchical: {{
                            direction: 'UD',
                            sortMethod: 'directed',
                            nodeSpacing: 150,
                            levelSeparation: 150
                        }}
                    }};
                    options.physics = {{
                        hierarchicalRepulsion: {{
                            nodeDistance: 120,
                            springLength: 100,
                            springConstant: 0.01,
                            damping: 0.09
                        }},
                        solver: 'hierarchicalRepulsion'
                    }};
                    break;
                    
                case 'force':
                    options.layout = {{ improvedLayout: true }};
                    options.physics = {{
                        forceAtlas2Based: {{
                            gravitationalConstant: -50,
                            centralGravity: 0.01,
                            springLength: 100,
                            springConstant: 0.08,
                            damping: 0.4
                        }},
                        solver: 'forceAtlas2Based',
                        stabilization: {{
                            enabled: true,
                            iterations: 1000,
                            updateInterval: 25
                        }}
                    }};
                    break;
                    
                case 'circular':
                    options.layout = {{
                        randomSeed: 42,
                        improvedLayout: true
                    }};
                    options.physics = {{
                        forceAtlas2Based: {{
                            gravitationalConstant: -50,
                            centralGravity: 0.01,
                            springLength: 100,
                            springConstant: 0.08,
                            damping: 0.4
                        }},
                        solver: 'forceAtlas2Based'
                    }};
                    break;
            }}
            
            network.setOptions(options);
            network.fit();
        }}
        
        // Expose functions to global scope for UI controls
        window['{div_id}_changeLayout'] = changeLayout;
    }});
    </script>
    
    <div style="margin-top: 10px;">
        <button onclick="window['{div_id}_changeLayout']('hierarchical')">Hierarchical</button>
        <button onclick="window['{div_id}_changeLayout']('force')">Force-Directed</button>
        <button onclick="window['{div_id}_changeLayout']('circular')">Circular</button>
    </div>
    """.format(
        div_id=div_id,
        nodes=graph_data['nodes'],
        edges=graph_data['edges'],
        layout=layout
    )
    
    display(HTML(html))


def callflow_trace(line):
    """
    Line magic to trace a single line of code.
    
    Usage:
        %callflow_trace my_function()
    """
    if not line:
        print("Usage: %callflow_trace <expression>")
        return
    
    # Execute the line in the user's namespace
    result = get_ipython().run_cell(line)
    
    # Get the current graph
    graph = get_current_graph()
    if graph is None:
        print("No call graph data captured. Make sure to use @trace decorator or trace_scope context manager.")
        return
    
    # Display the graph
    display_callgraph(graph.to_dict())
    
    return result


def callflow_cell_trace(line, cell):
    """
    Cell magic to trace an entire cell.
    
    Usage:
        %%callflow_cell_trace
        def my_function():
            return 42
            
        my_function()
    """
    clear_trace()
    
    # Execute the cell in the user's namespace with tracing enabled
    with trace_scope():
        result = get_ipython().run_cell(cell)
    
    # Get the current graph
    graph = get_current_graph()
    if graph is None:
        print("No call graph data captured.")
        return result
    
    # Display the graph
    display_callgraph(graph.to_dict())
    
    return result


# Load the extension when imported
if 'get_ipython' in globals():
    init_jupyter()
