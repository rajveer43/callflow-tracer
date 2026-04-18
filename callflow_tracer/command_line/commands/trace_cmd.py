"""
Concrete commands: trace, flamegraph, profile, memory-leak.

Each command is a stateless object. All mutable state lives in CommandContext.
execute() never calls sys.exit() — it returns CommandResult.
The call graph is stored in result.data["graph"] so TracingMiddleware can
forward it to the agent runtime via TRACE_RECORDED events.
"""

from __future__ import annotations

import json
import sys
import traceback as tb
from argparse import ArgumentParser
from pathlib import Path

from .._utils import execute_script, open_browser
from ..interfaces.command import BaseCommand, CommandContext, CommandResult


class TraceCommand(BaseCommand):
    """Trace function calls in a Python script → HTML / JSON call graph."""

    @property
    def name(self) -> str:
        return "trace"

    @property
    def aliases(self) -> list[str]:
        return ["trc"]

    @property
    def help(self) -> str:
        return "Trace function calls in a Python script"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("script", help="Python script to trace")
        parser.add_argument("script_args", nargs="*", help="Arguments to pass to the script")
        parser.add_argument("-o", "--output", default="callflow_trace.html")
        parser.add_argument("--format", choices=["html", "json", "both"], default="html")
        parser.add_argument("--3d", dest="three_d", action="store_true")
        parser.add_argument("--title")
        parser.add_argument("--include-args", action="store_true")
        parser.add_argument("--sampling-rate", type=float, default=1.0)
        parser.add_argument("--include-module", action="append", dest="include_modules")
        parser.add_argument("--exclude-module", action="append", dest="exclude_modules")
        parser.add_argument("--min-duration-ms", type=float, default=0.0)
        parser.add_argument("--no-browser", action="store_true")

    def execute(self, ctx: CommandContext) -> CommandResult:
        from ...core.tracer import trace_scope
        from ...visualization.exporter import export_html, export_json, export_html_3d
        from ...analysis.debug_summary import format_debug_summary, summarize_graph

        args = ctx.args
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
                else:
                    export_html(graph, html_path, title=title)
                print(f"Visualization saved to: {html_path}")
                if not args.no_browser:
                    open_browser(html_path)

            if args.format in ["json", "both"]:
                json_path = (
                    args.output if args.format == "json"
                    else args.output.replace(".html", ".json")
                )
                export_json(graph, json_path)
                print(f"JSON trace saved to: {json_path}")

            graph_dict = graph.to_dict()
            summary = summarize_graph(graph, top_n=5)
            print(f"\nTrace Summary:")
            print(f"  Nodes: {len(graph.nodes)}, Edges: {len(graph.edges)}")
            print(f"  Total calls: {sum(n.call_count for n in graph.nodes.values())}")
            print(f"\n{format_debug_summary(summary, top_n=5)}")

            # Store graph in result.data so TracingMiddleware can forward it
            return CommandResult.success(data={"graph": graph_dict, "summary": summary})

        except FileNotFoundError:
            return CommandResult.failure(f"Script not found: {args.script}")
        except Exception as e:
            tb.print_exc()
            return CommandResult.failure(str(e))


class FlamegraphCommand(BaseCommand):
    """Generate a flamegraph HTML from a traced script."""

    @property
    def name(self) -> str:
        return "flamegraph"

    @property
    def help(self) -> str:
        return "Generate flamegraph from traced script"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("script", help="Python script to trace")
        parser.add_argument("script_args", nargs="*")
        parser.add_argument("-o", "--output", default="flamegraph.html")
        parser.add_argument("--title")
        parser.add_argument("--min-time", type=float, default=0.0)
        parser.add_argument("--no-browser", action="store_true")

    def execute(self, ctx: CommandContext) -> CommandResult:
        from ...core.tracer import trace_scope
        from ...visualization.flamegraph import generate_flamegraph

        args = ctx.args
        try:
            with trace_scope(None) as graph:
                execute_script(args.script, args.script_args)

            title = args.title or f"Flamegraph: {Path(args.script).name}"
            html = generate_flamegraph(graph, title=title, min_time_ms=args.min_time)

            with open(args.output, "w", encoding="utf-8") as f:
                f.write(html)

            print(f"Flamegraph saved to: {args.output}")
            if not args.no_browser:
                open_browser(args.output)

            return CommandResult.success(data={"graph": graph.to_dict()})

        except Exception as e:
            tb.print_exc()
            return CommandResult.failure(str(e))


