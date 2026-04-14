"""
Continuous profiling module for CallFlow Tracer.

Provides always-on production profiling with minimal overhead. Automatically
collects and analyzes traces, sends alerts on anomalies, and builds baselines.

Example:
    from callflow_tracer.ai import ContinuousProfiler

    profiler = ContinuousProfiler(
        sampling_rate=0.01,   # 1% of requests
        aggregation_window='5m',
        storage='memory',
    )
    profiler.start()

Architecture:
    - StorageBackend (ABC)          — Strategy: swap memory/redis/file without touching profiler
    - MemoryStorageBackend          — default in-memory implementation
    - AlertObserver (ABC)           — Observer: decouple alert delivery from profiling
    - CallbackAlertObserver         — wraps a plain callable (backward compat)
    - ContinuousProfiler            — orchestrator: sampling, aggregation, baseline, anomaly
    - DSA:
        * snapshots     — deque(maxlen) — O(1) append+evict vs O(n) list slice
        * anomaly/alert flat deques   — O(1) access vs O(n·m) snapshot scan
        * window duration             — parsed once at init, not on every call
        * Welford's online algorithm  — corrected batch update for streaming mean
"""

import random
import statistics
import threading
import time
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Callable, Deque, Dict, List, Optional

from .comparison import GraphExtractor


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class ProfileSnapshot:
    """Aggregated profiling data for one time window."""

    timestamp:     str
    window_id:     str
    total_time:    float
    request_count: int
    functions:     Dict[str, Dict[str, Any]]
    anomalies:     List[Dict[str, Any]] = field(default_factory=list)
    alerts:        List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class BaselineProfile:
    """Running baseline built from all observed windows."""

    created_at:        str
    updated_at:        str
    function_stats:    Dict[str, Dict[str, float]]
    percentiles:       Dict[str, Dict[str, float]]
    anomaly_threshold: float


# ---------------------------------------------------------------------------
# Strategy pattern — storage backends
# ---------------------------------------------------------------------------

class StorageBackend(ABC):
    """
    One storage destination.

    Implement this to persist snapshots to Redis, S3, PostgreSQL etc.
    without changing any ContinuousProfiler logic.
    """

    @abstractmethod
    def save_snapshot(self, snapshot: ProfileSnapshot) -> None: ...

    @abstractmethod
    def load_snapshots(self, limit: int) -> List[ProfileSnapshot]: ...

    @abstractmethod
    def clear(self) -> None: ...


class MemoryStorageBackend(StorageBackend):
    """
    In-memory storage using a bounded deque.

    DSA: deque(maxlen=N) gives O(1) append + automatic O(1) eviction
    from the left when full.  The old code used list.append() + periodic
    slice (self.snapshots = self.snapshots[-1000:]) which is O(n) every
    1000 appends.
    """

    def __init__(self, maxlen: int = 1000) -> None:
        self._snapshots: Deque[ProfileSnapshot] = deque(maxlen=maxlen)

    def save_snapshot(self, snapshot: ProfileSnapshot) -> None:
        self._snapshots.append(snapshot)

    def load_snapshots(self, limit: int) -> List[ProfileSnapshot]:
        snaps = list(self._snapshots)
        return snaps[-limit:]

    def clear(self) -> None:
        self._snapshots.clear()


class FileStorageBackend(StorageBackend):
    """Persists snapshots as newline-delimited JSON to a file."""

    def __init__(self, path: str, maxlen: int = 1000) -> None:
        import json as _json
        self._path   = path
        self._maxlen = maxlen
        self._json   = _json
        self._mem    = MemoryStorageBackend(maxlen)  # cache in memory too

    def save_snapshot(self, snapshot: ProfileSnapshot) -> None:
        self._mem.save_snapshot(snapshot)
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(self._json.dumps(asdict(snapshot)) + "\n")

    def load_snapshots(self, limit: int) -> List[ProfileSnapshot]:
        return self._mem.load_snapshots(limit)

    def clear(self) -> None:
        self._mem.clear()
        open(self._path, "w").close()


def _build_storage(storage: str, **kwargs) -> StorageBackend:
    """Factory: map storage name string → StorageBackend instance."""
    if storage == "memory":
        return MemoryStorageBackend(maxlen=kwargs.get("maxlen", 1000))
    if storage == "file":
        path = kwargs.get("path", "profiler_snapshots.jsonl")
        return FileStorageBackend(path=path, maxlen=kwargs.get("maxlen", 1000))
    raise ValueError(
        f"Unknown storage backend: {storage!r}. "
        f"Supported: 'memory', 'file'. "
        f"Register custom backends via ContinuousProfiler(storage_backend=...)"
    )


