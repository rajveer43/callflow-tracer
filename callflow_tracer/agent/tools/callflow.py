"""
tools/callflow.py — Tools that call into callflow-tracer's own pipeline.

These tools bridge the agent layer with the core tracer and command-line
analysis modules. They are the only tools that import from callflow_tracer.

Layer 2 — imports from tools/base.py and callflow_tracer.core / command_line.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import Tool


class RunContextTool(Tool):
    """
    Trace a Python script and extract the most relevant functions.
    Calls the _context_extractor pipeline directly (no CLI subprocess).
    """

    @property
    def name(self) -> str:
        return "run_context"

    @property
    def description(self) -> str:
        return "Trace a Python script and return the top N most relevant functions for a query"

    @property
    def param_schema(self) -> dict[str, str]:
        return {
            "script": "path to Python script or test file to trace",
            "query": "what you are investigating (optional)",
            "top_n": "number of functions to return (default: 6)",
        }

    def execute(self, script: str = "", query: str = "", top_n: int = 6) -> str:
        if not script:
            return "Error: script path is required"
        if not Path(script).exists():
            return f"Error: script not found: {script}"

        try:
            from ...core.tracer import trace_scope
            from ...command_line._utils import execute_script
            from ...command_line._context_extractor import (
                WeightedRankingStrategy, rank_nodes, extract_source,
            )

            with trace_scope(None) as graph:
                try:
                    execute_script(script, [])
                except SystemExit:
                    pass

            if not graph.nodes:
                return "No function calls recorded during tracing."

            strategy = WeightedRankingStrategy()
            ranked   = rank_nodes(graph, query=query, top_n=top_n, strategy=strategy)

            if not ranked:
                return "No user-code nodes found after filtering."

            lines = [f"Traced {sum(n.call_count for n in graph.nodes.values())} calls. Top {len(ranked)} functions:\n"]
            for i, r in enumerate(ranked, 1):
                avg_ms = round((r.node.total_time / max(r.node.call_count, 1)) * 1000, 2)
                lines.append(
                    f"{i}. {r.full_name} — called {r.node.call_count}×, "
                    f"avg {avg_ms}ms, depth {r.depth}, score {r.score:.1f}"
                )
            return "\n".join(lines)

        except Exception as exc:
            return f"run_context failed: {exc}"


class RunWhyTool(Tool):
    """
    Show all call chains leading to a function.
    Calls _call_graph_analyzer BFS directly.
    """

    @property
    def name(self) -> str:
        return "run_why"

    @property
    def description(self) -> str:
        return "Show every call chain leading to a function (BFS, shortest first)"

    @property
    def param_schema(self) -> dict[str, str]:
        return {
            "function_name": "full or partial function name to investigate",
            "trace_script": "Python script to trace",
            "max_chains": "max chains to return (default: 10)",
        }

    def execute(
        self,
        function_name: str = "",
        trace_script: str = "",
        max_chains: int = 10,
    ) -> str:
        if not function_name:
            return "Error: function_name is required"
        if not trace_script or not Path(trace_script).exists():
            return f"Error: trace_script not found: {trace_script}"

        try:
            from ...core.tracer import trace_scope
            from ...command_line._utils import execute_script
            from ...command_line._call_graph_analyzer import (
                build_reverse_graph, find_call_chains,
                resolve_target_names, format_chain_as_tree,
            )

            with trace_scope(None) as graph:
                try:
                    execute_script(trace_script, [])
                except SystemExit:
                    pass

            candidates = resolve_target_names(graph, function_name)
            if not candidates:
                return f"Function '{function_name}' not found in trace."

            target  = candidates[0]
            reverse = build_reverse_graph(graph)
            chains  = find_call_chains(reverse, target, max_chains=max_chains)

            if not chains:
                return f"'{target}' has no recorded callers — may be an entry point."

            lines = [f"{len(chains)} call chain(s) to '{target}':\n"]
            for i, chain in enumerate(chains, 1):
                lines.append(format_chain_as_tree(chain, graph, i))
                lines.append("")
            return "\n".join(lines)

        except Exception as exc:
            return f"run_why failed: {exc}"


class RunAgentTraceTool(Tool):
    """Trace an LLM agent script and return a cost + timeline summary."""

    @property
    def name(self) -> str:
        return "run_agent_trace"

    @property
    def description(self) -> str:
        return "Trace a script that calls LLM APIs and return a timeline with cost estimates"

    @property
    def param_schema(self) -> dict[str, str]:
        return {
            "script": "path to the agent/LLM script to trace",
        }

    def execute(self, script: str = "") -> str:
        if not script:
            return "Error: script path is required"
        if not Path(script).exists():
            return f"Error: script not found: {script}"

        try:
            from ...core.tracer import trace_scope
            from ...command_line._utils import execute_script
            from ...command_line._agent_adapters import build_agent_timeline

            with trace_scope(None) as graph:
                try:
                    execute_script(script, [])
                except SystemExit:
                    pass

            timeline = build_agent_timeline(graph)
            if not timeline.events:
                return "No LLM or tool calls detected in this script."

            lines = [
                f"{len(timeline.events)} agent event(s) detected:\n",
                f"Total time : {timeline.total_time_ms:,.1f} ms",
                f"LLM calls  : {len(timeline.llm_events)}",
                f"Tool calls : {len(timeline.tool_events)}",
                f"~Input tok : {timeline.total_input_tokens:,} (estimated)",
                f"~Output tok: {timeline.total_output_tokens:,} (estimated)",
                f"~Cost USD  : ${timeline.total_cost_usd:.6f} (estimated)\n",
                "Events (slowest first):",
            ]
            for e in timeline.events[:10]:
                lines.append(
                    f"  [{e.kind}] {e.provider}: {e.name} "
                    f"({e.call_count}×, {e.avg_time_ms:.1f}ms avg)"
                )
            return "\n".join(lines)

        except Exception as exc:
            return f"run_agent_trace failed: {exc}"
