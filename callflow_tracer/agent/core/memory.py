"""
core/memory.py — lightweight swarm run memory.

Stores compact run snapshots as JSONL so new swarm runs can reuse recent
diagnostic context from the same workspace.

Compaction: when entry count exceeds _COMPACT_THRESHOLD, compact() keeps
the newest _KEEP_RECENT entries and rotates the old file to a timestamped
.bak backup, retaining at most _MAX_BAK_FILES backups.

Design patterns:
  Strategy       — CompactionStrategy ABC; TruncateCompaction (default, no LLM)
  Template Method — compact() skeleton; strategy fills summarisation step

DSA:
  Two-pass read: pass 1 counts lines O(N), pass 2 reads tail O(K) via deque(maxlen=K)
  Path.rename() rotation — O(1) filesystem op; no data loss window
"""

from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

_COMPACT_THRESHOLD = 100   # entries before compaction triggers
_KEEP_RECENT       = 20    # entries to keep after compaction
_MAX_BAK_FILES     = 3     # number of .bak files to retain


@dataclass
class RunMemory:
    """Compact snapshot of one swarm execution."""

    question: str
    answer: str
    findings: dict[str, str]
    cwd: str
    scope: str | None = None
    trace_script: str | None = None
    elapsed_ms: int = 0
    timestamp_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RunMemory":
        return cls(
            question=str(payload.get("question", "")),
            answer=str(payload.get("answer", "")),
            findings=dict(payload.get("findings", {})),
            cwd=str(payload.get("cwd", "")),
            scope=payload.get("scope"),
            trace_script=payload.get("trace_script"),
            elapsed_ms=int(payload.get("elapsed_ms", 0) or 0),
            timestamp_ms=int(payload.get("timestamp_ms", int(time.time() * 1000))),
        )


# ── Compaction strategies ──────────────────────────────────────────────────────

class CompactionStrategy(ABC):
    """Strategy ABC — subclasses decide what to write into the compacted file."""

    @abstractmethod
    def select(self, store: "JsonlMemoryStore") -> list[RunMemory]:
        """Return the entries to keep in the compacted file."""


class TruncateCompaction(CompactionStrategy):
    """Default strategy — keep the newest _KEEP_RECENT entries, no LLM needed."""

    def select(self, store: "JsonlMemoryStore") -> list[RunMemory]:
        return store.load_recent(limit=_KEEP_RECENT)


# ── Memory store ───────────────────────────────────────────────────────────────

class JsonlMemoryStore:
    """
    Append-only JSONL store for run memories with optional compaction.

    The backing file lives at <root_cwd>/.callflow/memory/runs.jsonl.
    Compaction rotates the file to a .bak.{timestamp} backup and rewrites
    the active file with only the newest _KEEP_RECENT entries.
    """

    def __init__(self, root_cwd: str) -> None:
        self._path = Path(root_cwd) / ".callflow" / "memory" / "runs.jsonl"

    def append(self, memory: RunMemory) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(memory), ensure_ascii=False) + "\n")

    def load_recent(self, limit: int = 5) -> list[RunMemory]:
        if not self._path.exists():
            return []
        # Two-pass O(K) tail read via deque(maxlen=limit)
        tail: deque[str] = deque(maxlen=max(limit, 0))
        with self._path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    tail.append(line)
        result: list[RunMemory] = []
        for raw in tail:
            try:
                result.append(RunMemory.from_dict(json.loads(raw)))
            except Exception:
                continue
        return result

    def entry_count(self) -> int:
        """O(N) line count — used to decide if compaction is needed."""
        if not self._path.exists():
            return 0
        count = 0
        with self._path.open("r", encoding="utf-8") as f:
            for _ in f:
                count += 1
        return count

    def compact(self, strategy: CompactionStrategy | None = None) -> bool:
        """
        Compact the store if entry count exceeds _COMPACT_THRESHOLD.

        Returns True if compaction ran, False if not needed.
        """
        if self.entry_count() <= _COMPACT_THRESHOLD:
            return False
        _strategy = strategy or TruncateCompaction()
        recent = _strategy.select(self)
        self.rotate()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", encoding="utf-8") as f:
            for mem in recent:
                f.write(json.dumps(asdict(mem), ensure_ascii=False) + "\n")
        self._cleanup_old_baks()
        return True

    def rotate(self) -> None:
        """Rename current file to .bak.{timestamp}. O(1) filesystem op."""
        if self._path.exists():
            ts = int(time.time())
            self._path.rename(self._path.with_suffix(f".jsonl.bak.{ts}"))

    def _cleanup_old_baks(self) -> None:
        baks = sorted(
            self._path.parent.glob("runs.jsonl.bak.*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        for old in baks[_MAX_BAK_FILES:]:
            old.unlink(missing_ok=True)

    @property
    def path(self) -> Path:
        return self._path


def build_memory_brief(memories: list[RunMemory], max_chars: int = 1500) -> str:
    """Render recent memories as compact text for agent prompts."""
    if not memories:
        return ""
    lines = ["Recent swarm memory (same workspace):"]
    for i, memory in enumerate(reversed(memories), 1):
        lines.append(f"{i}. Q: {memory.question[:140]}")
        if memory.findings:
            top = ", ".join(f"{k}: {v[:80]}" for k, v in list(memory.findings.items())[:3])
            lines.append(f"   Findings: {top}")
        lines.append(f"   A: {memory.answer[:180]}")
    text = "\n".join(lines)
    if len(text) > max_chars:
        return text[:max_chars] + "\n...[truncated]"
    return text
