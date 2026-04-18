"""
agents/router.py — RouterAgent.

Moved from agent/router_agent.py; imports updated to new layer paths.
"""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING

from ..core.context import SwarmContext
from ..core.types import AgentTask, DispatchPlan, Finding, NullFinding
from ..tools.registry import ToolRegistry
from ..tools.search import GrepCodebaseTool, ListFilesTool
from .base import BaseAgent

if TYPE_CHECKING:
    from ...ai.llm_provider import LLMProvider
    from ..skills.base import SkillRegistry

_DISPATCHABLE: frozenset[str] = frozenset({
    "ContextAgent", "WhyAgent", "CostAgent", "GrepAgent",
})

_KEYWORD_HINTS: dict[str, list[str]] = {
    "slow":       ["ContextAgent", "WhyAgent"],
    "expensive":  ["ContextAgent", "CostAgent"],
    "cost":       ["CostAgent"],
    "token":      ["CostAgent"],
    "llm":        ["CostAgent", "ContextAgent"],
    "why":        ["WhyAgent", "ContextAgent"],
    "called":     ["WhyAgent"],
    "where":      ["GrepAgent", "WhyAgent"],
    "find":       ["GrepAgent"],
    "which file": ["GrepAgent"],
    "hot":        ["ContextAgent"],
    "frequent":   ["ContextAgent", "WhyAgent"],
    "agent":      ["CostAgent", "ContextAgent"],
}


def _keyword_agents(question: str) -> list[str]:
    q_lower = question.lower()
    seen: set[str] = set()
    ordered: list[str] = []
    for kw, agents in _KEYWORD_HINTS.items():
        if kw in q_lower:
            for a in agents:
                if a not in seen:
                    seen.add(a)
                    ordered.append(a)
    if not ordered:
        ordered = ["GrepAgent", "ContextAgent"]
    return ordered


class RouterAgent(BaseAgent):
    """
    Reads the question and inspects the codebase structure,
    then produces a DispatchPlan telling the Swarm which specialists to run.
    """

    def __init__(
        self,
        provider: "LLMProvider",
        plugin_agent_names: frozenset[str] | None = None,
        skill_registry: "SkillRegistry | None" = None,
    ) -> None:
        super().__init__(provider, max_turns=3, temperature=0.0)
        self._registry = ToolRegistry([GrepCodebaseTool(), ListFilesTool()])
        self._plugin_agent_names: frozenset[str] = plugin_agent_names or frozenset()
        self._skill_registry: "SkillRegistry | None" = skill_registry

    @property
    def name(self) -> str:
        return "RouterAgent"

    @property
    def _tool_registry(self) -> ToolRegistry:
        return self._registry

    def _build_system_prompt(self, ctx: SwarmContext) -> str:
        keyword_suggestions = _keyword_agents(ctx.question)

        plugin_section = ""
        if self._plugin_agent_names:
            names_list = ", ".join(sorted(self._plugin_agent_names))
            plugin_section = (
                f"\nPlugin specialists (custom): {names_list}\n"
                "These are user-defined agents — dispatch them by exact name if the question fits.\n"
            )

        skill_section = ""
        if self._skill_registry and self._skill_registry.names():
            skill_section = (
                "\n## Available Skills (assign to agents via 'skills' key)\n"
                + self._skill_registry.descriptions_for_router()
                + "\n"
            )

        from ..tools import TOOL_CATALOG
        tool_names = ", ".join(TOOL_CATALOG.keys())
        tool_section = (
            f"\n## Available Extra Tools (assign individually via 'tools' key)\n"
            f"  {tool_names}\n"
        )

        return (
            "You are the RouterAgent for the callflow-tracer swarm.\n"
            "Your job: decide which specialist agents to run AND which skills/tools to assign them.\n\n"
            "## Built-in Specialists\n"
            f"Available: ContextAgent, WhyAgent, CostAgent, GrepAgent\n"
            f"Keyword analysis suggests: {keyword_suggestions}\n\n"
            "ContextAgent  — hot/slow functions, call frequency, execution flow\n"
            "WhyAgent      — why a function is called, call chain analysis\n"
            "CostAgent     — LLM cost, token usage, agent call overhead\n"
            "GrepAgent     — find code, files, patterns statically\n"
            + plugin_section
            + skill_section
            + tool_section
            + "\nUse list_files to understand the codebase, then grep_codebase if needed.\n"
            "Then output FINAL and a JSON dispatch plan."
        )

    def _build_initial_prompt(self, ctx: SwarmContext) -> str:
        return (
            f"Question: {ctx.question}\n"
            f"Working directory: {ctx.cwd}\n"
            f"Scope: {ctx.scope or 'entire codebase'}\n\n"
            "1. List Python files to understand the codebase structure.\n"
            "2. Decide which specialists to deploy, which skills to activate on each,\n"
            "   and which extra tools (if any) to add beyond what the skills provide.\n"
            "3. Output FINAL with a JSON dispatch plan in this exact format:\n\n"
            '```json\n{"tool": "FINAL", "params": {}}\n```\n\n'
            "DISPATCH_PLAN:\n"
            '{"agents": ["ContextAgent", "GrepAgent"], "mode": "parallel", '
            '"skills": {"ContextAgent": ["DependencyTrace"], "GrepAgent": ["StaticAnalysis"]}, '
            '"tools": {"GrepAgent": ["read_file"]}, '
            '"hints": {"ContextAgent": {"query": "slow functions"}}}'
        )

    def _parse_finding(
        self,
        ctx: SwarmContext,
        conversation: list[dict],
        tool_calls_made: list[str],
    ) -> Finding:
        last = self._last_assistant_text(conversation)
        plan = _extract_dispatch_plan(last, ctx, extra_dispatchable=self._plugin_agent_names)
        ctx.dispatch_plan = plan

        return Finding(
            agent_name=self.name,
            summary=f"Dispatching: {plan.agent_names()} in {plan.mode} mode",
            raw_data={"plan": plan.agent_names(), "mode": plan.mode},
            confidence=0.9,
            tool_calls_made=tool_calls_made,
        )


