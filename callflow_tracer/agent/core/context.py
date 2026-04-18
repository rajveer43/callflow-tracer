"""
core/context.py — SwarmContext: the single shared spine of the swarm.

Every agent reads from and writes to SwarmContext. Agents never import
each other — SwarmContext is the only shared mutable object.

Layer 1 — imports only from core/ (same layer). No tools, no agents.

DSA:
  dict[str, Finding]  : O(1) finding lookup/write by agent name
  list[SwarmMessage]  : append-only audit trail — O(1) amortised append
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from .events import EventKind, SwarmMessage
from .hooks import HookBus, HookKind, NullHookBus
from .types import AgentTask, DispatchPlan, Finding


# ── SwarmContext ───────────────────────────────────────────────────────────────

@dataclass
class SwarmContext:
    """
    The single shared state object threaded through every agent.

    Read-only fields (set at construction):
      question, cwd, scope, trace_script

    Written by RouterAgent:
      dispatch_plan

    Written by specialist agents (one entry each):
      findings[agent_name]

    Written by SynthesizerAgent:
      final_answer

    Thread safety: dict.__setitem__ and list.append are GIL-protected in CPython.
    The Swarm executor guarantees each agent writes only its own slot in findings.
    No explicit locking is required for these specific operations.
    """

    question: str                         # original user question
    cwd: str                              # root directory to analyse
    scope: str | None = None              # optional subdirectory filter
    trace_script: str | None = None       # optional explicit trace target

    # Set by RouterAgent (always before specialists start)
    dispatch_plan: DispatchPlan | None = None

    # Written by each specialist; keyed by agent name for O(1) lookup
    findings: dict[str, Finding] = field(default_factory=dict)

    # Append-only audit trail — thread-safe (GIL + single-writer per agent)
    messages: list[SwarmMessage] = field(default_factory=list)

    # Set by SynthesizerAgent; read by the caller
    final_answer: str | None = None

    # Observable event bus — NullHookBus by default (zero overhead)
    hook_bus: HookBus = field(default_factory=NullHookBus)

    # ── Convenience methods ───────────────────────────────────────────────

    def add_message(
        self,
        from_agent: str,
        event: EventKind | str,
        payload: dict,
    ) -> None:
        """Append one audit event. Accepts EventKind enum or plain string."""
        kind = event if isinstance(event, EventKind) else EventKind(event)
        self.messages.append(SwarmMessage(from_agent=from_agent, event=kind, payload=payload))

    def set_finding(self, finding: Finding) -> None:
        """Write a finding, emit a finding_ready audit event, and fire the hook."""
        self.findings[finding.agent_name] = finding
        self.add_message(
            finding.agent_name,
            EventKind.FINDING_READY,
            {"summary": finding.summary[:120]},
        )
        self.hook_bus.fire(
            HookKind.FINDING_READY,
            {"agent": finding.agent_name, "summary": finding.summary[:120]},
        )

    def active_findings(self) -> list[Finding]:
        """Return non-null findings only — used by SynthesizerAgent. O(N)."""
        return [f for f in self.findings.values() if not f.is_null]

    def search_scope(self) -> str:
        """Resolved directory to search — scope joined with cwd, or just cwd."""
        if self.scope:
            return os.path.join(self.cwd, self.scope)
        return self.cwd
