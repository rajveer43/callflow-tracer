"""
agents/cost.py — CostAgent.

Moved from agent/cost_agent.py; imports updated to new layer paths.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..core.context import SwarmContext
from ..core.types import Finding
from ..tools.callflow import RunAgentTraceTool
from ..tools.registry import ToolRegistry
from ..tools.search import GrepCodebaseTool, ListFilesTool
from .base import BaseAgent

if TYPE_CHECKING:
    from ...ai.llm_provider import LLMProvider


class CostAgent(BaseAgent):
    """Traces agent scripts and surfaces LLM cost/token patterns."""

    def __init__(self, provider: "LLMProvider") -> None:
        super().__init__(provider, max_turns=3, temperature=0.1)
        self._registry = ToolRegistry([
            RunAgentTraceTool(),
            ListFilesTool(),
            GrepCodebaseTool(),
        ])

    @property
    def name(self) -> str:
        return "CostAgent"

    @property
    def _tool_registry(self) -> ToolRegistry:
        return self._registry

    def _build_system_prompt(self, ctx: SwarmContext) -> str:
        hints = ctx.dispatch_plan.hints_for("CostAgent") if ctx.dispatch_plan else {}
        return (
            "You are the CostAgent, a specialist in LLM cost and token analysis.\n"
            "Your job: find LLM API calls, estimate their cost, and detect waste.\n\n"
            "Strategy:\n"
            "  1. Find agent/LLM scripts using list_files or grep_codebase (look for 'anthropic', 'openai', 'langchain').\n"
            "  2. Use run_agent_trace on the most likely script.\n"
            "  3. Identify: total cost, redundant calls, slowest call, token waste.\n"
            "  4. Output FINAL with a cost summary.\n\n"
            f"Extra hints: {hints}\n"
            f"Codebase: {ctx.cwd}"
        )

    def _build_initial_prompt(self, ctx: SwarmContext) -> str:
        hints  = ctx.dispatch_plan.hints_for("CostAgent") if ctx.dispatch_plan else {}
        script = hints.get("script", "")
        return (
            f"Question: {ctx.question}\n"
            f"Script hint: {script or 'find using grep for openai/anthropic/langchain'}\n\n"
            "Find and trace the LLM agent script. Report cost and token usage."
        )

    def _parse_finding(
        self,
        ctx: SwarmContext,
        conversation: list[dict],
        tool_calls_made: list[str],
    ) -> Finding:
        last         = self._last_assistant_text(conversation)
        observations = [
            m["content"].replace("OBSERVATION:", "").strip()
            for m in conversation
            if m["role"] == "user" and "OBSERVATION:" in m["content"]
        ]
        summary    = _extract_cost_summary(observations) or last[:400]
        confidence = 0.85 if "run_agent_trace" in tool_calls_made else 0.3

        return Finding(
            agent_name=self.name,
            summary=summary,
            raw_data={"observations": observations, "llm_analysis": last[:600]},
            confidence=confidence,
            tool_calls_made=tool_calls_made,
        )


def _extract_cost_summary(observations: list[str]) -> str:
    for obs in reversed(observations):
        if "cost" in obs.lower() and ("usd" in obs.lower() or "$" in obs):
            lines = [l for l in obs.splitlines() if any(k in l.lower() for k in ("cost", "token", "llm", "tool", "time"))]
            if lines:
                return "Cost analysis:\n" + "\n".join(lines[:10])
    return ""
