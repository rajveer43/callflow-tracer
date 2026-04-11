import * as vscode from 'vscode';
import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';

import * as state from './state';
import { runCallflowCli, runJsonCliReport } from './cliRunner';
import { generateSummary, explainTraces, runBenchmarkCurrentFile } from './reports';
import { buildVisWebviewHtml, buildThreeWebviewHtml, getAnomalyReportHtml, getPluginManagerHtml, getAnalysisResultHtml } from './webviews';
import type { TraceData, Spacing, AnomalyReport, PluginList } from './types';

let visualizationPanel: vscode.WebviewPanel | null = null;

// ---------------------------------------------------------------------------
// Activation
// ---------------------------------------------------------------------------

export function activate(context: vscode.ExtensionContext): void {
  console.log('CallFlow Tracer extension is now active');

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
    vscode.commands.registerCommand('callflow-tracer.generateSummary', generateSummary),
    vscode.commands.registerCommand('callflow-tracer.explainTraces', explainTraces),
    vscode.commands.registerCommand('callflow-tracer.runBenchmark', runBenchmarkCurrentFile),
    vscode.commands.registerCommand('callflow-tracer.enableAutoInstrumentation', enableAutoInstrumentation),
    vscode.commands.registerCommand('callflow-tracer.showPluginManager', showPluginManager),
    vscode.commands.registerCommand('callflow-tracer.runCustomAnalyzer', runCustomAnalyzer),
  );

  // Auto-trace on save
  context.subscriptions.push(
    vscode.workspace.onDidSaveTextDocument((document) => {
      const config = vscode.workspace.getConfiguration('callflowTracer');
      if (config.get<boolean>('autoTrace') && document.languageId === 'python') {
        traceCurrentFile();
      }
    }),
  );

  // Status bar
  const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
  statusBarItem.command = 'callflow-tracer.showVisualization';
  statusBarItem.text = '$(graph) CallFlow';
  statusBarItem.tooltip = 'Show CallFlow Visualization';
  statusBarItem.show();
  context.subscriptions.push(statusBarItem);
}

export function deactivate(): void {
  // nothing to clean up
}

// ---------------------------------------------------------------------------
// Tracing — uses the CLI (safe, no shell injection)
// ---------------------------------------------------------------------------

async function runTrace(filePath: string): Promise<TraceData> {
  const config = vscode.workspace.getConfiguration('callflowTracer');
  const includeArgs = config.get<boolean>('includeArgs', false);

  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'callflow-trace-'));
  const outputPath = path.join(tempDir, 'trace.json');

  const args = ['trace', filePath, '-o', outputPath, '--format', 'json', '--no-browser'];
  if (includeArgs) {
    args.push('--include-args');
  }

  try {
    await runCallflowCli(args, path.dirname(filePath));

    if (!fs.existsSync(outputPath)) {
      throw new Error('Trace data not generated');
    }

    return JSON.parse(fs.readFileSync(outputPath, 'utf8')) as TraceData;
  } finally {
    try {
      fs.rmSync(tempDir, { recursive: true, force: true });
    } catch {
      // ignore cleanup errors
    }
  }
}

async function traceCurrentFile(): Promise<void> {
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
  await vscode.window.withProgress(
    { location: vscode.ProgressLocation.Notification, title: 'Tracing function calls...', cancellable: false },
    async (progress) => {
      try {
        progress.report({ increment: 0, message: 'Running trace...' });
        const traceData = await runTrace(filePath);

        progress.report({ increment: 50, message: 'Processing results...' });
        state.setCurrentTraceData(traceData);
        state.setCurrentTraceFilePath(filePath);

        progress.report({ increment: 100, message: 'Complete!' });
        await showVisualization();
        vscode.window.showInformationMessage('CallFlow trace completed successfully!');
      } catch (error: unknown) {
        const msg = error instanceof Error ? error.message : String(error);
        vscode.window.showErrorMessage(`Trace failed: ${msg}`);
      }
    },
  );
}

async function traceSelection(): Promise<void> {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showErrorMessage('No active editor');
    return;
  }

  const selectedText = editor.document.getText(editor.selection);
  if (!selectedText) {
    vscode.window.showErrorMessage('No text selected');
    return;
  }

  const functionMatch = selectedText.match(/def\s+(\w+)/);
  if (!functionMatch) {
    vscode.window.showErrorMessage('No function definition found in selection');
    return;
  }

  const functionName = functionMatch[1];
  const filePath = editor.document.uri.fsPath;

  await vscode.window.withProgress(
    { location: vscode.ProgressLocation.Notification, title: `Tracing function: ${functionName}...`, cancellable: false },
    async () => {
      try {
        const traceData = await runTrace(filePath);
        state.setCurrentTraceData(traceData);
        state.setCurrentTraceFilePath(filePath);
        await showVisualization();
        vscode.window.showInformationMessage(`Traced function: ${functionName}`);
      } catch (error: unknown) {
        const msg = error instanceof Error ? error.message : String(error);
        vscode.window.showErrorMessage(`Trace failed: ${msg}`);
      }
    },
  );
}

