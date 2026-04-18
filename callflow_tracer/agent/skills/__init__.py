"""
agent/skills — Skill system for runtime capability composition.

Skills are named bundles of tools + prompt fragments. RouterAgent assigns
skills (and individual extra tools) to agents at dispatch time; agents
compose their effective tool registry and system prompt from their active skills.

Three tiers:
  Bundled   — ships with callflow-tracer (see bundled.py)
  Workspace — discovered from ~/.callflow/skills/*.py (see loader.py)
  Managed   — future: downloadable from a registry

Public surface:
  Skill, SkillTier, SkillRegistry  — core types
  build_skill_registry()           — builds bundled + workspace registry
"""

from __future__ import annotations

from pathlib import Path

from .base import Skill, SkillRegistry, SkillTier
from .bundled import BUNDLED_SKILLS, build_bundled_registry
from .loader import load_workspace_skills

__all__ = [
    "Skill",
    "SkillRegistry",
    "SkillTier",
    "BUNDLED_SKILLS",
    "build_bundled_registry",
    "build_skill_registry",
    "load_workspace_skills",
]


def build_skill_registry(skill_dir: Path | None = None) -> SkillRegistry:
    """
    Build a SkillRegistry with bundled skills + any workspace skills.

    Workspace skills in skill_dir override bundled skills of the same name.
    """
    registry = build_bundled_registry()
    load_workspace_skills(skill_dir=skill_dir, registry=registry)
    return registry
