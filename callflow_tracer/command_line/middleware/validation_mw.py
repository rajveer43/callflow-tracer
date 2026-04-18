"""
Validation middleware — short-circuits the chain on bad input.

Chain of Responsibility: if validation fails, this node returns a failure
result immediately WITHOUT calling call_next(). The remaining middleware
and the command itself never run. This is the correct pattern for input
guards: validate early, fail fast, no side effects.
"""

from __future__ import annotations

import os
import sys

from ..interfaces.command import CommandContext, CommandResult
from ..interfaces.middleware import Middleware, NextHandler


class ValidationMiddleware(Middleware):
    """
    Pre-execution validation. Current checks:
      - Script file exists (for trace/flamegraph/profile/memory-leak)
      - JSON trace file is readable (for compare/explain/export)
      - Sampling rate is in [0.0, 1.0]

    Add new validators by appending to _validators. Each validator is a
    Strategy: a callable(ctx) -> str | None (None = pass, str = error message).
    """

    def __init__(self) -> None:
        # Strategy pattern: list of validation functions.
        # Each returns None on pass or an error string on failure.
        self._validators = [
            self._validate_script_exists,
            self._validate_trace_file_readable,
            self._validate_sampling_rate,
        ]

    def process(self, ctx: CommandContext, call_next: NextHandler) -> CommandResult:
        for validator in self._validators:
            error = validator(ctx)
            if error:
                # Short-circuit: do not call call_next
                print(f"Validation error: {error}", file=sys.stderr)
                return CommandResult.failure(error)
        return call_next(ctx)

    # ── Individual validators (Strategy callables) ────────────────────────────

    @staticmethod
    def _validate_script_exists(ctx: CommandContext) -> str | None:
        script = getattr(ctx.args, "script", None)
        if script and not os.path.isfile(script):
            return f"Script not found: {script}"
        return None

    @staticmethod
    def _validate_trace_file_readable(ctx: CommandContext) -> str | None:
        for attr in ("file", "file1", "file2", "before", "after", "input"):
            path = getattr(ctx.args, attr, None)
            if path and not os.path.isfile(path):
                return f"File not found: {path}"
        return None

    @staticmethod
    def _validate_sampling_rate(ctx: CommandContext) -> str | None:
        rate = getattr(ctx.args, "sampling_rate", None)
        if rate is not None and not (0.0 <= rate <= 1.0):
            return f"--sampling-rate must be between 0.0 and 1.0, got {rate}"
        return None
