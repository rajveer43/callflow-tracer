"""
agents/synthesizer.py — SynthesizerAgent.

Moved from agent/synthesizer_agent.py; imports updated to new layer paths.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..core.context import SwarmContext
from ..core.types import Finding, NullFinding
from ..tools.registry import ToolRegistry
from .base import BaseAgent

if TYPE_CHECKING:
    from ...ai.llm_provider import LLMProvider


class SynthesizerAgent(BaseAgent):
    """
    Read-only agent — synthesizes all findings into a final structured answer.
    Has no tools; max_turns=1 (one LLM call is enough with all context loaded).
    """

    def __init__(self, provider: "LLMProvider") -> None:
        super().__init__(provider, max_turns=1, temperature=0.2)
        self._registry = ToolRegistry([])   # no tools — read-only

    @property
    def name(self) -> str:
        return "SynthesizerAgent"

    @property
    def _tool_registry(self) -> ToolRegistry:
        return self._registry

    def _build_system_prompt(self, ctx: SwarmContext) -> str:
        return (
            "You are the SynthesizerAgent for the callflow-tracer swarm.\n"
            "You receive findings from specialist agents and produce ONE clear, structured answer.\n\n"
            "Output format (use exactly these section headers):\n"
            "ROOT CAUSE  : <what is wrong — be specific, one sentence>\n"
            "LOCATION    : <file path, function name, line number if known>\n"
            "CALL CHAIN  : <how the function is reached, if known>\n"
            "COST IMPACT : <LLM/token waste estimate, if applicable — else 'N/A'>\n"
            "FIX         : <concrete, actionable recommendation — 1-3 bullets>\n"
            "CONFIDENCE  : <overall swarm confidence — high/medium/low>\n\n"
            "Rules:\n"
            "  - Be specific. Never say 'it depends' or 'check your code'.\n"
            "  - If a finding is empty or uncertain, say so rather than guessing.\n"
            "  - Keep total response under 300 words.\n"
            "  - Do not output any JSON action blocks."
        )

    def _build_initial_prompt(self, ctx: SwarmContext) -> str:
        active = sorted(ctx.active_findings(), key=lambda f: f.confidence, reverse=True)

        if not active:
            return (
                f"Question: {ctx.question}\n\n"
                "No specialist findings available. "
                "Provide the best answer you can from the question alone."
            )

        findings_text = "\n\n".join(
            f"[{f.agent_name} — confidence {f.confidence:.0%}]\n{f.summary}"
            for f in active
        )
        avg_conf = sum(f.confidence for f in active) / len(active)

        return (
            f"User question: {ctx.question}\n\n"
            f"Specialist findings ({len(active)} agent(s), avg confidence {avg_conf:.0%}):\n\n"
            f"{findings_text}\n\n"
            "Synthesize all findings into the structured answer format."
        )

    def _parse_finding(
        self,
        ctx: SwarmContext,
        conversation: list[dict],
        tool_calls_made: list[str],
    ) -> Finding:
        last = self._last_assistant_text(conversation)

        ctx.final_answer = _format_final_answer(last)

        active   = ctx.active_findings()
        avg_conf = sum(f.confidence for f in active) / max(len(active), 1)

        return Finding(
            agent_name=self.name,
            summary=last[:400],
            raw_data={"final_answer": ctx.final_answer},
            confidence=avg_conf,
            tool_calls_made=[],
        )


# ── Output formatting ──────────────────────────────────────────────────────────

_SECTION_KEYS = ("ROOT CAUSE", "LOCATION", "CALL CHAIN", "COST IMPACT", "FIX", "CONFIDENCE")
_BORDER = "═" * 58


def _format_final_answer(raw: str) -> str:
    has_sections = any(key + " " in raw or key + ":" in raw for key in _SECTION_KEYS)

    if not has_sections:
        return f"\n{_BORDER}\n{raw.strip()}\n{_BORDER}\n"

    lines: list[str] = [f"\n{_BORDER}"]
    for line in raw.strip().splitlines():
        lines.append(f"  {line}")
    lines.append(_BORDER + "\n")
    return "\n".join(lines)