// ---------------------------------------------------------------------------
// Visualization
// ---------------------------------------------------------------------------

async function showVisualization(): Promise<void> {
  const traceData = state.getCurrentTraceData();
  if (!traceData) {
    vscode.window.showWarningMessage('No trace data available. Run a trace first.');
    return;
  }

  const config = vscode.workspace.getConfiguration('callflowTracer');
  const defaultLayout = config.get<string>('defaultLayout', 'force');
  const defaultSpacing = config.get<Spacing>('defaultSpacing', 'normal');

  if (visualizationPanel) {
    visualizationPanel.reveal(vscode.ViewColumn.Two);
  } else {
    visualizationPanel = vscode.window.createWebviewPanel(
      'callflowVisualization',
      'CallFlow Visualization',
      vscode.ViewColumn.Two,
      { enableScripts: true, retainContextWhenHidden: true },
    );

    visualizationPanel.onDidDispose(() => {
      visualizationPanel = null;
    });

    visualizationPanel.webview.onDidReceiveMessage((message: { command: string; text?: string }) => {
      switch (message.command) {
        case 'export-png':
          exportPNG();
          break;
        case 'export-json':
          exportJSON();
          break;
        case 'alert':
          vscode.window.showInformationMessage(message.text ?? '');
          break;
      }
    });
  }

  visualizationPanel.webview.html = buildVisWebviewHtml(traceData, defaultLayout, defaultSpacing);
}

async function show3DVisualization(): Promise<void> {
  const traceData = state.getCurrentTraceData();
  if (!traceData) {
    vscode.window.showWarningMessage('No trace data available. Run a trace first.');
    return;
  }

  const config = vscode.workspace.getConfiguration('callflowTracer');
  const defaultLayout = config.get<string>('default3DLayout', 'force');

  const panel = vscode.window.createWebviewPanel(
    'callflow3DVisualization',
    'CallFlow 3D Visualization',
    vscode.ViewColumn.Two,
    { enableScripts: true },
  );

  panel.webview.html = buildThreeWebviewHtml(traceData, defaultLayout);
}

// ---------------------------------------------------------------------------
// Export / Layout commands
// ---------------------------------------------------------------------------

function clearTrace(): void {
  state.clearTraceState();
  if (visualizationPanel) {
    visualizationPanel.dispose();
  }
  vscode.window.showInformationMessage('Trace data cleared');
}

async function exportPNG(): Promise<void> {
  const traceData = state.getCurrentTraceData();
  if (!traceData) {
    vscode.window.showWarningMessage('No trace data to export');
    return;
  }
  const uri = await vscode.window.showSaveDialog({
    defaultUri: vscode.Uri.file('callflow-graph.png'),
    filters: { 'PNG Images': ['png'] },
  });
  if (uri) {
    vscode.window.showInformationMessage('PNG export functionality requires browser canvas access');
  }
}

async function exportJSON(): Promise<void> {
  const traceData = state.getCurrentTraceData();
  if (!traceData) {
    vscode.window.showWarningMessage('No trace data to export');
    return;
  }
  const uri = await vscode.window.showSaveDialog({
    defaultUri: vscode.Uri.file('callflow-graph.json'),
    filters: { 'JSON Files': ['json'] },
  });
  if (uri) {
    fs.writeFileSync(uri.fsPath, JSON.stringify(traceData, null, 2));
    vscode.window.showInformationMessage('Trace data exported successfully');
  }
}

async function changeLayout(): Promise<void> {
  const layouts = [
    'Hierarchical',
    'Force-Directed',
    'Circular',
    'Radial Tree',
    'Grid',
    'Tree (Vertical)',
    'Tree (Horizontal)',
    'Timeline',
    'Organic',
  ];

  const selected = await vscode.window.showQuickPick(layouts, { placeHolder: 'Select graph layout' });
  if (selected && visualizationPanel) {
    visualizationPanel.webview.postMessage({
      command: 'changeLayout',
      layout: selected.toLowerCase().replace(/[^a-z-]/g, ''),
    });
  }
}

