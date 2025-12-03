const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');
const { promisify } = require('util');

const execAsync = promisify(exec);

let visualizationPanel = null;
let currentTraceData = null;

/**
 * Activate the extension
 */
function activate(context) {
    console.log('CallFlow Tracer extension is now active');

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('callflow-tracer.traceFile', traceCurrentFile),
        vscode.commands.registerCommand('callflow-tracer.traceSelection', traceSelection),
        vscode.commands.registerCommand('callflow-tracer.showVisualization', showVisualization),
        vscode.commands.registerCommand('callflow-tracer.show3DVisualization', show3DVisualization),
        vscode.commands.registerCommand('callflow-tracer.clearTrace', clearTrace),
        vscode.commands.registerCommand('callflow-tracer.exportPNG', exportPNG),
        vscode.commands.registerCommand('callflow-tracer.exportJSON', exportJSON),
        vscode.commands.registerCommand('callflow-tracer.changeLayout', changeLayout),
        vscode.commands.registerCommand('callflow-tracer.exportToOtel', exportToOtel),
        vscode.commands.registerCommand('callflow-tracer.exportToOtelAdvanced', exportToOtelAdvanced),
        vscode.commands.registerCommand('callflow-tracer.analyzeAnomalies', analyzeAnomalies),
        vscode.commands.registerCommand('callflow-tracer.enableAutoInstrumentation', enableAutoInstrumentation),
        vscode.commands.registerCommand('callflow-tracer.showPluginManager', showPluginManager),
        vscode.commands.registerCommand('callflow-tracer.runCustomAnalyzer', runCustomAnalyzer)
    );

    // Register webview provider
    const provider = new CallFlowViewProvider(context.extensionUri);
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('callflowVisualization', provider)
    );

    // Auto-trace on save if enabled
    context.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument(document => {
            const config = vscode.workspace.getConfiguration('callflowTracer');
            if (config.get('autoTrace') && document.languageId === 'python') {
                traceCurrentFile();
            }
        })
    );

    // Status bar item
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.command = 'callflow-tracer.showVisualization';
    statusBarItem.text = '$(graph) CallFlow';
    statusBarItem.tooltip = 'Show CallFlow Visualization';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);
}

/**
 * Trace the current Python file
 */
async function traceCurrentFile() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No active editor');
        return;
    }

    if (editor.document.languageId !== 'python') {
        vscode.window.showErrorMessage('Current file is not a Python file');
        return;
    }

    const filePath = editor.document.uri.fsPath;
    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: 'Tracing function calls...',
        cancellable: false
    }, async (progress) => {
        try {
            progress.report({ increment: 0, message: 'Running trace...' });
            
            const traceData = await runTrace(filePath);
            
            progress.report({ increment: 50, message: 'Processing results...' });
            
            currentTraceData = traceData;
            
            progress.report({ increment: 100, message: 'Complete!' });
            
            await showVisualization();
            
            vscode.window.showInformationMessage('CallFlow trace completed successfully!');
        } catch (error) {
            vscode.window.showErrorMessage(`Trace failed: ${error.message}`);
        }
    });
}

/**
 * Trace selected function
 */
async function traceSelection() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No active editor');
        return;
    }

    const selection = editor.selection;
    const selectedText = editor.document.getText(selection);
    
    if (!selectedText) {
        vscode.window.showErrorMessage('No text selected');
        return;
    }

    // Extract function name from selection
    const functionMatch = selectedText.match(/def\s+(\w+)/);
    if (!functionMatch) {
        vscode.window.showErrorMessage('No function definition found in selection');
        return;
    }

    const functionName = functionMatch[1];
    const filePath = editor.document.uri.fsPath;

    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: `Tracing function: ${functionName}...`,
        cancellable: false
    }, async (progress) => {
        try {
            const traceData = await runTrace(filePath, functionName);
            currentTraceData = traceData;
            await showVisualization();
            vscode.window.showInformationMessage(`Traced function: ${functionName}`);
        } catch (error) {
            vscode.window.showErrorMessage(`Trace failed: ${error.message}`);
        }
    });
}

/**
 * Run the Python trace
 */
async function runTrace(filePath, functionName = null) {
    const config = vscode.workspace.getConfiguration('callflowTracer');
    const pythonPath = config.get('pythonPath', 'python3');
    const includeArgs = config.get('includeArgs', false);
    const enableProfiling = config.get('enableProfiling', true);

    // Create temporary trace script
    const traceScript = createTraceScript(filePath, functionName, includeArgs, enableProfiling);
    const tempScriptPath = path.join(path.dirname(filePath), '.callflow_trace_temp.py');
    
    fs.writeFileSync(tempScriptPath, traceScript);

    try {
        const { stdout, stderr } = await execAsync(`${pythonPath} "${tempScriptPath}"`);
        
        if (stderr && !stderr.includes('Warning')) {
            console.error('Trace stderr:', stderr);
        }

        // Read the generated JSON
        const jsonPath = path.join(path.dirname(filePath), '.callflow_trace.json');
        if (!fs.existsSync(jsonPath)) {
            throw new Error('Trace data not generated');
        }

        const traceData = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
        
        // Clean up temp files
        fs.unlinkSync(tempScriptPath);
        fs.unlinkSync(jsonPath);

        return traceData;
    } catch (error) {
        // Clean up on error
        if (fs.existsSync(tempScriptPath)) {
            fs.unlinkSync(tempScriptPath);
        }
        throw error;
    }
}

/**
 * Create Python trace script
 */
function createTraceScript(filePath, functionName, includeArgs, enableProfiling) {
    const fileName = path.basename(filePath, '.py');
    const dirPath = path.dirname(filePath);
    
    return `
import sys
import os
sys.path.insert(0, '${dirPath.replace(/\\/g, '\\\\')}')

from callflow_tracer import trace, get_current_graph, export_json
${enableProfiling ? 'from callflow_tracer import profile_section' : ''}

# Import the target module
import ${fileName}

# Trace all functions in the module
for name in dir(${fileName}):
    obj = getattr(${fileName}, name)
    if callable(obj) and not name.startswith('_'):
        setattr(${fileName}, name, trace(obj))

# Run the main function or specified function
try:
    ${functionName ? `${fileName}.${functionName}()` : `
    if hasattr(${fileName}, 'main'):
        ${fileName}.main()
    elif hasattr(${fileName}, '__main__'):
        exec(open('${filePath.replace(/\\/g, '\\\\')}').read())
    `}
except Exception as e:
    print(f"Execution error: {e}", file=sys.stderr)

# Export the trace data
graph = get_current_graph()
if graph:
    export_json(graph, '${path.join(dirPath, '.callflow_trace.json').replace(/\\/g, '\\\\')}')
else:
    print("No trace data collected", file=sys.stderr)
    sys.exit(1)
`;
}

/**
 * Show 3D visualization panel
 */
async function show3DVisualization() {
    if (!currentTraceData) {
        vscode.window.showWarningMessage('No trace data available. Run a trace first.');
        return;
    }

    const config = vscode.workspace.getConfiguration('callflowTracer');
    const defaultLayout = config.get('default3DLayout', 'force');

    const panel = vscode.window.createWebviewPanel(
        'callflow3DVisualization',
        'CallFlow 3D Visualization',
        vscode.ViewColumn.Two,
        {
            enableScripts: true,
            retainContextWhenHidden: true,
            localResourceRoots: []
        }
    );

    panel.webview.html = get3DWebviewContent(currentTraceData, defaultLayout);
}

/**
 * Show visualization panel
 */
async function showVisualization() {
    if (!currentTraceData) {
        vscode.window.showWarningMessage('No trace data available. Run a trace first.');
        return;
    }

    const config = vscode.workspace.getConfiguration('callflowTracer');
    const defaultLayout = config.get('defaultLayout', 'force');
    const defaultSpacing = config.get('defaultSpacing', 'normal');

    if (visualizationPanel) {
        visualizationPanel.reveal(vscode.ViewColumn.Two);
    } else {
        visualizationPanel = vscode.window.createWebviewPanel(
            'callflowVisualization',
            'CallFlow Visualization',
            vscode.ViewColumn.Two,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        visualizationPanel.onDidDispose(() => {
            visualizationPanel = null;
        });

        // Handle messages from webview
        visualizationPanel.webview.onDidReceiveMessage(
            message => {
                switch (message.command) {
                    case 'export-png':
                        exportPNG();
                        break;
                    case 'export-json':
                        exportJSON();
                        break;
                    case 'alert':
                        vscode.window.showInformationMessage(message.text);
                        break;
                }
            }
        );
    }

    visualizationPanel.webview.html = getWebviewContent(currentTraceData, defaultLayout, defaultSpacing);
}

/**
 * Generate webview HTML content
 */
function getWebviewContent(traceData, defaultLayout, defaultSpacing) {
    const nodes = traceData.nodes.map(node => ({
        id: node.full_name,
        label: node.name,
        title: `Module: ${node.module}\\nCalls: ${node.call_count}\\nTotal Time: ${node.total_time.toFixed(3)}s\\nAvg Time: ${node.avg_time.toFixed(3)}s`,
        group: node.module || 'main',
        value: node.call_count,
        color: getNodeColor(node.avg_time),
        module: node.module,
        shape: 'circle',
        total_time: node.total_time
    }));

    const edges = traceData.edges.map(edge => ({
        from: edge.caller,
        to: edge.callee,
        label: `${edge.call_count} calls`,
        title: `Calls: ${edge.call_count}\\nTotal Time: ${edge.total_time.toFixed(3)}s\\nAvg Time: ${edge.avg_time.toFixed(3)}s`,
        width: Math.min(Math.max(1, edge.call_count / 5), 10),
        color: getEdgeColor(edge.avg_time)
    }));

    const spacingMap = {
        'compact': 100,
        'normal': 150,
        'relaxed': 200,
        'wide': 300
    };

    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CallFlow Visualization</title>
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: var(--vscode-font-family);
            background-color: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
        }
        #controls {
            padding: 10px;
            background-color: var(--vscode-sideBar-background);
            border-bottom: 1px solid var(--vscode-panel-border);
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            align-items: center;
        }
        .control-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        .control-group label {
            font-size: 11px;
            font-weight: 600;
            color: var(--vscode-descriptionForeground);
        }
        select, button {
            padding: 4px 8px;
            background-color: var(--vscode-dropdown-background);
            color: var(--vscode-dropdown-foreground);
            border: 1px solid var(--vscode-dropdown-border);
            border-radius: 2px;
            font-size: 13px;
        }
        button {
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            cursor: pointer;
        }
        button:hover {
            background-color: var(--vscode-button-hoverBackground);
        }
        #mynetwork {
            width: 100%;
            height: calc(100vh - 60px);
            background-color: var(--vscode-editor-background);
        }
        .stats {
            display: flex;
            gap: 20px;
            padding: 10px;
            background-color: var(--vscode-sideBar-background);
            border-bottom: 1px solid var(--vscode-panel-border);
            font-size: 12px;
        }
        .stat-item {
            display: flex;
            flex-direction: column;
        }
        .stat-value {
            font-size: 16px;
            font-weight: bold;
            color: var(--vscode-textLink-foreground);
        }
        .stat-label {
            color: var(--vscode-descriptionForeground);
        }
    </style>
