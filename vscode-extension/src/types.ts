export interface TraceNode {
  name: string;
  full_name: string;
  module: string;
  call_count: number;
  total_time: number;
  avg_time: number;
}

export interface TraceEdge {
  caller: string;
  callee: string;
  call_count: number;
  total_time: number;
  avg_time: number;
}

export interface TraceMetadata {
  duration: number;
  total_calls: number;
  [key: string]: unknown;
}

export interface TraceData {
  nodes: TraceNode[];
  edges: TraceEdge[];
  metadata: TraceMetadata;
  [key: string]: unknown;
}

export interface ReportCard {
  label: string;
  value: string | number;
  detail?: string;
  kind?: string;
}

export interface ReportSectionList {
  type: 'list';
  title: string;
  items: string[];
}

export interface ReportSectionTable {
  type: 'table';
  title: string;
  headers: string[];
  rows: string[][];
}

export interface ReportSectionKeyValue {
  type: 'keyvalue';
  title: string;
  items: { key: string; value: string | number }[];
}

export interface ReportSectionText {
  type: 'text';
  title: string;
  body: string;
}

export type ReportSection =
  | ReportSectionList
  | ReportSectionTable
  | ReportSectionKeyValue
  | ReportSectionText;

export interface SummaryReport {
  summary?: {
    total_calls?: number;
    total_time?: number;
    recorded_calls?: number;
    total_nodes?: number;
    total_edges?: number;
    skipped_sampling?: number;
    skipped_filtering?: number;
    skipped_duration?: number;
    trace_options?: { sampling_rate?: number };
  };
  suspect_function?: { full_name: string };
  suspect_module?: { module: string };
  slow_functions?: Array<{
    full_name: string;
    call_count: number;
    total_time: number;
    avg_time: number;
    share_pct: number;
  }>;
  hot_modules?: Array<{
    module: string;
    call_count: number;
    total_time: number;
    functions: number;
    share_pct: number;
  }>;
  next_steps?: string[];
}

export interface ExplainReport {
  summary?: {
    time_change?: number;
    time_change_pct?: number;
    regressions?: number;
    improvements?: number;
    nodes_added?: number;
  };
  regression_driver?: { name: string };
  structural_driver?: { module: string };
  top_regressions?: Array<{
    name: string;
    time_diff: number;
    time_diff_pct: number;
    calls_before: number;
    calls_after: number;
  }>;
  module_deltas?: Array<{
    module: string;
    time_diff: number;
    time_diff_pct: number;
    calls_before: number;
    calls_after: number;
  }>;
  next_steps?: string[];
}

export interface BenchmarkReport {
  summary?: {
    runs?: number;
    baseline_avg_time_s?: number;
    traced_avg_time_s?: number;
    overhead_pct?: number;
    recommended_sampling_rate?: number;
    memory_delta_mb?: number;
    total_traced_calls?: number;
    total_traced_nodes?: number;
    total_traced_edges?: number;
    baseline_avg_memory_mb?: number;
    traced_avg_memory_mb?: number;
  };
  top_functions?: Array<{
    full_name: string;
    call_count: number;
    total_time: number;
    avg_time: number;
  }>;
  recommendations?: string[];
}

export interface AnomalyReport {
  report_generated: string;
  period_hours: number;
  total_alerts: number;
  severity_breakdown: {
    critical?: number;
    high?: number;
    medium?: number;
    low?: number;
  };
  top_anomalies: Array<{
    metric_name: string;
    description: string;
    severity: string;
    z_score: number;
    timestamp: string;
  }>;
}

export interface PluginList {
  analyzers: string[];
  exporters: Record<string, string[]>;
  ui_widgets: string[];
  plugin_info: Record<string, unknown>;
}

export type Spacing = 'compact' | 'normal' | 'relaxed' | 'wide';

export const SPACING_MAP: Record<Spacing, number> = {
  compact: 100,
  normal: 150,
  relaxed: 200,
  wide: 300,
};
