"""
agents/base.py — BaseAgent (Template Method Pattern).

Moved from agent/base_agent.py; imports updated to new layer paths.

The react_loop() skeleton is fixed here. Subclasses implement the three hooks:
  _build_system_prompt()  — agent's role + rules
  _build_initial_prompt() — first user message
  _parse_finding()        — convert conversation into a typed Finding

Skill/tool injection:
  configure_from_task(task, skill_registry) is called by Swarm._run_specialists()
  before run() to inject skills and extra tools assigned by RouterAgent.
  _effective_tool_registry() merges base tools + skill tools + extra tools.
  _effective_system_prompt() appends skill prompt fragments to the base prompt.

DSA:
  list[dict]  : conversation history (append-only, never mutated)
  dict[str,T] : O(1) tool dispatch in ToolRegistry
"""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from ..core.context import SwarmContext
from ..core.types import AgentTask, Finding, NullFinding
from ..tools.registry import ToolRegistry

if TYPE_CHECKING:
    from ...ai.llm_provider import LLMProvider
    from ..skills.base import Skill, SkillRegistry

# ── Action parsing ─────────────────────────────────────────────────────────────

_JSON_BLOCK_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)
_INLINE_JSON_RE = re.compile(r'\{"tool"\s*:.*?\}', re.DOTALL)


def _parse_action(text: str) -> dict[str, Any] | None:
    """
    Extract the first JSON action block from an LLM response.

    Tries two formats:
      1. Fenced code block:  ```json {"tool": "...", "params": {...}} ```
      2. Bare inline JSON:   {"tool": "...", "params": {...}}

    Returns None if no valid action found or tool == "FINAL".
    """
    for pattern in (_JSON_BLOCK_RE, _INLINE_JSON_RE):
        match = pattern.search(text)
        if match:
            raw = match.group(1) if pattern is _JSON_BLOCK_RE else match.group(0)
            try:
                obj = json.loads(raw)
                if isinstance(obj, dict) and "tool" in obj:
                    if obj["tool"] == "FINAL":
                        return None
                    return obj
            except json.JSONDecodeError:
                continue
    return None


def _build_tool_prompt(registry: ToolRegistry) -> str:
    """Format the tool descriptions for the system prompt."""
    return (
        "You have access to these tools. Call one per turn using a JSON block:\n\n"
        "```json\n"
        '{"tool": "<tool_name>", "params": {<key>: <value>, ...}}\n'
        "```\n\n"
        + registry.descriptions()
        + "\n\nWhen you have gathered enough information, output:\n"
        '```json\n{"tool": "FINAL", "params": {}}\n```\n'
        "Then write your FINDING on the next line."
    )


# ── BaseAgent ABC ──────────────────────────────────────────────────────────────