</head>
<body>
    <div class="stats">
        <div class="stat-item">
            <span class="stat-value">${nodes.length}</span>
            <span class="stat-label">Functions</span>
        </div>
        <div class="stat-item">
            <span class="stat-value">${edges.length}</span>
            <span class="stat-label">Relationships</span>
        </div>
        <div class="stat-item">
            <span class="stat-value">${traceData.metadata.duration.toFixed(3)}s</span>
            <span class="stat-label">Duration</span>
        </div>
    </div>
    
    <div id="controls">
        <div class="control-group">
            <label>Layout</label>
            <select id="layout">
                <option value="hierarchical">Hierarchical</option>
                <option value="force" ${defaultLayout === 'force' ? 'selected' : ''}>Force-Directed</option>
                <option value="circular">Circular</option>
                <option value="radial">Radial Tree</option>
                <option value="grid">Grid</option>
                <option value="tree">Tree (Vertical)</option>
                <option value="tree-horizontal">Tree (Horizontal)</option>
                <option value="timeline">Timeline</option>
                <option value="organic">Organic</option>
            </select>
        </div>
        
        <div class="control-group">
            <label>Spacing</label>
            <select id="spacing">
                <option value="compact">Compact</option>
                <option value="normal" ${defaultSpacing === 'normal' ? 'selected' : ''}>Normal</option>
                <option value="relaxed">Relaxed</option>
                <option value="wide">Wide</option>
            </select>
        </div>
        
        <div class="control-group">
            <label>Physics</label>
            <select id="physics">
                <option value="true">Enabled</option>
                <option value="false">Disabled</option>
            </select>
        </div>
        
        <button onclick="exportPNG()">Export PNG</button>
        <button onclick="exportJSON()">Export JSON</button>
    </div>
    
    <div id="mynetwork"></div>

    <script>
        const vscode = acquireVsCodeApi();
        
        const nodes = ${JSON.stringify(nodes)};
        const edges = ${JSON.stringify(edges)};
        
        const container = document.getElementById('mynetwork');
        const data = {
            nodes: new vis.DataSet(nodes),
            edges: new vis.DataSet(edges)
        };
        
        window.allNodes = new vis.DataSet(nodes);
        window.allEdges = new vis.DataSet(edges);
        window.currentSpacing = ${spacingMap[defaultSpacing]};
        
        const options = {
            nodes: {
                shape: 'box',
                font: { size: 12, color: '#ffffff' },
                borderWidth: 1,
                shadow: true,
                margin: 10
            },
            edges: {
                width: 1,
                shadow: true,
                smooth: { type: 'continuous' },
                arrows: { to: { enabled: true, scaleFactor: 0.8 } }
            },
            layout: { hierarchical: false },
            physics: { enabled: true, solver: "forceAtlas2Based" },
            interaction: { hover: true, tooltipDelay: 200 }
        };
        
        const network = new vis.Network(container, data, options);
        window.network = network;
        
        // Layout change handler with all 9 layouts
        window.changeLayout = function(layoutType) {
            if (layoutType === "hierarchical") {
                var resetNodes = nodes.map(function(node) {
                    return { ...node, x: undefined, y: undefined, fixed: {x: false, y: false} };
                });
                data.nodes.clear();
                data.nodes.add(resetNodes);
                network.setOptions({
                    layout: { hierarchical: { enabled: true, direction: 'UD', sortMethod: 'directed' } },
                    physics: {enabled: false}
                });
                document.getElementById('layout').value = "hierarchical";
                document.getElementById('physics').value = "false";
            } else if (layoutType === "force") {
                var resetNodes = nodes.map(function(node) {
                    return { ...node, x: undefined, y: undefined, fixed: {x: false, y: false} };
                });
                data.nodes.clear();
                data.nodes.add(resetNodes);
                network.setOptions({
                    layout: {hierarchical: false},
                    physics: {enabled: true, solver: "forceAtlas2Based"}
                });
                document.getElementById('layout').value = "force";
                document.getElementById('physics').value = "true";
            } else if (layoutType === "circular") {
                var spacing = window.currentSpacing || 150;
                var radius = spacing * 2;
                var centerX = 400, centerY = 300;
                var angleStep = 2 * Math.PI / nodes.length;
                var updatedNodes = nodes.map(function(node, i) {
                    var angle = i * angleStep;
                    return { ...node, x: centerX + radius * Math.cos(angle), y: centerY + radius * Math.sin(angle), fixed: {x: true, y: true} };
                });
                data.nodes.clear();
                data.nodes.add(updatedNodes);
                network.setOptions({ layout: {hierarchical: false}, physics: {enabled: false} });
                document.getElementById('layout').value = "circular";
                document.getElementById('physics').value = "false";
                setTimeout(() => network.fit(), 100);
            } else if (layoutType === "radial") {
                var nodeMap = {};
                nodes.forEach(n => nodeMap[n.id] = n);
                var adjacency = {};
                nodes.forEach(n => adjacency[n.id] = []);
                edges.forEach(e => {
                    if (!adjacency[e.from]) adjacency[e.from] = [];
                    adjacency[e.from].push(e.to);
                });
                var inDegree = {};
                nodes.forEach(n => inDegree[n.id] = 0);
                edges.forEach(e => inDegree[e.to] = (inDegree[e.to] || 0) + 1);
                var roots = nodes.filter(n => inDegree[n.id] === 0).map(n => n.id);
                if (roots.length === 0 && nodes.length > 0) roots = [nodes[0].id];
                var levels = {};
                var queue = roots.map(r => [r, 0]);
                var visited = new Set();
                while (queue.length > 0) {
                    var [nodeId, level] = queue.shift();
                    if (visited.has(nodeId)) continue;
                    visited.add(nodeId);
                    levels[nodeId] = level;
                    (adjacency[nodeId] || []).forEach(child => {
                        if (!visited.has(child)) queue.push([child, level + 1]);
                    });
                }
                nodes.forEach(n => { if (!(n.id in levels)) levels[n.id] = 0; });
                var levelGroups = {};
                Object.keys(levels).forEach(id => {
                    var level = levels[id];
                    if (!levelGroups[level]) levelGroups[level] = [];
                    levelGroups[level].push(id);
                });
                var centerX = 400, centerY = 300;
                var radiusStep = window.currentSpacing || 150;
                var updatedNodes = [];
                Object.keys(levelGroups).forEach(level => {
                    var levelNodes = levelGroups[level];
                    var radius = level * radiusStep + 50;
                    var angleStep = (2 * Math.PI) / levelNodes.length;
                    levelNodes.forEach((nodeId, i) => {
                        var angle = i * angleStep;
                        var node = nodeMap[nodeId];
                        updatedNodes.push({ ...node, x: centerX + radius * Math.cos(angle), y: centerY + radius * Math.sin(angle), fixed: {x: true, y: true} });
                    });
                });
                data.nodes.clear();
                data.nodes.add(updatedNodes);
                network.setOptions({ layout: {hierarchical: false}, physics: {enabled: false} });
                document.getElementById('layout').value = "radial";
                document.getElementById('physics').value = "false";
                setTimeout(() => network.fit(), 100);
            } else if (layoutType === "grid") {
                var cols = Math.ceil(Math.sqrt(nodes.length));
                var spacing = window.currentSpacing || 200;
                var startX = 100, startY = 100;
                var updatedNodes = nodes.map(function(node, i) {
                    var row = Math.floor(i / cols);
                    var col = i % cols;
                    return { ...node, x: startX + col * spacing, y: startY + row * spacing, fixed: {x: true, y: true} };
                });
                data.nodes.clear();
                data.nodes.add(updatedNodes);
                network.setOptions({ layout: {hierarchical: false}, physics: {enabled: false} });
                document.getElementById('layout').value = "grid";
                document.getElementById('physics').value = "false";
                setTimeout(() => network.fit(), 100);
            } else if (layoutType === "tree") {
                var resetNodes = nodes.map(function(node) {
                    return { ...node, x: undefined, y: undefined, fixed: {x: false, y: false} };
                });
                data.nodes.clear();
                data.nodes.add(resetNodes);
                var spacing = window.currentSpacing || 150;
                network.setOptions({
                    layout: { hierarchical: { enabled: true, direction: 'UD', sortMethod: 'directed', nodeSpacing: spacing, levelSeparation: spacing * 1.3, treeSpacing: spacing * 1.3 } },
                    physics: {enabled: false}
                });
                document.getElementById('layout').value = "tree";
                document.getElementById('physics').value = "false";
            } else if (layoutType === "tree-horizontal") {
                var resetNodes = nodes.map(function(node) {
                    return { ...node, x: undefined, y: undefined, fixed: {x: false, y: false} };
                });
                data.nodes.clear();
                data.nodes.add(resetNodes);
                var spacing = window.currentSpacing || 150;
                network.setOptions({
                    layout: { hierarchical: { enabled: true, direction: 'LR', sortMethod: 'directed', nodeSpacing: spacing, levelSeparation: spacing * 1.7, treeSpacing: spacing * 1.3 } },
                    physics: {enabled: false}
                });
                document.getElementById('layout').value = "tree-horizontal";
                document.getElementById('physics').value = "false";
            } else if (layoutType === "timeline") {
                var sorted = nodes.slice().sort(function(a, b) { return a.total_time - b.total_time; });
                var startX = 100;
                var customSpacing = window.currentSpacing || 150;
                var spacing = Math.max(customSpacing, 800 / sorted.length);
                var timelineY = 300;
                var updatedNodes = sorted.map(function(node, i) {
                    return { ...node, x: startX + i * spacing, y: timelineY, fixed: {x: true, y: true} };
                });
                data.nodes.clear();
                data.nodes.add(updatedNodes);
                network.setOptions({ layout: {hierarchical: false}, physics: {enabled: false} });
                document.getElementById('layout').value = "timeline";
                document.getElementById('physics').value = "false";
                setTimeout(() => network.fit(), 100);
            } else if (layoutType === "organic") {
                var resetNodes = nodes.map(function(node) {
                    return { ...node, x: undefined, y: undefined, fixed: {x: false, y: false} };
                });
                data.nodes.clear();
                data.nodes.add(resetNodes);
                var spacing = window.currentSpacing || 150;
                network.setOptions({
                    layout: {hierarchical: false},
                    physics: {
                        enabled: true,
                        solver: 'barnesHut',
                        barnesHut: {
                            gravitationalConstant: -8000,
                            centralGravity: 0.3,
                            springLength: spacing,
                            springConstant: 0.04,
                            damping: 0.09,
                            avoidOverlap: 0.5
                        },
                        stabilization: { iterations: 200, fit: true }
                    }
                });
                document.getElementById('layout').value = "organic";
                document.getElementById('physics').value = "true";
            }
        };
        
        // Event listeners
        document.getElementById('layout').addEventListener('change', function() {
            window.changeLayout(this.value);
        });
        
        document.getElementById('spacing').addEventListener('change', function() {
            const spacingMap = { compact: 100, normal: 150, relaxed: 200, wide: 300 };
            window.currentSpacing = spacingMap[this.value];
            const currentLayout = document.getElementById('layout').value;
            window.changeLayout(currentLayout);
        });
        
        document.getElementById('physics').addEventListener('change', function() {
            const enabled = this.value === 'true';
            if (window.network) {
                window.network.setOptions({ physics: { enabled: enabled } });
            }
        });
        
        function exportPNG() {
            vscode.postMessage({ command: 'export-png' });
        }
        
        function exportJSON() {
            vscode.postMessage({ command: 'export-json' });
        }
    </script>
