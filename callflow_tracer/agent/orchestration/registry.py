"""
orchestration/registry.py — Agent registry factory.

Creates all agent instances with one injected LLM provider and returns a
dict[name → agent] for O(1) lookup by the orchestrator.

Plugin agents (from ~/.callflow/agents/*.py) are merged after built-ins
so they can be dispatched by name alongside the built-in specialists.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ..agents.base import BaseAgent
from ..agents.context import ContextAgent
from ..agents.cost import CostAgent
from ..agents.grep import GrepAgent
from ..agents.router import RouterAgent
from ..agents.synthesizer import SynthesizerAgent
from ..agents.why import WhyAgent
from ..skills.base import SkillRegistry
from .plugin_loader import load_agent_plugins

if TYPE_CHECKING:
    from ...ai.llm_provider import LLMProvider


def build_agent_registry(
    provider: "LLMProvider",
    plugin_dir: Path | None = None,
    skill_registry: SkillRegistry | None = None,
) -> dict[str, BaseAgent]:
    """
    Create every swarm agent with the shared provider.

    Plugin agents loaded from plugin_dir (default: ~/.callflow/agents/) are
    merged after built-ins. Built-in names always take precedence.

    skill_registry is passed to RouterAgent so it can include available skills
    in its system prompt and assign them in the dispatch plan.
    """
    plugins = load_agent_plugins(provider, plugin_dir=plugin_dir)
    plugin_names = frozenset(plugins.keys())

    registry: dict[str, BaseAgent] = {
        "RouterAgent": RouterAgent(
            provider,
            plugin_agent_names=plugin_names,
            skill_registry=skill_registry,
        ),
        "ContextAgent": ContextAgent(provider),
        "WhyAgent": WhyAgent(provider),
        "CostAgent": CostAgent(provider),
        "GrepAgent": GrepAgent(provider),
        "SynthesizerAgent": SynthesizerAgent(provider),
    }
    registry.update(plugins)
    return registry
