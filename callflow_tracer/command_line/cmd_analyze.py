"""CLI subcommands: compare, explain, benchmark, info, summary."""

import json
import sys
import traceback

from ._utils import load_graph_from_json, open_browser
from ..visualization.comparison import compare_graphs, export_comparison_html
from ..analysis.debug_summary import format_debug_summary, summarize_graph
from ..analysis.regression_explainer import explain_regression, format_regression_report
from ..benchmark import (
    benchmark_report_to_dict,
    export_benchmark_html,
    format_benchmark_report,
    run_benchmark,
)


# ── Parser registration ────────────────────────────────────────────────────────

def add_compare_parser(subparsers) -> None:
    p = subparsers.add_parser("compare", help="Compare two trace files")
    p.add_argument("file1", help="First trace file (JSON)")
    p.add_argument("file2", help="Second trace file (JSON)")
    p.add_argument("-o", "--output", default="comparison.html", help="Output HTML file")
    p.add_argument("--label1", default="Trace 1", help="Label for first trace")
    p.add_argument("--label2", default="Trace 2", help="Label for second trace")
    p.add_argument("--no-browser", action="store_true", help="Do not open browser")


def add_explain_parser(subparsers) -> None:
    p = subparsers.add_parser(
        "explain",
        help="Explain what changed between two traces and highlight regressions",
    )
    p.add_argument("before", help="Baseline trace file (JSON)")
    p.add_argument("after", help="New trace file (JSON)")
    p.add_argument("-o", "--output", help="Optional file path for the report")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument("--top", type=int, default=5, help="Number of items to include")
    p.add_argument("--label1", default="Before", help="Label for baseline trace")
    p.add_argument("--label2", default="After", help="Label for new trace")


def add_benchmark_parser(subparsers) -> None:
    p = subparsers.add_parser(
        "benchmark",
        help="Measure tracing overhead and produce benchmark recommendations",
    )
    p.add_argument("script", help="Python script to benchmark")
    p.add_argument("script_args", nargs="*", help="Arguments to pass to the script")
    p.add_argument("--runs", type=int, default=3, help="Number of runs to average")
    p.add_argument("--sampling-rate", type=float, default=1.0, help="Tracing sampling rate")
    p.add_argument("--include-module", action="append", dest="include_modules",
                   help="Only include module prefixes (repeatable)")
    p.add_argument("--exclude-module", action="append", dest="exclude_modules",
                   help="Exclude module prefixes (repeatable)")
    p.add_argument("--min-duration-ms", type=float, default=0.0,
                   help="Skip calls faster than this threshold")
    p.add_argument("--include-args", action="store_true", help="Include function arguments")
    p.add_argument("-o", "--output", help="Output file path for text/json/html reports")
    p.add_argument("--format", choices=["text", "json", "html"], default="text")
    p.add_argument("--no-browser", action="store_true", help="Do not open browser")


def add_info_parser(subparsers) -> None:
    p = subparsers.add_parser("info", help="Show information about a trace file")
    p.add_argument("file", help="Trace file to analyze (JSON)")
    p.add_argument("--detailed", action="store_true", help="Show detailed statistics")


def add_summary_parser(subparsers) -> None:
    p = subparsers.add_parser(
        "summary", help="Generate an actionable debug summary from trace JSON"
    )
    p.add_argument("file", help="Trace file to analyze (JSON)")
    p.add_argument("-o", "--output", help="Optional output file for the summary")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument("--top", type=int, default=5, help="Number of items to show")


# ── Handlers ──────────────────────────────────────────────────────────────────