</body>
</html>`;
}

/**
 * Get node color based on execution time
 */
function getNodeColor(avgTime) {
    if (avgTime > 0.1) return "#ff6b6b";
    if (avgTime > 0.01) return "#4ecdc4";
    return "#45b7d1";
}

/**
 * Get edge color based on execution time
 */
function getEdgeColor(avgTime) {
    if (avgTime > 0.1) return "#ff6b6b";
    if (avgTime > 0.01) return "#4ecdc4";
    return "#45b7d1";
}

/**
 * Clear trace data
 */
function clearTrace() {
    currentTraceData = null;
    if (visualizationPanel) {
        visualizationPanel.dispose();
    }
    vscode.window.showInformationMessage('Trace data cleared');
}

/**
 * Export as PNG
 */
async function exportPNG() {
    if (!currentTraceData) {
        vscode.window.showWarningMessage('No trace data to export');
        return;
    }
    
    const uri = await vscode.window.showSaveDialog({
        defaultUri: vscode.Uri.file('callflow-graph.png'),
        filters: { 'PNG Images': ['png'] }
    });
    
    if (uri) {
        vscode.window.showInformationMessage('PNG export functionality requires browser canvas access');
    }
}

/**
 * Export as JSON
 */
async function exportJSON() {
    if (!currentTraceData) {
        vscode.window.showWarningMessage('No trace data to export');
        return;
    }
    
    const uri = await vscode.window.showSaveDialog({
        defaultUri: vscode.Uri.file('callflow-graph.json'),
        filters: { 'JSON Files': ['json'] }
    });
    
    if (uri) {
        fs.writeFileSync(uri.fsPath, JSON.stringify(currentTraceData, null, 2));
        vscode.window.showInformationMessage('Trace data exported successfully');
    }
}

/**
 * Export current trace to OpenTelemetry via CLI (basic mode)
 */
async function exportToOtel() {
    if (!currentTraceData) {
        vscode.window.showWarningMessage('No trace data to export. Run a trace first.');
        return;
    }

    const config = vscode.workspace.getConfiguration('callflowTracer');
    const serviceName = config.get('otelServiceName', 'callflow-tracer');
    const workspaceFolders = vscode.workspace.workspaceFolders;

    if (!workspaceFolders || workspaceFolders.length === 0) {
        vscode.window.showErrorMessage('No workspace folder found to write temporary trace file.');
        return;
    }

    const tempDir = workspaceFolders[0].uri.fsPath;
    const tempJsonPath = path.join(tempDir, '.callflow_trace_otel.json');

    try {
        fs.writeFileSync(tempJsonPath, JSON.stringify(currentTraceData, null, 2));
    } catch (err) {
        vscode.window.showErrorMessage(`Failed to write temporary trace file: ${err.message}`);
        return;
    }

    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: 'Exporting CallFlow trace to OpenTelemetry...',
        cancellable: false
    }, async () => {
        try {
            const command = `callflow-tracer export "${tempJsonPath}" --format otel --service-name "${serviceName}"`;
            const { stdout, stderr } = await execAsync(command, { cwd: tempDir });

            if (stderr && stderr.trim()) {
                console.error('OTel export stderr:', stderr);
            }

            vscode.window.showInformationMessage('CallFlow trace exported to OpenTelemetry. Check your configured OTel backend.');
        } catch (error) {
            vscode.window.showErrorMessage(`OpenTelemetry export failed: ${error.message}`);
        } finally {
            try {
                if (fs.existsSync(tempJsonPath)) {
                    fs.unlinkSync(tempJsonPath);
                }
            } catch (cleanupErr) {
                console.error('Failed to clean up temporary OTel trace file:', cleanupErr);
            }
        }
    });
}

/**
 * Export current trace to OpenTelemetry via advanced CLI (with config, sampling, exemplars)
 */
async function exportToOtelAdvanced() {
    if (!currentTraceData) {
        vscode.window.showWarningMessage('No trace data to export. Run a trace first.');
        return;
    }

    const config = vscode.workspace.getConfiguration('callflowTracer');
    const workspaceFolders = vscode.workspace.workspaceFolders;

    if (!workspaceFolders || workspaceFolders.length === 0) {
        vscode.window.showErrorMessage('No workspace folder found.');
        return;
    }

    const tempDir = workspaceFolders[0].uri.fsPath;
    const tempJsonPath = path.join(tempDir, '.callflow_trace_otel.json');

    // Prompt for advanced options
    const serviceName = await vscode.window.showInputBox({
        prompt: 'Service name',
        value: config.get('otelServiceName', 'callflow-tracer')
    });

    if (!serviceName) return;

    const environment = await vscode.window.showQuickPick(
        ['production', 'staging', 'development'],
        { placeHolder: 'Select environment' }
    );

    if (!environment) return;

    const samplingRateStr = await vscode.window.showInputBox({
        prompt: 'Sampling rate (0.0-1.0)',
        value: '1.0'
    });

    const samplingRate = parseFloat(samplingRateStr || '1.0');

    try {
        fs.writeFileSync(tempJsonPath, JSON.stringify(currentTraceData, null, 2));
    } catch (err) {
        vscode.window.showErrorMessage(`Failed to write temporary trace file: ${err.message}`);
        return;
    }

    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: 'Exporting to OpenTelemetry (advanced)...',
        cancellable: false
    }, async () => {
        try {
            const command = `callflow-tracer otel "${tempJsonPath}" --service-name "${serviceName}" --environment "${environment}" --sampling-rate ${samplingRate}`;
            const { stdout, stderr } = await execAsync(command, { cwd: tempDir });

            if (stdout) {
                console.log('OTel export output:', stdout);
            }

            vscode.window.showInformationMessage(
                `OTel export complete: ${serviceName} (${environment}, sampling=${samplingRate})`
            );
        } catch (error) {
            vscode.window.showErrorMessage(`Advanced OTel export failed: ${error.message}`);
        } finally {
            try {
                if (fs.existsSync(tempJsonPath)) {
                    fs.unlinkSync(tempJsonPath);
                }
            } catch (cleanupErr) {
                console.error('Failed to clean up temporary trace file:', cleanupErr);
            }
        }
    });
}

/**
 * Change layout
 */
async function changeLayout() {
    const layouts = [
        'Hierarchical',
        'Force-Directed',
        'Circular',
        'Radial Tree',
        'Grid',
        'Tree (Vertical)',
        'Tree (Horizontal)',
        'Timeline',
        'Organic'
    ];
    
    const selected = await vscode.window.showQuickPick(layouts, {
        placeHolder: 'Select graph layout'
    });
    
    if (selected && visualizationPanel) {
        visualizationPanel.webview.postMessage({
            command: 'changeLayout',
            layout: selected.toLowerCase().replace(/[^a-z-]/g, '')
        });
    }
}

/**
 * Webview provider for sidebar
 */
class CallFlowViewProvider {
    constructor(extensionUri) {
        this._extensionUri = extensionUri;
    }

    resolveWebviewView(webviewView) {
        webviewView.webview.options = {
            enableScripts: true
        };

        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);
    }

    _getHtmlForWebview(webview) {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CallFlow Tracer</title>
    <style>
        body {
            padding: 10px;
            font-family: var(--vscode-font-family);
            color: var(--vscode-foreground);
        }
        .welcome {
            text-align: center;
            padding: 20px;
        }
        .icon {
            font-size: 48px;
            margin-bottom: 10px;
        }
        h2 {
            margin: 10px 0;
        }
        p {
            color: var(--vscode-descriptionForeground);
            line-height: 1.5;
        }
        .actions {
            margin-top: 20px;
        }
        button {
            width: 100%;
            padding: 8px;
            margin: 5px 0;
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 2px;
            cursor: pointer;
        }
        button:hover {
            background-color: var(--vscode-button-hoverBackground);
        }
    </style>
</head>
<body>
    <div class="welcome">
        <div class="icon">📊</div>
        <h2>CallFlow Tracer</h2>
        <p>Visualize Python function call flows with interactive graphs</p>
        
        <div class="actions">
            <button onclick="traceFile()">Trace Current File</button>
            <button onclick="showVisualization()">Show Visualization</button>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        
        function traceFile() {
            vscode.postMessage({ command: 'traceFile' });
        }
        
        function showVisualization() {
            vscode.postMessage({ command: 'showVisualization' });
        }
    </script>
</body>
</html>`;
    }
}

