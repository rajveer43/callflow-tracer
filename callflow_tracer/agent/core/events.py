"""
core/events.py — Swarm event types.

SwarmMessage is the append-only audit record written by every agent.
EventKind is a StrEnum so events are both type-safe and string-comparable.

Layer 1 — imports nothing from the rest of the agent package.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EventKind(str, Enum):
    """All possible event kinds in the swarm audit trail."""

    STARTED          = "started"
    TOOL_CALLED      = "tool_called"
    FINDING_READY    = "finding_ready"
    HANDOFF_REQUEST  = "handoff_request"
    ERROR            = "error"
    SWARM_START      = "swarm_start"
    SWARM_COMPLETE   = "swarm_complete"


@dataclass(frozen=True)
class SwarmMessage:
    """
    One immutable event record in the swarm audit trail.

    frozen=True: messages are never modified after creation — the list is
    append-only.  This makes the audit trail safe to read from any thread
    without locking.
    """

    from_agent: str
    event: EventKind
    payload: dict[str, Any]
    timestamp: float = field(default_factory=time.monotonic)

    def __str__(self) -> str:
        return f"[{self.from_agent}] {self.event.value}: {self.payload}"
