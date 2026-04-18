"""
agents — Layer 3: all swarm agents.

Public surface:
  BaseAgent                                        ← base.py
  RouterAgent                                      ← router.py
  ContextAgent, WhyAgent, CostAgent, GrepAgent     ← specialist agents
  SynthesizerAgent                                 ← synthesizer.py
"""

from .base import BaseAgent
from .context import ContextAgent
from .cost import CostAgent
from .grep import GrepAgent
from .router import RouterAgent
from .synthesizer import SynthesizerAgent
from .why import WhyAgent

__all__ = [
    "BaseAgent",
    "RouterAgent",
    "ContextAgent",
    "WhyAgent",
    "CostAgent",
    "GrepAgent",
    "SynthesizerAgent",
]
