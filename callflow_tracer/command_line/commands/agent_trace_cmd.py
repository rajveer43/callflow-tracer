"""
`callflow agent-trace` command — LLM Agent Execution Inspector.

Runs a Python script (which calls any LLM SDK), traces every function, detects
LLM/tool calls via the Adapter Pattern, and prints a readable timeline showing:
  - which calls were made and to which provider
  - per-call timing
  - estimated token usage and cost
  - total cost/time summary

Usage:
    callflow-tracer agent-trace python_agent.py
    callflow-tracer agent-trace my_chain.py --args "--verbose"
    callflow-tracer agent-trace run.py --from trace.json   # re-use saved trace
    callflow-tracer agent-trace run.py --output timeline.md

Patterns used (see _agent_adapters.py):
    Adapter  → LLMCallAdapter hierarchy  (normalize each SDK → AgentEvent)
    Registry → LLMAdapterRegistry        (first-match dispatch)
"""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from .._utils import execute_script, load_graph_from_json
from .._agent_adapters import AgentEvent, AgentTimeline, build_agent_timeline
from ..interfaces.command import BaseCommand, CommandContext, CommandResult

# Kind → display label mapping
_KIND_LABEL: dict[str, str] = {
    "llm":   "LLM  ",
    "tool":  "TOOL ",
    "embed": "EMBED",
    "chain": "CHAIN",
}
_KIND_ICON: dict[str, str] = {
    "llm":   "🤖",
    "tool":  "🔧",
    "embed": "📐",
    "chain": "🔗",
}


class AgentTraceCommand(BaseCommand):
    """Trace an LLM agent script and print a timeline of every AI call."""

    @property
    def name(self) -> str:
        return "agent-trace"

    @property
    def aliases(self) -> list[str]:
        return ["at"]

    @property
    def help(self) -> str:
        return "Trace an LLM agent and show a timeline of tool/LLM calls"

    # ── Argument registration ──────────────────────────────────────────────

    def add_arguments(self, parser: ArgumentParser) -> None:
        source_group = parser.add_mutually_exclusive_group(required=True)
        source_group.add_argument(
            "script",
            nargs="?",
            default=None,
            help="Python agent script to trace",
        )
        source_group.add_argument(
            "--from", "-f",
            dest="from_file",
            metavar="FILE",
            help="Load a previously saved JSON trace instead of running a script",
        )
        parser.add_argument(
            "--args",
            nargs="*",
            default=[],
            metavar="ARG",
            help="Arguments forwarded to the script",
        )
        parser.add_argument(
            "--output", "-o",
            default=None,
            metavar="FILE",
            help="Also write the timeline to a Markdown file",
        )
        parser.add_argument(
            "--min-time-ms",
            type=float,
            default=0.0,
            metavar="MS",
            help="Hide events faster than this threshold (default: 0)",
        )

    # ── Execution ──────────────────────────────────────────────────────────

    def execute(self, ctx: CommandContext) -> CommandResult:
        args = ctx.args

        # --- 1. Obtain the call graph -------------------------------------
        graph, err = _load_graph(args)
        if err:
            return CommandResult.failure(err)

        if not graph.nodes:
            return CommandResult.failure("No calls were recorded in the trace.")

        # --- 2. Build timeline via Adapter registry -----------------------
        timeline = build_agent_timeline(graph)

        if not timeline.events:
            return CommandResult.failure(
                "No LLM or tool calls detected.\n"
                "  Tip: make sure the agent actually ran and the SDK calls were not "
                "hidden inside C extensions."
            )

        # --- 3. Apply min-time filter -------------------------------------
        if args.min_time_ms > 0:
            timeline.events = [
                e for e in timeline.events if e.total_time_ms >= args.min_time_ms
            ]

        # --- 4. Render terminal output ------------------------------------
        _print_timeline(timeline)

        # --- 5. Optional Markdown output ----------------------------------
        if args.output:
            md = _build_markdown_timeline(timeline)
            try:
                Path(args.output).write_text(md, encoding="utf-8")
                print(f"  Timeline saved to: {args.output}\n")
            except OSError as exc:
                print(f"  Warning: could not write output file: {exc}")

        return CommandResult.success(data={
            "events": len(timeline.events),
            "llm_calls": len(timeline.llm_events),
            "tool_calls": len(timeline.tool_events),
            "total_time_ms": round(timeline.total_time_ms, 2),
            "total_cost_usd": timeline.total_cost_usd,
            "total_input_tokens": timeline.total_input_tokens,
            "total_output_tokens": timeline.total_output_tokens,
        })


# ── Private helpers ────────────────────────────────────────────────────────────