# ---------------------------------------------------------------------------
# Observer pattern — alert delivery
# ---------------------------------------------------------------------------

class AlertObserver(ABC):
    """
    Implement to react to alerts without touching ContinuousProfiler.

    Replaces the raw `alert_callback: Callable` parameter which had no
    contract, no typing, and couldn't be composed (only one callback).
    """

    @abstractmethod
    def on_alert(self, alert: Dict[str, Any]) -> None: ...


class CallbackAlertObserver(AlertObserver):
    """Wraps a plain callable — backward-compatible with the old API."""

    def __init__(self, callback: Callable[[Dict[str, Any]], Any]) -> None:
        self._callback = callback

    def on_alert(self, alert: Dict[str, Any]) -> None:
        self._callback(alert)


class LoggingAlertObserver(AlertObserver):
    """Prints every alert to stdout — useful for development."""

    def on_alert(self, alert: Dict[str, Any]) -> None:
        print(
            f"[{alert.get('timestamp', '?')}] "
            f"ALERT {alert.get('severity', '?').upper()}: "
            f"{alert.get('message', '')}"
        )


# ---------------------------------------------------------------------------
# Welford's online algorithm (corrected)
# ---------------------------------------------------------------------------

def _welford_update(
    current_mean:    float,
    current_m2:      float,
    current_samples: int,
    new_value:       float,
) -> tuple:
    """
    Welford's online algorithm for mean + variance with a single new sample.

    Returns (new_mean, new_M2, new_n) where variance = M2 / (n - 1).

    The old code used:
        mean += delta * batch_size / new_n
    which is a broken batch approximation — it under-weights the delta
    when batch_size > 1 and gives wrong results when samples differ.

    This version is the canonical single-sample Welford update (Knuth Vol. 2).
    """
    n     = current_samples + 1
    delta = new_value - current_mean
    new_mean = current_mean + delta / n
    delta2   = new_value - new_mean
    new_m2   = current_m2 + delta * delta2
    return new_mean, new_m2, n


# ---------------------------------------------------------------------------
# ContinuousProfiler
# ---------------------------------------------------------------------------

