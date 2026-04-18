"""
`callflow ask` command — Swarm agent entry point.

Accepts a natural-language question, deploys the specialist swarm,
and prints the final structured answer to the terminal.

Usage:
    callflow-tracer ask "why is my payment processing slow?"
    callflow-tracer ask "what LLM calls cost the most?" --provider openai --api-key sk-...
    callflow-tracer ask "why is apply_fee called 800 times?" --scope ./payment/ --sequential
    callflow-tracer ask "find where user auth fails" --trace tests/test_auth.py --output report.md
"""

from __future__ import annotations

import os
import sys
from argparse import ArgumentParser
from pathlib import Path

from ..interfaces.command import BaseCommand, CommandContext, CommandResult


class AskCommand(BaseCommand):
    """Ask a natural-language question about your codebase using the swarm."""

    @property
    def name(self) -> str:
        return "ask"

    @property
    def aliases(self) -> list[str]:
        return []

    @property
    def help(self) -> str:
        return "Ask a question about your codebase — swarm agents answer it automatically"

    # ── Argument registration ──────────────────────────────────────────────

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "question",
            help='Natural-language question (e.g. "why is checkout slow?")',
        )
        parser.add_argument(
            "--provider", "-p",
            default=None,
            choices=["anthropic", "openai", "gemini", "ollama"],
            help="LLM provider (auto-detected from env if not set)",
        )
        parser.add_argument(
            "--api-key", "-k",
            default=None,
            metavar="KEY",
            dest="api_key",
            help="LLM API key (or set ANTHROPIC_API_KEY / OPENAI_API_KEY / GEMINI_API_KEY)",
        )
        parser.add_argument(
            "--scope", "-s",
            default=None,
            metavar="DIR",
            help="Restrict search to a subdirectory (e.g. ./payment/)",
        )
        parser.add_argument(
            "--trace", "-t",
            default=None,
            metavar="SCRIPT",
            help="Explicit Python script to trace (optional)",
        )
        parser.add_argument(
            "--output", "-o",
            default=None,
            metavar="FILE",
            help="Also save the answer to a Markdown file",
        )
        parser.add_argument(
            "--sequential",
            action="store_true",
            help="Run specialists sequentially instead of in parallel (debug mode)",
        )
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Print swarm progress as it runs",
        )
        parser.add_argument(
            "--timeout",
            type=int,
            default=120,
            metavar="SECONDS",
            help="Per-agent timeout in seconds (default: 120)",
        )

    # ── Execution ──────────────────────────────────────────────────────────

    def execute(self, ctx: CommandContext) -> CommandResult:
        from ...ai.llm_provider import get_default_provider
        from ...agent.core.bindings import BindingStore
        from ...agent.orchestration import SwarmBuilder

        args = ctx.args
        cwd  = os.getcwd()

        # ── Merge per-cwd bindings with CLI flags ──────────────────────────
        store   = BindingStore()
        stored  = store.load(cwd)
        binding = store.merge(stored, {
            "trace":    args.trace,
            "scope":    args.scope,
            "provider": args.provider,
        })
        effective_trace    = binding.trace
        effective_scope    = binding.scope
        effective_provider = binding.provider

        # ── Validate inputs ────────────────────────────────────────────────
        if not args.question.strip():
            return CommandResult.failure("Question cannot be empty.")

        if effective_trace and not Path(effective_trace).exists():
            return CommandResult.failure(f"Trace script not found: {effective_trace}")

        if effective_scope and not Path(effective_scope).exists():
            return CommandResult.failure(f"Scope directory not found: {effective_scope}")

        # ── Configure LLM provider ─────────────────────────────────────────
        try:
            llm = get_default_provider(provider_name=effective_provider)
        except ValueError as exc:
            return CommandResult.failure(
                f"{exc}\n\n"
                "Set one of:\n"
                "  export ANTHROPIC_API_KEY=sk-ant-...\n"
                "  export OPENAI_API_KEY=sk-...\n"
                "  export GEMINI_API_KEY=AI...\n"
                "Or pass --api-key KEY --provider anthropic"
            )

        if args.api_key and hasattr(llm, "api_key"):
            llm.api_key = args.api_key

        # ── Build swarm ────────────────────────────────────────────────────
        mode = "sequential" if args.sequential else "parallel"
        builder = SwarmBuilder(llm).with_mode(mode).with_timeout(args.timeout)
        if args.verbose:
            builder = builder.verbose()
        swarm = builder.build()

        # ── Print header ───────────────────────────────────────────────────
        _print_header(args.question, mode, args.verbose)

        # ── Run the swarm ──────────────────────────────────────────────────
        try:
            answer = swarm.ask(
                question=args.question,
                cwd=cwd,
                scope=effective_scope,
                trace_script=effective_trace,
            )
        except Exception as exc:
            return CommandResult.failure(f"Swarm failed: {exc}")

        # ── Persist effective bindings for next run ────────────────────────
        try:
            store.save(cwd, binding)
        except Exception:
            pass  # binding save failures must not block the user

        # ── Print answer ───────────────────────────────────────────────────
        print(answer)

        # ── Optional: save to file ─────────────────────────────────────────
        if args.output:
            md = _build_markdown_report(args.question, answer)
            try:
                Path(args.output).write_text(md, encoding="utf-8")
                print(f"\n  Report saved to: {args.output}")
            except OSError as exc:
                print(f"\n  Warning: could not write report: {exc}", file=sys.stderr)

        return CommandResult.success(data={"answer": answer})


# ── Private helpers ────────────────────────────────────────────────────────────

def _print_header(question: str, mode: str, verbose: bool) -> None:
    sep = "─" * 58
    print(f"\n{sep}")
    print(f"  callflow ask  [{mode} mode]")
    print(f"  Q: {question[:52]}")
    print(f"{sep}")
    if verbose:
        print()


def _build_markdown_report(question: str, answer: str) -> str:
    from datetime import datetime
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    return (
        f"# callflow ask — Report\n\n"
        f"**Question:** {question}  \n"
        f"**Generated:** {ts}\n\n"
        f"---\n\n"
        f"{answer.strip()}\n\n"
        f"---\n\n"
        f"_Generated by [callflow-tracer](https://github.com/rajveer43/callflow-tracer) swarm_\n"
    )
