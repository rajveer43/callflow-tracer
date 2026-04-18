"""
MiddlewareChain — Chain of Responsibility builder.

DSA rationale:
  - Middleware list is a Python list (dynamic array). Building the chain is
    O(n). Each invocation traverses the chain by building a nested closure
    stack — O(n) setup, O(1) per node during traversal.
  - The closure-based approach (wrap end_handler in successive middleware
    closures) avoids recursion depth issues: Python's default recursion limit
    is 1000; with ≤ 20 middleware layers, zero risk. The alternative
    (actual recursion) would be cleaner but fragile at scale.

Usage:
    chain = MiddlewareChain()
    chain.use(LoggingMiddleware(bus))
    chain.use(ValidationMiddleware())
    chain.use(TimingMiddleware())

    result = chain.run(ctx, terminal_handler)
    # terminal_handler is the function that actually calls command.execute(ctx)

Order matters: first added = outermost wrapper (runs first on entry, last on exit).
This matches Express.js / WSGI middleware conventions.
"""

from __future__ import annotations

from typing import Callable

from ..interfaces.command import CommandContext, CommandResult
from ..interfaces.middleware import Middleware, NextHandler


class MiddlewareChain:
    """
    Builds and executes a chain of middleware around a terminal handler.

    Each call to use() appends a middleware layer. run() composes them into
    a single callable using closure wrapping, then invokes it.
    """

    def __init__(self) -> None:
        # Ordered list of middleware — insertion order is execution order.
        self._layers: list[Middleware] = []

    def use(self, middleware: Middleware) -> "MiddlewareChain":
        """Append a middleware layer. Returns self for fluent chaining."""
        self._layers.append(middleware)
        return self

    def run(
        self,
        ctx: CommandContext,
        terminal: Callable[[CommandContext], CommandResult],
    ) -> CommandResult:
        """
        Compose the middleware stack and execute it.

        Builds from the inside out: start with `terminal` as the innermost
        handler, then wrap each middleware around it in reverse order.
        The outermost wrapper (first-added middleware) is called first.

        Example with [A, B, C] and terminal T:
            composed = A(B(C(T)))
            execution: A.process → B.process → C.process → T → C exit → B exit → A exit
        """
        composed: NextHandler = terminal
        for middleware in reversed(self._layers):
            # Capture `middleware` and `composed` in a closure to avoid
            # the classic loop-variable-capture bug.
            outer_mw = middleware
            inner_next = composed

            def make_next(mw: Middleware, nxt: NextHandler) -> NextHandler:
                def _next(c: CommandContext) -> CommandResult:
                    return mw.process(c, nxt)
                return _next

            composed = make_next(outer_mw, inner_next)

        return composed(ctx)

    def __len__(self) -> int:
        return len(self._layers)

    def __repr__(self) -> str:
        layers = " → ".join(type(m).__name__ for m in self._layers)
        return f"<MiddlewareChain [{layers}]>"