class ProfileCommand(BaseCommand):
    """Profile a script with cProfile and optionally memory tracking."""

    @property
    def name(self) -> str:
        return "profile"

    @property
    def help(self) -> str:
        return "Profile script performance"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("script")
        parser.add_argument("script_args", nargs="*")
        parser.add_argument("-o", "--output", default="profile.html")
        parser.add_argument("--format", choices=["html", "json", "text"], default="html")
        parser.add_argument("--memory", action="store_true")
        parser.add_argument("--no-browser", action="store_true")

    def execute(self, ctx: CommandContext) -> CommandResult:
        import cProfile
        import pstats
        from io import StringIO
        from ...core.tracer import trace_scope
        from ...visualization.exporter import export_html
        from ...performance.profiling import get_memory_usage

        args = ctx.args
        try:
            profiler = cProfile.Profile()
            with trace_scope(None) as graph:
                profiler.enable()
                execute_script(args.script, args.script_args)
                profiler.disable()

            stream = StringIO()
            pstats.Stats(profiler, stream=stream).sort_stats("cumulative").print_stats(50)
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
                payload = {
                    "graph": {
                        "nodes": [n.to_dict() for n in graph.nodes.values()],
                        "edges": [e.to_dict() for e in graph.edges.values()],
                    },
                    "cpu_profile": profile_text,
                    "memory_stats": memory_stats,
                }
                with open(args.output, "w") as f:
                    json.dump(payload, f, indent=2)
                print(f"Profile saved to: {args.output}")
            elif args.format == "text":
                with open(args.output, "w") as f:
                    f.write("=== CPU PROFILE ===\n\n" + profile_text)
                    if memory_stats:
                        f.write("\n\n=== MEMORY STATS ===\n\n" + json.dumps(memory_stats, indent=2))
                print(f"Profile saved to: {args.output}")

            return CommandResult.success(data={"graph": graph.to_dict()})

        except Exception as e:
            tb.print_exc()
            return CommandResult.failure(str(e))


class MemoryLeakCommand(BaseCommand):
    """Detect memory leaks in a script."""

    @property
    def name(self) -> str:
        return "memory-leak"

    @property
    def help(self) -> str:
        return "Detect memory leaks in a script"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("script")
        parser.add_argument("script_args", nargs="*")
        parser.add_argument("-o", "--output", default="memory_leak_report.html")
        parser.add_argument("--threshold", type=float, default=5.0)
        parser.add_argument("--interval", type=float, default=0.1)
        parser.add_argument("--top", type=int, default=10)
        parser.add_argument("--no-browser", action="store_true")

    def execute(self, ctx: CommandContext) -> CommandResult:
        from ...performance.memory_leak_detector import MemoryLeakDetector, get_top_memory_consumers
        from ...performance.memory_leak_visualizer import generate_memory_leak_html

        args = ctx.args
        try:
            detector = MemoryLeakDetector(
                threshold_mb=args.threshold, sample_interval=args.interval
            )
            detector.start()
            execute_script(args.script, args.script_args)
            report = detector.stop()
            top_consumers = get_top_memory_consumers(args.top)

            with open(args.output, "w", encoding="utf-8") as f:
                f.write(generate_memory_leak_html(report, top_consumers, args.script))

            print(f"\nMemory Leak Report:")
            print(f"  Peak memory: {report['peak_memory_mb']:.2f} MB")
            print(f"  Memory growth: {report['memory_growth_mb']:.2f} MB")
            print(f"  Potential leaks: {len(report.get('potential_leaks', []))}")
            print(f"\nReport saved to: {args.output}")

            if not args.no_browser:
                open_browser(args.output)

            return CommandResult.success(data={"report": report})

        except Exception as e:
            tb.print_exc()
            return CommandResult.failure(str(e))