_PLAN_MARKER_RE = re.compile(r"DISPATCH_PLAN:\s*(\{)", re.DOTALL)


def _extract_balanced_json(text: str, start: int) -> str | None:
    """
    Extract the JSON object starting at text[start] (which must be '{').
    Uses a brace counter — handles nested objects correctly.
    """
    depth = 0
    i = start
    in_string = False
    escape_next = False
    while i < len(text):
        ch = text[i]
        if escape_next:
            escape_next = False
        elif ch == "\\" and in_string:
            escape_next = True
        elif ch == '"':
            in_string = not in_string
        elif not in_string:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
        i += 1
    return None


def _extract_dispatch_plan(
    text: str,
    ctx: SwarmContext,
    extra_dispatchable: frozenset[str] | None = None,
) -> DispatchPlan:
    dispatchable = _DISPATCHABLE | (extra_dispatchable or frozenset())
    marker = _PLAN_MARKER_RE.search(text)
    if marker:
        raw_json = _extract_balanced_json(text, marker.start(1))
        try:
            obj    = json.loads(raw_json) if raw_json else None
            if not isinstance(obj, dict):
                raise ValueError("not a dict")
            agents = [a for a in obj.get("agents", []) if a in dispatchable]
            hints  = obj.get("hints", {})
            skills = obj.get("skills", {})   # dict[agent_name → list[skill_name]]
            tools  = obj.get("tools", {})    # dict[agent_name → list[tool_name]]
            mode   = obj.get("mode", "parallel")
            if agents:
                return DispatchPlan(
                    tasks=[
                        AgentTask(
                            agent_name=a,
                            hints=hints.get(a, {}),
                            skills=skills.get(a, []),
                            extra_tools=tools.get(a, []),
                        )
                        for a in agents
                    ],
                    mode=mode,
                    reasoning=text[:300],
                )
        except (json.JSONDecodeError, TypeError, ValueError):
            pass

    fallback_agents = _keyword_agents(ctx.question)
    return DispatchPlan(
        tasks=[AgentTask(agent_name=a) for a in fallback_agents],
        mode="parallel",
        reasoning="fallback: keyword-based dispatch",
    )
