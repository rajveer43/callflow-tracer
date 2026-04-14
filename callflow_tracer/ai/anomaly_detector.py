"""
Anomaly Detection for CallFlow Tracer.

Uses statistical analysis to detect anomalies in execution patterns.
Helps proactively identify performance issues before they become critical.

Architecture:
    - Anomaly / AnomalyType / Severity  — typed value objects (no raw dicts)
    - AnomalyDetectionStrategy (ABC)    — Strategy: one class per detection algorithm
    - SeverityClassifier                — extracted severity logic, independently testable
    - BaselineRegistry                  — encapsulates optional baseline stats
    - RecommendationEngine              — generates recommendations from any Anomaly list
    - AnomalyDetector                   — thin orchestrator: registers strategies, runs pipeline
"""

import statistics
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple


# ---------------------------------------------------------------------------
# Enums — replace all magic strings
# ---------------------------------------------------------------------------

class AnomalyType(str, Enum):
    TIME      = "time"
    FREQUENCY = "frequency"
    PATTERN   = "pattern"
    OUTLIER   = "outlier"


class Severity(str, Enum):
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    CRITICAL = "critical"

    def __lt__(self, other: "Severity") -> bool:
        _order = [Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]
        return _order.index(self) < _order.index(other)


class PatternSubtype(str, Enum):
    EXCESSIVE_FANOUT = "excessive_fanout"
    N_PLUS_ONE       = "n_plus_one"


# ---------------------------------------------------------------------------
# Anomaly — typed value object (replaces raw dict)
# ---------------------------------------------------------------------------

@dataclass
class Anomaly:
    """
    A single detected anomaly.

    Using a dataclass instead of a raw dict means:
    - IDE autocomplete and type checking work
    - Typos in key names are caught at parse time, not runtime
    - asdict() still gives a JSON-serialisable dict for callers that need it
    """

    anomaly_type:  AnomalyType
    node_id:       str
    function:      str
    module:        str
    severity:      Severity
    description:   str
    value:         float
    expected:      float          = 0.0
    deviation:     float          = 0.0
    z_score:       float          = 0.0
    threshold:     float          = 0.0
    subtype:       Optional[str]  = None
    baseline_note: Optional[str]  = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["anomaly_type"] = self.anomaly_type.value
        d["severity"]     = self.severity.value
        return d


# ---------------------------------------------------------------------------
# Node / Edge extraction helpers
# ---------------------------------------------------------------------------

@dataclass
class NodeData:
    """Typed view of a CallGraph node used internally by detectors."""
    node_id:    str
    function:   str
    module:     str
    total_time: float
    call_count: int
    avg_time:   float


def _extract_nodes(graph) -> Dict[str, NodeData]:
    nodes: Dict[str, NodeData] = {}
    for node_id, node in graph.nodes.items():
        call_count = node.call_count or 0
        nodes[node_id] = NodeData(
            node_id    = node_id,
            function   = node.name,
            module     = node.module,
            total_time = node.total_time,
            call_count = call_count,
            avg_time   = (node.total_time / call_count) if call_count > 0 else 0.0,
        )
    return nodes


def _extract_edges(graph) -> List[Tuple[str, str]]:
    return [(caller, callee) for (caller, callee) in graph.edges]


# ---------------------------------------------------------------------------
# SeverityClassifier — extracted from _calculate_anomaly_severity
# ---------------------------------------------------------------------------

class SeverityClassifier:
    """
    Maps z-scores to Severity levels.

    Thresholds are configurable at construction time so tests can control
    them precisely and callers can tune sensitivity without subclassing.
    """

    def __init__(
        self,
        critical_z: float = 3.0,
        high_z:     float = 2.5,
        medium_z:   float = 2.0,
    ) -> None:
        self._critical_z = critical_z
        self._high_z     = high_z
        self._medium_z   = medium_z

    def from_z_score(self, z_score: float) -> Severity:
        abs_z = abs(z_score)
        if abs_z > self._critical_z:
            return Severity.CRITICAL
        if abs_z > self._high_z:
            return Severity.HIGH
        if abs_z > self._medium_z:
            return Severity.MEDIUM
        return Severity.LOW

    def overall(self, anomalies: List[Anomaly]) -> Severity:
        """Derive one Severity that summarises a whole list of anomalies."""
        if not anomalies:
            return Severity.LOW
        counts: Dict[Severity, int] = defaultdict(int)
        for a in anomalies:
            counts[a.severity] += 1

        if counts[Severity.CRITICAL] > 0:
            return Severity.CRITICAL
        if counts[Severity.HIGH] > 2:
            return Severity.HIGH
        if counts[Severity.HIGH] > 0 or counts[Severity.MEDIUM] > 3:
            return Severity.MEDIUM
        return Severity.LOW