/**
 * Generate 3D Webview Content with all features from Python exporter
 */
function get3DWebviewContent(traceData, defaultLayout) {
    const nodes = traceData.nodes.map(node => ({
        id: node.full_name,
        label: node.name,
        module: node.module || 'unknown',
        call_count: node.call_count,
        avg_time: node.avg_time,
        total_time: node.total_time
    }));

    const edges = traceData.edges.map(edge => ({
        source: edge.caller,
        target: edge.callee,
        call_count: edge.call_count,
        total_time: edge.total_time,
        avg_time: edge.avg_time || 0
    }));

    // Read the complete 3D template from the Python exporter
    // For now, we'll use a CDN-based Three.js implementation
    const fs = require('fs');
    const path = require('path');
    
    // Try to read from Python library's exporter if available
    const pythonExporterPath = path.join(__dirname, '..', 'callflow_tracer', 'exporter.py');
    
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CallFlow 3D Visualization</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: var(--vscode-font-family);
            background: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
            overflow: hidden;
        }
        #container { width: 100vw; height: 100vh; }
        #loading {
            position: absolute; top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            font-size: 24px; z-index: 200;
        }
        #codePreview {
            position: absolute;
            background: rgba(10, 10, 10, 0.95);
            color: #e0e0e0;
            padding: 15px;
            border-radius: 8px;
            border: 2px solid #4fc3f7;
            display: none;
            z-index: 1000;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            max-width: 500px;
            max-height: 400px;
            overflow-y: auto;
            pointer-events: none;
        }
        #codePreview .code-header {
            color: #4fc3f7;
            font-weight: bold;
            margin-bottom: 10px;
            padding-bottom: 5px;
            border-bottom: 1px solid #333;
        }
        #codePreview .code-line {
            padding: 2px 0;
            white-space: pre;
        }
        #codePreview .keyword { color: #c678dd; font-weight: bold; }
        #codePreview .string { color: #98c379; }
        #codePreview .comment { color: #5c6370; font-style: italic; }
        #codePreview .number { color: #d19a66; }
        #controls {
            position: absolute; top: 10px; left: 10px;
            background: var(--vscode-sideBar-background);
            padding: 15px; border-radius: 8px; z-index: 100;
            max-width: 280px; max-height: calc(100vh - 20px);
            overflow-y: auto; font-size: 12px;
        }
        #controls h3 { margin-bottom: 10px; font-size: 14px; }
        .control-group { margin-bottom: 12px; }
        .control-group label { display: block; margin-bottom: 4px; font-size: 11px; }
        select, input[type="range"], button {
            width: 100%; padding: 6px;
            background: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px; font-size: 12px;
        }
        button {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            cursor: pointer; margin-top: 6px;
        }
        button:hover { background: var(--vscode-button-hoverBackground); }
        #stats {
            position: absolute; top: 10px; right: 10px;
            background: var(--vscode-sideBar-background);
            padding: 15px; border-radius: 8px; z-index: 100;
            font-size: 12px;
        }
        .stat-item { margin-bottom: 8px; }
        .stat-value { font-size: 16px; font-weight: bold; color: var(--vscode-textLink-foreground); }
    </style>