def _load_graph(args):
    """Return (CallGraph | None, error_str | None)."""
    from ...core.tracer import trace_scope

    if getattr(args, "from_file", None):
        fpath = args.from_file
        if not Path(fpath).exists():
            return None, f"Trace file not found: {fpath}"
        try:
            return load_graph_from_json(fpath), None
        except Exception as exc:
            return None, f"Failed to load trace file: {exc}"

    script = getattr(args, "script", None)
    if not script:
        return None, "Provide a script to trace or use --from to load a trace file."
    if not Path(script).exists():
        return None, f"Script not found: {script}"

    try:
        with trace_scope(None) as graph:
            execute_script(script, getattr(args, "args", []) or [])
    except SystemExit:
        pass
    except Exception as exc:
        return None, f"Script raised an exception: {exc}"

    return graph, None


def _format_event_row(event: AgentEvent, cumulative_ms: float) -> str:
    """
    Format one AgentEvent as a fixed-width timeline row.
    Example:
        1,340ms  [LLM  ] anthropic  claude / messages.create (3×) — 12ms avg
    """
    kind_label = _KIND_LABEL.get(event.kind, event.kind.upper()[:5].ljust(5))
    time_str   = f"{cumulative_ms:>8.0f}ms"
    name_short = event.name.split(".")[-1][:35].ljust(35)
    prov       = event.provider[:10].ljust(10)
    calls      = f"({event.call_count}×)"
    avg_str    = f"avg {event.avg_time_ms:.1f}ms"
    return f"  {time_str}  [{kind_label}] {prov}  {name_short} {calls} — {avg_str}"


def _print_timeline(timeline: AgentTimeline) -> None:
    """Print the full timeline to stdout."""
    sep  = "═" * 72
    thin = "─" * 72

    print(f"\n{sep}")
    print(f"  Agent Execution Timeline")
    print(f"  {len(timeline.events)} event(s) detected")
    print(f"{sep}\n")

    cumulative: float = 0.0
    for event in timeline.events:
        cumulative += event.total_time_ms
        print(_format_event_row(event, cumulative))

    print(f"\n{thin}")
    print(f"  Total time     : {timeline.total_time_ms:,.1f} ms")
    print(f"  LLM calls      : {len(timeline.llm_events)}")
    print(f"  Tool calls     : {len(timeline.tool_events)}")
    print(f"  ~Input tokens  : {timeline.total_input_tokens:,}  (estimated)")
    print(f"  ~Output tokens : {timeline.total_output_tokens:,}  (estimated)")
    print(f"  ~Cost (USD)    : ${timeline.total_cost_usd:.6f}  (estimated)")
    print(f"{thin}\n")

    if timeline.llm_events:
        slowest = max(timeline.llm_events, key=lambda e: e.avg_time_ms)
        print(f"  Slowest LLM call : {slowest.name} ({slowest.avg_time_ms:.1f}ms avg)")
    if timeline.tool_events:
        most_called = max(timeline.tool_events, key=lambda e: e.call_count)
        print(f"  Most-called tool : {most_called.name} ({most_called.call_count}×)")
    print()


def _build_markdown_timeline(timeline: AgentTimeline) -> str:
    """Build a Markdown document from the timeline for --output."""
    lines: list[str] = [
        "# Agent Execution Timeline\n",
        f"**{len(timeline.events)} events** | "
        f"**{timeline.total_time_ms:,.1f} ms total** | "
        f"**~${timeline.total_cost_usd:.6f} estimated**\n\n",
        "---\n\n",
        "| # | Kind | Provider | Function | Calls | Avg Time | Est. Tokens |\n",
        "|---|------|----------|----------|-------|----------|-------------|\n",
    ]

    for i, event in enumerate(timeline.events, start=1):
        total_tok = (event.input_tokens_est + event.output_tokens_est) * event.call_count
        lines.append(
            f"| {i} | `{event.kind}` | {event.provider} "
            f"| `{event.name}` "
            f"| {event.call_count}× "
            f"| {event.avg_time_ms:.1f} ms "
            f"| ~{total_tok:,} |\n"
        )

    lines += [
        "\n---\n\n",
        "## Summary\n\n",
        f"- **LLM calls:** {len(timeline.llm_events)}\n",
        f"- **Tool calls:** {len(timeline.tool_events)}\n",
        f"- **Total input tokens (est.):** ~{timeline.total_input_tokens:,}\n",
        f"- **Total output tokens (est.):** ~{timeline.total_output_tokens:,}\n",
        f"- **Estimated cost (USD):** ~${timeline.total_cost_usd:.6f}\n\n",
        "_Token and cost figures are heuristic estimates based on timing and "
        "typical provider throughput rates._\n",
    ]

    return "".join(lines)
