#!/usr/bin/env python3
"""
CLI bootstrap — wires registry, middleware chain, event bus, and dispatcher.

Responsibilities of this file (and ONLY this file):
  1. Build the CommandRegistry (HashMap of command objects)
  2. Build the EventBus and subscribe any global observers
  3. Build the MiddlewareChain (Chain of Responsibility)
  4. Discover any plugin commands from ~/.callflow/plugins/
  5. Parse argv with argparse (using subparsers from each command)
  6. Dispatch: resolve command → run through middleware chain → sys.exit

Nothing else. Command logic lives in commands/. Patterns live in their layers.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys

from .. import __version__
from .commands import (
    TraceCommand, FlamegraphCommand, ProfileCommand, MemoryLeakCommand,
    CompareCommand, ExplainCommand, BenchmarkCommand, InfoCommand, SummaryCommand,
    QualityCommand, PredictCommand, ChurnCommand,
    OtelCommand, ExportCommand,
    ContextCommand, WhyCommand, AgentTraceCommand, AskCommand,
)
from .events import EventBus
from .factory import CommandFactory
from .interfaces.command import CommandContext, CommandResult
from .middleware import (
    MiddlewareChain,
    LoggingMiddleware,
    ValidationMiddleware,
    TimingMiddleware,
    TracingMiddleware,
)
from .registry import CommandRegistry

# ── Factory Pattern: new product commands ─────────────────────────────────────
# A dict of name → zero-arg constructor.  Adding a new command = one new entry.
# _build_registry() calls each constructor — concrete instantiation is deferred
# (lazy) so startup pays no cost for commands that are never used.
_NEW_COMMAND_FACTORIES: dict[str, type] = {
    "context":     ContextCommand,
    "why":         WhyCommand,
    "agent-trace": AgentTraceCommand,
    "ask":         AskCommand,
}


def _create_new_commands() -> list:
    """Instantiate new product commands via the factory dict."""
    return [cls() for cls in _NEW_COMMAND_FACTORIES.values()]


# ── Default command set (registration order = --help order) ───────────────────
_DEFAULT_COMMANDS = [
    TraceCommand(),
    FlamegraphCommand(),
    ProfileCommand(),
    MemoryLeakCommand(),
    CompareCommand(),
    ExplainCommand(),
    BenchmarkCommand(),
    InfoCommand(),
    SummaryCommand(),
    QualityCommand(),
    PredictCommand(),
    ChurnCommand(),
    OtelCommand(),
    ExportCommand(),
    # Product commands (created via Factory Pattern)
    *_create_new_commands(),
]


def _build_registry() -> CommandRegistry:
    """Populate registry from default command set + optional plugin discovery."""
    registry = CommandRegistry()
    for cmd in _DEFAULT_COMMANDS:
        registry.register(cmd)
    return registry


def _build_middleware(bus: EventBus) -> MiddlewareChain:
    """
    Compose the middleware chain in execution order:
      LoggingMiddleware (outermost) → ValidationMiddleware → TimingMiddleware
      → TracingMiddleware (innermost, runs just before execute())

    Execution flow on entry:  Logging → Validation → Timing → Tracing → execute()
    Execution flow on exit:   Tracing → Timing → Logging (each sees the result)
    """
    return (
        MiddlewareChain()
        .use(LoggingMiddleware(bus))
        .use(ValidationMiddleware())
        .use(TimingMiddleware())
        .use(TracingMiddleware(bus))
    )


def _build_argparser(registry: CommandRegistry) -> argparse.ArgumentParser:
    """Build the top-level argparse parser from the registered command set."""
    parser = argparse.ArgumentParser(
        prog="callflow-tracer",
        description="CallFlow Tracer — Visualize and analyze Python function call flows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  callflow-tracer trace script.py -o output.html
  callflow-tracer flamegraph script.py -o flamegraph.html
  callflow-tracer quality . -o quality_report.html
  callflow-tracer otel trace.json --service-name my-service
  callflow-tracer compare before.json after.json
        """,
    )
    parser.add_argument("--version", action="version", version=f"callflow-tracer {__version__}")
    parser.add_argument("--debug", action="store_true", help=argparse.SUPPRESS)

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    for cmd in registry.all():
        sub = subparsers.add_parser(
            cmd.name,
            help=cmd.help,
            aliases=cmd.aliases,
        )
        cmd.add_arguments(sub)

    # Funnel CLI is click-based — register as passthrough if available
    if importlib.util.find_spec("callflow_tracer.funnel.cli") is not None:
        fp = subparsers.add_parser(
            "funnel",
            help="Funnel analysis commands",
            add_help=False,
        )
        fp.add_argument("funnel_args", nargs=argparse.REMAINDER)

    return parser


def _dispatch_funnel(parsed: argparse.Namespace) -> int:
    """Delegate funnel subcommand to the click-based funnel CLI."""
    from ..funnel.cli import funnel as funnel_group
    funnel_args = getattr(parsed, "funnel_args", []) or []
    try:
        funnel_group.main(funnel_args, standalone_mode=False)
        return 0
    except SystemExit as exc:
        return int(exc.code) if exc.code is not None else 0
    except Exception as exc:
        print(f"Error in funnel command: {exc}", file=sys.stderr)
        return 1


def main(args: list[str] | None = None) -> int:
    """
    Entry point. Returns exit code (caller does sys.exit).

    Flow:
      build registry → build bus → build middleware chain
      → parse argv → resolve command → run pipeline → return exit_code
    """
    registry = _build_registry()
    bus = EventBus()
    chain = _build_middleware(bus)
    parser = _build_argparser(registry)

    # Optional: discover plugin commands from ~/.callflow/plugins/
    import os
    plugin_dir = os.path.expanduser("~/.callflow/plugins")
    if os.path.isdir(plugin_dir):
        factory = CommandFactory()
        factory.discover_plugins(plugin_dir)
        # Re-register any new commands found (safe: CommandRegistry raises on dupe)
        for name in factory.registered_names():
            cmd = factory.create(name)
            if not registry.contains(name):
                registry.register(cmd)
                sub = parser._subparsers._group_actions[0]  # type: ignore[attr-defined]
                s = sub.add_parser(name, help=cmd.help)
                cmd.add_arguments(s)

    parsed = parser.parse_args(args)

    if not parsed.command:
        parser.print_help()
        return 1

    if parsed.command == "funnel":
        return _dispatch_funnel(parsed)

    # Resolve command from registry (O(1) HashMap lookup)
    try:
        command = registry.resolve(parsed.command)
    except KeyError as e:
        print(str(e), file=sys.stderr)
        return 1

    # Build context (value object for this invocation)
    ctx = CommandContext(args=parsed, raw_argv=args or sys.argv[1:])

    # Run through middleware chain; terminal handler calls command.execute()
    def terminal(c: CommandContext) -> CommandResult:
        return command.execute(c)

    result = chain.run(ctx, terminal)

    if result.error and not result.ok:
        print(f"Error: {result.error}", file=sys.stderr)

    return result.exit_code


# Preserve backward-compatible class name for any callers importing CallflowCLI
class CallflowCLI:
    """Thin wrapper kept for backward compatibility. Prefer calling main() directly."""

    def run(self, args: list[str] | None = None) -> int:
        return main(args)


if __name__ == "__main__":
    sys.exit(main())
