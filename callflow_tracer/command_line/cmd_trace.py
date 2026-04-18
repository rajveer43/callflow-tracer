"""CLI subcommands: trace, flamegraph, profile, memory-leak."""

import json
import sys
import traceback
from pathlib import Path

from ._utils import execute_script, open_browser
from ..core.tracer import trace_scope
from ..visualization.exporter import export_html, export_json, export_html_3d
from ..visualization.flamegraph import generate_flamegraph
from ..performance.memory_leak_detector import MemoryLeakDetector, get_top_memory_consumers
from ..performance.profiling import get_memory_usage
from ..analysis.debug_summary import format_debug_summary, summarize_graph


# ── Parser registration ────────────────────────────────────────────────────────

def add_trace_parser(subparsers) -> None:
    p = subparsers.add_parser("trace", help="Trace function calls in a Python script")
    p.add_argument("script", help="Python script to trace")
    p.add_argument("script_args", nargs="*", help="Arguments to pass to the script")
    p.add_argument("-o", "--output", default="callflow_trace.html", help="Output file path")
    p.add_argument("--format", choices=["html", "json", "both"], default="html")
    p.add_argument("--3d", dest="three_d", action="store_true", help="3D visualization")
    p.add_argument("--title", help="Title for the visualization")
    p.add_argument("--include-args", action="store_true", help="Include function arguments")
    p.add_argument("--sampling-rate", type=float, default=1.0, help="Sampling rate (0.0-1.0)")
    p.add_argument("--include-module", action="append", dest="include_modules",
                   help="Only include module prefixes (repeatable)")
    p.add_argument("--exclude-module", action="append", dest="exclude_modules",
                   help="Exclude module prefixes (repeatable)")
    p.add_argument("--min-duration-ms", type=float, default=0.0,
                   help="Skip calls faster than this threshold")
    p.add_argument("--no-browser", action="store_true", help="Do not open browser")


def add_flamegraph_parser(subparsers) -> None:
    p = subparsers.add_parser("flamegraph", help="Generate flamegraph from traced script")
    p.add_argument("script", help="Python script to trace")
    p.add_argument("script_args", nargs="*", help="Arguments to pass to the script")
    p.add_argument("-o", "--output", default="flamegraph.html", help="Output HTML file path")
    p.add_argument("--title", help="Title for the flamegraph")
    p.add_argument("--min-time", type=float, default=0.0, help="Minimum time threshold (ms)")
    p.add_argument("--no-browser", action="store_true", help="Do not open browser")


def add_profile_parser(subparsers) -> None:
    p = subparsers.add_parser("profile", help="Profile script performance")
    p.add_argument("script", help="Python script to profile")
    p.add_argument("script_args", nargs="*", help="Arguments to pass to the script")
    p.add_argument("-o", "--output", default="profile.html", help="Output file path")
    p.add_argument("--format", choices=["html", "json", "text"], default="html")
    p.add_argument("--memory", action="store_true", help="Include memory profiling")
    p.add_argument("--cpu", action="store_true", help="Include CPU profiling")
    p.add_argument("--no-browser", action="store_true", help="Do not open browser")


def add_memory_leak_parser(subparsers) -> None:
    p = subparsers.add_parser("memory-leak", help="Detect memory leaks in a script")
    p.add_argument("script", help="Python script to analyze")
    p.add_argument("script_args", nargs="*", help="Arguments to pass to the script")
    p.add_argument("-o", "--output", default="memory_leak_report.html", help="Output file")
    p.add_argument("--threshold", type=float, default=5.0, help="Memory growth threshold (MB)")
    p.add_argument("--interval", type=float, default=0.1, help="Sampling interval (seconds)")
    p.add_argument("--top", type=int, default=10, help="Top memory consumers to show")
    p.add_argument("--no-browser", action="store_true", help="Do not open browser")


# ── Handlers ──────────────────────────────────────────────────────────────────