</head>
<body>
    <div id="loading">Loading 3D Visualization...</div>
    <div id="container"></div>
    <div id="codePreview">
        <div class="code-header" id="codeHeader">Function Code</div>
        <div id="codeContent"></div>
    </div>
    
    <div id="controls">
        <h3 style="color: #4fc3f7; margin-bottom: 15px;">🎮 Controls</h3>
        
        <div style="color: #4fc3f7; font-weight: bold; margin: 15px 0 10px 0; padding-bottom: 5px; border-bottom: 1px solid #333;">📐 Layout</div>
        <div class="control-group">
            <label>Algorithm</label>
            <select id="layout">
                <option value="force" ${defaultLayout === 'force' ? 'selected' : ''}>Force 3D</option>
                <option value="sphere">Sphere</option>
                <option value="helix">Helix</option>
                <option value="grid">Grid 3D</option>
                <option value="tree">Tree 3D</option>
            </select>
        </div>
        <div class="control-group">
            <label>Spread: <span id="spreadVal">441</span></label>
            <input type="range" id="spread" min="100" max="1000" value="441">
        </div>
        
        <div style="color: #4fc3f7; font-weight: bold; margin: 15px 0 10px 0; padding-bottom: 5px; border-bottom: 1px solid #333;">🎨 Appearance</div>
        <div class="control-group">
            <label>Node Size: <span id="nodeSizeVal">8</span></label>
            <input type="range" id="nodeSize" min="5" max="30" value="8">
        </div>
        <div class="control-group">
            <label>Edge Thickness: <span id="edgeThicknessVal">5</span></label>
            <input type="range" id="edgeThickness" min="1" max="10" value="5">
        </div>
        <div class="control-group">
            <label>Node Opacity: <span id="nodeOpacityVal">100</span>%</label>
            <input type="range" id="nodeOpacity" min="10" max="100" value="100">
        </div>
        <div class="control-group">
            <label>Background Color</label>
            <select id="bgColor">
                <option value="0x0a0a0a">Dark (Default)</option>
                <option value="0x1a1a2e">Deep Blue</option>
                <option value="0x0f0f23">Midnight</option>
                <option value="0x1a0a1a">Purple Dark</option>
            </select>
        </div>
        
        <div style="color: #4fc3f7; font-weight: bold; margin: 15px 0 10px 0; padding-bottom: 5px; border-bottom: 1px solid #333;">✨ Effects</div>
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <input type="checkbox" id="showLabels" checked style="width: auto; margin-right: 8px;">
            <label for="showLabels" style="margin: 0; cursor: pointer;">Show Labels</label>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <input type="checkbox" id="showEdges" checked style="width: auto; margin-right: 8px;">
            <label for="showEdges" style="margin: 0; cursor: pointer;">Show Connections</label>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <input type="checkbox" id="pulseNodes" checked style="width: auto; margin-right: 8px;">
            <label for="pulseNodes" style="margin: 0; cursor: pointer;">Pulse Animation</label>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <input type="checkbox" id="particleEffect" style="width: auto; margin-right: 8px;">
            <label for="particleEffect" style="margin: 0; cursor: pointer;">Particle Effects</label>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <input type="checkbox" id="highlightPaths" style="width: auto; margin-right: 8px;">
            <label for="highlightPaths" style="margin: 0; cursor: pointer;">Highlight Paths</label>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <input type="checkbox" id="showGrid" style="width: auto; margin-right: 8px;">
            <label for="showGrid" style="margin: 0; cursor: pointer;">Show Grid</label>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <input type="checkbox" id="showStatsPanel" checked style="width: auto; margin-right: 8px;">
            <label for="showStatsPanel" style="margin: 0; cursor: pointer;">Show Stats Panel</label>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <input type="checkbox" id="codePreview" style="width: auto; margin-right: 8px;">
            <label for="codePreview" style="margin: 0; cursor: pointer;">Code Preview on Hover</label>
        </div>
        
        <div style="color: #4fc3f7; font-weight: bold; margin: 15px 0 10px 0; padding-bottom: 5px; border-bottom: 1px solid #333;">🎬 Animation</div>
        <div class="control-group">
            <label>Rotation Speed: <span id="rotationSpeedVal">7</span></label>
            <input type="range" id="rotationSpeed" min="0" max="100" value="7">
        </div>
        <div class="control-group">
            <label>Flow Speed: <span id="flowSpeedVal">5</span>x</label>
            <input type="range" id="flowSpeed" min="1" max="10" value="5">
        </div>
        <button onclick="playAnimation()">▶️ Play Flow Animation</button>
        <button onclick="pauseResume()">⏸️ Pause/Resume</button>
        <button onclick="timelinePlayback()">⏱️ Timeline Playback</button>
        
        <div style="color: #4fc3f7; font-weight: bold; margin: 15px 0 10px 0; padding-bottom: 5px; border-bottom: 1px solid #333;">🎯 Navigation</div>
        <button onclick="resetView()">🔄 Reset View</button>
        <button onclick="focusOnSlowest()">🐌 Focus Slowest</button>
        <button onclick="focusOnFastest()">⚡ Focus Fastest</button>
        <button onclick="fitAllNodes()">📏 Fit All Nodes</button>
        <button onclick="topView()">⬆️ Top View</button>
        <button onclick="sideView()">↔️ Side View</button>
        
        <div style="color: #4fc3f7; font-weight: bold; margin: 15px 0 10px 0; padding-bottom: 5px; border-bottom: 1px solid #333;">🔍 Analysis</div>
        <button onclick="showCallChain()">🔗 Show Call Chain</button>
        <button onclick="filterByModule()">📦 Filter by Module</button>
        <button onclick="searchFunction()">🔎 Search Function</button>
        <button onclick="showHotspots()">🔥 Show Hotspots</button>
        <button onclick="compareSelected()">⚖️ Compare Selected</button>
        <button onclick="advancedFilters()">🎛️ Advanced Filters</button>
        <button onclick="showCriticalPath()">🛤️ Critical Path</button>
        <button onclick="autoCluster()">📦 Auto-Cluster</button>
    </div>
    
    <div id="stats">
        <h3>📊 Stats</h3>
        <div class="stat-item">
            <div>Functions</div>
            <div class="stat-value">${nodes.length}</div>
        </div>
        <div class="stat-item">
            <div>Edges</div>
            <div class="stat-value">${edges.length}</div>
        </div>
        <div class="stat-item">
            <div>Duration</div>
            <div class="stat-value">${traceData.metadata.duration.toFixed(3)}s</div>
        </div>
    </div>

    <script>
        const nodes = ${JSON.stringify(nodes)};
        const edges = ${JSON.stringify(edges)};
        
        let scene, camera, renderer, controls;
        let nodeMeshes = [], edgeLines = [], nodeLabels = [];
        let labelsVisible = true;
        let codePreviewEnabled = false;
        let raycaster = new THREE.Raycaster();
        let mouse = new THREE.Vector2();
        let hoveredNode = null;
        
        function init() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x1e1e1e);
            
            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 10000);
            camera.position.z = 1000;
            
            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.getElementById('container').appendChild(renderer.domElement);
            
            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            
            createGraph('${defaultLayout}');
            
            document.getElementById('layout').addEventListener('change', (e) => createGraph(e.target.value));
            document.getElementById('nodeSize').addEventListener('input', (e) => {
                document.getElementById('nodeSizeVal').textContent = e.target.value;
                updateNodeSize(parseInt(e.target.value));
            });
            document.getElementById('spread').addEventListener('input', (e) => {
                document.getElementById('spreadVal').textContent = e.target.value;
                createGraph(document.getElementById('layout').value);
            });
            
            window.addEventListener('resize', () => {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            });
            
            // ESC key to reset visualization
            window.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    // Reset all nodes to original state
                    nodeMeshes.forEach((mesh, i) => {
                        const color = getNodeColor(nodes[i].avg_time);
                        mesh.material.color.setHex(color);
                        mesh.material.emissive.setHex(color);
                        mesh.material.emissiveIntensity = 0.3;
                        mesh.material.opacity = 1.0;
                        mesh.scale.set(1, 1, 1);
                    });
                    
                    // Reset all edges
                    edgeLines.forEach(line => {
                        line.visible = true;
                    });
                    
                    // Recreate layout
                    createGraph(document.getElementById('layout').value);
                }
            });
            
            // Mouse move for code preview
            renderer.domElement.addEventListener('mousemove', onMouseMove);
            
            document.getElementById('loading').style.display = 'none';
            animate();
        }
        
        function onMouseMove(event) {
            if (!codePreviewEnabled) {
                document.getElementById('codePreview').style.display = 'none';
                return;
            }
            
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
            
            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(nodeMeshes);
            
            if (intersects.length > 0) {
                const intersectedMesh = intersects[0].object;
                const node = intersectedMesh.userData;
                
                if (hoveredNode !== node) {
                    hoveredNode = node;
                    showCodePreview(node, event.clientX, event.clientY);
                }
            } else {
                hoveredNode = null;
                document.getElementById('codePreview').style.display = 'none';
            }
        }
        
        function generateMockCode(node) {
            const funcName = node.label;
            const module = node.module || 'unknown';
            
            let code = 'def ' + funcName + '(';
            
            if (funcName.includes('get') || funcName.includes('fetch')) {
                code += 'id: int';
            } else if (funcName.includes('process') || funcName.includes('handle')) {
                code += 'data: dict';
            } else if (funcName.includes('save') || funcName.includes('update')) {
                code += 'obj: object, **kwargs';
            } else {
                code += '*args, **kwargs';
            }
            code += '):\\n';
            
            code += '    """\\n';
            code += '    ' + funcName.replace(/_/g, ' ') + '\\n';
            code += '    \\n';
            code += '    Module: ' + module + '\\n';
            code += '    Calls: ' + node.call_count + '\\n';
            code += '    Avg Time: ' + node.avg_time.toFixed(4) + 's\\n';
            code += '    Total Time: ' + node.total_time.toFixed(4) + 's\\n';
            code += '    """\\n';
            
            if (funcName.includes('get') || funcName.includes('fetch')) {
                code += '    result = database.query(id)\\n';
                code += '    if not result:\\n';
                code += '        return None\\n';
                code += '    return result\\n';
            } else if (funcName.includes('process')) {
                code += '    try:\\n';
                code += '        validated = validate(data)\\n';
                code += '        transformed = transform(validated)\\n';
                code += '        return transformed\\n';
                code += '    except Exception as e:\\n';
                code += '        logger.error(f"Error: {e}")\\n';
                code += '        raise\\n';
            } else {
                code += '    result = perform_operation()\\n';
                code += '    return result\\n';
            }
            
            return code;
        }
        
        function syntaxHighlight(code) {
            let highlighted = code;
            
            highlighted = highlighted.replace(/\\n/g, '<br>');
            highlighted = highlighted.replace(/(#.*$)/gm, '<span class="comment">$1</span>');
            highlighted = highlighted.replace(/\\b(def|class|if|else|elif|return|import|from|try|except|finally|with|as|for|while|in|not|and|or|is|None|True|False|raise|pass|break|continue)\\b/g, '<span class="keyword">$1</span>');
            highlighted = highlighted.replace(/(".*?"|'.*?')/g, '<span class="string">$1</span>');
            highlighted = highlighted.replace(/\\b(\\d+\\.?\\d*)\\b/g, '<span class="number">$1</span>');
            
            return highlighted;
        }
        
        function showCodePreview(node, x, y) {
            const preview = document.getElementById('codePreview');
            const header = document.getElementById('codeHeader');
            const content = document.getElementById('codeContent');
            
            header.textContent = '📄 ' + node.label + ' (' + node.module + ')';
            
            const code = generateMockCode(node);
            content.innerHTML = syntaxHighlight(code);
            
            let left = x + 20;
            let top = y + 20;
            
            if (left + 520 > window.innerWidth) {
                left = x - 520;
            }
            if (top + 420 > window.innerHeight) {
                top = window.innerHeight - 420;
            }
            
            preview.style.left = Math.max(10, left) + 'px';
            preview.style.top = Math.max(10, top) + 'px';
            preview.style.display = 'block';
        }
        
        function createTextSprite(text, position) {
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            canvas.width = 256;
            canvas.height = 64;
            
            context.fillStyle = 'rgba(0, 0, 0, 0.7)';
            context.fillRect(0, 0, canvas.width, canvas.height);
            
            context.font = 'Bold 20px Arial';
            context.fillStyle = 'white';
            context.textAlign = 'center';
            context.textBaseline = 'middle';
            context.fillText(text, canvas.width / 2, canvas.height / 2);
            
            const texture = new THREE.CanvasTexture(canvas);
            const material = new THREE.SpriteMaterial({ map: texture });
            const sprite = new THREE.Sprite(material);
            sprite.position.copy(position);
            sprite.position.y += 25;
            sprite.scale.set(100, 25, 1);
            
            return sprite;
        }
        
        function createGraph(layout) {
            nodeMeshes.forEach(m => scene.remove(m));
            edgeLines.forEach(l => scene.remove(l));
            nodeLabels.forEach(label => scene.remove(label));
            nodeMeshes = []; edgeLines = []; nodeLabels = [];
            
            const spread = parseInt(document.getElementById('spread').value);
            const nodeSize = parseInt(document.getElementById('nodeSize').value);
            const positions = calculatePositions(layout, nodes.length, spread);
            
            // Create nodes
            nodes.forEach((node, i) => {
                const geometry = new THREE.SphereGeometry(nodeSize, 16, 16);
                const color = getNodeColor(node.avg_time);
                const material = new THREE.MeshPhongMaterial({ 
                    color: color, 
                    emissive: color, 
                    emissiveIntensity: 0.3 
                });
                const mesh = new THREE.Mesh(geometry, material);
                mesh.position.copy(positions[i]);
                mesh.userData = node;
                scene.add(mesh);
                nodeMeshes.push(mesh);
                
                // Create text label
                const label = createTextSprite(node.label, positions[i]);
                label.visible = labelsVisible;
                scene.add(label);
                nodeLabels.push(label);
            });
            
            // Create edges with arrows
            const nodeMap = {};
            nodes.forEach((n, i) => nodeMap[n.id] = i);
            
            edges.forEach(edge => {
                const sourceIdx = nodeMap[edge.source];
                const targetIdx = nodeMap[edge.target];
                if (sourceIdx !== undefined && targetIdx !== undefined) {
                    const start = positions[sourceIdx];
                    const end = positions[targetIdx];
                    
                    // Create line
                    const points = [start, end];
                    const geometry = new THREE.BufferGeometry().setFromPoints(points);
                    const material = new THREE.LineBasicMaterial({ 
                        color: 0xff9800,  // Orange color for edges
                        opacity: 0.8, 
                        transparent: true 
                    });
                    const line = new THREE.Line(geometry, material);
                    scene.add(line);
                    edgeLines.push(line);
                    
                    // Create arrow at the end
                    const direction = new THREE.Vector3().subVectors(end, start);
                    const length = direction.length();
                    direction.normalize();
                    
                    const arrowHelper = new THREE.ArrowHelper(
                        direction,
                        start,
                        length,
                        0xff9800,  // Orange color for arrows
                        length * 0.1,  // Head length (10% of edge length)
                        length * 0.08   // Head width (8% of edge length)
                    );
                    scene.add(arrowHelper);
                    edgeLines.push(arrowHelper);
                }
            });
            
            // Add lights
            if (scene.children.filter(c => c.type === 'AmbientLight').length === 0) {
                const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
                scene.add(ambientLight);
                const pointLight = new THREE.PointLight(0xffffff, 0.8);
                pointLight.position.set(500, 500, 500);
                scene.add(pointLight);
            }
        }
        
        function calculatePositions(layout, count, spread) {
            const positions = [];
            
            if (layout === 'sphere') {
                const radius = spread;
                for (let i = 0; i < count; i++) {
                    const phi = Math.acos(-1 + (2 * i) / count);
                    const theta = Math.sqrt(count * Math.PI) * phi;
                    positions.push(new THREE.Vector3(
                        radius * Math.cos(theta) * Math.sin(phi),
                        radius * Math.sin(theta) * Math.sin(phi),
                        radius * Math.cos(phi)
                    ));
                }
            } else if (layout === 'helix') {
                const radius = spread / 2;
                const height = spread * 2;
                for (let i = 0; i < count; i++) {
                    const t = (i / count) * Math.PI * 4;
                    const y = (i / count) * height - height / 2;
                    positions.push(new THREE.Vector3(
                        radius * Math.cos(t),
                        y,
                        radius * Math.sin(t)
                    ));
                }
            } else if (layout === 'grid') {
                const cols = Math.ceil(Math.sqrt(count));
                const spacing = spread / cols;
                for (let i = 0; i < count; i++) {
                    const x = (i % cols) * spacing - (cols * spacing) / 2;
                    const z = Math.floor(i / cols) * spacing - (cols * spacing) / 2;
                    positions.push(new THREE.Vector3(x, 0, z));
                }
            } else if (layout === 'tree') {
                // Simple tree layout
                const levels = Math.ceil(Math.log2(count + 1));
                for (let i = 0; i < count; i++) {
                    const level = Math.floor(Math.log2(i + 1));
                    const posInLevel = i - (Math.pow(2, level) - 1);
                    const nodesInLevel = Math.pow(2, level);
                    const x = (posInLevel - nodesInLevel / 2) * spread / nodesInLevel;
                    const y = -level * spread / 2;
                    positions.push(new THREE.Vector3(x, y, 0));
                }
            } else {
                // Force-directed (random initial)
                for (let i = 0; i < count; i++) {
                    positions.push(new THREE.Vector3(
                        (Math.random() - 0.5) * spread,
                        (Math.random() - 0.5) * spread,
                        (Math.random() - 0.5) * spread
                    ));
                }
            }
            
            return positions;
        }
        
        function getNodeColor(avgTime) {
            if (avgTime > 0.1) return 0xff0000;
            if (avgTime > 0.01) return 0xffff00;
            return 0x00ff00;
        }
        
        function updateNodeSize(size) {
            nodeMeshes.forEach(mesh => {
                mesh.geometry.dispose();
                mesh.geometry = new THREE.SphereGeometry(size, 16, 16);
            });
        }
        
        function resetView() {
            camera.position.set(0, 0, 1000);
            controls.target.set(0, 0, 0);
            controls.update();
        }
        
        function focusOnSlowest() {
            let slowest = nodes[0];
            nodes.forEach(n => {
                if (n.avg_time > slowest.avg_time) slowest = n;
            });
            const idx = nodes.indexOf(slowest);
            if (idx >= 0 && nodeMeshes[idx]) {
                const pos = nodeMeshes[idx].position;
                camera.position.set(pos.x, pos.y, pos.z + 300);
                controls.target.copy(pos);
                controls.update();
            }
        }
        
        function takeScreenshot() {
            renderer.render(scene, camera);
            const dataURL = renderer.domElement.toDataURL('image/png');
            const link = document.createElement('a');
            link.download = 'callflow-3d.png';
            link.href = dataURL;
            link.click();
        }
        
        // Additional feature functions
        let isPaused = false;
        let rotationSpeedValue = 0.007;
        let pulseEnabled = true;
        let particlesEnabled = false;
        let gridHelperObj = null;
        
        function playAnimation() {
            // Animate flow through edges
            alert('Flow animation started');
        }
        
        function pauseResume() {
            isPaused = !isPaused;
            alert(isPaused ? 'Paused' : 'Resumed');
        }
        
        function timelinePlayback() {
            alert('Timeline playback - feature in development');
        }
        
        function focusOnFastest() {
            let fastest = nodes[0];
            nodes.forEach(n => {
                if (n.avg_time < fastest.avg_time) fastest = n;
            });
            const idx = nodes.indexOf(fastest);
            if (idx >= 0 && nodeMeshes[idx]) {
                const pos = nodeMeshes[idx].position;
                camera.position.set(pos.x, pos.y, pos.z + 300);
                controls.target.copy(pos);
                controls.update();
            }
        }
        
        function fitAllNodes() {
            const box = new THREE.Box3();
            nodeMeshes.forEach(mesh => box.expandByObject(mesh));
            const center = box.getCenter(new THREE.Vector3());
            const size = box.getSize(new THREE.Vector3());
            const maxDim = Math.max(size.x, size.y, size.z);
            const fov = camera.fov * (Math.PI / 180);
            let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));
            cameraZ *= 1.5;
            camera.position.set(center.x, center.y, center.z + cameraZ);
            controls.target.copy(center);
            controls.update();
        }
        
        function topView() {
            const center = new THREE.Vector3();
            nodeMeshes.forEach(m => center.add(m.position));
            center.divideScalar(nodeMeshes.length);
            camera.position.set(center.x, center.y + 800, center.z);
            controls.target.copy(center);
            controls.update();
        }
        
        function sideView() {
            const center = new THREE.Vector3();
            nodeMeshes.forEach(m => center.add(m.position));
            center.divideScalar(nodeMeshes.length);
            camera.position.set(center.x + 800, center.y, center.z);
            controls.target.copy(center);
            controls.update();
        }
        
        function showCallChain() {
            alert('Call Chain: Shows execution path through selected nodes');
        }
        
        function filterByModule() {
            const modules = [...new Set(nodes.map(n => n.module))];
            const module = prompt('Enter module name:\\n' + modules.join('\\n'));
            if (module) {
                nodeMeshes.forEach((mesh, i) => {
                    mesh.visible = nodes[i].module === module;
                });
            }
        }
        
        function searchFunction() {
            const query = prompt('Search function name:');
            if (query) {
                const found = nodes.find(n => n.label.toLowerCase().includes(query.toLowerCase()));
                if (found) {
                    const idx = nodes.indexOf(found);
                    if (nodeMeshes[idx]) {
                        const pos = nodeMeshes[idx].position;
                        camera.position.set(pos.x, pos.y, pos.z + 300);
                        controls.target.copy(pos);
                        controls.update();
                        alert('Found: ' + found.label);
                    }
                } else {
                    alert('Function not found');
                }
            }
        }
        
        function showHotspots() {
            // Highlight top 10 slowest
            const sorted = [...nodes].sort((a, b) => b.avg_time - a.avg_time).slice(0, 10);
            nodeMeshes.forEach((mesh, i) => {
                if (sorted.includes(nodes[i])) {
                    mesh.material.emissiveIntensity = 0.8;
                } else {
                    mesh.material.opacity = 0.3;
                }
            });
            alert('Highlighted top 10 hotspots');
        }
        
        function compareSelected() {
            alert('Select 2 nodes to compare (feature in development)');
        }
        
        function advancedFilters() {
            alert('Advanced Filters: Min/Max time, call count, module filters');
        }
        
        function showCriticalPath() {
            // Find critical path using DFS
            const adjacency = {};
            nodes.forEach(n => adjacency[n.id] = []);
            edges.forEach(e => {
                if (!adjacency[e.source]) adjacency[e.source] = [];
                adjacency[e.source].push({ target: e.target, time: e.total_time });
            });
            
            // Find root nodes (no incoming edges)
            const hasIncoming = new Set();
            edges.forEach(e => hasIncoming.add(e.target));
            const roots = nodes.filter(n => !hasIncoming.has(n.id));
            
            if (roots.length === 0) {
                alert('No root nodes found');
                return;
            }
            
            // DFS to find longest path (critical path)
            let criticalPath = [];
            let maxTime = 0;
            
            function dfs(nodeId, path, totalTime) {
                const currentPath = [...path, nodeId];
                const currentTime = totalTime + (nodes.find(n => n.id === nodeId)?.total_time || 0);
                
                if (currentTime > maxTime) {
                    maxTime = currentTime;
                    criticalPath = currentPath;
                }
                
                if (adjacency[nodeId]) {
                    adjacency[nodeId].forEach(edge => {
                        dfs(edge.target, currentPath, currentTime);
                    });
                }
            }
            
            roots.forEach(root => dfs(root.id, [], 0));
            
            // Highlight critical path
            nodeMeshes.forEach((mesh, i) => {
                if (criticalPath.includes(nodes[i].id)) {
                    mesh.material.color.setHex(0xff0000);
                    mesh.material.emissiveIntensity = 0.9;
                    mesh.scale.set(1.5, 1.5, 1.5);
                } else {
                    mesh.material.opacity = 0.2;
                }
            });
            
            edgeLines.forEach(line => {
                line.visible = false;
            });
            
            // Highlight critical path edges
            for (let i = 0; i < criticalPath.length - 1; i++) {
                const sourceId = criticalPath[i];
                const targetId = criticalPath[i + 1];
                const edge = edges.find(e => e.source === sourceId && e.target === targetId);
                if (edge) {
                    const sourceIdx = nodes.findIndex(n => n.id === sourceId);
                    const targetIdx = nodes.findIndex(n => n.id === targetId);
                    if (sourceIdx >= 0 && targetIdx >= 0) {
                        // Find corresponding edge line
                        edgeLines.forEach(line => {
                            line.visible = true;
                        });
                    }
                }
            }
            
            alert('Critical Path Highlighted!\\n' + 
                  'Path length: ' + criticalPath.length + ' functions\\n' +
                  'Total time: ' + maxTime.toFixed(4) + 's\\n' +
                  'Red nodes = critical path\\n' +
                  'Press ESC to reset');
        }
        
        function autoCluster() {
            // Cluster nodes by module using colors
            const modules = [...new Set(nodes.map(n => n.module))];
            const colors = [
                0xff6b6b, 0x4ecdc4, 0x45b7d1, 0xf9ca24, 
                0x6c5ce7, 0xa29bfe, 0xfd79a8, 0xfdcb6e,
                0x00b894, 0x00cec9, 0x0984e3, 0x6c5ce7
            ];
            
            const moduleColors = {};
            modules.forEach((module, i) => {
                moduleColors[module] = colors[i % colors.length];
            });
            
            // Apply colors and group by module
            const moduleGroups = {};
            nodes.forEach((node, i) => {
                const module = node.module || 'unknown';
                if (!moduleGroups[module]) {
                    moduleGroups[module] = [];
                }
                moduleGroups[module].push(i);
                
                // Color the node
                nodeMeshes[i].material.color.setHex(moduleColors[module]);
                nodeMeshes[i].material.emissive.setHex(moduleColors[module]);
            });
            
            // Position nodes in clusters
            const spread = parseInt(document.getElementById('spread').value);
            const clusterSpacing = spread * 1.5;
            let clusterIndex = 0;
            
            Object.keys(moduleGroups).forEach(module => {
                const nodeIndices = moduleGroups[module];
                const angle = (clusterIndex / Object.keys(moduleGroups).length) * Math.PI * 2;
                const clusterX = Math.cos(angle) * clusterSpacing;
                const clusterZ = Math.sin(angle) * clusterSpacing;
                
                // Arrange nodes in this cluster in a small circle
                nodeIndices.forEach((nodeIdx, i) => {
                    const localAngle = (i / nodeIndices.length) * Math.PI * 2;
                    const localRadius = spread / 3;
                    nodeMeshes[nodeIdx].position.set(
                        clusterX + Math.cos(localAngle) * localRadius,
                        0,
                        clusterZ + Math.sin(localAngle) * localRadius
                    );
                });
                
                clusterIndex++;
            });
            
            let clusterInfo = 'Auto-Clustered by Module!\\n\\n';
            Object.keys(moduleGroups).forEach(module => {
                clusterInfo += module + ': ' + moduleGroups[module].length + ' functions\\n';
            });
            
            alert(clusterInfo + '\\nEach color = different module\\nPress ESC to reset');
        }
        
        // Event listeners for new controls
        document.getElementById('nodeSize').addEventListener('input', (e) => {
            document.getElementById('nodeSizeVal').textContent = e.target.value;
            updateNodeSize(parseInt(e.target.value));
        });
        
        document.getElementById('spread').addEventListener('input', (e) => {
            document.getElementById('spreadVal').textContent = e.target.value;
            createGraph(document.getElementById('layout').value);
        });
        
        document.getElementById('edgeThickness').addEventListener('input', (e) => {
            document.getElementById('edgeThicknessVal').textContent = e.target.value;
        });
        
        document.getElementById('nodeOpacity').addEventListener('input', (e) => {
            const val = parseInt(e.target.value);
            document.getElementById('nodeOpacityVal').textContent = val;
            nodeMeshes.forEach(mesh => {
                mesh.material.opacity = val / 100;
                mesh.material.transparent = val < 100;
            });
        });
        
        document.getElementById('bgColor').addEventListener('change', (e) => {
            scene.background = new THREE.Color(parseInt(e.target.value));
        });
        
        document.getElementById('showLabels').addEventListener('change', (e) => {
            labelsVisible = e.target.checked;
            nodeLabels.forEach(label => {
                label.visible = labelsVisible;
            });
        });
        
        document.getElementById('showEdges').addEventListener('change', (e) => {
            edgeLines.forEach(line => line.visible = e.target.checked);
        });
        
        document.getElementById('pulseNodes').addEventListener('change', (e) => {
            pulseEnabled = e.target.checked;
        });
        
        document.getElementById('particleEffect').addEventListener('change', (e) => {
            particlesEnabled = e.target.checked;
        });
        
        document.getElementById('showGrid').addEventListener('change', (e) => {
            if (e.target.checked && !gridHelperObj) {
                gridHelperObj = new THREE.GridHelper(1000, 20, 0x444444, 0x222222);
                scene.add(gridHelperObj);
            } else if (!e.target.checked && gridHelperObj) {
                scene.remove(gridHelperObj);
                gridHelperObj = null;
            }
        });
        
        document.getElementById('showStatsPanel').addEventListener('change', (e) => {
            document.getElementById('stats').style.display = e.target.checked ? 'block' : 'none';
        });
        
        document.getElementById('codePreview').addEventListener('change', (e) => {
            codePreviewEnabled = e.target.checked;
            if (!codePreviewEnabled) {
                document.getElementById('codePreview').style.display = 'none';
            }
        });
        
        document.getElementById('rotationSpeed').addEventListener('input', (e) => {
            const val = parseInt(e.target.value);
            document.getElementById('rotationSpeedVal').textContent = val;
            rotationSpeedValue = val / 1000;
        });
        
        document.getElementById('flowSpeed').addEventListener('input', (e) => {
            document.getElementById('flowSpeedVal').textContent = e.target.value;
        });
        
        function animate() {
            requestAnimationFrame(animate);
            
            if (!isPaused) {
                // Auto rotation
                if (rotationSpeedValue > 0) {
                    nodeMeshes.forEach(mesh => {
                        mesh.rotation.y += rotationSpeedValue;
                    });
                }
                
                // Pulse animation
                if (pulseEnabled) {
                    const time = Date.now() * 0.001;
                    nodeMeshes.forEach((mesh, i) => {
                        const scale = 1 + Math.sin(time * 2 + i * 0.1) * 0.1;
                        mesh.scale.set(scale, scale, scale);
                    });
                }
            }
            
            controls.update();
            renderer.render(scene, camera);
        }
        
        init();
    </script>
