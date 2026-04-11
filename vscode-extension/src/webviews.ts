import { escapeHtml } from './ui';
import type { TraceData, Spacing, AnomalyReport, PluginList } from './types';
import { SPACING_MAP } from './types';

function edgeColorForTime(avgTime: number): string {
  if (avgTime > 0.1) return '#ff6b6b';
  if (avgTime > 0.01) return '#4ecdc4';
  return '#45b7d1';
}

function colorForTime(avgTime: number): number {
  if (avgTime > 0.1) return 0xff6b6b;
  if (avgTime > 0.01) return 0x4ecdc4;
  return 0x45b7d1;
}

const VIS_CSP = `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline' https://unpkg.com; style-src 'unsafe-inline'; connect-src https://unpkg.com;">`;

export function buildVisWebviewHtml(
  traceData: TraceData,
  defaultLayout: string,
  defaultSpacing: Spacing,
): string {
  const nodes = traceData.nodes.map((node) => ({
    id: node.full_name,
    label: node.name,
    title: `Module: ${node.module}\nCalls: ${node.call_count}\nTotal Time: ${node.total_time.toFixed(3)}s\nAvg Time: ${node.avg_time.toFixed(3)}s`,
    group: node.module || 'main',
    value: node.call_count,
    color: edgeColorForTime(node.avg_time),
    module: node.module,
    shape: 'circle' as const,
    total_time: node.total_time,
    avg_time: node.avg_time,
  }));

  const edges = traceData.edges.map((edge) => ({
    from: edge.caller,
    to: edge.callee,
    label: `${edge.call_count} calls`,
    title: `Calls: ${edge.call_count}\nTotal Time: ${edge.total_time.toFixed(3)}s\nAvg Time: ${edge.avg_time.toFixed(3)}s`,
    width: Math.min(Math.max(1, edge.call_count / 5), 10),
    color: edgeColorForTime(edge.avg_time),
  }));

  const spacing = SPACING_MAP[defaultSpacing];

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  ${VIS_CSP}
  <title>CallFlow Visualization</title>
  <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
  <style>
    body { margin: 0; font-family: var(--vscode-font-family); background: var(--vscode-editor-background); color: var(--vscode-editor-foreground); }
    #controls, .stats { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; padding: 10px 12px; background: var(--vscode-sideBar-background); border-bottom: 1px solid var(--vscode-panel-border); }
    .control-group { display: flex; flex-direction: column; gap: 4px; }
    .control-group label { font-size: 11px; font-weight: 600; color: var(--vscode-descriptionForeground); }
    select, button { padding: 4px 8px; background: var(--vscode-dropdown-background); color: var(--vscode-dropdown-foreground); border: 1px solid var(--vscode-dropdown-border); border-radius: 3px; font-size: 13px; }
    button { background: var(--vscode-button-background); color: var(--vscode-button-foreground); cursor: pointer; }
    button:hover { background: var(--vscode-button-hoverBackground); }
    #mynetwork { width: 100%; height: calc(100vh - 116px); }
    .stat-item { display: flex; flex-direction: column; min-width: 100px; }
    .stat-value { font-size: 16px; font-weight: 700; color: var(--vscode-textLink-foreground); }
    .stat-label { color: var(--vscode-descriptionForeground); font-size: 12px; }
  </style>
</head>
<body>
  <div class="stats">
    <div class="stat-item"><span class="stat-value">${nodes.length}</span><span class="stat-label">Functions</span></div>
    <div class="stat-item"><span class="stat-value">${edges.length}</span><span class="stat-label">Relationships</span></div>
    <div class="stat-item"><span class="stat-value">${traceData.metadata.duration.toFixed(3)}s</span><span class="stat-label">Duration</span></div>
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
        <option value="tree">Tree</option>
        <option value="tree-horizontal">Tree Horizontal</option>
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
    <button onclick="doExportPNG()">Export PNG</button>
    <button onclick="doExportJSON()">Export JSON</button>
  </div>
  <div id="mynetwork"></div>

  <script>
    var vscodeApi = acquireVsCodeApi();
    var nodes = ${JSON.stringify(nodes)};
    var edges = ${JSON.stringify(edges)};

    function buildGraphIndex(nodeList, edgeList) {
      var nodeById = new Map();
      var adjacency = new Map();
      var inDegree = new Map();
      nodeList.forEach(function(n) { nodeById.set(n.id, n); adjacency.set(n.id, []); inDegree.set(n.id, 0); });
      edgeList.forEach(function(e) { (adjacency.get(e.from) || []).push(e.to); inDegree.set(e.to, (inDegree.get(e.to) || 0) + 1); });
      var roots = [];
      inDegree.forEach(function(deg, id) { if (deg === 0) roots.push(id); });
      return { nodeById: nodeById, adjacency: adjacency, inDegree: inDegree, roots: roots };
    }

    var graphIndex = buildGraphIndex(nodes, edges);
    var container = document.getElementById('mynetwork');
    var data = { nodes: new vis.DataSet(nodes), edges: new vis.DataSet(edges) };
    window.allNodes = new vis.DataSet(nodes);
    window.allEdges = new vis.DataSet(edges);
    window.currentSpacing = ${spacing};

    var options = {
      nodes: { shape: 'box', font: { size: 12, color: '#ffffff' }, borderWidth: 1, shadow: true, margin: 10 },
      edges: { width: 1, shadow: true, smooth: { type: 'continuous' }, arrows: { to: { enabled: true, scaleFactor: 0.8 } } },
      layout: { hierarchical: false },
      physics: { enabled: true, solver: 'forceAtlas2Based' },
      interaction: { hover: true, tooltipDelay: 200 }
    };

    var network = new vis.Network(container, data, options);
    window.network = network;

    window.changeLayout = function(layoutType) {
      var resetNodes = nodes.map(function(n) { return Object.assign({}, n, { x: undefined, y: undefined, fixed: {x:false,y:false} }); });
      if (layoutType === 'hierarchical' || layoutType === 'tree' || layoutType === 'tree-horizontal') {
        data.nodes.clear(); data.nodes.add(resetNodes);
        var dir = layoutType === 'tree-horizontal' ? 'LR' : 'UD';
        var sp = window.currentSpacing || 150;
        network.setOptions({ layout: { hierarchical: { enabled: true, direction: dir, sortMethod: 'directed', nodeSpacing: sp, levelSeparation: sp * 1.3 } }, physics: { enabled: false } });
      } else if (layoutType === 'force') {
        data.nodes.clear(); data.nodes.add(resetNodes);
        network.setOptions({ layout: { hierarchical: false }, physics: { enabled: true, solver: 'forceAtlas2Based' } });
      } else if (layoutType === 'circular') {
        var radius = (window.currentSpacing || 150) * 2;
        var cx = 400, cy = 300, step = 2 * Math.PI / nodes.length;
        var cn = nodes.map(function(n, i) { var a = i * step; return Object.assign({}, n, { x: cx + radius * Math.cos(a), y: cy + radius * Math.sin(a), fixed: {x:true,y:true} }); });
        data.nodes.clear(); data.nodes.add(cn);
        network.setOptions({ layout: { hierarchical: false }, physics: { enabled: false } });
        setTimeout(function() { network.fit(); }, 100);
      } else if (layoutType === 'radial') {
        var adj = graphIndex.adjacency, roots = graphIndex.roots.slice();
        if (roots.length === 0 && nodes.length > 0) roots = [nodes[0].id];
        var levels = new Map(), queue = roots.map(function(r) { return [r, 0]; }), visited = new Set(), qi = 0;
        while (qi < queue.length) { var pair = queue[qi++], nid = pair[0], lvl = pair[1]; if (visited.has(nid)) continue; visited.add(nid); levels.set(nid, lvl); (adj.get(nid)||[]).forEach(function(c) { if (!visited.has(c)) queue.push([c, lvl+1]); }); }
        nodes.forEach(function(n) { if (!levels.has(n.id)) levels.set(n.id, 0); });
        var lg = new Map();
        levels.forEach(function(l, id) { if (!lg.has(l)) lg.set(l, []); lg.get(l).push(id); });
        var rs = window.currentSpacing || 150, un = [];
        lg.forEach(function(lnodes, l) { var r = l * rs + 50, as = 2 * Math.PI / lnodes.length; lnodes.forEach(function(id, i) { var a = i * as, nd = graphIndex.nodeById.get(id); un.push(Object.assign({}, nd, { x: 400 + r * Math.cos(a), y: 300 + r * Math.sin(a), fixed: {x:true,y:true} })); }); });
        data.nodes.clear(); data.nodes.add(un);
        network.setOptions({ layout: { hierarchical: false }, physics: { enabled: false } });
        setTimeout(function() { network.fit(); }, 100);
      } else if (layoutType === 'grid') {
        var cols = Math.ceil(Math.sqrt(nodes.length)), sp2 = window.currentSpacing || 200;
        var gn = nodes.map(function(n, i) { return Object.assign({}, n, { x: 100 + (i % cols) * sp2, y: 100 + Math.floor(i / cols) * sp2, fixed: {x:true,y:true} }); });
        data.nodes.clear(); data.nodes.add(gn);
        network.setOptions({ layout: { hierarchical: false }, physics: { enabled: false } });
        setTimeout(function() { network.fit(); }, 100);
      } else if (layoutType === 'timeline') {
        var sorted = nodes.slice().sort(function(a,b) { return (b.total_time||0) - (a.total_time||0); });
        var sp3 = window.currentSpacing || 150;
        var tn = sorted.map(function(n, i) { return Object.assign({}, n, { x: 100 + i * sp3, y: 300, fixed: {x:true,y:true} }); });
        data.nodes.clear(); data.nodes.add(tn);
        network.setOptions({ layout: { hierarchical: false }, physics: { enabled: false } });
        setTimeout(function() { network.fit(); }, 100);
      } else if (layoutType === 'organic') {
        data.nodes.clear(); data.nodes.add(resetNodes);
        network.setOptions({ layout: { hierarchical: false }, physics: { enabled: true, solver: 'barnesHut' } });
      }
    };

    document.getElementById('layout').addEventListener('change', function(e) { window.changeLayout(e.target.value); });
    document.getElementById('spacing').addEventListener('change', function(e) { window.currentSpacing = {compact:100,normal:150,relaxed:200,wide:300}[e.target.value]||150; window.changeLayout(document.getElementById('layout').value); });
    document.getElementById('physics').addEventListener('change', function(e) { network.setOptions({ physics: { enabled: e.target.value === 'true' } }); });

    function doExportPNG() { vscodeApi.postMessage({ command: 'export-png' }); }
    function doExportJSON() { vscodeApi.postMessage({ command: 'export-json' }); }
  </script>
</body>
</html>`;
}

export function buildThreeWebviewHtml(traceData: TraceData, defaultLayout: string): string {
  const nodes = traceData.nodes.map((node) => ({
    id: node.full_name,
    label: node.name,
    module: node.module || 'main',
    call_count: node.call_count,
    total_time: node.total_time,
    avg_time: node.avg_time,
    color: colorForTime(node.avg_time),
  }));

  const edges = traceData.edges.map((edge) => ({
    from: edge.caller,
    to: edge.callee,
    call_count: edge.call_count,
    total_time: edge.total_time,
    color: edgeColorForTime(edge.avg_time),
  }));

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  ${VIS_CSP}
  <title>CallFlow 3D</title>
  <script src="https://unpkg.com/three@0.157.0/build/three.min.js"></script>
  <style>
    body { margin: 0; overflow: hidden; background: #0a0a1a; font-family: var(--vscode-font-family); }
    canvas { display: block; }
    #info { position: absolute; top: 10px; left: 10px; color: #94a3b8; font-size: 12px; background: rgba(0,0,0,0.6); padding: 8px 12px; border-radius: 6px; }
  </style>
</head>
<body>
  <div id="info">Nodes: ${nodes.length} | Edges: ${edges.length} | Duration: ${traceData.metadata.duration.toFixed(3)}s</div>
  <script>
    var nodes = ${JSON.stringify(nodes)};
    var edges = ${JSON.stringify(edges)};
    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 0, 50);
    var renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setClearColor(0x0a0a1a);
    document.body.appendChild(renderer.domElement);

    var nodeMap = {};
    nodes.forEach(function(node, i) {
      var angle = (2 * Math.PI * i) / nodes.length;
      var radius = 20;
      var size = Math.max(0.3, Math.min(2, node.call_count / 5));
      var geo = new THREE.SphereGeometry(size, 16, 16);
      var mat = new THREE.MeshPhongMaterial({ color: node.color, emissive: node.color, emissiveIntensity: 0.3 });
      var mesh = new THREE.Mesh(geo, mat);
      mesh.position.set(radius * Math.cos(angle), radius * Math.sin(angle), (Math.random() - 0.5) * 10);
      scene.add(mesh);
      nodeMap[node.id] = mesh;
    });

    edges.forEach(function(edge) {
      var from = nodeMap[edge.from], to = nodeMap[edge.to];
      if (!from || !to) return;
      var points = [from.position.clone(), to.position.clone()];
      var geo = new THREE.BufferGeometry().setFromPoints(points);
      var mat = new THREE.LineBasicMaterial({ color: edge.color, opacity: 0.5, transparent: true });
      scene.add(new THREE.Line(geo, mat));
    });

    scene.add(new THREE.AmbientLight(0x404040));
    var dl = new THREE.DirectionalLight(0xffffff, 0.8);
    dl.position.set(10, 10, 10);
    scene.add(dl);

    var isDragging = false, prevMouse = { x: 0, y: 0 };
    renderer.domElement.addEventListener('mousedown', function(e) { isDragging = true; prevMouse = { x: e.clientX, y: e.clientY }; });
    renderer.domElement.addEventListener('mouseup', function() { isDragging = false; });
    renderer.domElement.addEventListener('mousemove', function(e) {
      if (!isDragging) return;
      var dx = e.clientX - prevMouse.x, dy = e.clientY - prevMouse.y;
      scene.rotation.y += dx * 0.005;
      scene.rotation.x += dy * 0.005;
      prevMouse = { x: e.clientX, y: e.clientY };
    });
    renderer.domElement.addEventListener('wheel', function(e) { camera.position.z += e.deltaY * 0.05; });
    window.addEventListener('resize', function() { camera.aspect = window.innerWidth / window.innerHeight; camera.updateProjectionMatrix(); renderer.setSize(window.innerWidth, window.innerHeight); });

    function animate() { requestAnimationFrame(animate); renderer.render(scene, camera); }
    animate();
  </script>
</body>
</html>`;
}