class BaseAgent(ABC):
    """
    Abstract base for all swarm agents.

    Template Method: run() calls react_loop() which calls the three abstract hooks.
    Subclasses NEVER override run() or react_loop() — only the three hooks below.

    Thread safety: each agent instance is created fresh per swarm run
    (see AgentRegistry), so there is no shared mutable state between parallel runs.
    """

    def __init__(
        self,
        provider: "LLMProvider",
        max_turns: int = 4,
        temperature: float = 0.1,
    ) -> None:
        self._provider    = provider
        self._max_turns   = max_turns
        self._temperature = temperature
        # Populated by configure_from_task() before run() — empty by default
        self._active_skills: list["Skill"] = []
        self._extra_tool_names: list[str]   = []

    # ── Skill / tool injection (called by Swarm before run()) ─────────────

    def configure_from_task(
        self,
        task: AgentTask,
        skill_registry: "SkillRegistry",
    ) -> None:
        """
        Inject skills and extra tools from the RouterAgent's dispatch decision.

        Called by Swarm._run_specialists() in the main thread before the
        agent is submitted to the executor — always single-threaded at call time.

        skills      → resolved from skill_registry by name; unknowns silently skipped
        extra_tools → individual tool names looked up in TOOL_CATALOG at run time
        """
        self._active_skills = [
            s for name in task.skills
            if (s := skill_registry.get(name)) is not None
        ]
        self._extra_tool_names = list(task.extra_tools)

    def _effective_tool_registry(self) -> ToolRegistry:
        """
        Merge base tools + skill-contributed tools + extra tools.

        Deduplicates by tool name — base tools take precedence; skills append
        only tools whose names are not already present.
        """
        from ..tools import TOOL_CATALOG

        seen: set[str] = set()
        merged: list = []

        for tool in self._tool_registry.tools:
            if tool.name not in seen:
                seen.add(tool.name)
                merged.append(tool)

        for skill in self._active_skills:
            for tool in skill.tools:
                if tool.name not in seen:
                    seen.add(tool.name)
                    merged.append(tool)

        for name in self._extra_tool_names:
            if name not in seen and name in TOOL_CATALOG:
                seen.add(name)
                merged.append(TOOL_CATALOG[name])

        return ToolRegistry(merged)

    def _effective_system_prompt(self, ctx: SwarmContext) -> str:
        """
        Compose base system prompt + skill prompt fragments.

        Each active skill appends its fragment under an ## Active Skills header
        so the LLM understands the extra capabilities and focus areas.
        """
        base = self._build_system_prompt(ctx)
        fragments = [
            f"**{s.name}:** {s.prompt_fragment}"
            for s in self._active_skills
            if s.prompt_fragment.strip()
        ]
        if not fragments:
            return base
        skill_section = "\n\n## Active Skills\n" + "\n\n".join(fragments)
        return base + skill_section

    # ── Identity ──────────────────────────────────────────────────────────

    @property
    @abstractmethod
    def name(self) -> str:
        """Stable agent name — must match an entry in AGENT_NAMES."""

    @property
    @abstractmethod
    def _tool_registry(self) -> ToolRegistry:
        """Base tools for this agent type (before skill injection)."""

    # ── Template Method hooks (subclasses implement these) ─────────────────

    @abstractmethod
    def _build_system_prompt(self, ctx: SwarmContext) -> str:
        """Return the system prompt string for this agent's role."""

    @abstractmethod
    def _build_initial_prompt(self, ctx: SwarmContext) -> str:
        """Return the first user-turn message to kick off the ReAct loop."""

    @abstractmethod
    def _parse_finding(
        self,
        ctx: SwarmContext,
        conversation: list[dict],
        tool_calls_made: list[str],
    ) -> Finding:
        """Convert the completed conversation into a typed Finding."""

    # ── Template Method skeleton (DO NOT override) ─────────────────────────

    def run(self, ctx: SwarmContext) -> Finding:
        """
        Fixed execution skeleton:
          1. Announce start (fires AGENT_START hook)
          2. Run ReAct loop
          3. Write Finding to SwarmContext
          4. Handle exceptions → NullFinding (degraded mode, never crashes)
        """
        from ..core.events import EventKind
        from ..core.hooks import HookKind
        ctx.add_message(self.name, EventKind.STARTED, {})
        ctx.hook_bus.fire(HookKind.AGENT_START, {"agent": self.name})
        try:
            finding = self._react_loop(ctx)
        except Exception as exc:
            finding = NullFinding(self.name, error=str(exc))
            ctx.add_message(self.name, EventKind.ERROR, {"error": str(exc)})

        ctx.set_finding(finding)
        return finding

    # ── ReAct loop (Reason → Act → Observe) ───────────────────────────────

    def _react_loop(self, ctx: SwarmContext) -> Finding:
        """
        Core ReAct cycle.

        Each turn:
          1. Send accumulated conversation to LLM
          2. Parse a JSON action block from the response
          3. Execute the tool via ToolRegistry (fires TOOL_CALLED + TOOL_RESULT hooks)
          4. Append OBSERVATION to conversation
          5. Repeat until FINAL action or max_turns exceeded
        """
        from ..core.events import EventKind
        from ..core.hooks import HookKind
        registry = self._effective_tool_registry()
        system   = self._effective_system_prompt(ctx) + "\n\n" + _build_tool_prompt(registry)

        conversation: list[dict] = []
        tool_calls_made: list[str] = []

        running_prompt = self._build_initial_prompt(ctx)

        for _turn in range(self._max_turns):
            response = self._provider.generate(
                prompt=running_prompt,
                system_prompt=system,
                temperature=self._temperature,
                max_tokens=1200,
            )

            conversation.append({"role": "assistant", "content": response})

            action = _parse_action(response)

            if action is None:
                break

            tool_name = action.get("tool", "")
            params    = action.get("params", {})
            tool_calls_made.append(tool_name)

            ctx.add_message(self.name, EventKind.TOOL_CALLED, {"tool": tool_name, "params": params})
            ctx.hook_bus.fire(HookKind.TOOL_CALLED, {"agent": self.name, "tool": tool_name, "params": params})

            observation = registry.execute(tool_name, params)

            if len(observation) > 3000:
                observation = observation[:3000] + "\n...[truncated]"

            ctx.hook_bus.fire(HookKind.TOOL_RESULT, {"agent": self.name, "tool": tool_name, "result": observation[:200]})

            obs_block = f"\nOBSERVATION:\n{observation}"
            running_prompt = (
                running_prompt
                + f"\n\nAssistant:\n{response}"
                + obs_block
                + "\n\nContinue your analysis. Use another tool or output FINAL:"
            )

            conversation.append({"role": "user", "content": obs_block})

        return self._parse_finding(ctx, conversation, tool_calls_made)

    # ── Shared helper ──────────────────────────────────────────────────────

    @staticmethod
    def _last_assistant_text(conversation: list[dict]) -> str:
        """Return the last assistant message text, or empty string."""
        for msg in reversed(conversation):
            if msg["role"] == "assistant":
                return msg["content"]
        return ""
