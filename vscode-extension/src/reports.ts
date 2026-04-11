import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';
import * as vscode from 'vscode';

import * as state from './state';
import { runJsonCliReport } from './cliRunner';
import { createRichReportPanel } from './ui';
import type { SummaryReport, ExplainReport, BenchmarkReport } from './types';

export async function generateSummary(): Promise<void> {
  const traceData = state.getCurrentTraceData();
  if (!traceData) {
    vscode.window.showWarningMessage('No trace data available. Run a trace first.');
    return;
  }

  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'callflow-summary-'));
  const tracePath = path.join(tempDir, 'trace.json');

  try {
    fs.writeFileSync(tracePath, JSON.stringify(traceData, null, 2));
    const report = await runJsonCliReport<SummaryReport>(
      ['summary', tracePath, '--top', '5'],
      'callflow-summary-report-',
    );
    const summary = report.summary ?? {};
    const suspectFunction = report.suspect_function;
    const suspectModule = report.suspect_module;

    createRichReportPanel(
      'CallFlow Summary',
      'Actionable trace overview with the slowest functions and next steps.',
      [
        { label: 'Total Calls', value: summary.total_calls ?? 0 },
        { label: 'Total Time', value: `${(summary.total_time ?? 0).toFixed(6)}s` },
        { label: 'Recorded Calls', value: summary.recorded_calls ?? 0 },
        { label: 'Sampling', value: `${(summary.trace_options?.sampling_rate ?? 1.0).toFixed(2)}` },
      ],
      [
        {
          type: 'keyvalue',
          title: 'Trace Stats',
          items: [
            { key: 'Total Nodes', value: summary.total_nodes ?? 0 },
            { key: 'Total Edges', value: summary.total_edges ?? 0 },
            { key: 'Skipped by Sampling', value: summary.skipped_sampling ?? 0 },
            { key: 'Skipped by Filtering', value: summary.skipped_filtering ?? 0 },
            { key: 'Skipped by Duration', value: summary.skipped_duration ?? 0 },
          ],
        },
        {
          type: 'keyvalue',
          title: 'Primary Hotspots',
          items: [
            { key: 'Suspect Function', value: suspectFunction?.full_name ?? 'None' },
            { key: 'Suspect Module', value: suspectModule?.module ?? 'None' },
          ],
        },
        {
          type: 'table',
          title: 'Top Slow Functions',
          headers: ['Function', 'Calls', 'Total', 'Avg', 'Share'],
          rows: (report.slow_functions ?? []).slice(0, 5).map((item) => [
            item.full_name,
            String(item.call_count),
            `${Number(item.total_time).toFixed(6)}s`,
            `${Number(item.avg_time).toFixed(6)}s`,
            `${Number(item.share_pct).toFixed(1)}%`,
          ]),
        },
        {
          type: 'table',
          title: 'Top Modules',
          headers: ['Module', 'Calls', 'Total', 'Functions', 'Share'],
          rows: (report.hot_modules ?? []).slice(0, 5).map((item) => [
            item.module,
            String(item.call_count),
            `${Number(item.total_time).toFixed(6)}s`,
            String(item.functions),
            `${Number(item.share_pct).toFixed(1)}%`,
          ]),
        },
        {
          type: 'list',
          title: 'Next Steps',
          items: report.next_steps ?? [],
        },
      ],
    );
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : String(error);
    vscode.window.showErrorMessage(`Summary generation failed: ${msg}`);
  } finally {
    try {
      fs.rmSync(tempDir, { recursive: true, force: true });
    } catch {
      // ignore cleanup errors
    }
  }
}