export function getAnomalyReportHtml(report: AnomalyReport): string {
  const alertsHtml = report.top_anomalies
    .map(
      (alert) => `
      <div class="alert ${escapeHtml(alert.severity)}">
        <div class="metric">${escapeHtml(alert.metric_name)}</div>
        <div>${escapeHtml(alert.description)}</div>
        <small>Z-score: ${alert.z_score.toFixed(2)} | Time: ${escapeHtml(alert.timestamp)}</small>
      </div>`,
    )
    .join('');

  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline';">
  <style>
    body { font-family: var(--vscode-font-family); padding: 20px; background: var(--vscode-editor-background); color: var(--vscode-editor-foreground); }
    .header { background: var(--vscode-sideBar-background); padding: 15px; border-radius: 5px; margin-bottom: 20px; }
    .alert { padding: 10px; margin: 5px 0; border-radius: 5px; }
    .critical { background: rgba(244,67,54,0.15); border-left: 4px solid #f44336; }
    .high { background: rgba(255,152,0,0.15); border-left: 4px solid #ff9800; }
    .medium { background: rgba(255,193,7,0.15); border-left: 4px solid #ffc107; }
    .low { background: rgba(76,175,80,0.15); border-left: 4px solid #4caf50; }
    .metric { font-weight: bold; }
  </style>
</head>
<body>
  <div class="header">
    <h1>Anomaly Detection Report</h1>
    <p>Generated: ${escapeHtml(report.report_generated)}</p>
    <p>Period: Last ${report.period_hours} hours</p>
  </div>
  <h2>Summary</h2>
  <p><strong>Total Alerts:</strong> ${report.total_alerts}</p>
  <ul>
    <li>Critical: ${report.severity_breakdown.critical ?? 0}</li>
    <li>High: ${report.severity_breakdown.high ?? 0}</li>
    <li>Medium: ${report.severity_breakdown.medium ?? 0}</li>
    <li>Low: ${report.severity_breakdown.low ?? 0}</li>
  </ul>
  <h2>Top Anomalies</h2>
  ${alertsHtml}
</body>
</html>`;
}

export function getPluginManagerHtml(plugins: PluginList): string {
  const analyzersHtml = plugins.analyzers
    .map((name) => `<div class="plugin"><div class="plugin-name">${escapeHtml(name)}</div><div class="plugin-type">Custom Analyzer</div></div>`)
    .join('');

  const exportersHtml = Object.entries(plugins.exporters)
    .map(([name, extensions]) => `<div class="plugin"><div class="plugin-name">${escapeHtml(name)}</div><div class="plugin-type">Exports: ${escapeHtml((extensions as string[]).join(', '))}</div></div>`)
    .join('');

  const widgetsHtml = plugins.ui_widgets
    .map((name) => `<div class="plugin"><div class="plugin-name">${escapeHtml(name)}</div><div class="plugin-type">UI Widget</div></div>`)
    .join('');

  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline';">
  <style>
    body { font-family: var(--vscode-font-family); padding: 20px; background: var(--vscode-editor-background); color: var(--vscode-editor-foreground); }
    .plugin { background: var(--vscode-sideBar-background); padding: 10px; margin: 5px 0; border-radius: 5px; }
    .plugin-name { font-weight: bold; }
    .plugin-type { color: var(--vscode-descriptionForeground); font-size: 0.9em; }
  </style>
</head>
<body>
  <h1>Plugin Manager</h1>
  <h2>Analyzers (${plugins.analyzers.length})</h2>
  ${analyzersHtml || '<p>No analyzers registered</p>'}
  <h2>Exporters (${Object.keys(plugins.exporters).length})</h2>
  ${exportersHtml || '<p>No exporters registered</p>'}
  <h2>UI Widgets (${plugins.ui_widgets.length})</h2>
  ${widgetsHtml || '<p>No widgets registered</p>'}
</body>
</html>`;
}

export function getAnalysisResultHtml(analyzerName: string, result: Record<string, unknown>): string {
  const metricsHtml = Object.entries(result)
    .map(
      ([key, value]) => `
      <div class="metric">
        <div class="metric-name">${escapeHtml(key)}</div>
        <div class="metric-value">${escapeHtml(typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value))}</div>
      </div>`,
    )
    .join('');

  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline';">
  <style>
    body { font-family: var(--vscode-font-family); padding: 20px; background: var(--vscode-editor-background); color: var(--vscode-editor-foreground); }
    .metric { background: var(--vscode-sideBar-background); padding: 10px; margin: 5px 0; border-radius: 5px; }
    .metric-name { font-weight: bold; }
    .metric-value { color: var(--vscode-descriptionForeground); font-size: 1.2em; white-space: pre-wrap; }
  </style>
</head>
<body>
  <h1>${escapeHtml(analyzerName)} Analysis Results</h1>
  <p>Generated: ${escapeHtml(new Date().toISOString())}</p>
  <h2>Metrics</h2>
  ${metricsHtml}
</body>
</html>`;
}
