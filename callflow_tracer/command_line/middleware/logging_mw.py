"""Logging middleware — emits COMMAND_STARTED / SUCCEEDED / FAILED events."""

from __future__ import annotations

import logging

from ..events.bus import EventBus
from ..events.types import CLIEvent, EventType
from ..interfaces.command import CommandContext, CommandResult
from ..interfaces.middleware import Middleware, NextHandler

log = logging.getLogger("callflow.cli")


class LoggingMiddleware(Middleware):
    """
    Outermost middleware: fires Observer events and writes structured logs.

    Subscribing to EventType.COMMAND_STARTED lets the agent runtime know a
    command is about to execute (useful for trace correlation and cost tracking).
    """

    def __init__(self, bus: EventBus) -> None:
        self._bus = bus

    def process(self, ctx: CommandContext, call_next: NextHandler) -> CommandResult:
        name = ctx.args.command if hasattr(ctx.args, "command") else "unknown"

        self._bus.emit(CLIEvent(EventType.COMMAND_STARTED, name))
        log.debug("command=%s argv=%s", name, ctx.raw_argv)

        result = call_next(ctx)

        if result.ok:
            self._bus.emit(CLIEvent(
                EventType.COMMAND_SUCCEEDED, name,
                payload={"duration_ms": result.duration_ms, "data": result.data},
            ))
            log.debug("command=%s exit=0 duration_ms=%.1f", name, result.duration_ms)
        else:
            self._bus.emit(CLIEvent(
                EventType.COMMAND_FAILED, name,
                payload={"exit_code": result.exit_code, "error": result.error},
            ))
            log.warning("command=%s exit=%d error=%s", name, result.exit_code, result.error)

        return result
