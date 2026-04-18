"""
orchestration/builder.py — fluent Swarm builder.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from .swarm import Swarm

if TYPE_CHECKING:
    from ...ai.llm_provider import LLMProvider


class SwarmBuilder:
    """Fluent builder for Swarm configuration."""

    def __init__(self, provider: "LLMProvider") -> None:
        self._provider = provider
        self._mode = "parallel"
        self._timeout = 120
        self._max_workers = 4
        self._verbose = False
        self._plugin_dir: Path | None = None
        self._skill_dir: Path | None = None

    def with_mode(self, mode: str) -> "SwarmBuilder":
        assert mode in ("parallel", "sequential"), f"Invalid mode: {mode}"
        self._mode = mode
        return self

    def with_timeout(self, seconds: int) -> "SwarmBuilder":
        self._timeout = seconds
        return self

    def with_max_workers(self, n: int) -> "SwarmBuilder":
        self._max_workers = max(1, n)
        return self

    def with_plugin_dir(self, plugin_dir: str | Path) -> "SwarmBuilder":
        """Override the default plugin discovery directory (~/.callflow/agents/)."""
        self._plugin_dir = Path(plugin_dir)
        return self

    def with_skill_dir(self, skill_dir: str | Path) -> "SwarmBuilder":
        """Override the default workspace skill directory (~/.callflow/skills/)."""
        self._skill_dir = Path(skill_dir)
        return self

    def verbose(self) -> "SwarmBuilder":
        self._verbose = True
        return self

    def build(self) -> Swarm:
        return Swarm(
            provider=self._provider,
            mode=self._mode,
            timeout=self._timeout,
            max_workers=self._max_workers,
            verbose=self._verbose,
            plugin_dir=self._plugin_dir,
            skill_dir=self._skill_dir,
        )
