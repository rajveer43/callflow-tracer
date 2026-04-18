"""
core/types.py — Canonical data types shared across the entire agent system.

Rules:
  - No business logic — only data + trivial derived properties.
  - No imports from tools/, agents/, or orchestration/.
  - All types here are value objects (dataclasses or frozen dataclasses).

DSA:
  frozenset[str] : O(1) agent-name membership (AGENT_NAMES, _DISPATCHABLE)
  dict           : DispatchPlan.hints_for — O(N) where N ≤ 5 (acceptable)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# ── Canonical agent name registry ─────────────────────────────────────────────

AGENT_NAMES: frozenset[str] = frozenset({
    "RouterAgent",
    "ContextAgent",
    "WhyAgent",
    "CostAgent",
    "GrepAgent",
    "SynthesizerAgent",
})

# Agents the router may dispatch (excludes Router itself and Synthesizer)
DISPATCHABLE_AGENTS: frozenset[str] = frozenset({
    "ContextAgent",
    "WhyAgent",
    "CostAgent",
    "GrepAgent",
})


# ── Finding — output of one specialist ────────────────────────────────────────

@dataclass
class Finding:
    """
    Structured result from a specialist agent.

    confidence  : 0.0–1.0; SynthesizerAgent weights findings by this.
    raw_data    : untyped dict forwarded to the synthesizer as context.
    error       : None for successful findings; set on NullFinding.
    """

    agent_name: str
    summary: str                        # ≤ 3 sentences — for synthesizer
    raw_data: dict[str, Any]
    confidence: float                   # 0.0–1.0
    tool_calls_made: list[str]
    error: str | None = None

    @property
    def is_null(self) -> bool:
        """True if this finding carries no useful information."""
        return bool(self.error) or not self.summary.strip()

    def truncated_summary(self, max_chars: int = 120) -> str:
        return self.summary[:max_chars] + ("…" if len(self.summary) > max_chars else "")


class NullFinding(Finding):
    """
    Null Object pattern — returned when an agent fails or is not dispatched.

    SynthesizerAgent calls ctx.active_findings() which silently skips these,
    eliminating all None checks across the codebase.
    """

    def __init__(self, agent_name: str, error: str = "not dispatched") -> None:
        super().__init__(
            agent_name=agent_name,
            summary="",
            raw_data={},
            confidence=0.0,
            tool_calls_made=[],
            error=error,
        )


# ── AgentTask — unit of work in a DispatchPlan ────────────────────────────────

@dataclass
class AgentTask:
    """
    One work item produced by RouterAgent for one specialist.

    hints       : free-form context to help the specialist focus its ReAct loop.
                  e.g. {"function": "apply_fee", "trace_script": "tests/test_api.py"}
    skills      : skill names to activate on this agent before it runs.
                  e.g. ["DependencyTrace", "SecurityScan"]
    extra_tools : individual tool names to add beyond what the agent's skills provide.
                  e.g. ["read_file"] — looked up in TOOL_CATALOG at configure time.
    """

    agent_name: str
    hints: dict[str, Any] = field(default_factory=dict)
    skills: list[str] = field(default_factory=list)
    extra_tools: list[str] = field(default_factory=list)


# ── DispatchPlan — RouterAgent's output ───────────────────────────────────────

@dataclass
class DispatchPlan:
    """
    Produced by RouterAgent; consumed by the Swarm executor.

    tasks     : ordered list of AgentTasks to execute
    mode      : "parallel" | "sequential"
    reasoning : RouterAgent's chain-of-thought (for transparency / debugging)
    """

    tasks: list[AgentTask]
    mode: str = "parallel"
    reasoning: str = ""

    def agent_names(self) -> list[str]:
        """Ordered list of agent names to activate. O(N)."""
        return [t.agent_name for t in self.tasks]

    def hints_for(self, agent_name: str) -> dict[str, Any]:
        """Return hints for a specific agent. O(N), N ≤ 5."""
        for task in self.tasks:
            if task.agent_name == agent_name:
                return task.hints
        return {}

    def is_empty(self) -> bool:
        return not self.tasks
