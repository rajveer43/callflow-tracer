"""Data models for benchmark mode."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class BenchmarkRunResult:
    """Single benchmark run result."""

    label: str
    wall_time_s: float
    memory_mb: float
    return_code: int
    stdout: str = ""
    stderr: str = ""
    trace_file: Optional[str] = None
    trace_summary: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BenchmarkSummary:
    """Aggregated benchmark summary."""

    runs: int
    baseline_avg_time_s: float
    traced_avg_time_s: float
    overhead_s: float
    overhead_pct: float
    baseline_avg_memory_mb: float
    traced_avg_memory_mb: float
    memory_delta_mb: float
    recommended_sampling_rate: float
    total_traced_calls: int = 0
    total_traced_nodes: int = 0
    total_traced_edges: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BenchmarkReport:
    """Full benchmark report."""

    script: str
    script_args: List[str]
    summary: BenchmarkSummary
    baseline_runs: List[BenchmarkRunResult] = field(default_factory=list)
    traced_runs: List[BenchmarkRunResult] = field(default_factory=list)
    top_functions: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    trace_summary: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "script": self.script,
            "script_args": self.script_args,
            "summary": self.summary.to_dict(),
            "baseline_runs": [run.to_dict() for run in self.baseline_runs],
            "traced_runs": [run.to_dict() for run in self.traced_runs],
            "top_functions": self.top_functions,
            "recommendations": self.recommendations,
            "trace_summary": self.trace_summary,
        }