def handle_compare(args) -> int:
    print(f"Comparing traces: {args.file1} vs {args.file2}")
    try:
        graph1 = load_graph_from_json(args.file1)
        graph2 = load_graph_from_json(args.file2)

        comparison = compare_graphs(graph1, graph2, args.label1, args.label2)
        export_comparison_html(
            graph1, graph2, args.output, label1=args.label1, label2=args.label2
        )

        print(f"\nComparison Summary:")
        print(f"  {args.label1}: {len(graph1.nodes)} nodes, {len(graph1.edges)} edges")
        print(f"  {args.label2}: {len(graph2.nodes)} nodes, {len(graph2.edges)} edges")
        print(f"  New nodes: {len(comparison.get('added_nodes', []))}")
        print(f"  Removed nodes: {len(comparison.get('removed_nodes', []))}")
        print(f"\nComparison saved to: {args.output}")

        if not args.no_browser:
            open_browser(args.output)
        return 0

    except Exception as e:
        print(f"Error comparing traces: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1


def handle_explain(args) -> int:
    print(f"Explaining trace change: {args.before} -> {args.after}")
    try:
        before_graph = load_graph_from_json(args.before)
        after_graph = load_graph_from_json(args.after)

        report = explain_regression(
            before_graph, after_graph,
            label1=args.label1, label2=args.label2, top_n=args.top,
        )

        output = json.dumps(report, indent=2) if args.format == "json" \
            else format_regression_report(report, top_n=args.top)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Regression report saved to: {args.output}")
        else:
            print("\n" + output)
        return 0

    except Exception as e:
        print(f"Error explaining traces: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1


def handle_benchmark(args) -> int:
    print(f"Running benchmark: {args.script}")
    try:
        report = run_benchmark(
            args.script,
            script_args=args.script_args,
            runs=args.runs,
            sampling_rate=args.sampling_rate,
            include_modules=args.include_modules,
            exclude_modules=args.exclude_modules,
            min_duration_ms=args.min_duration_ms,
            include_args=args.include_args,
        )

        if args.format == "html":
            output_path = args.output or "benchmark_report.html"
            export_benchmark_html(report, output_path)
            print(f"Benchmark report saved to: {output_path}")
            if not args.no_browser:
                open_browser(output_path)
            return 0

        output = (
            json.dumps(benchmark_report_to_dict(report), indent=2)
            if args.format == "json"
            else format_benchmark_report(report)
        )

        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Benchmark report saved to: {args.output}")
        else:
            print("\n" + output)
        return 0

    except Exception as e:
        print(f"Error running benchmark: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1


def handle_info(args) -> int:
    print(f"Analyzing trace file: {args.file}")
    try:
        with open(args.file, "r") as f:
            trace_data = json.load(f)

        nodes = trace_data.get("nodes", [])
        edges = trace_data.get("edges", [])
        total_calls = sum(n["call_count"] for n in nodes)
        total_time = sum(n["total_time"] for n in nodes)
        sorted_nodes = sorted(nodes, key=lambda x: x["total_time"], reverse=True)

        print(f"\n=== Trace Information ===")
        print(f"File: {args.file}")
        print(f"Total nodes: {len(nodes)}")
        print(f"Total edges: {len(edges)}")
        print(f"Total function calls: {total_calls}")
        print(f"Total execution time: {total_time:.6f}s")

        if args.detailed:
            print(f"\n=== Top 10 Functions by Time ===")
            for i, node in enumerate(sorted_nodes[:10], 1):
                print(f"{i}. {node['full_name']}")
                print(f"   Calls: {node['call_count']}, Time: {node['total_time']:.6f}s")

            modules: dict = {}
            for node in nodes:
                mod = node.get("module", "__main__")
                if mod not in modules:
                    modules[mod] = {"count": 0, "time": 0.0}
                modules[mod]["count"] += 1
                modules[mod]["time"] += node["total_time"]

            print(f"\n=== Module Statistics ===")
            for mod, stats in sorted(modules.items(), key=lambda x: x[1]["time"], reverse=True):
                print(f"{mod}: {stats['count']} functions, {stats['time']:.6f}s")

        return 0

    except Exception as e:
        print(f"Error analyzing trace: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1


def handle_summary(args) -> int:
    print(f"Generating summary for: {args.file}")
    try:
        graph = load_graph_from_json(args.file)
        report = summarize_graph(graph, top_n=args.top)

        output = json.dumps(report, indent=2) if args.format == "json" \
            else format_debug_summary(report, top_n=args.top)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Summary saved to: {args.output}")
        else:
            print("\n" + output)
        return 0

    except Exception as e:
        print(f"Error generating summary: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1