# ---------------------------------------------------------------------------
# BaselineRegistry — encapsulates optional baseline statistics
# ---------------------------------------------------------------------------

@dataclass
class FunctionBaseline:
    mean_time:  float
    std_time:   float
    mean_count: float
    std_count:  float


class BaselineRegistry:
    """
    Holds per-function baseline statistics computed from historical graphs.

    Using a dedicated class instead of an Optional[Dict] on AnomalyDetector
    means the null-check is in one place and callers get a clean lookup API.
    """

    def __init__(self) -> None:
        self._stats: Dict[str, FunctionBaseline] = {}

    def add_graph(self, graph) -> None:
        """Incorporate one graph's data into the running baseline."""
        buckets: Dict[str, Dict[str, List[float]]] = defaultdict(
            lambda: {"times": [], "counts": []}
        )
        for node_id, node in graph.nodes.items():
            key = f"{node.module}.{node.name}"
            buckets[key]["times"].append(node.total_time)
            buckets[key]["counts"].append(float(node.call_count))

        for key, data in buckets.items():
            if len(data["times"]) > 1:
                self._stats[key] = FunctionBaseline(
                    mean_time  = statistics.mean(data["times"]),
                    std_time   = statistics.stdev(data["times"]),
                    mean_count = statistics.mean(data["counts"]),
                    std_count  = statistics.stdev(data["counts"]),
                )

    def get(self, module: str, function: str) -> Optional[FunctionBaseline]:
        return self._stats.get(f"{module}.{function}")

    def is_empty(self) -> bool:
        return len(self._stats) == 0


# ---------------------------------------------------------------------------
# Strategy pattern — one class per detection algorithm
# ---------------------------------------------------------------------------

class AnomalyDetectionStrategy(ABC):
    """
    One detection algorithm.

    Implement this to add new anomaly types without touching AnomalyDetector.
    Register your strategy via AnomalyDetector.register_strategy().
    """

    @property
    @abstractmethod
    def anomaly_type(self) -> AnomalyType:
        """The type of anomaly this strategy detects."""
        ...

    @abstractmethod
    def detect(
        self,
        nodes:    Dict[str, NodeData],
        edges:    List[Tuple[str, str]],
        baseline: BaselineRegistry,
        classifier: SeverityClassifier,
        sensitivity: float,
    ) -> List[Anomaly]:
        """Return all anomalies found. Empty list means nothing detected."""
        ...


class TimeAnomalyStrategy(AnomalyDetectionStrategy):
    """Detects functions whose execution time exceeds the population mean by N std devs."""

    @property
    def anomaly_type(self) -> AnomalyType:
        return AnomalyType.TIME

    def detect(self, nodes, edges, baseline, classifier, sensitivity) -> List[Anomaly]:
        anomalies: List[Anomaly] = []
        times = [n.total_time for n in nodes.values()]
        if len(times) < 2:
            return anomalies

        mean_time = statistics.mean(times)
        std_time  = statistics.stdev(times)
        if std_time == 0:
            return anomalies

        threshold = mean_time + sensitivity * std_time

        for node in nodes.values():
            if node.total_time <= threshold:
                continue

            z_score = (node.total_time - mean_time) / std_time
            desc    = f"{node.function} took {node.total_time:.3f}s (expected ~{mean_time:.3f}s)"

            baseline_note: Optional[str] = None
            bl = baseline.get(node.module, node.function)
            if bl is not None:
                bl_threshold = bl.mean_time + sensitivity * bl.std_time
                if node.total_time > bl_threshold:
                    baseline_note = f"baseline mean: {bl.mean_time:.3f}s"

            anomalies.append(Anomaly(
                anomaly_type  = AnomalyType.TIME,
                node_id       = node.node_id,
                function      = node.function,
                module        = node.module,
                value         = node.total_time,
                expected      = mean_time,
                deviation     = node.total_time - mean_time,
                z_score       = z_score,
                severity      = classifier.from_z_score(z_score),
                description   = desc,
                baseline_note = baseline_note,
            ))

        return sorted(anomalies, key=lambda a: a.severity, reverse=True)