</body>
</html>`;
}

// Anomaly Detection Command
async function analyzeAnomalies() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No file is currently open');
        return;
    }

    try {
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Analyzing anomalies...",
            cancellable: false
        }, async (progress) => {
            progress.report({ increment: 0, message: "Running anomaly detection..." });
            
            // Create a Python script for anomaly detection
            const script = `
import sys
sys.path.append('${path.dirname(editor.document.fileName)}')

from callflow_tracer import trace_scope
from callflow_tracer.anomaly_detection import get_anomaly_detector, generate_anomaly_report

# Trace the current file
with trace_scope() as graph:
    # Execute the file to collect data
    exec(open('${editor.document.fileName}').read())

# Run anomaly detection
detector = get_anomaly_detector()
report = generate_anomaly_report(hours=24)

# Save report
import json
with open('anomaly_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print(f"Anomalies detected: {report['total_alerts']}")
print(f"Severity breakdown: {report['severity_breakdown']}")
`;

            progress.report({ increment: 50, message: "Processing results..." });
            
            // Write and execute the script
            const scriptPath = path.join(path.dirname(editor.document.fileName), 'anomaly_detection.py');
            fs.writeFileSync(scriptPath, script);
            
            await execAsync(`cd "${path.dirname(editor.document.fileName)}" && python anomaly_detection.py`);
            
            progress.report({ increment: 100, message: "Complete!" });
        });

        // Show results
        const reportPath = path.join(path.dirname(editor.document.fileName), 'anomaly_report.json');
        if (fs.existsSync(reportPath)) {
            const report = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
            
            // Create a webview to show the report
            const panel = vscode.window.createWebviewPanel(
                'anomalyReport',
                'Anomaly Detection Report',
                vscode.ViewColumn.One,
                {}
            );
            
            panel.webview.html = getAnomalyReportHtml(report);
        }
        
        vscode.window.showInformationMessage('Anomaly detection completed!');
    } catch (error) {
        vscode.window.showErrorMessage(`Anomaly detection failed: ${error.message}`);
    }
}

// Auto-Instrumentation Command
async function enableAutoInstrumentation() {
    const options = ['HTTP (requests, httpx, aiohttp)', 'Redis', 'Boto3 (AWS)', 'All Libraries'];
    const selected = await vscode.window.showQuickPick(options, {
        placeHolder: 'Select libraries to auto-instrument'
    });
    
    if (!selected) return;
    
    try {
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Enabling auto-instrumentation...",
            cancellable: false
        }, async (progress) => {
            progress.report({ increment: 0, message: "Setting up auto-instrumentation..." });
            
            let libraries = [];
            if (selected.includes('HTTP')) libraries.push('http');
            if (selected.includes('Redis')) libraries.push('redis');
            if (selected.includes('Boto3')) libraries.push('boto3');
            if (selected.includes('All')) libraries = ['http', 'redis', 'boto3'];
            
            // Create auto-instrumentation setup script
            const script = `
from callflow_tracer.auto_instrumentation import enable_auto_instrumentation

# Enable auto-instrumentation for selected libraries
enable_auto_instrumentation(${JSON.stringify(libraries)})

print("Auto-instrumentation enabled for: ${libraries.join(', ')}")
`;
            
            progress.report({ increment: 50, message: "Applying configuration..." });
            
            // Write the setup script
            const setupPath = path.join(vscode.workspace.rootPath || '', 'auto_instrumentation_setup.py');
            fs.writeFileSync(setupPath, script);
            
            progress.report({ increment: 100, message: "Complete!" });
        });
        
        vscode.window.showInformationMessage(
            `Auto-instrumentation enabled for ${selected}!\n\n` +
            `Add this to your code:\n` +
            `from callflow_tracer.auto_instrumentation import enable_auto_instrumentation\n` +
            `enable_auto_instrumentation(${JSON.stringify(selected.includes('All') ? ['http', 'redis', 'boto3'] : 
              (selected.includes('HTTP') ? ['http'] : []))})`
        );
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to enable auto-instrumentation: ${error.message}`);
    }
}