def handle_trace(args) -> int:
    print(f"Tracing script: {args.script}")
    try:
        title = args.title or f"Call Flow: {Path(args.script).name}"

        with trace_scope(
            None,
            include_args=args.include_args,
            sampling_rate=args.sampling_rate,
            include_modules=args.include_modules,
            exclude_modules=args.exclude_modules,
            min_duration_ms=args.min_duration_ms,
        ) as graph:
            execute_script(args.script, args.script_args)

        if args.format in ["html", "both"]:
            html_path = (
                args.output if args.format == "html"
                else args.output.replace(".json", ".html")
            )
            if args.three_d:
                export_html_3d(graph, html_path, title=title)
                print(f"3D visualization saved to: {html_path}")
            else:
                export_html(graph, html_path, title=title)
                print(f"HTML visualization saved to: {html_path}")
            if not args.no_browser:
                open_browser(html_path)

        if args.format in ["json", "both"]:
            json_path = (
                args.output if args.format == "json"
                else args.output.replace(".html", ".json")
            )
            export_json(graph, json_path)
            print(f"JSON trace saved to: {json_path}")

        print(f"\nTrace Summary:")
        print(f"  Total nodes: {len(graph.nodes)}")
        print(f"  Total edges: {len(graph.edges)}")
        print(f"  Total calls: {sum(n.call_count for n in graph.nodes.values())}")

        debug_report = summarize_graph(graph, top_n=5)
        print(f"\n{format_debug_summary(debug_report, top_n=5)}")
        return 0

    except FileNotFoundError:
        print(f"Error: Script not found: {args.script}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error executing script: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1


def handle_flamegraph(args) -> int:
    print(f"Generating flamegraph for: {args.script}")
    try:
        with trace_scope(None) as graph:
            execute_script(args.script, args.script_args)

        title = args.title or f"Flamegraph: {Path(args.script).name}"
        flamegraph_html = generate_flamegraph(graph, title=title, min_time_ms=args.min_time)

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(flamegraph_html)

        print(f"Flamegraph saved to: {args.output}")
        if not args.no_browser:
            open_browser(args.output)
        return 0

    except Exception as e:
        print(f"Error generating flamegraph: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1


def handle_profile(args) -> int:
    print(f"Profiling script: {args.script}")
    try:
        import cProfile
        import pstats
        from io import StringIO

        profiler = cProfile.Profile()
        with trace_scope(None) as graph:
            profiler.enable()
            execute_script(args.script, args.script_args)
            profiler.disable()

        stream = StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.sort_stats("cumulative")
        stats.print_stats(50)
        profile_text = stream.getvalue()
        memory_stats = get_memory_usage() if args.memory else None

        if args.format == "html":
            export_html(
                graph, args.output,
                title=f"Profile: {Path(args.script).name}",
                profiling_stats={"cpu_profile": profile_text, "memory_stats": memory_stats},
            )
            print(f"Profile saved to: {args.output}")
            if not args.no_browser:
                open_browser(args.output)

        elif args.format == "json":
            profile_data = {
                "graph": {
                    "nodes": [n.to_dict() for n in graph.nodes.values()],
                    "edges": [e.to_dict() for e in graph.edges.values()],
                },
                "cpu_profile": profile_text,
                "memory_stats": memory_stats,
            }
            with open(args.output, "w") as f:
                json.dump(profile_data, f, indent=2)
            print(f"Profile saved to: {args.output}")

        elif args.format == "text":
            with open(args.output, "w") as f:
                f.write("=== CPU PROFILE ===\n\n")
                f.write(profile_text)
                if memory_stats:
                    f.write("\n\n=== MEMORY STATS ===\n\n")
                    f.write(json.dumps(memory_stats, indent=2))
            print(f"Profile saved to: {args.output}")

        return 0

    except Exception as e:
        print(f"Error profiling script: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1


def handle_memory_leak(args) -> int:
    print(f"Detecting memory leaks in: {args.script}")
    try:
        detector = MemoryLeakDetector(
            threshold_mb=args.threshold, sample_interval=args.interval
        )
        detector.start()
        execute_script(args.script, args.script_args)
        report = detector.stop()
        top_consumers = get_top_memory_consumers(args.top)

        from ..performance.memory_leak_visualizer import generate_memory_leak_html
        html_content = generate_memory_leak_html(report, top_consumers, args.script)

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"\nMemory Leak Report:")
        print(f"  Peak memory: {report['peak_memory_mb']:.2f} MB")
        print(f"  Memory growth: {report['memory_growth_mb']:.2f} MB")
        print(f"  Potential leaks: {len(report.get('potential_leaks', []))}")
        print(f"\nReport saved to: {args.output}")

        if not args.no_browser:
            open_browser(args.output)
        return 0

    except Exception as e:
        print(f"Error detecting memory leaks: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1