class ContinuousProfiler:
    """
    Always-on production profiler with configurable sampling and storage.

    Thread-safe: record_trace() may be called from any thread.
    The aggregation loop runs in a daemon thread.
    """

    def __init__(
        self,
        sampling_rate:      float            = 0.01,
        aggregation_window: str              = "5m",
        storage:            str              = "memory",
        anomaly_threshold:  float            = 2.0,
        alert_callback:     Optional[Callable] = None,
        storage_backend:    Optional[StorageBackend] = None,
    ) -> None:
        self.sampling_rate     = sampling_rate
        self.anomaly_threshold = anomaly_threshold

        # Parse window duration ONCE at init — not on every _get_window_key call
        self._window_seconds: float = self._parse_window(aggregation_window)

        # Storage (Strategy)
        self._storage: StorageBackend = (
            storage_backend
            if storage_backend is not None
            else _build_storage(storage)
        )

        # Observers
        self._observers: List[AlertObserver] = []
        if alert_callback is not None:
            self._observers.append(CallbackAlertObserver(alert_callback))

        # State
        self.baseline: Optional[BaselineProfile] = None
        self._enabled = False
        self._lock    = threading.Lock()
        self._thread: Optional[threading.Thread] = None

        # Shared extractor (same logic as comparison.py — DRY)
        self._extractor = GraphExtractor()

        # Current window accumulator
        self._current_window: Dict[str, Any] = self._empty_window()

        # Flat bounded deques for O(1) access — no more O(n·m) snapshot scan
        # Old: get_anomalies() iterated all snapshots → O(n * avg_anomalies_per_snap)
        # New: O(1) deque append + O(limit) slice
        self._all_anomalies: Deque[Dict[str, Any]] = deque(maxlen=10_000)
        self._all_alerts:    Deque[Dict[str, Any]] = deque(maxlen=10_000)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        if self._enabled:
            return
        self._enabled = True
        self._thread  = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._enabled = False
        if self._thread:
            self._thread.join(timeout=5)

    def register_observer(self, observer: AlertObserver) -> None:
        """Add an alert observer. Multiple observers are all notified."""
        self._observers.append(observer)

    def record_trace(self, graph: Dict[str, Any]) -> None:
        """Record a trace. Sampled at `sampling_rate`; thread-safe."""
        if not self._enabled:
            return
        if random.random() > self.sampling_rate:
            return
        with self._lock:
            self._ingest(graph)

    def get_baseline(self) -> Optional[Dict[str, Any]]:
        return asdict(self.baseline) if self.baseline else None

    def get_latest_snapshot(self) -> Optional[Dict[str, Any]]:
        snaps = self._storage.load_snapshots(1)
        return asdict(snaps[-1]) if snaps else None

    def get_snapshots(self, limit: int = 10) -> List[Dict[str, Any]]:
        return [asdict(s) for s in self._storage.load_snapshots(limit)]

    def get_anomalies(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        O(limit) — reads from flat deque.

        Old code: O(n_snapshots * avg_anomalies) — scanned every snapshot.
        """
        items = list(self._all_anomalies)
        return items[-limit:]

    def get_alerts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """O(limit) — reads from flat deque."""
        items = list(self._all_alerts)
        return items[-limit:]

    # ------------------------------------------------------------------
    # Internal — ingestion
    # ------------------------------------------------------------------

    def _ingest(self, graph: Dict[str, Any]) -> None:
        """Accumulate one sampled trace into the current window."""
        nodes      = self._extractor.extract_nodes(graph)
        total_time = self._extractor.get_total_time(graph)

        self._current_window["times"].append(total_time)

        for node_key, node in nodes.items():
            fd = self._current_window["functions"][node_key]
            fd["times"].append(float(node.get("total_time", 0)))
            fd["counts"].append(int(node.get("call_count", 1)))

    # ------------------------------------------------------------------
    # Internal — aggregation loop
    # ------------------------------------------------------------------

    def _loop(self) -> None:
        """Background thread: sleep one window, then aggregate."""
        while self._enabled:
            try:
                time.sleep(self._window_seconds)
                self._aggregate()
            except Exception as exc:
                # Log but keep running — don't let one bad window kill the profiler
                print(f"[ContinuousProfiler] aggregation error: {exc}")

    def _aggregate(self) -> None:
        with self._lock:
            window = self._current_window
            self._current_window = self._empty_window()   # swap atomically

        if not window["times"]:
            return

        window_id = self._window_key()

        functions: Dict[str, Dict[str, Any]] = {}
        for node_key, fd in window["functions"].items():
            if fd["times"]:
                functions[node_key] = {
                    "mean_time":  statistics.mean(fd["times"]),
                    "max_time":   max(fd["times"]),
                    "min_time":   min(fd["times"]),
                    "call_count": sum(fd["counts"]),
                    "samples":    len(fd["times"]),
                }

        snapshot = ProfileSnapshot(
            timestamp     = datetime.now().isoformat(),
            window_id     = window_id,
            total_time    = statistics.mean(window["times"]),
            request_count = len(window["times"]),
            functions     = functions,
        )

        if self.baseline:
            snapshot.anomalies = self._detect_anomalies(snapshot)
            snapshot.alerts    = self._generate_alerts(snapshot)

            self._all_anomalies.extend(snapshot.anomalies)
            self._all_alerts.extend(snapshot.alerts)

            for alert in snapshot.alerts:
                self._notify(alert)

        if not self.baseline:
            self.baseline = self._create_baseline(snapshot)
        else:
            self._update_baseline(snapshot)

        self._storage.save_snapshot(snapshot)

    # ------------------------------------------------------------------
    # Internal — anomaly detection
    # ------------------------------------------------------------------

    def _detect_anomalies(self, snapshot: ProfileSnapshot) -> List[Dict[str, Any]]:
        if not self.baseline:
            return []

        anomalies: List[Dict[str, Any]] = []

        for node_key, func_stats in snapshot.functions.items():
            bl = self.baseline.function_stats.get(node_key)
            if bl is None:
                continue

            baseline_mean  = bl.get("mean",  0.0)
            baseline_stdev = bl.get("stdev", 0.0)

            if baseline_stdev <= 0:
                continue

            current_time = func_stats["mean_time"]
            z_score      = (current_time - baseline_mean) / baseline_stdev

            if abs(z_score) <= self.anomaly_threshold:
                continue

            # Severity scales with the configurable threshold, not a hardcoded 3.0
            severity = (
                "critical"
                if abs(z_score) > self.anomaly_threshold * 1.5
                else "high"
            )

            anomalies.append({
                "function":      node_key,
                "current_time":  current_time,
                "baseline_mean": baseline_mean,
                "z_score":       z_score,
                "severity":      severity,
            })

        return anomalies

    def _generate_alerts(self, snapshot: ProfileSnapshot) -> List[Dict[str, Any]]:
        alerts: List[Dict[str, Any]] = []

        critical = [a for a in snapshot.anomalies if a["severity"] == "critical"]
        if critical:
            alerts.append({
                "timestamp": snapshot.timestamp,
                "type":      "anomaly",
                "severity":  "critical",
                "message":   (
                    f"Critical anomalies detected in {len(critical)} function(s)"
                ),
                "anomalies": critical,
            })

        return alerts

    def _notify(self, alert: Dict[str, Any]) -> None:
        for observer in self._observers:
            try:
                observer.on_alert(alert)
            except Exception:
                pass  # observers must never crash the profiler

    # ------------------------------------------------------------------
    # Internal — baseline
    # ------------------------------------------------------------------

    def _create_baseline(self, snapshot: ProfileSnapshot) -> BaselineProfile:
        function_stats: Dict[str, Dict[str, float]] = {}
        for node_key, fs in snapshot.functions.items():
            function_stats[node_key] = {
                "mean":    fs["mean_time"],
                "stdev":   0.0,
                "m2":      0.0,       # running sum of squared deltas (Welford)
                "min":     fs["min_time"],
                "max":     fs["max_time"],
                "samples": float(fs["samples"]),
            }

        return BaselineProfile(
            created_at        = datetime.now().isoformat(),
            updated_at        = datetime.now().isoformat(),
            function_stats    = function_stats,
            percentiles       = {},
            anomaly_threshold = self.anomaly_threshold,
        )

    def _update_baseline(self, snapshot: ProfileSnapshot) -> None:
        """
        Update baseline using Welford's online algorithm (corrected).

        Old code used a broken batch-delta formula:
            mean += delta * batch_size / new_n
        which is wrong when batch_size varies across windows.

        Welford's single-sample update is exact and numerically stable.
        """
        if not self.baseline:
            return

        for node_key, fs in snapshot.functions.items():
            if node_key not in self.baseline.function_stats:
                # New function seen — initialise its stats
                self.baseline.function_stats[node_key] = {
                    "mean":    fs["mean_time"],
                    "stdev":   0.0,
                    "m2":      0.0,
                    "min":     fs["min_time"],
                    "max":     fs["max_time"],
                    "samples": float(fs["samples"]),
                }
                continue

            bl = self.baseline.function_stats[node_key]

            # Welford one sample at a time using the window mean as the new point
            new_mean, new_m2, new_n = _welford_update(
                current_mean    = bl["mean"],
                current_m2      = bl["m2"],
                current_samples = int(bl["samples"]),
                new_value       = fs["mean_time"],
            )

            bl["mean"]    = new_mean
            bl["m2"]      = new_m2
            bl["samples"] = float(new_n)
            bl["stdev"]   = (new_m2 / (new_n - 1)) ** 0.5 if new_n > 1 else 0.0
            bl["min"]     = min(bl["min"], fs["min_time"])
            bl["max"]     = max(bl["max"], fs["max_time"])

        self.baseline.updated_at = datetime.now().isoformat()

    # ------------------------------------------------------------------
    # Internal — utilities
    # ------------------------------------------------------------------

    @staticmethod
    def _empty_window() -> Dict[str, Any]:
        return {
            "times":     [],
            "functions": defaultdict(lambda: {"times": [], "counts": []}),
        }

    def _window_key(self) -> str:
        """Stable key for the current aggregation window."""
        now   = datetime.now()
        epoch = now.timestamp()
        start = epoch - (epoch % self._window_seconds)
        return datetime.fromtimestamp(start).isoformat()

    @staticmethod
    def _parse_window(window: str) -> float:
        """
        Parse '5m' → 300.0, '1h' → 3600.0, '30s' → 30.0.

        Called ONCE at __init__, not on every window-key computation.
        Old code called this inside both _profiling_loop and _get_window_key
        on every iteration.
        """
        window = window.strip()
        if window.endswith("m"):
            return int(window[:-1]) * 60.0
        if window.endswith("h"):
            return int(window[:-1]) * 3600.0
        if window.endswith("s"):
            return int(window[:-1]) * 1.0
        return 300.0   # default 5 minutes
