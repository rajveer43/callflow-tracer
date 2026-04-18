"""
orchestration — Layer 4: swarm execution and composition.
"""

from .builder import SwarmBuilder
from .executor import ExecutorStrategy, ParallelExecutor, SequentialExecutor
from .plugin_loader import AgentPluginApi, PluginError, load_agent_plugins
from .registry import build_agent_registry
from .swarm import Swarm

from ..skills import Skill, SkillRegistry, SkillTier, build_skill_registry

__all__ = [
    "ExecutorStrategy",
    "ParallelExecutor",
    "SequentialExecutor",
    "build_agent_registry",
    "SwarmBuilder",
    "Swarm",
    "AgentPluginApi",
    "PluginError",
    "load_agent_plugins",
    "Skill",
    "SkillRegistry",
    "SkillTier",
    "build_skill_registry",
]
