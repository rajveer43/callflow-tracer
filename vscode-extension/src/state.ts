import type { TraceData } from './types';

let currentTraceData: TraceData | null = null;
let currentTraceFilePath: string | null = null;

export function setCurrentTraceData(data: TraceData): void {
  currentTraceData = data;
}

export function getCurrentTraceData(): TraceData | null {
  return currentTraceData;
}

export function setCurrentTraceFilePath(filePath: string): void {
  currentTraceFilePath = filePath;
}

export function getCurrentTraceFilePath(): string | null {
  return currentTraceFilePath;
}

export function clearTraceState(): void {
  currentTraceData = null;
  currentTraceFilePath = null;
}