// Plugin Manager Command
async function showPluginManager() {
    const panel = vscode.window.createWebviewPanel(
        'pluginManager',
        'Plugin Manager',
        vscode.ViewColumn.One,
        {}
    );
    
    try {
        // Create a script to list plugins
        const script = `
from callflow_tracer.plugin_system import get_plugin_manager
import json

manager = get_plugin_manager()
plugins = {
    'analyzers': manager.list_analyzers(),
    'exporters': manager.list_exporters(),
    'ui_widgets': manager.list_ui_widgets(),
    'plugin_info': manager.plugin_info
}

print(json.dumps(plugins, indent=2))
`;
        
        const scriptPath = path.join(vscode.workspace.rootPath || '', 'plugin_list.py');
        fs.writeFileSync(scriptPath, script);
        
        const { stdout } = await execAsync(`cd "${vscode.workspace.rootPath || ''}" && python plugin_list.py`);
        const plugins = JSON.parse(stdout);
        
        panel.webview.html = getPluginManagerHtml(plugins);
    } catch (error) {
        panel.webview.html = `
        <html>
        <body>
            <h2>Plugin Manager</h2>
            <p>Error loading plugins: ${error.message}</p>
        </body>
        </html>
        `;
    }
}

// Custom Analyzer Command
async function runCustomAnalyzer() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No file is currently open');
        return;
    }
    
    try {
        // Get available analyzers
        const script = `
from callflow_tracer.plugin_system import get_plugin_manager
import json

manager = get_plugin_manager()
analyzers = manager.list_analyzers()
print(json.dumps(analyzers))
`;
        
        const scriptPath = path.join(path.dirname(editor.document.fileName), 'list_analyzers.py');
        fs.writeFileSync(scriptPath, script);
        
        const { stdout } = await execAsync(`cd "${path.dirname(editor.document.fileName)}" && python list_analyzers.py`);
        const analyzers = JSON.parse(stdout);
        
        if (analyzers.length === 0) {
            vscode.window.showInformationMessage('No custom analyzers available');
            return;
        }
        
        const selected = await vscode.window.showQuickPick(analyzers, {
            placeHolder: 'Select an analyzer to run'
        });
        
        if (!selected) return;
        
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: `Running ${selected} analyzer...`,
            cancellable: false
        }, async (progress) => {
            progress.report({ increment: 0, message: "Analyzing..." });
            
            const analysisScript = `
import sys
sys.path.append('${path.dirname(editor.document.fileName)}')

from callflow_tracer import trace_scope
from callflow_tracer.plugin_system import get_plugin_manager

# Trace the current file
with trace_scope() as graph:
    exec(open('${editor.document.fileName}').read())

# Run custom analyzer
manager = get_plugin_manager()
result = manager.run_analyzer('${selected}', graph)

# Save results
import json
with open('analysis_result.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f"Analysis completed: {len(result)} metrics generated")
`;
            
            progress.report({ increment: 50, message: "Processing results..." });
            
            const analysisScriptPath = path.join(path.dirname(editor.document.fileName), 'run_analysis.py');
            fs.writeFileSync(analysisScriptPath, analysisScript);
            
            await execAsync(`cd "${path.dirname(editor.document.fileName)}" && python run_analysis.py`);
            
            progress.report({ increment: 100, message: "Complete!" });
        });
        
        // Show results
        const resultPath = path.join(path.dirname(editor.document.fileName), 'analysis_result.json');
        if (fs.existsSync(resultPath)) {
            const result = JSON.parse(fs.readFileSync(resultPath, 'utf8'));
            
            // Create a webview to show results
            const panel = vscode.window.createWebviewPanel(
                'analysisResult',
                `${selected} Analysis Results`,
                vscode.ViewColumn.One,
                {}
            );
            
            panel.webview.html = getAnalysisResultHtml(selected, result);
        }
        
        vscode.window.showInformationMessage(`${selected} analysis completed!`);
    } catch (error) {
        vscode.window.showErrorMessage(`Analysis failed: ${error.message}`);
    }
}

