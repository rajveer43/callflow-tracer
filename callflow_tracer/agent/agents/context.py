"""
agents/context.py — ContextAgent.

Moved from agent/context_agent.py; imports updated to new layer paths.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..core.context import SwarmContext
from ..core.types import Finding
from ..tools.callflow import RunContextTool
from ..tools.registry import ToolRegistry
from ..tools.search import GrepCodebaseTool, ListFilesTool
from .base import BaseAgent

if TYPE_CHECKING:
    from ...ai.llm_provider import LLMProvider


class ContextAgent(BaseAgent):
    """Traces execution and surfaces the most relevant functions."""

    def __init__(self, provider: "LLMProvider") -> None:
        super().__init__(provider, max_turns=3, temperature=0.1)
        self._registry = ToolRegistry([
            RunContextTool(),
            ListFilesTool(),
            GrepCodebaseTool(),
        ])

    @property
    def name(self) -> str:
        return "ContextAgent"

    @property
    def _tool_registry(self) -> ToolRegistry:
        return self._registry

    def _build_system_prompt(self, ctx: SwarmContext) -> str:
        hints = ctx.dispatch_plan.hints_for("ContextAgent") if ctx.dispatch_plan else {}
        return (
            "You are the ContextAgent, a specialist in Python execution tracing.\n"
            "Your job: find which functions actually execute and are most relevant to the question.\n\n"
            "Strategy:\n"
            "  1. Use list_files to find test files or the main script to trace.\n"
            "  2. Use run_context with the best candidate script and the user's question as query.\n"
            "  3. If the result is empty or uninformative, try a different script.\n"
            "  4. Output FINAL once you have a clear list of hot functions.\n\n"
            f"Extra hints from RouterAgent: {hints}\n"
            f"Codebase: {ctx.cwd} | Scope: {ctx.scope or 'full'}"
        )

    def _build_initial_prompt(self, ctx: SwarmContext) -> str:
        hints = ctx.dispatch_plan.hints_for("ContextAgent") if ctx.dispatch_plan else {}
        query = hints.get("query", ctx.question)
        suggested_script = hints.get("trace_script", "")
        return (
            f"Question: {ctx.question}\n"
            f"Search dir: {ctx.search_scope()}\n"
            f"Suggested script: {suggested_script or 'find one using list_files'}\n"
            f"Query hint: {query}\n\n"
            "Find and trace the most relevant Python script. "
            "Report which functions are hottest."
        )

    def _parse_finding(
        self,
        ctx: SwarmContext,
        conversation: list[dict],
        tool_calls_made: list[str],
    ) -> Finding:
        last         = self._last_assistant_text(conversation)
        observations = _collect_observations(conversation)
        summary      = _summarise_context_obs(observations) or last[:400]
        confidence   = 0.8 if "run_context" in tool_calls_made else 0.4

        return Finding(
            agent_name=self.name,
            summary=summary,
            raw_data={"observations": observations, "llm_analysis": last[:600]},
            confidence=confidence,
            tool_calls_made=tool_calls_made,
        )


def _collect_observations(conversation: list[dict]) -> list[str]:
    return [
        m["content"].replace("OBSERVATION:", "").strip()
        for m in conversation
        if m["role"] == "user" and "OBSERVATION:" in m["content"]
    ]


def _summarise_context_obs(observations: list[str]) -> str:
    for obs in reversed(observations):
        if "called" in obs and "×" in obs:
            lines = [l for l in obs.splitlines() if "×" in l][:5]
            if lines:
                return "Hot functions found:\n" + "\n".join(lines)
    return ""