// ---------------------------------------------------------------------------
// OpenTelemetry export — uses CLI (no shell injection)
// ---------------------------------------------------------------------------

async function exportToOtel(): Promise<void> {
  const traceData = state.getCurrentTraceData();
  if (!traceData) {
    vscode.window.showWarningMessage('No trace data to export. Run a trace first.');
    return;
  }

  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'callflow-otel-'));
  const tempJsonPath = path.join(tempDir, 'trace.json');

  try {
    fs.writeFileSync(tempJsonPath, JSON.stringify(traceData, null, 2));
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    vscode.window.showErrorMessage(`Failed to write temporary trace file: ${msg}`);
    return;
  }

  await vscode.window.withProgress(
    { location: vscode.ProgressLocation.Notification, title: 'Exporting CallFlow trace to OpenTelemetry...', cancellable: false },
    async () => {
      try {
        const config = vscode.workspace.getConfiguration('callflowTracer');
        const serviceName = config.get<string>('otelServiceName', 'callflow-tracer');
        await runCallflowCli(['export', tempJsonPath, '--format', 'otel', '--service-name', serviceName]);
        vscode.window.showInformationMessage('CallFlow trace exported to OpenTelemetry.');
      } catch (error: unknown) {
        const msg = error instanceof Error ? error.message : String(error);
        vscode.window.showErrorMessage(`OpenTelemetry export failed: ${msg}`);
      } finally {
        try {
          fs.rmSync(tempDir, { recursive: true, force: true });
        } catch {
          // ignore
        }
      }
    },
  );
}

async function exportToOtelAdvanced(): Promise<void> {
  const traceData = state.getCurrentTraceData();
  if (!traceData) {
    vscode.window.showWarningMessage('No trace data to export. Run a trace first.');
    return;
  }

  const config = vscode.workspace.getConfiguration('callflowTracer');

  const serviceName = await vscode.window.showInputBox({
    prompt: 'Service name',
    value: config.get<string>('otelServiceName', 'callflow-tracer'),
  });
  if (!serviceName) return;

  const environment = await vscode.window.showQuickPick(['production', 'staging', 'development'], {
    placeHolder: 'Select environment',
  });
  if (!environment) return;

  const samplingRateStr = await vscode.window.showInputBox({
    prompt: 'Sampling rate (0.0-1.0)',
    value: '1.0',
  });
  const samplingRate = parseFloat(samplingRateStr ?? '1.0');

  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'callflow-otel-adv-'));
  const tempJsonPath = path.join(tempDir, 'trace.json');

  try {
    fs.writeFileSync(tempJsonPath, JSON.stringify(traceData, null, 2));
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    vscode.window.showErrorMessage(`Failed to write temporary trace file: ${msg}`);
    return;
  }

  await vscode.window.withProgress(
    { location: vscode.ProgressLocation.Notification, title: 'Exporting to OpenTelemetry (advanced)...', cancellable: false },
    async () => {
      try {
        await runCallflowCli([
          'otel', tempJsonPath,
          '--service-name', serviceName,
          '--environment', environment,
          '--sampling-rate', String(samplingRate),
        ]);
        vscode.window.showInformationMessage(`OTel export complete: ${serviceName} (${environment}, sampling=${samplingRate})`);
      } catch (error: unknown) {
        const msg = error instanceof Error ? error.message : String(error);
        vscode.window.showErrorMessage(`Advanced OTel export failed: ${msg}`);
      } finally {
        try {
          fs.rmSync(tempDir, { recursive: true, force: true });
        } catch {
          // ignore
        }
      }
    },
  );
}

// ---------------------------------------------------------------------------
// Analysis commands — use CLI instead of generating Python scripts
// ---------------------------------------------------------------------------

async function analyzeAnomalies(): Promise<void> {
  const traceData = state.getCurrentTraceData();
  if (!traceData) {
    vscode.window.showWarningMessage('No trace data available. Run a trace first.');
    return;
  }

  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'callflow-anomaly-'));
  const tracePath = path.join(tempDir, 'trace.json');

  await vscode.window.withProgress(
    { location: vscode.ProgressLocation.Notification, title: 'Analyzing anomalies...', cancellable: false },
    async (progress) => {
      try {
        progress.report({ increment: 0, message: 'Running anomaly detection...' });
        fs.writeFileSync(tracePath, JSON.stringify(traceData, null, 2));

        const report = await runJsonCliReport<AnomalyReport>(
          ['anomalies', tracePath],
          'callflow-anomaly-report-',
        );

        progress.report({ increment: 100, message: 'Complete!' });

        const panel = vscode.window.createWebviewPanel(
          'anomalyReport',
          'Anomaly Detection Report',
          vscode.ViewColumn.One,
          { enableScripts: false },
        );
        panel.webview.html = getAnomalyReportHtml(report);
        vscode.window.showInformationMessage('Anomaly detection completed!');
      } catch (error: unknown) {
        const msg = error instanceof Error ? error.message : String(error);
        vscode.window.showErrorMessage(`Anomaly detection failed: ${msg}`);
      } finally {
        try {
          fs.rmSync(tempDir, { recursive: true, force: true });
        } catch {
          // ignore
        }
      }
    },
  );
}

