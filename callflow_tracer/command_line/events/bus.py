"""
EventBus — Observer pattern implementation for the CLI layer.

DSA rationale:
  - Subscriber store: dict[EventType, list[Callable]] — O(1) lookup by event
    type, O(n) fan-out where n = subscriber count for that event type.
    For the CLI layer n ≤ 5 in practice; fan-out cost is negligible.
  - Dead-letter Queue: collections.deque — O(1) append/popleft. Bounded
    (maxlen=500). Stores events that had zero subscribers so they're not
    silently dropped — observable in tests and REPL debug mode.

The bus is sync-first and deliberately simple. The async upgrade path:
  Replace the fan-out loop with asyncio.gather(*[h(event) for h in handlers])
  and mark emit() as async. The Queue becomes asyncio.Queue for backpressure.

Failure policy (matches EventBus in the agent runtime design):
  A failing handler logs a warning and does NOT abort the remaining handlers
  or raise to the caller. One bad subscriber must not crash the command.
"""

from __future__ import annotations

import logging
from collections import defaultdict, deque
from typing import Callable

from .types import CLIEvent, EventType

log = logging.getLogger(__name__)

# Type alias
EventHandler = Callable[[CLIEvent], None]


class EventBus:
    """
    Pub/sub hub for CLI lifecycle events.

    Usage:
        bus = EventBus()

        # Subscribe
        bus.subscribe(EventType.COMMAND_SUCCEEDED, my_handler)

        # Emit (called by middleware, not commands directly)
        bus.emit(CLIEvent(EventType.COMMAND_SUCCEEDED, command_name="trace"))

        # Inspect dead letters in tests
        assert len(bus.dead_letters) == 0
    """

    def __init__(self, dead_letter_capacity: int = 500) -> None:
        # Primary HashMap: EventType → list of handlers
        self._handlers: dict[EventType, list[EventHandler]] = defaultdict(list)
        # Dead-letter queue for events with no subscribers (bounded deque)
        self.dead_letters: deque[CLIEvent] = deque(maxlen=dead_letter_capacity)

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Register a handler for an event type. Handlers receive CLIEvent."""
        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
        handlers = self._handlers.get(event_type, [])
        self._handlers[event_type] = [h for h in handlers if h is not handler]

    def subscribe_all(self, handler: EventHandler) -> None:
        """Subscribe a handler to every EventType (useful for audit loggers)."""
        for et in EventType:
            self.subscribe(et, handler)

    def emit(self, event: CLIEvent) -> None:
        """
        Fan-out event to all registered handlers.
        Failures in individual handlers are logged but do not propagate.
        Events with no subscribers go to the dead-letter queue.
        """
        handlers = self._handlers.get(event.type, [])
        if not handlers:
            self.dead_letters.append(event)
            return
        for handler in handlers:
            try:
                handler(event)
            except Exception as exc:
                log.warning(
                    "EventBus handler %s failed for %s: %s",
                    handler,
                    event.type.name,
                    exc,
                )

    def __repr__(self) -> str:
        counts = {et.name: len(hs) for et, hs in self._handlers.items() if hs}
        return f"<EventBus subscribers={counts}>"
