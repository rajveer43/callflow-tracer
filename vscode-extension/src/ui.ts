import * as vscode from 'vscode';
import type { ReportCard, ReportSection } from './types';

export function escapeHtml(content: unknown): string {
  return String(content)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

const CSP = `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline';">`;

export function createTextReportPanel(title: string, content: string): vscode.WebviewPanel {
  const panel = vscode.window.createWebviewPanel(
    'callflowTextReport',
    title,
    vscode.ViewColumn.Two,
    { enableScripts: false },
  );

  panel.webview.html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  ${CSP}
  <title>${escapeHtml(title)}</title>
  <style>
    body {
      font-family: var(--vscode-font-family);
      background: var(--vscode-editor-background);
      color: var(--vscode-editor-foreground);
      margin: 0; padding: 20px;
    }
    pre {
      white-space: pre-wrap; word-break: break-word;
      background: var(--vscode-editor-inactiveSelectionBackground);
      padding: 16px; border-radius: 8px;
      border: 1px solid var(--vscode-panel-border);
    }
  </style>
</head>
<body>
  <h1>${escapeHtml(title)}</h1>
  <pre>${escapeHtml(content)}</pre>
</body>
</html>`;

  return panel;
}

function renderSection(section: ReportSection): string {
  if (section.type === 'list') {
    const items = section.items.map((item) => `<li>${escapeHtml(item)}</li>`).join('');
    return `
      <div class="section">
        <h2>${escapeHtml(section.title)}</h2>
        <ul>${items || '<li>None</li>'}</ul>
      </div>`;
  }

  if (section.type === 'table') {
    const headers = section.headers.map((h) => `<th>${escapeHtml(h)}</th>`).join('');
    const rows = section.rows
      .map((row) => `<tr>${row.map((cell) => `<td>${escapeHtml(cell)}</td>`).join('')}</tr>`)
      .join('');
    const emptyRow = `<tr><td colspan="${section.headers.length}">No data</td></tr>`;
    return `
      <div class="section">
        <h2>${escapeHtml(section.title)}</h2>
        <table>
          <thead><tr>${headers}</tr></thead>
          <tbody>${rows || emptyRow}</tbody>
        </table>
      </div>`;
  }

  if (section.type === 'keyvalue') {
    const items = section.items
      .map(
        (item) => `
        <div class="kv-row">
          <div class="kv-key">${escapeHtml(item.key)}</div>
          <div class="kv-value">${escapeHtml(item.value)}</div>
        </div>`,
      )
      .join('');
    return `
      <div class="section">
        <h2>${escapeHtml(section.title)}</h2>
        <div class="kv-grid">${items}</div>
      </div>`;
  }

  // text fallback
  return `
    <div class="section">
      <h2>${escapeHtml(section.title)}</h2>
      <pre>${escapeHtml(section.body)}</pre>
    </div>`;
}

export function createRichReportPanel(
  title: string,
  subtitle: string,
  cards: ReportCard[],
  sections: ReportSection[],
): vscode.WebviewPanel {
  const panel = vscode.window.createWebviewPanel(
    'callflowRichReport',
    title,
    vscode.ViewColumn.Two,
    { enableScripts: false },
  );

  const cardHtml = cards
    .map(
      (card) => `
      <div class="card ${escapeHtml(card.kind ?? '')}">
        <div class="card-label">${escapeHtml(card.label)}</div>
        <div class="card-value">${escapeHtml(card.value)}</div>
        ${card.detail ? `<div class="card-detail">${escapeHtml(card.detail)}</div>` : ''}
      </div>`,
    )
    .join('');

  const sectionHtml = sections.map(renderSection).join('');

  panel.webview.html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  ${CSP}
  <title>${escapeHtml(title)}</title>
  <style>
    :root { color-scheme: dark; }
    body {
      margin: 0; padding: 0;
      font-family: var(--vscode-font-family);
      background:
        radial-gradient(circle at top left, rgba(59, 130, 246, 0.16), transparent 30%),
        radial-gradient(circle at top right, rgba(168, 85, 247, 0.14), transparent 28%),
        var(--vscode-editor-background);
      color: var(--vscode-editor-foreground);
    }
    .container { max-width: 1180px; margin: 0 auto; padding: 28px; }
    .hero {
      background: linear-gradient(135deg, rgba(15, 23, 42, 0.92), rgba(30, 41, 59, 0.92));
      border: 1px solid rgba(148, 163, 184, 0.18);
      border-radius: 20px; padding: 24px 28px; margin-bottom: 24px;
      box-shadow: 0 24px 60px rgba(0, 0, 0, 0.24);
    }
    .hero h1 { margin: 0 0 8px 0; font-size: 30px; letter-spacing: -0.02em; }
    .hero p { margin: 0; color: var(--vscode-descriptionForeground); font-size: 14px; }
    .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 24px; }
    .card {
      background: rgba(15, 23, 42, 0.92);
      border: 1px solid rgba(148, 163, 184, 0.14);
      border-radius: 16px; padding: 18px;
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.18);
    }
    .card-label { font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; margin-bottom: 8px; }
    .card-value { font-size: 28px; font-weight: 700; color: #e2e8f0; word-break: break-word; }
    .card-detail { margin-top: 8px; font-size: 13px; color: #cbd5e1; }
    .section {
      background: rgba(15, 23, 42, 0.88);
      border: 1px solid rgba(148, 163, 184, 0.14);
      border-radius: 18px; padding: 20px 22px; margin-bottom: 20px;
    }
    .section h2 { margin: 0 0 16px 0; font-size: 18px; }
    ul { margin: 0; padding-left: 20px; color: #dbeafe; }
    li { margin-bottom: 8px; }
    table { width: 100%; border-collapse: collapse; }
    th, td { text-align: left; padding: 12px 10px; border-bottom: 1px solid rgba(148, 163, 184, 0.14); vertical-align: top; }
    th { color: #93c5fd; font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; }
    pre { white-space: pre-wrap; word-break: break-word; background: rgba(2, 6, 23, 0.82); padding: 16px; border-radius: 12px; border: 1px solid rgba(148, 163, 184, 0.14); }
    .kv-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
    .kv-row { background: rgba(2, 6, 23, 0.55); border: 1px solid rgba(148, 163, 184, 0.12); border-radius: 12px; padding: 14px; }
    .kv-key { font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; margin-bottom: 6px; }
    .kv-value { font-size: 14px; color: #e2e8f0; word-break: break-word; }
  </style>
</head>
<body>
  <div class="container">
    <div class="hero">
      <h1>${escapeHtml(title)}</h1>
      <p>${escapeHtml(subtitle)}</p>
    </div>
    <div class="cards">${cardHtml}</div>
    ${sectionHtml}
  </div>
</body>
</html>`;

  return panel;
}