async function enableAutoInstrumentation(): Promise<void> {
  const options = ['HTTP (requests, httpx, aiohttp)', 'Redis', 'Boto3 (AWS)', 'All Libraries'];
  const selected = await vscode.window.showQuickPick(options, {
    placeHolder: 'Select libraries to auto-instrument',
  });
  if (!selected) return;

  let libraries: string[] = [];
  if (selected.includes('All')) {
    libraries = ['http', 'redis', 'boto3'];
  } else {
    if (selected.includes('HTTP')) libraries.push('http');
    if (selected.includes('Redis')) libraries.push('redis');
    if (selected.includes('Boto3')) libraries.push('boto3');
  }

  try {
    await runCallflowCli(['auto-instrument', '--libraries', ...libraries]);
    vscode.window.showInformationMessage(
      `Auto-instrumentation enabled for ${selected}.\n` +
      `Add to your code:\n` +
      `from callflow_tracer.auto_instrumentation import enable_auto_instrumentation\n` +
      `enable_auto_instrumentation(${JSON.stringify(libraries)})`,
    );
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : String(error);
    vscode.window.showErrorMessage(`Failed to enable auto-instrumentation: ${msg}`);
  }
}

async function showPluginManager(): Promise<void> {
  const panel = vscode.window.createWebviewPanel(
    'pluginManager',
    'Plugin Manager',
    vscode.ViewColumn.One,
    { enableScripts: false },
  );

  try {
    const plugins = await runJsonCliReport<PluginList>(
      ['plugins', '--list'],
      'callflow-plugins-',
    );
    panel.webview.html = getPluginManagerHtml(plugins);
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : String(error);
    panel.webview.html = `<!DOCTYPE html><html><body><h2>Plugin Manager</h2><p>Error loading plugins: ${msg}</p></body></html>`;
  }
}

async function runCustomAnalyzer(): Promise<void> {
  const traceData = state.getCurrentTraceData();
  if (!traceData) {
    vscode.window.showWarningMessage('No trace data available. Run a trace first.');
    return;
  }

  let analyzers: string[];
  try {
    const result = await runJsonCliReport<{ analyzers: string[] }>(
      ['plugins', '--list-analyzers'],
      'callflow-analyzers-',
    );
    analyzers = result.analyzers;
  } catch {
    vscode.window.showErrorMessage('Failed to list analyzers');
    return;
  }

  if (analyzers.length === 0) {
    vscode.window.showInformationMessage('No custom analyzers available');
    return;
  }

  const selected = await vscode.window.showQuickPick(analyzers, {
    placeHolder: 'Select an analyzer to run',
  });
  if (!selected) return;

  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'callflow-analysis-'));
  const tracePath = path.join(tempDir, 'trace.json');

  await vscode.window.withProgress(
    { location: vscode.ProgressLocation.Notification, title: `Running ${selected} analyzer...`, cancellable: false },
    async (progress) => {
      try {
        progress.report({ increment: 0, message: 'Analyzing...' });
        fs.writeFileSync(tracePath, JSON.stringify(traceData, null, 2));

        const result = await runJsonCliReport<Record<string, unknown>>(
          ['analyze', tracePath, '--analyzer', selected],
          'callflow-analysis-result-',
        );

        progress.report({ increment: 100, message: 'Complete!' });

        const panel = vscode.window.createWebviewPanel(
          'analysisResult',
          `${selected} Analysis Results`,
          vscode.ViewColumn.One,
          { enableScripts: false },
        );
        panel.webview.html = getAnalysisResultHtml(selected, result);
        vscode.window.showInformationMessage(`${selected} analysis completed!`);
      } catch (error: unknown) {
        const msg = error instanceof Error ? error.message : String(error);
        vscode.window.showErrorMessage(`Analysis failed: ${msg}`);
      } finally {
        try {
          fs.rmSync(tempDir, { recursive: true, force: true });
        } catch {
          // ignore
        }
      }
    },
  );
}