class FrequencyAnomalyStrategy(AnomalyDetectionStrategy):
    """Detects functions called far more often than the population average."""

    @property
    def anomaly_type(self) -> AnomalyType:
        return AnomalyType.FREQUENCY

    def detect(self, nodes, edges, baseline, classifier, sensitivity) -> List[Anomaly]:
        anomalies: List[Anomaly] = []
        counts = [float(n.call_count) for n in nodes.values()]
        if len(counts) < 2:
            return anomalies

        mean_count = statistics.mean(counts)
        std_count  = statistics.stdev(counts)
        if std_count == 0:
            return anomalies

        threshold = mean_count + sensitivity * std_count

        for node in nodes.values():
            if node.call_count <= threshold:
                continue

            z_score = (node.call_count - mean_count) / std_count
            anomalies.append(Anomaly(
                anomaly_type = AnomalyType.FREQUENCY,
                node_id      = node.node_id,
                function     = node.function,
                module       = node.module,
                value        = float(node.call_count),
                expected     = mean_count,
                deviation    = node.call_count - mean_count,
                z_score      = z_score,
                severity     = classifier.from_z_score(z_score),
                description  = (
                    f"{node.function} called {node.call_count} times "
                    f"(expected ~{mean_count:.0f})"
                ),
            ))

        return sorted(anomalies, key=lambda a: a.severity, reverse=True)


class PatternAnomalyStrategy(AnomalyDetectionStrategy):
    """
    Detects structural call-pattern anomalies:
    - Excessive fan-out (one function calling > N others)
    - N+1 patterns (repeated calls with identical durations)
    """

    FANOUT_THRESHOLD = 10
    N_PLUS_ONE_MIN   = 3

    @property
    def anomaly_type(self) -> AnomalyType:
        return AnomalyType.PATTERN

    def detect(self, nodes, edges, baseline, classifier, sensitivity) -> List[Anomaly]:
        anomalies: List[Anomaly] = []

        call_map: Dict[str, List[str]] = defaultdict(list)
        for caller_id, callee_id in edges:
            if caller_id in nodes and callee_id in nodes:
                call_map[caller_id].append(callee_id)

        for node_id, callees in call_map.items():
            caller = nodes[node_id]

            if len(callees) > self.FANOUT_THRESHOLD:
                anomalies.append(Anomaly(
                    anomaly_type = AnomalyType.PATTERN,
                    subtype      = PatternSubtype.EXCESSIVE_FANOUT,
                    node_id      = node_id,
                    function     = caller.function,
                    module       = caller.module,
                    value        = float(len(callees)),
                    severity     = Severity.MEDIUM,
                    description  = (
                        f"{caller.function} calls {len(callees)} different functions "
                        f"(high complexity)"
                    ),
                ))

            callee_times = [nodes[c].total_time for c in callees]
            if len(callee_times) > self.N_PLUS_ONE_MIN:
                unique_rounded = set(round(t, 3) for t in callee_times)
                if len(unique_rounded) == 1:
                    anomalies.append(Anomaly(
                        anomaly_type = AnomalyType.PATTERN,
                        subtype      = PatternSubtype.N_PLUS_ONE,
                        node_id      = node_id,
                        function     = caller.function,
                        module       = caller.module,
                        value        = float(len(callees)),
                        severity     = Severity.HIGH,
                        description  = (
                            f"Potential N+1 pattern: {caller.function} makes "
                            f"{len(callees)} similar calls"
                        ),
                    ))

        return anomalies


