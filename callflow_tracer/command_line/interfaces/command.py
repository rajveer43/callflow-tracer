"""
Command Pattern interface.

Every CLI command is an object that knows how to:
  - describe itself (name, help, aliases)
  - register its arguments with argparse
  - execute given a CommandContext

CommandContext is the shared value object passed through the entire pipeline.
It carries parsed args, metadata, and accumulates results — similar to
ExecutionContext in the agent runtime but scoped to one CLI invocation.

CommandResult is a value object returned by execute(). Returning an object
(not a raw int) lets middleware inspect exit codes, errors, and timing
without parsing stdout.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CommandContext:
    """
    Immutable-by-convention carrier for one CLI invocation.

    Passed from the dispatcher through every middleware and into execute().
    Middleware may attach metadata via the `extra` dict — use namespaced keys
    (e.g. "tracing.start_time") to avoid collisions between middleware layers.

    DSA note: `extra` is a HashMap — O(1) read/write for middleware metadata.
    `history` is a Stack (list used as LIFO) — push on entry, used by REPL
    and undo support.
    """
    args: Namespace                          # parsed argparse namespace
    raw_argv: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)   # middleware scratch pad
    invoked_at: float = field(default_factory=time.monotonic)


@dataclass
class CommandResult:
    """
    Value object returned by BaseCommand.execute().

    exit_code follows POSIX convention (0 = success, non-zero = error).
    error is set when exit_code != 0.
    data carries any structured output the command wants to expose to callers
    (useful for programmatic use and testing without parsing stdout).
    """
    exit_code: int = 0
    error: str | None = None
    data: dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0

    @property
    def ok(self) -> bool:
        return self.exit_code == 0

    @classmethod
    def success(cls, data: dict | None = None, **kwargs) -> "CommandResult":
        return cls(exit_code=0, data=data or {}, **kwargs)

    @classmethod
    def failure(cls, error: str, exit_code: int = 1) -> "CommandResult":
        return cls(exit_code=exit_code, error=error)


class BaseCommand(ABC):
    """
    Command Pattern: every CLI command is a first-class object.

    Subclasses implement:
      - name: stable identifier used as registry key and CLI subcommand name
      - help: one-line description shown in --help
      - add_arguments(): registers flags/options with argparse
      - execute(): performs the command; returns CommandResult

    Design contract:
      - Commands are STATELESS. All state lives in CommandContext.
        This makes them trivially testable: call execute(ctx) directly.
      - Commands do NOT call sys.exit(). They return CommandResult.
        The dispatcher converts exit_code to sys.exit().
      - Commands do NOT import from main.py or the dispatcher.
        Dependency direction: commands → core domain, never upward.

    Aliases allow multiple CLI names to map to the same command object.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Stable registry key and primary CLI subcommand name."""
        ...

    @property
    def aliases(self) -> list[str]:
        """Optional alternative names. e.g. ['trc'] for 'trace'."""
        return []

    @property
    def help(self) -> str:
        """One-line description shown in --help listing."""
        return ""

    @abstractmethod
    def add_arguments(self, parser: ArgumentParser) -> None:
        """Register this command's flags and positional args with argparse."""
        ...

    @abstractmethod
    def execute(self, ctx: CommandContext) -> CommandResult:
        """
        Execute the command. Must not raise — catch and return CommandResult.failure().
        """
        ...

    def __repr__(self) -> str:
        return f"<Command:{self.name}>"
