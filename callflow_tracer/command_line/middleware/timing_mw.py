"""Timing middleware — measures wall-clock duration and stamps CommandResult."""

from __future__ import annotations

import time

from ..interfaces.command import CommandContext, CommandResult
from ..interfaces.middleware import Middleware, NextHandler


class TimingMiddleware(Middleware):
    """
    Stamps result.duration_ms with wall-clock time of the execute() call.
    Placed inside LoggingMiddleware so the logged duration is accurate.
    """

    def process(self, ctx: CommandContext, call_next: NextHandler) -> CommandResult:
        start = time.monotonic()
        result = call_next(ctx)
        result.duration_ms = (time.monotonic() - start) * 1000
        return result
