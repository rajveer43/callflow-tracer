"""
core/exceptions.py — Typed exception hierarchy for the agent system.

All agent exceptions inherit from AgentError so callers can catch
the whole family with one except clause if needed.

Layer 1 — no imports from the rest of the agent package.
"""

from __future__ import annotations


class AgentError(Exception):
    """Base class for all agent-system errors."""


class ToolError(AgentError):
    """Raised when a tool execution fails in a non-recoverable way."""

    def __init__(self, tool_name: str, reason: str) -> None:
        self.tool_name = tool_name
        self.reason = reason
        super().__init__(f"Tool '{tool_name}' failed: {reason}")


class ProviderError(AgentError):
    """Raised when no LLM provider can be configured."""

    def __init__(self, detail: str = "") -> None:
        msg = (
            "No LLM provider is configured.\n"
            "Set one of:\n"
            "  export ANTHROPIC_API_KEY=sk-ant-...\n"
            "  export OPENAI_API_KEY=sk-...\n"
            "  export GEMINI_API_KEY=AI...\n"
            "Or pass: ask(..., api_key=KEY, provider='anthropic')"
        )
        if detail:
            msg = f"{detail}\n\n{msg}"
        super().__init__(msg)


class DispatchError(AgentError):
    """Raised when RouterAgent cannot produce a valid DispatchPlan."""


class AgentTimeoutError(AgentError):
    """Raised when a specialist agent exceeds its timeout budget."""

    def __init__(self, agent_name: str, timeout_s: int) -> None:
        self.agent_name = agent_name
        super().__init__(f"Agent '{agent_name}' timed out after {timeout_s}s")