export async function explainTraces(): Promise<void> {
  const beforeUris = await vscode.window.showOpenDialog({
    canSelectMany: false,
    openLabel: 'Select baseline trace',
    filters: { 'Trace JSON': ['json'] },
  });
  if (!beforeUris || beforeUris.length === 0) return;

  const afterUris = await vscode.window.showOpenDialog({
    canSelectMany: false,
    openLabel: 'Select new trace',
    filters: { 'Trace JSON': ['json'] },
  });
  if (!afterUris || afterUris.length === 0) return;

  try {
    const report = await runJsonCliReport<ExplainReport>(
      ['explain', beforeUris[0].fsPath, afterUris[0].fsPath, '--top', '5'],
      'callflow-explain-report-',
    );

    const summary = report.summary ?? {};

    createRichReportPanel(
      'CallFlow Regression Explanation',
      'Compare two traces and immediately see what slowed down, what changed, and what to inspect next.',
      [
        {
          label: 'Time Change',
          value: `${Number(summary.time_change ?? 0).toFixed(6)}s`,
          detail: `${Number(summary.time_change_pct ?? 0).toFixed(2)}%`,
        },
        { label: 'Regressions', value: summary.regressions ?? 0 },
        { label: 'Improvements', value: summary.improvements ?? 0 },
        { label: 'Added Nodes', value: summary.nodes_added ?? 0 },
      ],
      [
        {
          type: 'keyvalue',
          title: 'Primary Drivers',
          items: [
            { key: 'Regression Driver', value: report.regression_driver?.name ?? 'None' },
            { key: 'Structural Driver', value: report.structural_driver?.module ?? 'None' },
          ],
        },
        {
          type: 'table',
          title: 'Top Regressions',
          headers: ['Function', 'Time Diff', 'Pct', 'Calls Before', 'Calls After'],
          rows: (report.top_regressions ?? []).map((item) => [
            item.name,
            `${Number(item.time_diff).toFixed(6)}s`,
            `${Number(item.time_diff_pct).toFixed(1)}%`,
            String(item.calls_before),
            String(item.calls_after),
          ]),
        },
        {
          type: 'table',
          title: 'Module Deltas',
          headers: ['Module', 'Time Diff', 'Pct', 'Calls Before', 'Calls After'],
          rows: (report.module_deltas ?? []).map((item) => [
            item.module,
            `${Number(item.time_diff).toFixed(6)}s`,
            `${Number(item.time_diff_pct).toFixed(1)}%`,
            String(item.calls_before),
            String(item.calls_after),
          ]),
        },
        {
          type: 'list',
          title: 'Next Steps',
          items: report.next_steps ?? [],
        },
      ],
    );
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : String(error);
    vscode.window.showErrorMessage(`Explain failed: ${msg}`);
  }
}

export async function runBenchmarkCurrentFile(): Promise<void> {
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
  const config = vscode.workspace.getConfiguration('callflowTracer');
  const runs = config.get<number>('benchmarkRuns', 3);

  await vscode.window.withProgress(
    { location: vscode.ProgressLocation.Notification, title: 'Running benchmark...', cancellable: false },
    async (progress) => {
      try {
        progress.report({ increment: 0, message: 'Measuring baseline and traced runs...' });

        const report = await runJsonCliReport<BenchmarkReport>(
          ['benchmark', filePath, '--runs', String(runs)],
          'callflow-benchmark-report-',
        );

        progress.report({ increment: 100, message: 'Complete!' });

        const summary = report.summary ?? {};
        createRichReportPanel(
          'CallFlow Benchmark Report',
          'Measure tracing overhead against a clean baseline and get a production-friendly sampling recommendation.',
          [
            { label: 'Baseline Avg', value: `${Number(summary.baseline_avg_time_s ?? 0).toFixed(6)}s` },
            { label: 'Traced Avg', value: `${Number(summary.traced_avg_time_s ?? 0).toFixed(6)}s` },
            { label: 'Overhead', value: `${Number(summary.overhead_pct ?? 0).toFixed(2)}%` },
            { label: 'Recommended Sampling', value: `${Number(summary.recommended_sampling_rate ?? 1.0).toFixed(2)}` },
          ],
          [
            {
              type: 'keyvalue',
              title: 'Benchmark Summary',
              items: [
                { key: 'Runs', value: summary.runs ?? 0 },
                { key: 'Memory Delta', value: `${Number(summary.memory_delta_mb ?? 0).toFixed(2)} MB` },
                { key: 'Total Traced Calls', value: summary.total_traced_calls ?? 0 },
                { key: 'Total Traced Nodes', value: summary.total_traced_nodes ?? 0 },
                { key: 'Total Traced Edges', value: summary.total_traced_edges ?? 0 },
              ],
            },
            {
              type: 'table',
              title: 'Top Functions',
              headers: ['Function', 'Calls', 'Total', 'Avg'],
              rows: (report.top_functions ?? []).slice(0, 8).map((item) => [
                item.full_name,
                String(item.call_count),
                `${Number(item.total_time).toFixed(6)}s`,
                `${Number(item.avg_time).toFixed(6)}s`,
              ]),
            },
            {
              type: 'list',
              title: 'Recommendations',
              items: report.recommendations ?? [],
            },
            {
              type: 'keyvalue',
              title: 'Run Quality',
              items: [
                { key: 'Baseline Memory', value: `${Number(summary.baseline_avg_memory_mb ?? 0).toFixed(2)} MB` },
                { key: 'Traced Memory', value: `${Number(summary.traced_avg_memory_mb ?? 0).toFixed(2)} MB` },
              ],
            },
          ],
        );

        vscode.window.showInformationMessage(`Benchmark completed for ${path.basename(filePath)}`);
      } catch (error: unknown) {
        const msg = error instanceof Error ? error.message : String(error);
        vscode.window.showErrorMessage(`Benchmark failed: ${msg}`);
      }
    },
  );
}