class StatisticalOutlierStrategy(AnomalyDetectionStrategy):
    """Detects outliers using the IQR (interquartile range) method."""

    IQR_MULTIPLIER = 1.5

    @property
    def anomaly_type(self) -> AnomalyType:
        return AnomalyType.OUTLIER

    def detect(self, nodes, edges, baseline, classifier, sensitivity) -> List[Anomaly]:
        anomalies: List[Anomaly] = []

        times  = sorted(n.total_time   for n in nodes.values())
        counts = sorted(n.call_count   for n in nodes.values())
        if len(times) < 4:
            return anomalies

        time_threshold  = self._iqr_threshold(times)
        count_threshold = self._iqr_threshold(counts)

        for node in nodes.values():
            if node.total_time > time_threshold:
                anomalies.append(Anomaly(
                    anomaly_type = AnomalyType.OUTLIER,
                    subtype      = "time",
                    node_id      = node.node_id,
                    function     = node.function,
                    module       = node.module,
                    value        = node.total_time,
                    threshold    = time_threshold,
                    severity     = Severity.HIGH,
                    description  = f"{node.function} is a time outlier ({node.total_time:.3f}s)",
                ))
            if node.call_count > count_threshold:
                anomalies.append(Anomaly(
                    anomaly_type = AnomalyType.OUTLIER,
                    subtype      = "frequency",
                    node_id      = node.node_id,
                    function     = node.function,
                    module       = node.module,
                    value        = float(node.call_count),
                    threshold    = count_threshold,
                    severity     = Severity.MEDIUM,
                    description  = f"{node.function} is a frequency outlier ({node.call_count} calls)",
                ))

        return anomalies

    def _iqr_threshold(self, sorted_values: List[float]) -> float:
        n  = len(sorted_values)
        q1 = sorted_values[n // 4]
        q3 = sorted_values[3 * n // 4]
        return q3 + self.IQR_MULTIPLIER * (q3 - q1)


# ---------------------------------------------------------------------------
# RecommendationEngine — decoupled from detector
# ---------------------------------------------------------------------------

class RecommendationEngine:
    """
    Generates human-readable recommendations from a list of Anomaly objects.

    Extend by registering a handler for a new AnomalyType without touching
    the existing recommendation logic.
    """

    def __init__(self) -> None:
        self._handlers: Dict[AnomalyType, Any] = {
            AnomalyType.TIME:      self._recommend_time,
            AnomalyType.FREQUENCY: self._recommend_frequency,
            AnomalyType.PATTERN:   self._recommend_pattern,
            AnomalyType.OUTLIER:   self._recommend_outlier,
        }

    def register_handler(self, anomaly_type: AnomalyType, handler) -> None:
        """Override or add a recommendation handler for a given type."""
        self._handlers[anomaly_type] = handler

    def generate(self, anomalies: List[Anomaly]) -> List[str]:
        if not anomalies:
            return ["✅ No significant anomalies detected"]

        by_type: Dict[AnomalyType, List[Anomaly]] = defaultdict(list)
        for a in anomalies:
            by_type[a.anomaly_type].append(a)

        recommendations: List[str] = []
        for anomaly_type, handler in self._handlers.items():
            group = by_type.get(anomaly_type, [])
            if group:
                rec = handler(group)
                if rec:
                    recommendations.append(rec)

        return recommendations or ["✅ No significant anomalies detected"]

    # ------------------------------------------------------------------
    # Default handlers
    # ------------------------------------------------------------------

    def _recommend_time(self, anomalies: List[Anomaly]) -> str:
        top = max(anomalies, key=lambda a: a.deviation)
        return (
            f"⚠️  Investigate {top.function} — "
            f"taking {top.deviation:.3f}s longer than expected"
        )

    def _recommend_frequency(self, anomalies: List[Anomaly]) -> str:
        top = max(anomalies, key=lambda a: a.value)
        return (
            f"⚠️  {top.function} called {int(top.value)} times — "
            f"consider caching or batching"
        )

    def _recommend_pattern(self, anomalies: List[Anomaly]) -> str:
        n_plus_one = [a for a in anomalies if a.subtype == PatternSubtype.N_PLUS_ONE]
        if n_plus_one:
            return (
                f"🔥 Potential N+1 query pattern in {n_plus_one[0].function} — "
                f"batch operations"
            )
        fanout = [a for a in anomalies if a.subtype == PatternSubtype.EXCESSIVE_FANOUT]
        if fanout:
            return (
                f"⚠️  {fanout[0].function} has excessive fan-out "
                f"({int(fanout[0].value)} callees) — consider decomposing"
            )
        return ""

    def _recommend_outlier(self, anomalies: List[Anomaly]) -> str:
        return (
            f"📊 {len(anomalies)} statistical outlier(s) detected — "
            f"review for optimization"
        )


# ---------------------------------------------------------------------------
# AnomalyDetector — thin orchestrator
# ---------------------------------------------------------------------------

class AnomalyDetector:
    """
    Orchestrates anomaly detection strategies against a CallGraph.

    Usage:
        detector = AnomalyDetector(sensitivity=2.5)
        detector.add_baseline(baseline_graph)
        result = detector.detect(my_graph)

    Extending:
        detector.register_strategy(MyCustomStrategy())
    """

    def __init__(
        self,
        baseline_graphs: Optional[List] = None,
        sensitivity: float = 2.0,
    ) -> None:
        self.sensitivity = sensitivity
        self._baseline   = BaselineRegistry()
        self._classifier = SeverityClassifier()
        self._recommender = RecommendationEngine()

        # Strategy registry — ordered dict preserves insertion order
        self._strategies: Dict[AnomalyType, AnomalyDetectionStrategy] = {}
        for strategy in [
            TimeAnomalyStrategy(),
            FrequencyAnomalyStrategy(),
            PatternAnomalyStrategy(),
            StatisticalOutlierStrategy(),
        ]:
            self.register_strategy(strategy)

        for graph in (baseline_graphs or []):
            self.add_baseline(graph)

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_strategy(self, strategy: AnomalyDetectionStrategy) -> None:
        """Replace or add a detection strategy for its AnomalyType."""
        self._strategies[strategy.anomaly_type] = strategy

    def remove_strategy(self, anomaly_type: AnomalyType) -> None:
        """Disable detection for a given type."""
        self._strategies.pop(anomaly_type, None)

    # ------------------------------------------------------------------
    # Baseline
    # ------------------------------------------------------------------

    def add_baseline(self, graph) -> None:
        """Add a graph to the baseline for comparative analysis."""
        self._baseline.add_graph(graph)

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    def detect(
        self,
        graph,
        detect_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Run all registered (or filtered) strategies against graph.

        Args:
            graph:        CallGraph to analyse
            detect_types: Optional list of AnomalyType values to restrict
                          which strategies run (e.g. ["time", "outlier"]).
                          Defaults to running all registered strategies.

        Returns:
            Dict with keys:
                time_anomalies, frequency_anomalies, pattern_anomalies,
                outlier_anomalies, severity_summary, recommendations
        """
        active_types: Optional[set] = None
        if detect_types is not None:
            active_types = {AnomalyType(t) for t in detect_types}

        nodes = _extract_nodes(graph)
        edges = _extract_edges(graph)

        result: Dict[str, List[Dict]] = {
            f"{t.value}_anomalies": [] for t in AnomalyType
        }
        all_anomalies: List[Anomaly] = []

        for anomaly_type, strategy in self._strategies.items():
            if active_types and anomaly_type not in active_types:
                continue

            found = strategy.detect(
                nodes      = nodes,
                edges      = edges,
                baseline   = self._baseline,
                classifier = self._classifier,
                sensitivity= self.sensitivity,
            )
            result[f"{anomaly_type.value}_anomalies"] = [a.to_dict() for a in found]
            all_anomalies.extend(found)

        result["severity_summary"]  = self._build_severity_summary(all_anomalies)
        result["recommendations"]   = self._recommender.generate(all_anomalies)
        return result

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _build_severity_summary(self, anomalies: List[Anomaly]) -> Dict[str, Any]:
        counts: Dict[Severity, int] = defaultdict(int)
        for a in anomalies:
            counts[a.severity] += 1

        return {
            "total":            len(anomalies),
            "critical":         counts[Severity.CRITICAL],
            "high":             counts[Severity.HIGH],
            "medium":           counts[Severity.MEDIUM],
            "low":              counts[Severity.LOW],
            "overall_severity": self._classifier.overall(anomalies).value,
        }


# ---------------------------------------------------------------------------
# Convenience function (public API unchanged)
# ---------------------------------------------------------------------------

def detect_anomalies(
    graph,
    baseline_graphs: Optional[List] = None,
    sensitivity: float = 2.0,
    detect_types: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Convenience function for one-shot anomaly detection.

    Example:
        >>> with trace_scope() as graph:
        ...     my_function()
        >>> anomalies = detect_anomalies(graph)
        >>> print(anomalies['severity_summary'])
    """
    detector = AnomalyDetector(
        baseline_graphs=baseline_graphs,
        sensitivity=sensitivity,
    )
    return detector.detect(graph, detect_types=detect_types)
