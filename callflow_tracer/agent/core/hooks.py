"""
core/hooks.py — HookBus and NullHookBus (Observer Pattern).

HookBus is the event bus threaded through SwarmContext. Agents fire events;
external subscribers react without modifying agent code.

Design patterns:
  Observer      — HookBus.subscribe() / fire(); agents don't know who's watching
  Null Object   — NullHookBus is the default; zero overhead when unused
  Template Method compatibility — fire points are fixed in BaseAgent.run() skeleton

DSA:
  defaultdict(list) — O(1) subscribe, O(K) fire where K = subscribers ≤ 5
  Exceptions in callbacks are caught and swallowed — hooks never crash the swarm.

Layer 1 — no imports from tools/, agents/, or orchestration/.
"""

from __future__ import annotations

from collections import defaultdict
from enum import Enum
from typing import Callable


class HookKind(str, Enum):
    AGENT_START    = "agent_start"
    TOOL_CALLED    = "tool_called"
    TOOL_RESULT    = "tool_result"
    FINDING_READY  = "finding_ready"
    SWARM_START    = "swarm_start"
    SWARM_COMPLETE = "swarm_complete"


HookCallback = Callable[["HookKind", dict], None]


class HookBus:
    """
    Observable event bus for swarm lifecycle events.

    Subscribers register for specific HookKind values; the swarm fires events
    at defined points in the pipeline. All callbacks are fire-and-forget:
    exceptions in callbacks are caught and logged (not propagated).
    """

    def __init__(self) -> None:
        self._subs: defaultdict[HookKind, list[HookCallback]] = defaultdict(list)

    def subscribe(self, kind: HookKind, fn: HookCallback) -> None:
        """Register fn to be called whenever kind is fired."""
        self._subs[kind].append(fn)

    def fire(self, kind: HookKind, payload: dict) -> None:
        """Invoke all subscribers for kind. Exceptions in callbacks are swallowed."""
        for fn in self._subs[kind]:
            try:
                fn(kind, payload)
            except Exception:
                pass  # Never let hooks crash the swarm


class NullHookBus(HookBus):
    """
    No-op bus — zero overhead when no subscribers are registered.
    Used as the default in SwarmContext so every code path can call
    fire() without None checks.
    """

    def fire(self, kind: HookKind, payload: dict) -> None:
        pass  # no-op

    def subscribe(self, kind: HookKind, fn: HookCallback) -> None:
        pass  # no-op — subscriptions silently discarded
