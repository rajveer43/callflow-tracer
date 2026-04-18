"""
Tests for the command_line architecture refactor.

Coverage:
  - CommandRegistry (HashMap, alias lookup, duplicate guard)
  - EventBus (fan-out, dead-letter, failing handler isolation)
  - MiddlewareChain (ordering, short-circuit, timing stamp)
  - CommandResult value object
  - CommandContext value object
  - CommandFactory (register + create)
  - Concrete commands via execute() with mock dependencies
  - main() integration (full dispatch with --help and real argv)
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import textwrap
from argparse import Namespace
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from callflow_tracer.command_line.events import EventBus, CLIEvent, EventType
from callflow_tracer.command_line.factory import CommandFactory
from callflow_tracer.command_line.interfaces import BaseCommand, CommandContext, CommandResult
from callflow_tracer.command_line.middleware import (
    MiddlewareChain,
    LoggingMiddleware,
    ValidationMiddleware,
    TimingMiddleware,
    TracingMiddleware,
)
from callflow_tracer.command_line.middleware.tracing_mw import get_execution_stack
from callflow_tracer.command_line.registry import CommandRegistry


# ── Fixtures & helpers ─────────────────────────────────────────────────────────

class EchoCommand(BaseCommand):
    """Minimal test command: echoes a message into result.data."""

    @property
    def name(self) -> str:
        return "echo"

    @property
    def aliases(self) -> list[str]:
        return ["ec"]

    @property
    def help(self) -> str:
        return "Test echo command"

    def add_arguments(self, parser) -> None:
        parser.add_argument("message", nargs="?", default="hello")

    def execute(self, ctx: CommandContext) -> CommandResult:
        return CommandResult.success(data={"message": getattr(ctx.args, "message", "hello")})


class FailCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "fail"

    def add_arguments(self, parser) -> None:
        pass

    def execute(self, ctx: CommandContext) -> CommandResult:
        return CommandResult.failure("intentional failure", exit_code=2)


def make_ctx(**kwargs) -> CommandContext:
    defaults = dict(command="echo", message="hello")
    defaults.update(kwargs)
    return CommandContext(args=Namespace(**defaults), raw_argv=[])


# ══════════════════════════════════════════════════════════════════════════════
# CommandResult
# ══════════════════════════════════════════════════════════════════════════════

class TestCommandResult:
    def test_success_defaults(self):
        r = CommandResult.success()
        assert r.ok is True
        assert r.exit_code == 0
        assert r.error is None

    def test_success_with_data(self):
        r = CommandResult.success(data={"x": 1})
        assert r.data["x"] == 1

    def test_failure_sets_exit_code(self):
        r = CommandResult.failure("bad", exit_code=3)
        assert r.ok is False
        assert r.exit_code == 3
        assert r.error == "bad"

    def test_failure_default_exit_code(self):
        r = CommandResult.failure("oops")
        assert r.exit_code == 1


# ══════════════════════════════════════════════════════════════════════════════
# CommandRegistry
# ══════════════════════════════════════════════════════════════════════════════

class TestCommandRegistry:
    def test_register_and_resolve_by_name(self):
        reg = CommandRegistry()
        reg.register(EchoCommand())
        cmd = reg.resolve("echo")
        assert cmd.name == "echo"

    def test_resolve_by_alias(self):
        reg = CommandRegistry()
        reg.register(EchoCommand())
        # EchoCommand has alias "ec"
        cmd = reg.resolve("ec")
        assert cmd.name == "echo"

    def test_resolve_unknown_raises(self):
        from callflow_tracer.command_line.registry.command_registry import CommandNotFoundError
        reg = CommandRegistry()
        with pytest.raises(CommandNotFoundError):
            reg.resolve("nonexistent")

    def test_duplicate_primary_name_raises(self):
        from callflow_tracer.command_line.registry.command_registry import DuplicateCommandError
        reg = CommandRegistry()
        reg.register(EchoCommand())
        with pytest.raises(DuplicateCommandError):
            reg.register(EchoCommand())

    def test_contains(self):
        reg = CommandRegistry()
        reg.register(EchoCommand())
        assert reg.contains("echo")
        assert reg.contains("ec")       # alias
        assert not reg.contains("xyz")

    def test_len(self):
        reg = CommandRegistry()
        assert len(reg) == 0
        reg.register(EchoCommand())
        reg.register(FailCommand())
        assert len(reg) == 2

    def test_names_in_registration_order(self):
        reg = CommandRegistry()
        reg.register(EchoCommand())
        reg.register(FailCommand())
        assert reg.names() == ["echo", "fail"]

    def test_all_yields_all_commands(self):
        reg = CommandRegistry()
        reg.register(EchoCommand())
        reg.register(FailCommand())
        names = [c.name for c in reg.all()]
        assert names == ["echo", "fail"]


# ══════════════════════════════════════════════════════════════════════════════
# EventBus
# ══════════════════════════════════════════════════════════════════════════════

class TestEventBus:
    def test_subscribe_and_emit(self):
        bus = EventBus()
        received: list[CLIEvent] = []
        bus.subscribe(EventType.COMMAND_SUCCEEDED, received.append)
        bus.emit(CLIEvent(EventType.COMMAND_SUCCEEDED, "echo"))
        assert len(received) == 1
        assert received[0].type == EventType.COMMAND_SUCCEEDED

    def test_unsubscribe(self):
        bus = EventBus()
        received = []
        handler = received.append
        bus.subscribe(EventType.COMMAND_SUCCEEDED, handler)
        bus.unsubscribe(EventType.COMMAND_SUCCEEDED, handler)
        bus.emit(CLIEvent(EventType.COMMAND_SUCCEEDED, "echo"))
        assert received == []

    def test_multiple_subscribers_all_receive(self):
        bus = EventBus()
        a, b = [], []
        bus.subscribe(EventType.COMMAND_STARTED, a.append)
        bus.subscribe(EventType.COMMAND_STARTED, b.append)
        bus.emit(CLIEvent(EventType.COMMAND_STARTED, "echo"))
        assert len(a) == 1
        assert len(b) == 1

    def test_dead_letter_when_no_subscribers(self):
        bus = EventBus()
        bus.emit(CLIEvent(EventType.COMMAND_STARTED, "echo"))
        assert len(bus.dead_letters) == 1

    def test_failing_handler_does_not_crash_bus(self):
        bus = EventBus()
        bus.subscribe(EventType.COMMAND_SUCCEEDED, lambda e: 1 / 0)  # always raises
        # should not raise
        bus.emit(CLIEvent(EventType.COMMAND_SUCCEEDED, "echo"))

    def test_subscribe_all_receives_every_type(self):
        bus = EventBus()
        received_types = []
        bus.subscribe_all(lambda e: received_types.append(e.type))
        bus.emit(CLIEvent(EventType.COMMAND_STARTED, "x"))
        bus.emit(CLIEvent(EventType.COMMAND_SUCCEEDED, "x"))
        assert EventType.COMMAND_STARTED in received_types
        assert EventType.COMMAND_SUCCEEDED in received_types

    def test_dead_letter_capacity_bounded(self):
        bus = EventBus(dead_letter_capacity=3)
        for _ in range(5):
            bus.emit(CLIEvent(EventType.PLUGIN_REGISTERED, "x"))
        # Bounded deque drops oldest
        assert len(bus.dead_letters) == 3


# ══════════════════════════════════════════════════════════════════════════════
# MiddlewareChain
# ══════════════════════════════════════════════════════════════════════════════

class TestMiddlewareChain:
    def test_empty_chain_calls_terminal(self):
        chain = MiddlewareChain()
        ctx = make_ctx()
        result = chain.run(ctx, lambda c: CommandResult.success(data={"called": True}))
        assert result.ok
        assert result.data["called"] is True

    def test_timing_middleware_stamps_duration(self):
        chain = MiddlewareChain().use(TimingMiddleware())
        ctx = make_ctx()
        result = chain.run(ctx, lambda c: CommandResult.success())
        assert result.duration_ms >= 0.0

    def test_validation_short_circuits_on_missing_script(self):
        chain = MiddlewareChain().use(ValidationMiddleware())
        ctx = CommandContext(
            args=Namespace(command="trace", script="/nonexistent_xyz.py"),
            raw_argv=[],
        )
        terminal_called = []
        result = chain.run(ctx, lambda c: (terminal_called.append(True), CommandResult.success())[1])
        assert not result.ok
        assert terminal_called == []   # terminal was never called

    def test_validation_passes_for_valid_input(self):
        chain = MiddlewareChain().use(ValidationMiddleware())
        ctx = make_ctx()   # no script arg → validator skips
        result = chain.run(ctx, lambda c: CommandResult.success())
        assert result.ok

    def test_middleware_execution_order(self):
        order = []

        from callflow_tracer.command_line.interfaces.middleware import Middleware, NextHandler

        class RecordMiddleware(Middleware):
            def __init__(self, tag: str):
                self.tag = tag
            def process(self, ctx, call_next):
                order.append(f"{self.tag}-enter")
                r = call_next(ctx)
                order.append(f"{self.tag}-exit")
                return r

        chain = (
            MiddlewareChain()
            .use(RecordMiddleware("A"))
            .use(RecordMiddleware("B"))
            .use(RecordMiddleware("C"))
        )
        chain.run(make_ctx(), lambda c: CommandResult.success())
        assert order == ["A-enter", "B-enter", "C-enter", "C-exit", "B-exit", "A-exit"]

    def test_logging_middleware_emits_events(self):
        bus = EventBus()
        events: list[CLIEvent] = []
        bus.subscribe_all(events.append)

        chain = MiddlewareChain().use(LoggingMiddleware(bus))
        chain.run(make_ctx(), lambda c: CommandResult.success())

        types = [e.type for e in events]
        assert EventType.COMMAND_STARTED in types
        assert EventType.COMMAND_SUCCEEDED in types

    def test_logging_middleware_emits_failed_event(self):
        bus = EventBus()
        events: list[CLIEvent] = []
        bus.subscribe_all(events.append)

        chain = MiddlewareChain().use(LoggingMiddleware(bus))
        chain.run(make_ctx(), lambda c: CommandResult.failure("oops"))

        types = [e.type for e in events]
        assert EventType.COMMAND_FAILED in types

    def test_tracing_middleware_pushes_and_pops_stack(self):
        bus = EventBus()
        captured_depth = []

        chain = MiddlewareChain().use(TracingMiddleware(bus))

        def terminal(c):
            captured_depth.append(c.extra.get("tracing.stack_depth", 0))
            return CommandResult.success()

        chain.run(make_ctx(), terminal)
        assert captured_depth == [1]
        # Stack should be empty after completion
        assert get_execution_stack() == []

    def test_tracing_middleware_emits_trace_recorded(self):
        bus = EventBus()
        trace_events: list[CLIEvent] = []
        bus.subscribe(EventType.TRACE_RECORDED, trace_events.append)

        chain = MiddlewareChain().use(TracingMiddleware(bus))
        # Provide a graph in result.data to trigger TRACE_RECORDED
        fake_graph = {"nodes": [], "edges": []}
        chain.run(make_ctx(), lambda c: CommandResult.success(data={"graph": fake_graph}))

        assert len(trace_events) == 1
        assert trace_events[0].payload["graph"] is fake_graph


# ══════════════════════════════════════════════════════════════════════════════
# CommandFactory
# ══════════════════════════════════════════════════════════════════════════════

class TestCommandFactory:
    def test_register_and_create(self):
        factory = CommandFactory()
        factory.register_class("echo", EchoCommand)
        cmd = factory.create("echo")
        assert isinstance(cmd, EchoCommand)

    def test_create_unknown_raises(self):
        factory = CommandFactory()
        with pytest.raises(KeyError):
            factory.create("nonexistent")

    def test_registered_names(self):
        factory = CommandFactory()
        factory.register_class("echo", EchoCommand)
        factory.register_class("fail", FailCommand)
        assert set(factory.registered_names()) == {"echo", "fail"}

    def test_discover_plugins_from_directory(self, tmp_path: Path):
        """Plugin file defining a BaseCommand subclass gets auto-registered."""
        plugin_file = tmp_path / "my_plugin.py"
        plugin_file.write_text(textwrap.dedent("""
            from callflow_tracer.command_line.interfaces.command import BaseCommand, CommandContext, CommandResult

            class GreetCommand(BaseCommand):
                @property
                def name(self): return "greet"
                @property
                def help(self): return "Say hi"
                def add_arguments(self, parser): pass
                def execute(self, ctx): return CommandResult.success(data={"msg": "hi"})
        """))
        factory = CommandFactory()
        registered = factory.discover_plugins(str(tmp_path))
        assert "greet" in registered
        cmd = factory.create("greet")
        assert cmd.name == "greet"

    def test_discover_plugins_bad_file_does_not_crash(self, tmp_path: Path):
        """Broken plugin file is skipped gracefully (degraded mode)."""
        bad = tmp_path / "broken.py"
        bad.write_text("raise RuntimeError('intentionally broken')\n")
        factory = CommandFactory()
        registered = factory.discover_plugins(str(tmp_path))
        assert registered == []


# ══════════════════════════════════════════════════════════════════════════════
# Concrete command: EchoCommand (Command Pattern in isolation)
# ══════════════════════════════════════════════════════════════════════════════

class TestEchoCommand:
    def test_execute_returns_success(self):
        cmd = EchoCommand()
        ctx = make_ctx(message="world")
        result = cmd.execute(ctx)
        assert result.ok
        assert result.data["message"] == "world"

    def test_execute_default_message(self):
        cmd = EchoCommand()
        ctx = make_ctx()
        result = cmd.execute(ctx)
        assert result.data["message"] == "hello"

    def test_name_and_aliases(self):
        cmd = EchoCommand()
        assert cmd.name == "echo"
        assert "ec" in cmd.aliases


# ══════════════════════════════════════════════════════════════════════════════
# Concrete command: TraceCommand (with real tracer, temp script)
# ══════════════════════════════════════════════════════════════════════════════

class TestTraceCommand:
    def test_trace_simple_script(self, tmp_path: Path):
        from callflow_tracer.command_line.commands.trace_cmd import TraceCommand

        script = tmp_path / "simple.py"
        script.write_text("x = 1 + 1\n")
        output_html = tmp_path / "out.html"

        cmd = TraceCommand()
        ctx = CommandContext(
            args=Namespace(
                command="trace",
                script=str(script),
                script_args=[],
                output=str(output_html),
                format="html",
                three_d=False,
                title=None,
                include_args=False,
                sampling_rate=1.0,
                include_modules=None,
                exclude_modules=None,
                min_duration_ms=0.0,
                no_browser=True,
            ),
            raw_argv=[],
        )
        result = cmd.execute(ctx)
        assert result.ok
        assert output_html.exists()
        assert "graph" in result.data

    def test_trace_missing_script_returns_failure(self, tmp_path: Path):
        from callflow_tracer.command_line.commands.trace_cmd import TraceCommand

        cmd = TraceCommand()
        ctx = CommandContext(
            args=Namespace(
                command="trace",
                script="/does/not/exist.py",
                script_args=[],
                output=str(tmp_path / "out.html"),
                format="html",
                three_d=False,
                title=None,
                include_args=False,
                sampling_rate=1.0,
                include_modules=None,
                exclude_modules=None,
                min_duration_ms=0.0,
                no_browser=True,
            ),
            raw_argv=[],
        )
        result = cmd.execute(ctx)
        assert not result.ok

    def test_trace_json_output(self, tmp_path: Path):
        from callflow_tracer.command_line.commands.trace_cmd import TraceCommand

        script = tmp_path / "fib.py"
        script.write_text(textwrap.dedent("""
            def fib(n):
                return n if n <= 1 else fib(n-1) + fib(n-2)
            fib(5)
        """))
        out = tmp_path / "trace.json"
        cmd = TraceCommand()
        ctx = CommandContext(
            args=Namespace(
                command="trace",
                script=str(script),
                script_args=[],
                output=str(out),
                format="json",
                three_d=False,
                title=None,
                include_args=False,
                sampling_rate=1.0,
                include_modules=None,
                exclude_modules=None,
                min_duration_ms=0.0,
                no_browser=True,
            ),
            raw_argv=[],
        )
        result = cmd.execute(ctx)
        assert result.ok
        assert out.exists()
        data = json.loads(out.read_text())
        assert "nodes" in data


# ══════════════════════════════════════════════════════════════════════════════
# Concrete command: InfoCommand (reads JSON, no tracer needed)
# ══════════════════════════════════════════════════════════════════════════════

class TestInfoCommand:
    def _write_trace(self, path: Path) -> None:
        path.write_text(json.dumps({
            "nodes": [
                {"full_name": "main.fib", "call_count": 15, "total_time": 0.001,
                 "module": "main", "function_name": "fib"},
            ],
            "edges": [
                {"caller": "main.fib", "callee": "main.fib", "call_count": 14},
            ],
        }))

    def test_info_basic(self, tmp_path: Path, capsys):
        from callflow_tracer.command_line.commands.analyze_cmd import InfoCommand

        trace = tmp_path / "trace.json"
        self._write_trace(trace)
        cmd = InfoCommand()
        ctx = CommandContext(
            args=Namespace(command="info", file=str(trace), detailed=False),
            raw_argv=[],
        )
        result = cmd.execute(ctx)
        assert result.ok
        assert result.data["node_count"] == 1
        assert result.data["total_calls"] == 15

    def test_info_detailed(self, tmp_path: Path, capsys):
        from callflow_tracer.command_line.commands.analyze_cmd import InfoCommand

        trace = tmp_path / "trace.json"
        self._write_trace(trace)
        cmd = InfoCommand()
        ctx = CommandContext(
            args=Namespace(command="info", file=str(trace), detailed=True),
            raw_argv=[],
        )
        result = cmd.execute(ctx)
        assert result.ok
        out = capsys.readouterr().out
        assert "Top 10 by Time" in out

    def test_info_missing_file_returns_failure(self):
        from callflow_tracer.command_line.commands.analyze_cmd import InfoCommand

        cmd = InfoCommand()
        ctx = CommandContext(
            args=Namespace(command="info", file="/no/such/file.json", detailed=False),
            raw_argv=[],
        )
        result = cmd.execute(ctx)
        assert not result.ok


# ══════════════════════════════════════════════════════════════════════════════
# main() integration — full dispatch
# ══════════════════════════════════════════════════════════════════════════════

class TestMainIntegration:
    def test_no_command_returns_1(self):
        from callflow_tracer.command_line.main import main
        assert main([]) == 1

    def test_unknown_command_returns_1(self):
        # argparse raises SystemExit(2) for unrecognized subcommands before
        # our registry lookup — both are non-zero error codes
        from callflow_tracer.command_line.main import main
        with pytest.raises(SystemExit) as exc:
            main(["nonexistent_xyz"])
        assert exc.value.code != 0

    def test_version_flag(self, capsys):
        from callflow_tracer.command_line.main import main
        with pytest.raises(SystemExit) as exc:
            main(["--version"])
        assert exc.value.code == 0

    def test_help_flag(self, capsys):
        from callflow_tracer.command_line.main import main
        with pytest.raises(SystemExit) as exc:
            main(["--help"])
        assert exc.value.code == 0
        out = capsys.readouterr().out
        assert "trace" in out
        assert "quality" in out

    def test_trace_command_dispatch(self, tmp_path: Path):
        from callflow_tracer.command_line.main import main

        script = tmp_path / "hello.py"
        script.write_text("print('hello')\n")
        out = tmp_path / "trace.html"

        exit_code = main([
            "trace", str(script),
            "-o", str(out),
            "--no-browser",
        ])
        assert exit_code == 0
        assert out.exists()

    def test_validation_catches_bad_sampling_rate(self, tmp_path: Path):
        from callflow_tracer.command_line.main import main

        script = tmp_path / "s.py"
        script.write_text("pass\n")
        exit_code = main([
            "trace", str(script),
            "--sampling-rate", "2.5",   # invalid
            "--no-browser",
        ])
        assert exit_code != 0

    def test_info_command_dispatch(self, tmp_path: Path):
        from callflow_tracer.command_line.main import main

        trace = tmp_path / "t.json"
        trace.write_text(json.dumps({
            "nodes": [{"full_name": "a.b", "call_count": 1,
                       "total_time": 0.001, "module": "a", "function_name": "b"}],
            "edges": [],
        }))
        exit_code = main(["info", str(trace)])
        assert exit_code == 0

    def test_callflow_cli_compat(self, tmp_path: Path):
        """CallflowCLI wrapper still works for backward compatibility."""
        from callflow_tracer.command_line import CallflowCLI

        trace = tmp_path / "t.json"
        trace.write_text(json.dumps({"nodes": [], "edges": []}))
        cli = CallflowCLI()
        assert cli.run(["info", str(trace)]) == 0
