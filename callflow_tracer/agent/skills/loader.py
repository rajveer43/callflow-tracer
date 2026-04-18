"""
agent/skills/loader.py — Workspace skill discovery from ~/.callflow/skills/.

A workspace skill file is a plain .py that exports a module-level
`SKILLS: list[Skill]` constant. The loader discovers these files, imports
them in sorted order, and merges them into the SkillRegistry.

Example workspace skill file:
  # ~/.callflow/skills/my_perf_skill.py
  from callflow_tracer.agent.skills import Skill
  from callflow_tracer.agent.tools import GrepCodebaseTool

  SKILLS = [
      Skill(
          name="PerfAnalysis",
          tools=(GrepCodebaseTool(),),
          description="Custom performance analysis for this project",
          prompt_fragment="Focus on O(N^2) loops and missing caches...",
      )
  ]
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from .base import Skill, SkillRegistry


def load_workspace_skills(
    skill_dir: Path | None = None,
    registry: SkillRegistry | None = None,
) -> list[Skill]:
    """
    Discover and load workspace skills from skill_dir.

    Loads files in sorted order for deterministic behaviour.
    Returns empty list if skill_dir does not exist.
    Silently skips files that don't export SKILLS or fail to import.

    If registry is provided, loaded skills are registered into it directly.
    """
    skill_dir = skill_dir or (Path.home() / ".callflow" / "skills")
    if not skill_dir.is_dir():
        return []

    loaded: list[Skill] = []
    for py_file in sorted(skill_dir.glob("*.py")):
        skills = _load_one_skill_file(py_file)
        loaded.extend(skills)
        if registry is not None:
            for skill in skills:
                registry.register(skill)

    return loaded


def _load_one_skill_file(py_file: Path) -> list[Skill]:
    """Dynamically import one skill file and return its SKILLS list."""
    module_name = f"_callflow_skill_mod_{py_file.stem}"
    spec = importlib.util.spec_from_file_location(module_name, py_file)
    if spec is None or spec.loader is None:
        return []
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)  # type: ignore[attr-defined]
        skills = getattr(module, "SKILLS", None)
        if not isinstance(skills, list):
            return []
        return [s for s in skills if isinstance(s, Skill)]
    except Exception:
        return []
    finally:
        sys.modules.pop(module_name, None)
