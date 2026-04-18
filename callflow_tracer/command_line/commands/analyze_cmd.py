"""Concrete commands: compare, explain, benchmark, info, summary."""

from __future__ import annotations

import json
import traceback as tb
from argparse import ArgumentParser

from .._utils import load_graph_from_json, open_browser
from ..interfaces.command import BaseCommand, CommandContext, CommandResult


class CompareCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "compare"

    @property
    def help(self) -> str:
        return "Compare two trace files side-by-side"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("file1", help="First trace file (JSON)")
        parser.add_argument("file2", help="Second trace file (JSON)")
        parser.add_argument("-o", "--output", default="comparison.html")
        parser.add_argument("--label1", default="Trace 1")
        parser.add_argument("--label2", default="Trace 2")
        parser.add_argument("--no-browser", action="store_true")

    def execute(self, ctx: CommandContext) -> CommandResult:
        from ...visualization.comparison import compare_graphs, export_comparison_html

        args = ctx.args
        try:
            graph1 = load_graph_from_json(args.file1)
            graph2 = load_graph_from_json(args.file2)
            comparison = compare_graphs(graph1, graph2, args.label1, args.label2)
            export_comparison_html(graph1, graph2, args.output,
                                   label1=args.label1, label2=args.label2)

            print(f"\nComparison Summary:")
            print(f"  {args.label1}: {len(graph1.nodes)} nodes")
            print(f"  {args.label2}: {len(graph2.nodes)} nodes")
            print(f"  New nodes: {len(comparison.get('added_nodes', []))}")
            print(f"  Removed: {len(comparison.get('removed_nodes', []))}")
            print(f"\nSaved to: {args.output}")
            if not args.no_browser:
                open_browser(args.output)

            return CommandResult.success(data={"comparison": comparison})
        except Exception as e:
            tb.print_exc()
            return CommandResult.failure(str(e))


class ExplainCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "explain"

    @property
    def help(self) -> str:
        return "Explain regressions between two traces"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("before", help="Baseline trace file (JSON)")
        parser.add_argument("after", help="New trace file (JSON)")
        parser.add_argument("-o", "--output")
        parser.add_argument("--format", choices=["text", "json"], default="text")
        parser.add_argument("--top", type=int, default=5)
        parser.add_argument("--label1", default="Before")
        parser.add_argument("--label2", default="After")

    def execute(self, ctx: CommandContext) -> CommandResult:
        from ...analysis.regression_explainer import explain_regression, format_regression_report

        args = ctx.args
        try:
            before = load_graph_from_json(args.before)
            after = load_graph_from_json(args.after)
            report = explain_regression(before, after,
                                        label1=args.label1, label2=args.label2,
                                        top_n=args.top)
            output = (json.dumps(report, indent=2) if args.format == "json"
                      else format_regression_report(report, top_n=args.top))

            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(output)
                print(f"Report saved to: {args.output}")
            else:
                print("\n" + output)

            return CommandResult.success(data={"report": report})
        except Exception as e:
            tb.print_exc()
            return CommandResult.failure(str(e))


class BenchmarkCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "benchmark"

    @property
    def help(self) -> str:
        return "Measure tracing overhead and produce benchmark recommendations"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("script")
        parser.add_argument("script_args", nargs="*")
        parser.add_argument("--runs", type=int, default=3)
        parser.add_argument("--sampling-rate", type=float, default=1.0)
        parser.add_argument("--include-module", action="append", dest="include_modules")
        parser.add_argument("--exclude-module", action="append", dest="exclude_modules")
        parser.add_argument("--min-duration-ms", type=float, default=0.0)
        parser.add_argument("--include-args", action="store_true")
        parser.add_argument("-o", "--output")
        parser.add_argument("--format", choices=["text", "json", "html"], default="text")
        parser.add_argument("--no-browser", action="store_true")

    def execute(self, ctx: CommandContext) -> CommandResult:
        from ...benchmark import (
            run_benchmark, benchmark_report_to_dict,
            export_benchmark_html, format_benchmark_report,
        )

        args = ctx.args
        try:
            report = run_benchmark(
                args.script, script_args=args.script_args, runs=args.runs,
                sampling_rate=args.sampling_rate,
                include_modules=args.include_modules,
                exclude_modules=args.exclude_modules,
                min_duration_ms=args.min_duration_ms,
                include_args=args.include_args,
            )
            if args.format == "html":
                out = args.output or "benchmark_report.html"
                export_benchmark_html(report, out)
                print(f"Benchmark saved to: {out}")
                if not args.no_browser:
                    open_browser(out)
            else:
                text = (json.dumps(benchmark_report_to_dict(report), indent=2)
                        if args.format == "json" else format_benchmark_report(report))
                if args.output:
                    with open(args.output, "w") as f:
                        f.write(text)
                    print(f"Benchmark saved to: {args.output}")
                else:
                    print("\n" + text)

            return CommandResult.success(data={"report": benchmark_report_to_dict(report)})
        except Exception as e:
            tb.print_exc()
            return CommandResult.failure(str(e))


class InfoCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "info"

    @property
    def help(self) -> str:
        return "Show information about a trace file"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("file", help="Trace file (JSON)")
        parser.add_argument("--detailed", action="store_true")

    def execute(self, ctx: CommandContext) -> CommandResult:
        args = ctx.args
        try:
            with open(args.file, "r") as f:
                trace_data = json.load(f)

            nodes = trace_data.get("nodes", [])
            edges = trace_data.get("edges", [])
            total_time = sum(n["total_time"] for n in nodes)
            total_calls = sum(n["call_count"] for n in nodes)

            print(f"\n=== Trace Information ===")
            print(f"File: {args.file}")
            print(f"Nodes: {len(nodes)}, Edges: {len(edges)}")
            print(f"Total calls: {total_calls}, Total time: {total_time:.6f}s")

            if args.detailed:
                sorted_nodes = sorted(nodes, key=lambda x: x["total_time"], reverse=True)
                print(f"\n=== Top 10 by Time ===")
                for i, n in enumerate(sorted_nodes[:10], 1):
                    print(f"{i}. {n['full_name']}  calls={n['call_count']}  time={n['total_time']:.6f}s")

            return CommandResult.success(data={
                "node_count": len(nodes),
                "edge_count": len(edges),
                "total_calls": total_calls,
                "total_time": total_time,
            })
        except Exception as e:
            tb.print_exc()
            return CommandResult.failure(str(e))


class SummaryCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "summary"

    @property
    def help(self) -> str:
        return "Generate an actionable debug summary from a trace file"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("file", help="Trace file (JSON)")
        parser.add_argument("-o", "--output")
        parser.add_argument("--format", choices=["text", "json"], default="text")
        parser.add_argument("--top", type=int, default=5)

    def execute(self, ctx: CommandContext) -> CommandResult:
        from ...analysis.debug_summary import format_debug_summary, summarize_graph

        args = ctx.args
        try:
            graph = load_graph_from_json(args.file)
            report = summarize_graph(graph, top_n=args.top)
            text = (json.dumps(report, indent=2) if args.format == "json"
                    else format_debug_summary(report, top_n=args.top))

            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"Summary saved to: {args.output}")
            else:
                print("\n" + text)

            return CommandResult.success(data={"report": report})
        except Exception as e:
            tb.print_exc()
            return CommandResult.failure(str(e))
