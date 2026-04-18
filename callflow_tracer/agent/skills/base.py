"""
agent/skills/base.py — Skill, SkillTier, and SkillRegistry.

A Skill is a named bundle of tools + a prompt fragment. When RouterAgent
assigns a skill to an agent, that agent gains the skill's tools and its
system prompt is extended with the skill's fragment before the ReAct loop.

Design:
  Value Object  — Skill is a frozen dataclass; never mutated after construction
  Registry      — SkillRegistry: O(1) lookup by name, formatted catalogue for LLM
  Strategy      — skills compose agent behaviour without subclassing

Layer: sits between tools/ (Layer 2) and agents/ (Layer 3).
Imports only from tools/ (same or lower layer). No imports from agents/.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..tools.base import Tool


class SkillTier(str, Enum):
    BUNDLED   = "bundled"    # ships with callflow-tracer
    WORKSPACE = "workspace"  # ~/.callflow/skills/*.py
    MANAGED   = "managed"    # downloaded from a registry


@dataclass(frozen=True)
class Skill:
    """
    Immutable bundle of tools + a prompt fragment.

    tools           : stateless Tool instances contributed to an agent's registry
    prompt_fragment : appended to the agent's system prompt when this skill is active
    description     : one-line summary shown to RouterAgent for selection
    tier            : provenance of this skill
    """

    name: str
    tools: tuple["Tool", ...]                 # frozen → tuple (not list)
    prompt_fragment: str = ""
    description: str = ""
    tier: SkillTier = SkillTier.BUNDLED

    def __post_init__(self) -> None:
        # Accept list at construction time and coerce to tuple for immutability
        if isinstance(self.tools, list):
            object.__setattr__(self, "tools", tuple(self.tools))


class SkillRegistry:
    """
    Holds a dict[name → Skill] for O(1) lookup.

    Built once at Swarm startup from bundled + workspace skills.
    RouterAgent reads `descriptions_for_router()` to know what's available.
    """

    def __init__(self, skills: list[Skill]) -> None:
        self._skills: dict[str, Skill] = {s.name: s for s in skills}

    def get(self, name: str) -> Skill | None:
        return self._skills.get(name)

    def names(self) -> list[str]:
        return list(self._skills.keys())

    def all_skills(self) -> list[Skill]:
        return list(self._skills.values())

    def register(self, skill: Skill) -> None:
        """Add or replace a skill (used by workspace loader)."""
        self._skills[skill.name] = skill

    def descriptions_for_router(self) -> str:
        """
        Compact catalogue formatted for inclusion in RouterAgent's system prompt.
        Each line: '  SkillName (tier) — description  [tools: t1, t2]'
        """
        lines: list[str] = []
        for skill in self._skills.values():
            tool_names = ", ".join(t.name for t in skill.tools)
            desc = skill.description or skill.prompt_fragment[:80]
            lines.append(
                f"  {skill.name} ({skill.tier.value}) — {desc}  [tools: {tool_names}]"
            )
        return "\n".join(lines)
