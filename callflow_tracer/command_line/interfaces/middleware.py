"""
Middleware interface for the Chain of Responsibility pattern.

Each middleware in the chain receives a CommandContext, may mutate ctx.extra,
and calls next_handler() to continue the chain. If it does NOT call
next_handler(), the chain is short-circuited (useful for auth/validation).

This is intentionally sync-first. The async variant (for REPL / streaming)
is a future extension: replace Callable with Awaitable[CommandResult] and
wrap the chain in asyncio.run().
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable

from .command import CommandContext, CommandResult

# Type alias: a function that continues the chain when called.
NextHandler = Callable[[CommandContext], CommandResult]


class Middleware(ABC):
    """
    Chain of Responsibility node.

    process() receives context and a `call_next` callable.
    Middleware must call call_next(ctx) to continue; returning without calling
    it short-circuits the chain (e.g. validation failure).

    Example:

        class TimingMiddleware(Middleware):
            def process(self, ctx, call_next):
                start = time.monotonic()
                result = call_next(ctx)
                result.duration_ms = (time.monotonic() - start) * 1000
                return result
    """

    @abstractmethod
    def process(self, ctx: CommandContext, call_next: NextHandler) -> CommandResult:
        ...

    def __repr__(self) -> str:
        return f"<Middleware:{type(self).__name__}>"
