"""
core — Layer 1 public surface.

No business logic lives here — only re-exports for clean imports by layers above.
"""

from .bindings import BindingStore, CwdBinding
from .context import SwarmContext
from .events import EventKind, SwarmMessage
from .exceptions import (
    AgentError,
    AgentTimeoutError,
    DispatchError,
    ProviderError,
    ToolError,
)
from .hooks import HookBus, HookKind, NullHookBus
from .types import (
    AGENT_NAMES,
    DISPATCHABLE_AGENTS,
    AgentTask,
    DispatchPlan,
    Finding,
    NullFinding,
)

__all__ = [
    "AGENT_NAMES", "DISPATCHABLE_AGENTS",
    "AgentTask", "DispatchPlan", "Finding", "NullFinding",
    "SwarmContext",
    "EventKind", "SwarmMessage",
    "AgentError", "AgentTimeoutError", "DispatchError", "ProviderError", "ToolError",
    "HookBus", "HookKind", "NullHookBus",
    "BindingStore", "CwdBinding",
]
