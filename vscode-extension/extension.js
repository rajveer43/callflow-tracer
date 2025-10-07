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
        vscode.commands.registerCommand('callflow-tracer.clearTrace', clearTrace),
        vscode.commands.registerCommand('callflow-tracer.exportPNG', exportPNG),
        vscode.commands.registerCommand('callflow-tracer.exportJSON', exportJSON),
        vscode.commands.registerCommand('callflow-tracer.changeLayout', changeLayout)
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

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
