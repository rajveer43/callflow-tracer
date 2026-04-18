"""
core/bindings.py — Persistent per-cwd bindings for the swarm agent.

Stores trace/scope/provider preferences per working directory so users don't
have to retype --trace, --scope, --provider on every `callflow ask` run.

Design patterns:
  Repository   — BindingStore abstracts JSON persistence from callers
  Value Object — CwdBinding is a frozen dataclass; never mutated in place
  Precedence chain (highest → lowest):
    1. CLI flags (explicit user input)
    2. ~/.callflow/bindings.json for os.getcwd()
    3. Hardcoded defaults (None)

DSA:
  dict[str, CwdBinding] keyed by realpath(cwd) — O(1) lookup; canonical paths
    prevent duplicates from symlinks.
  Atomic write: .json.tmp → os.replace() — safe on POSIX + Windows.

Layer 1 — no imports from tools/, agents/, or orchestration/.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CwdBinding:
    """
    Immutable value object — per-cwd binding snapshot.
    None means "not set" — callers fall through to hardcoded defaults.
    """

    trace: str | None = None
    scope: str | None = None
    provider: str | None = None


class BindingStore:
    """
    Repository — abstracts JSON persistence for CwdBinding objects.

    The backing file lives at ~/.callflow/bindings.json (configurable for
    testing). Keys are realpath(cwd) strings to prevent symlink duplicates.
    Writes are atomic via os.replace().
    """

    _DEFAULT_PATH: Path = Path.home() / ".callflow" / "bindings.json"

    def __init__(self, path: str | Path | None = None) -> None:
        self._path = Path(path) if path is not None else self._DEFAULT_PATH

    def load(self, cwd: str) -> CwdBinding:
        """Return the stored binding for cwd, or an empty CwdBinding."""
        key = os.path.realpath(cwd)
        data = self._read_all()
        entry = data.get(key, {})
        return CwdBinding(
            trace=entry.get("trace") or None,
            scope=entry.get("scope") or None,
            provider=entry.get("provider") or None,
        )

    def save(self, cwd: str, b: CwdBinding) -> None:
        """Atomically persist the binding for cwd."""
        key = os.path.realpath(cwd)
        data = self._read_all()
        data[key] = {
            "trace": b.trace,
            "scope": b.scope,
            "provider": b.provider,
        }
        self._write_all(data)

    def merge(self, stored: CwdBinding, cli_flags: dict[str, Any]) -> CwdBinding:
        """
        Merge stored binding with CLI flags.

        Precedence: CLI flag (non-None/non-empty) > stored value > None.
        """
        def _pick(flag_val: Any, stored_val: str | None) -> str | None:
            if flag_val:
                return str(flag_val)
            return stored_val

        return CwdBinding(
            trace=_pick(cli_flags.get("trace"), stored.trace),
            scope=_pick(cli_flags.get("scope"), stored.scope),
            provider=_pick(cli_flags.get("provider"), stored.provider),
        )

    # ── Internal ──────────────────────────────────────────────────────────────

    def _read_all(self) -> dict[str, Any]:
        if not self._path.exists():
            return {}
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _write_all(self, data: dict[str, Any]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_suffix(".json.tmp")
        tmp.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        os.replace(tmp, self._path)
