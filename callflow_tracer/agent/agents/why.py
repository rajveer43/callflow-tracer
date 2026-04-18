"""
agents/why.py — WhyAgent.

Moved from agent/why_agent.py; imports updated to new layer paths.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..core.context import SwarmContext
from ..core.types import Finding
from ..tools.callflow import RunContextTool, RunWhyTool
from ..tools.registry import ToolRegistry
from ..tools.search import GrepCodebaseTool, ListFilesTool
from .base import BaseAgent

if TYPE_CHECKING:
    from ...ai.llm_provider import LLMProvider


class WhyAgent(BaseAgent):
    """Traces call chains to explain how a function is reached."""

    def __init__(self, provider: "LLMProvider") -> None:
        super().__init__(provider, max_turns=3, temperature=0.1)
        self._registry = ToolRegistry([
            RunWhyTool(),
            RunContextTool(),
            ListFilesTool(),
            GrepCodebaseTool(),
        ])

    @property
    def name(self) -> str:
        return "WhyAgent"

    @property
    def _tool_registry(self) -> ToolRegistry:
        return self._registry

    def _build_system_prompt(self, ctx: SwarmContext) -> str:
        hints = ctx.dispatch_plan.hints_for("WhyAgent") if ctx.dispatch_plan else {}
        return (
            "You are the WhyAgent, a specialist in call-chain analysis.\n"
            "Your job: find how a function is called and from where.\n\n"
            "Strategy:\n"
            "  1. Identify the target function from the question (or use hints).\n"
            "  2. Find a test script with list_files or grep_codebase.\n"
            "  3. Use run_why to get all call chains to that function.\n"
            "  4. If the function isn't in the trace, use run_context to find the real hot function first.\n"
            "  5. Output FINAL with a clear chain summary.\n\n"
            f"Extra hints from RouterAgent: {hints}\n"
            f"Codebase: {ctx.cwd}"
        )

    def _build_initial_prompt(self, ctx: SwarmContext) -> str:
        hints  = ctx.dispatch_plan.hints_for("WhyAgent") if ctx.dispatch_plan else {}
        fn     = hints.get("function", "")
        script = hints.get("trace_script", "")
        return (
            f"Question: {ctx.question}\n"
            f"Target function hint: {fn or 'extract from question'}\n"
            f"Trace script hint: {script or 'find with list_files'}\n\n"
            "Find the function being asked about and trace its call chains."
        )

    def _parse_finding(
        self,
        ctx: SwarmContext,
        conversation: list[dict],
        tool_calls_made: list[str],
    ) -> Finding:
        last         = self._last_assistant_text(conversation)
        observations = _collect_observations(conversation)
        summary      = _extract_chain_summary(observations) or last[:400]
        confidence   = 0.85 if "run_why" in tool_calls_made else 0.3

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


def _extract_chain_summary(observations: list[str]) -> str:
    for obs in reversed(observations):
        if "chain" in obs.lower() and ("→" in obs or "└─" in obs):
            lines = obs.splitlines()[:12]
            return "Call chains:\n" + "\n".join(lines)
    return ""
