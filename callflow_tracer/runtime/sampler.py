"""Low-overhead statistical sampling profiler — Template Method Pattern.

Samples the call stack at a fixed interval (default 10 ms) using a background
thread + sys._current_frames() so it imposes near-zero overhead on the target
program (unlike sys.setprofile which fires on every call).

DSA used:
  - Circular buffer (deque with maxlen) for raw samples — O(1) append/pop
  - Counter for frame frequency tallying — O(n)
  - Min-heap (heapq.nlargest) for top-k hot paths — O(n log k)
"""

from __future__ import annotations

import collections
import sys
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class StackSample:
    thread_id: int
    frames: List[Tuple[str, str, int]]  # (module, funcname, lineno)
    timestamp: float


@dataclass
class HotPath:
    frames: Tuple[str, ...]  # joined frame labels
    hit_count: int
    fraction: float           # fraction of total samples

    def to_dict(self) -> dict:
        return {
            "frames": list(self.frames),
            "hit_count": self.hit_count,
            "fraction": round(self.fraction, 4),
        }


class SamplingProfiler:
    """Template Method: subclasses can override _collect_sample() and _process().

    Usage::

        profiler = SamplingProfiler(interval_ms=10)
        profiler.start()
        # ... run workload ...
        profiler.stop()
        report = profiler.top_hot_paths(20)
    """

    def __init__(self, interval_ms: float = 10.0, max_samples: int = 50_000) -> None:
        self.interval_s = interval_ms / 1_000.0
        self._buffer: collections.deque[StackSample] = collections.deque(maxlen=max_samples)
        self._running = False
        self._thread: Optional[threading.Thread] = None

    # ------------------------------------------------------------------
    # Template Method hooks
    # ------------------------------------------------------------------

    def _collect_sample(self) -> List[StackSample]:
        """Snapshot all live Python threads."""
        samples = []
        ts = time.perf_counter()
        for tid, frame in sys._current_frames().items():
            frames: List[Tuple[str, str, int]] = []
            f = frame
            while f is not None:
                module = f.f_globals.get("__name__", "")
                frames.append((module, f.f_code.co_name, f.f_lineno))
                f = f.f_back
            frames.reverse()  # root → leaf
            samples.append(StackSample(thread_id=tid, frames=frames, timestamp=ts))
        return samples

    def _should_skip_frame(self, module: str, funcname: str) -> bool:
        """Filter out profiler internals and threading boilerplate."""
        _skip_mods = {"callflow_tracer.runtime.sampler", "threading", "_thread"}
        return module in _skip_mods or funcname in ("<module>", "_bootstrap")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True, name="cfsampler")
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)

    def __enter__(self) -> "SamplingProfiler":
        self.start()
        return self

    def __exit__(self, *_: object) -> None:
        self.stop()

    def _run(self) -> None:
        while self._running:
            for sample in self._collect_sample():
                self._buffer.append(sample)
            time.sleep(self.interval_s)

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def top_hot_paths(self, k: int = 20) -> List[HotPath]:
        import heapq
        samples = list(self._buffer)
        if not samples:
            return []
        total = len(samples)
        counter: Dict[Tuple[str, ...], int] = collections.Counter()
        for s in samples:
            key = tuple(
                f"{mod}.{fn}" if mod else fn
                for mod, fn, _ in s.frames
                if not self._should_skip_frame(mod, fn)
            )
            if key:
                counter[key] += 1

        result = heapq.nlargest(k, counter.items(), key=lambda x: x[1])
        return [
            HotPath(frames=frames, hit_count=count, fraction=count / total)
            for frames, count in result
        ]

    def frame_frequency(self) -> Dict[str, int]:
        """Return per-function frame hit counts (flat profile)."""
        counter: collections.Counter = collections.Counter()
        for sample in self._buffer:
            for mod, fn, _ in sample.frames:
                if not self._should_skip_frame(mod, fn):
                    label = f"{mod}.{fn}" if mod else fn
                    counter[label] += 1
        return dict(counter)

    def total_samples(self) -> int:
        return len(self._buffer)
