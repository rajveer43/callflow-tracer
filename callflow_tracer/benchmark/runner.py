"""Subprocess benchmark runner."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Optional

from ..analysis.debug_summary import summarize_trace_data
from .models import BenchmarkReport, BenchmarkRunResult, BenchmarkSummary
from .recommendations import build_benchmark_recommendations, recommend_sampling_rate


def run_benchmark(
    script: str,
    script_args: Optional[List[str]] = None,
    runs: int = 3,
    sampling_rate: float = 1.0,
    include_modules: Optional[List[str]] = None,
    exclude_modules: Optional[List[str]] = None,
    min_duration_ms: float = 0.0,
    include_args: bool = False,
) -> BenchmarkReport:
    """Run baseline and traced benchmarks and return a report."""
    script_args = script_args or []

    baseline_runs = [
        _run_once(
            script,
            script_args,
            mode="baseline",
            include_args=include_args,
        )
        for _ in range(runs)
    ]
    _ensure_success(baseline_runs)

    traced_runs = [
        _run_once(
            script,
            script_args,
            mode="traced",
            include_args=include_args,
            sampling_rate=sampling_rate,
            include_modules=include_modules,
            exclude_modules=exclude_modules,
            min_duration_ms=min_duration_ms,
        )
        for _ in range(runs)
    ]
    _ensure_success(traced_runs)

    trace_summary = traced_runs[-1].trace_summary if traced_runs else None
    top_functions = trace_summary.get("slow_functions", []) if trace_summary else []
    total_nodes = (
        trace_summary.get("summary", {}).get("total_nodes", 0) if trace_summary else 0
    )
    total_calls = (
        trace_summary.get("summary", {}).get("total_calls", 0) if trace_summary else 0
    )
    total_edges = (
        trace_summary.get("summary", {}).get("total_edges", 0) if trace_summary else 0
    )

    baseline_avg_time = mean(run.wall_time_s for run in baseline_runs)
    traced_avg_time = mean(run.wall_time_s for run in traced_runs)
    baseline_avg_memory = mean(run.memory_mb for run in baseline_runs)
    traced_avg_memory = mean(run.memory_mb for run in traced_runs)

    overhead = traced_avg_time - baseline_avg_time
    overhead_pct = (
        (overhead / baseline_avg_time * 100.0) if baseline_avg_time > 0 else 0.0
    )
    memory_delta = traced_avg_memory - baseline_avg_memory

    summary = BenchmarkSummary(
        runs=runs,
        baseline_avg_time_s=baseline_avg_time,
        traced_avg_time_s=traced_avg_time,
        overhead_s=overhead,
        overhead_pct=overhead_pct,
        baseline_avg_memory_mb=baseline_avg_memory,
        traced_avg_memory_mb=traced_avg_memory,
        memory_delta_mb=memory_delta,
        recommended_sampling_rate=recommend_sampling_rate(
            overhead_pct=overhead_pct, total_nodes=total_nodes
        ),
        total_traced_calls=total_calls,
        total_traced_nodes=total_nodes,
        total_traced_edges=total_edges,
    )

    recommendations = build_benchmark_recommendations(
        overhead_pct=overhead_pct,
        memory_delta_mb=memory_delta,
        total_nodes=total_nodes,
        trace_summary=trace_summary,
    )

    return BenchmarkReport(
        script=script,
        script_args=script_args,
        summary=summary,
        baseline_runs=baseline_runs,
        traced_runs=traced_runs,
        top_functions=top_functions,
        recommendations=recommendations,
        trace_summary=trace_summary,
    )


def _ensure_success(runs: Iterable[BenchmarkRunResult]) -> None:
    """Raise a descriptive error if any benchmark run failed."""
    for run in runs:
        if run.return_code != 0:
            raise RuntimeError(
                f"Benchmark run failed for {run.label} with exit code {run.return_code}\n"
                f"STDERR:\n{run.stderr}"
            )


def _run_once(
    script: str,
    script_args: List[str],
    mode: str,
    include_args: bool = False,
    sampling_rate: float = 1.0,
    include_modules: Optional[List[str]] = None,
    exclude_modules: Optional[List[str]] = None,
    min_duration_ms: float = 0.0,
) -> BenchmarkRunResult:
    """Run a single baseline or traced benchmark."""
    with tempfile.TemporaryDirectory(prefix="callflow-benchmark-") as tmpdir:
        tmpdir_path = Path(tmpdir)
        runner_path = tmpdir_path / "benchmark_runner.py"
        result_path = tmpdir_path / "result.json"
        trace_path = tmpdir_path / "trace.json"
        runner_path.write_text(_build_runner_script(), encoding="utf-8")

        cmd = [
            sys.executable,
            str(runner_path),
            "--mode",
            mode,
            "--script",
            script,
            "--result-file",
            str(result_path),
        ]

        if mode == "traced":
            cmd.extend(["--trace-file", str(trace_path)])
            cmd.extend(["--sampling-rate", str(sampling_rate)])
            cmd.extend(["--min-duration-ms", str(min_duration_ms)])
            if include_args:
                cmd.append("--include-args")
            for module in include_modules or []:
                cmd.extend(["--include-module", module])
            for module in exclude_modules or []:
                cmd.extend(["--exclude-module", module])

        if script_args:
            cmd.append("--")
            cmd.extend(script_args)

        result = subprocess.run(cmd, capture_output=True, text=True)

        if not result_path.exists():
            raise RuntimeError(
                "Benchmark runner did not write a result file.\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

        payload = json.loads(result_path.read_text(encoding="utf-8"))
        trace_summary = None
        trace_file = payload.get("trace_file")

        if trace_file and Path(trace_file).exists():
            with open(trace_file, "r", encoding="utf-8") as f:
                trace_data = json.load(f)
            trace_summary = summarize_trace_data(trace_data)
            trace_summary = _clean_trace_summary(trace_summary)

        return BenchmarkRunResult(
            label=mode,
            wall_time_s=float(payload.get("wall_time_s", 0.0)),
            memory_mb=float(payload.get("memory_mb", 0.0)),
            return_code=int(payload.get("return_code", result.returncode)),
            stdout=result.stdout,
            stderr=result.stderr,
            trace_file=trace_file,
            trace_summary=trace_summary,
        )


def _clean_trace_summary(trace_summary: Dict[str, Any]) -> Dict[str, Any]:
    """Remove benchmark-wrapper noise from the hotspot list."""
    if not trace_summary:
        return trace_summary

    slow_functions = trace_summary.get("slow_functions", [])
    filtered = [
        item
        for item in slow_functions
        if not _is_noise_function(item.get("full_name", ""), item.get("module", ""))
    ]

    if filtered:
        trace_summary["slow_functions"] = filtered
        trace_summary["suspect_function"] = filtered[0]
    else:
        trace_summary["slow_functions"] = slow_functions

    return trace_summary


def _is_noise_function(full_name: str, module: str) -> bool:
    """Return True for helper/runtime functions we should hide from benchmark output."""
    noisy_prefixes = (
        "runpy.",
        "importlib.",
        "pkgutil.",
        "site.",
        "<frozen ",
    )
    noisy_modules = {"runpy", "importlib", "pkgutil", "site"}

    if full_name == "<module>" or full_name.endswith(".<module>"):
        return True
    if any(full_name.startswith(prefix) for prefix in noisy_prefixes):
        return True
    if module in noisy_modules:
        return True
    return False


def _build_runner_script() -> str:
    """Return the source for the helper script executed in subprocesses."""
    return textwrap.dedent(
        """
        from __future__ import annotations

        import argparse
        import json
        import os
        import runpy
        import sys
        import time
        import traceback
        from pathlib import Path

        try:
            import resource
        except ImportError:
            resource = None

        from callflow_tracer.core.tracer import trace_scope
        from callflow_tracer.visualization.exporter import export_json


        def _memory_mb() -> float:
            if resource is None:
                return 0.0
            usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            if sys.platform == "darwin":
                return usage / (1024 * 1024)
            return usage / 1024.0


        def main() -> int:
            parser = argparse.ArgumentParser()
            parser.add_argument("--mode", choices=["baseline", "traced"], required=True)
            parser.add_argument("--script", required=True)
            parser.add_argument("--result-file", required=True)
            parser.add_argument("--trace-file")
            parser.add_argument("--sampling-rate", type=float, default=1.0)
            parser.add_argument("--include-module", action="append", dest="include_modules")
            parser.add_argument("--exclude-module", action="append", dest="exclude_modules")
            parser.add_argument("--min-duration-ms", type=float, default=0.0)
            parser.add_argument("--include-args", action="store_true")
            parser.add_argument("script_args", nargs=argparse.REMAINDER)
            args = parser.parse_args()

            script_args = args.script_args
            if script_args[:1] == ["--"]:
                script_args = script_args[1:]

            result = {
                "wall_time_s": 0.0,
                "memory_mb": 0.0,
                "return_code": 0,
                "trace_file": args.trace_file,
                "stdout": "",
                "stderr": "",
            }

            original_argv = sys.argv[:]
            start = time.perf_counter()
            try:
                sys.argv = [args.script] + script_args
                if args.mode == "traced":
                    trace_kwargs = {
                        "include_args": args.include_args,
                        "sampling_rate": args.sampling_rate,
                        "include_modules": args.include_modules,
                        "exclude_modules": args.exclude_modules,
                        "min_duration_ms": args.min_duration_ms,
                    }
                    with trace_scope(None, **trace_kwargs) as graph:
                        runpy.run_path(args.script, run_name="__main__")
                    if args.trace_file:
                        export_json(graph, args.trace_file)
                else:
                    runpy.run_path(args.script, run_name="__main__")
            except SystemExit as exc:
                code = exc.code if isinstance(exc.code, int) else 0
                result["return_code"] = int(code or 0)
            except Exception:
                result["return_code"] = 1
                result["stderr"] = traceback.format_exc()
            finally:
                sys.argv = original_argv
                result["wall_time_s"] = time.perf_counter() - start
                result["memory_mb"] = _memory_mb()
                Path(args.result_file).write_text(json.dumps(result), encoding="utf-8")

            return result["return_code"]


        if __name__ == "__main__":
            raise SystemExit(main())
        """
    ).strip()
