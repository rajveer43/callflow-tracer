"""
agents/grep.py — GrepAgent.

Moved from agent/grep_agent.py; imports updated to new layer paths.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..core.context import SwarmContext
from ..core.types import Finding
from ..tools.registry import ToolRegistry
from ..tools.search import GrepCodebaseTool, ListFilesTool, ReadFileTool
from .base import BaseAgent

if TYPE_CHECKING:
    from ...ai.llm_provider import LLMProvider


class GrepAgent(BaseAgent):
    """Searches the codebase statically to locate files and patterns."""

    def __init__(self, provider: "LLMProvider") -> None:
        super().__init__(provider, max_turns=3, temperature=0.1)
        self._registry = ToolRegistry([
            GrepCodebaseTool(),
            ListFilesTool(),
            ReadFileTool(),
        ])

    @property
    def name(self) -> str:
        return "GrepAgent"

    @property
    def _tool_registry(self) -> ToolRegistry:
        return self._registry

    def _build_system_prompt(self, ctx: SwarmContext) -> str:
        return (
            "You are the GrepAgent, a specialist in static code search.\n"
            "Your job: find where code lives without executing it.\n\n"
            "Strategy:\n"
            "  1. Extract keywords from the question (function names, class names, patterns).\n"
            "  2. Use grep_codebase to find matching files and lines.\n"
            "  3. Use read_file to read the most relevant section.\n"
            "  4. Output FINAL with file paths and line numbers.\n\n"
            f"Codebase: {ctx.cwd}"
        )

    def _build_initial_prompt(self, ctx: SwarmContext) -> str:
        hints   = ctx.dispatch_plan.hints_for("GrepAgent") if ctx.dispatch_plan else {}
        pattern = hints.get("pattern", "")
        return (
            f"Question: {ctx.question}\n"
            f"Search pattern hint: {pattern or 'derive from question'}\n"
            f"Search dir: {ctx.search_scope()}\n\n"
            "Find the relevant code locations."
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
        summary    = _extract_grep_summary(observations) or last[:400]
        confidence = 0.75 if "grep_codebase" in tool_calls_made else 0.3

        return Finding(
            agent_name=self.name,
            summary=summary,
            raw_data={"observations": observations, "llm_analysis": last[:600]},
            confidence=confidence,
            tool_calls_made=tool_calls_made,
        )


def _extract_grep_summary(observations: list[str]) -> str:
    for obs in reversed(observations):
        if "match" in obs.lower() or ".py:" in obs:
            lines = [l for l in obs.splitlines() if ".py:" in l][:8]
            if lines:
                return "Code locations found:\n" + "\n".join(lines)
    return ""
