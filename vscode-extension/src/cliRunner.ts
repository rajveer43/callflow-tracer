import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';
import { execFile } from 'child_process';
import { promisify } from 'util';
import * as vscode from 'vscode';

const execFileAsync = promisify(execFile);

export async function runCallflowCli(
  args: string[],
  cwd: string | null = null,
): Promise<{ stdout: string; stderr: string }> {
  const config = vscode.workspace.getConfiguration('callflowTracer');
  const pythonPath = config.get<string>('pythonPath', 'python3');
  const workspaceRoot =
    cwd ?? vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

  return execFileAsync(pythonPath, ['-m', 'callflow_tracer', ...args], {
    cwd: workspaceRoot ?? undefined,
    maxBuffer: 1024 * 1024 * 10,
  });
}

export async function runJsonCliReport<T = Record<string, unknown>>(
  args: string[],
  prefix = 'callflow-report-',
): Promise<T> {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), prefix));
  const outputPath = path.join(tempDir, 'report.json');

  try {
    await runCallflowCli([...args, '--format', 'json', '-o', outputPath]);
    if (!fs.existsSync(outputPath)) {
      throw new Error('Report JSON was not generated');
    }
    return JSON.parse(fs.readFileSync(outputPath, 'utf8')) as T;
  } finally {
    try {
      fs.rmSync(tempDir, { recursive: true, force: true });
    } catch {
      // ignore cleanup errors
    }
  }
}