// Helper functions for HTML generation
function getAnomalyReportHtml(report) {
    return `
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Anomaly Detection Report</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            .header { background: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
            .alert { padding: 10px; margin: 5px 0; border-radius: 5px; }
            .critical { background: #ffebee; border-left: 4px solid #f44336; }
            .high { background: #fff3e0; border-left: 4px solid #ff9800; }
            .medium { background: #fff8e1; border-left: 4px solid #ffc107; }
            .low { background: #e8f5e8; border-left: 4px solid #4caf50; }
            .metric { font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔍 Anomaly Detection Report</h1>
            <p>Generated: ${new Date(report.report_generated).toLocaleString()}</p>
            <p>Period: Last ${report.period_hours} hours</p>
        </div>
        
        <h2>Summary</h2>
        <p><strong>Total Alerts:</strong> ${report.total_alerts}</p>
        <p><strong>Severity Breakdown:</strong></p>
        <ul>
            <li>Critical: ${report.severity_breakdown.critical || 0}</li>
            <li>High: ${report.severity_breakdown.high || 0}</li>
            <li>Medium: ${report.severity_breakdown.medium || 0}</li>
            <li>Low: ${report.severity_breakdown.low || 0}</li>
        </ul>
        
        <h2>Top Anomalies</h2>
        ${report.top_anomalies.map(alert => `
            <div class="alert ${alert.severity}">
                <div class="metric">${alert.metric_name}</div>
                <div>${alert.description}</div>
                <small>Z-score: ${alert.z_score.toFixed(2)} | Time: ${new Date(alert.timestamp).toLocaleString()}</small>
            </div>
        `).join('')}
    </body>
    </html>`;
}

function getPluginManagerHtml(plugins) {
    return `
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Plugin Manager</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            .section { margin: 20px 0; }
            .plugin { background: #f5f5f5; padding: 10px; margin: 5px 0; border-radius: 5px; }
            .plugin-name { font-weight: bold; color: #333; }
            .plugin-type { color: #666; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <h1>🔌 Plugin Manager</h1>
        
        <div class="section">
            <h2>📊 Analyzers (${plugins.analyzers.length})</h2>
            ${plugins.analyzers.map(name => `
                <div class="plugin">
                    <div class="plugin-name">${name}</div>
                    <div class="plugin-type">Custom Analyzer</div>
                </div>
            `).join('')}
        </div>
        
        <div class="section">
            <h2>📤 Exporters (${plugins.exporters.length})</h2>
            ${Object.entries(plugins.exporters).map(([name, extensions]) => `
                <div class="plugin">
                    <div class="plugin-name">${name}</div>
                    <div class="plugin-type">Exports: ${extensions.join(', ')}</div>
                </div>
            `).join('')}
        </div>
        
        <div class="section">
            <h2>🎨 UI Widgets (${plugins.ui_widgets.length})</h2>
            ${plugins.ui_widgets.map(name => `
                <div class="plugin">
                    <div class="plugin-name">${name}</div>
                    <div class="plugin-type">UI Widget</div>
                </div>
            `).join('')}
        </div>
    </body>
    </html>`;
}

function getAnalysisResultHtml(analyzerName, result) {
    return `
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${analyzerName} Analysis Results</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            .header { background: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
            .metric { background: #f5f5f5; padding: 10px; margin: 5px 0; border-radius: 5px; }
            .metric-name { font-weight: bold; color: #333; }
            .metric-value { color: #666; font-size: 1.2em; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📈 ${analyzerName} Analysis Results</h1>
            <p>Generated: ${new Date().toLocaleString()}</p>
        </div>
        
        <h2>Metrics</h2>
        ${Object.entries(result).map(([key, value]) => `
            <div class="metric">
                <div class="metric-name">${key}</div>
                <div class="metric-value">${typeof value === 'object' ? JSON.stringify(value, null, 2) : value}</div>
            </div>
        `).join('')}
    </body>
    </html>`;
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
