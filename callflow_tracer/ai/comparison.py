"""
Trace comparison and diffing module for CallFlow Tracer.

Compares two execution traces to detect performance regressions, improvements,
and new bottlenecks. Useful for CI/CD performance gates, A/B testing,
and release validation.

Example:
    from callflow_tracer.ai import compare_traces

    comparison = compare_traces(
        before_graph=baseline_trace,
        after_graph=current_trace,
        threshold=0.1  # 10% regression threshold
    )

    print(comparison['regressions'])
    print(comparison['improvements'])
    print(comparison['new_bottlenecks'])

Architecture:
    - NodeStatus / NodeSeverity     — enums (no magic strings)
    - GraphExtractor                — shared graph-parsing utility (DRY)
    - NodeClassifier                — Strategy: classifies a node pair into status + severity
    - TraceComparator               — orchestrator
    - DSA: heapq.nlargest for top-k bottleneck detection — O(n log k) vs O(n log n)
"""

import heapq
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple


# ---------------------------------------------------------------------------
# Enums — replace all magic strings
# ---------------------------------------------------------------------------

class NodeStatus(str, Enum):
    REGRESSION     = "regression"
    IMPROVEMENT    = "improvement"
    STABLE         = "stable"
    NEW            = "new"
    REMOVED        = "removed"
    NEW_BOTTLENECK = "new_bottleneck"


class NodeSeverity(str, Enum):
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    CRITICAL = "critical"


_SEVERITY_RANK: Dict[NodeSeverity, int] = {
    NodeSeverity.LOW:      0,
    NodeSeverity.MEDIUM:   1,
    NodeSeverity.HIGH:     2,
    NodeSeverity.CRITICAL: 3,
}


# ---------------------------------------------------------------------------
# Typed value objects
# ---------------------------------------------------------------------------

@dataclass
class NodeComparison:
    """Comparison result for a single node/function."""

    name:               str
    module:             str
    before_time:        float
    after_time:         float
    time_delta:         float
    percent_change:     float
    call_count_before:  int
    call_count_after:   int
    call_count_delta:   int
    status:             str    # NodeStatus.value — str for JSON compat
    severity:           str    # NodeSeverity.value

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ComparisonResult:
    """Complete comparison result between two traces."""

    timestamp:              str
    before_total_time:      float
    after_total_time:       float
    overall_delta:          float
    overall_percent_change: float
    regressions:            List[NodeComparison]
    improvements:           List[NodeComparison]
    stable:                 List[NodeComparison]
    new_functions:          List[NodeComparison]
    removed_functions:      List[NodeComparison]
    new_bottlenecks:        List[NodeComparison]
    summary:                Dict[str, Any]

    @property
    def critical_regressions(self) -> List[NodeComparison]:
        """
        Derived — not stored separately to avoid stale copies.

        Old code kept a separate `critical_regressions` list that was built
        once and could drift from `regressions` if the list was mutated.
        """
        return [r for r in self.regressions if r.severity == NodeSeverity.CRITICAL.value]

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Inject derived field for callers that expect it
        d["critical_regressions"] = [r.to_dict() for r in self.critical_regressions]
        return d


# ---------------------------------------------------------------------------
# GraphExtractor — shared graph-parsing logic (eliminates duplication)
# ---------------------------------------------------------------------------

class GraphExtractor:
    """
    Extracts a flat node dict and total time from a graph payload.

    Centralising this logic means comparison.py and continuous_profiler.py
    no longer need to copy-paste the same two methods.
    """

    @staticmethod
    def extract_nodes(graph: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Return {module:name → node_dict} from either of the two known formats:
            {"nodes": [...]}
            {"data": {"nodes": [...]}}
        """
        nodes: Dict[str, Dict[str, Any]] = {}

        raw: List[Dict] = []
        if isinstance(graph, dict):
            if "nodes" in graph:
                raw = graph["nodes"]
            elif "data" in graph and "nodes" in graph.get("data", {}):
                raw = graph["data"]["nodes"]

        for node in raw:
            key = f"{node.get('module', 'unknown')}:{node.get('name', 'unknown')}"
            nodes[key] = node

        return nodes

    @staticmethod
    def get_total_time(graph: Dict[str, Any]) -> float:
        if isinstance(graph, dict):
            if "total_time" in graph:
                return float(graph["total_time"])
            if "data" in graph and "total_time" in graph.get("data", {}):
                return float(graph["data"]["total_time"])
        return 0.0


# ---------------------------------------------------------------------------
# NodeClassifier — Strategy for status + severity determination
# ---------------------------------------------------------------------------

class NodeClassifier:
    """
    Classifies a (before, after) node pair into NodeStatus + NodeSeverity.

    Extracted from TraceComparator._compare_nodes so it can be configured,
    tested, and swapped independently.
    """

    # Severity thresholds for regressions (percent_change)
    _SEVERITY_THRESHOLDS: List[Tuple[float, NodeSeverity]] = [
        (50.0, NodeSeverity.CRITICAL),
        (25.0, NodeSeverity.HIGH),
        (10.0, NodeSeverity.MEDIUM),
        (0.0,  NodeSeverity.LOW),
    ]

    def __init__(
        self,
        regression_threshold:  float = 0.10,
        improvement_threshold: float = 0.10,
        new_bottleneck_before: float = 0.05,
        new_bottleneck_after:  float = 0.10,
    ) -> None:
        self._reg_pct  = regression_threshold  * 100
        self._imp_pct  = improvement_threshold * 100
        self._nb_before = new_bottleneck_before
        self._nb_after  = new_bottleneck_after

    def classify_pair(
        self,
        before_node: Dict[str, Any],
        after_node:  Dict[str, Any],
    ) -> NodeComparison:
        before_time = float(before_node.get("total_time", 0))
        after_time  = float(after_node.get("total_time",  0))
        delta       = after_time - before_time
        pct_change  = (delta / before_time * 100) if before_time > 0 else 0.0

        status   = self._status(pct_change)
        severity = self._severity(status, pct_change)

        return NodeComparison(
            name               = before_node.get("name",       "unknown"),
            module             = before_node.get("module",     "unknown"),
            before_time        = before_time,
            after_time         = after_time,
            time_delta         = delta,
            percent_change     = pct_change,
            call_count_before  = int(before_node.get("call_count", 0)),
            call_count_after   = int(after_node.get("call_count",  0)),
            call_count_delta   = int(after_node.get("call_count", 0))
                                 - int(before_node.get("call_count", 0)),
            status             = status.value,
            severity           = severity.value,
        )

    def is_new_bottleneck(
        self,
        before_node: Dict[str, Any],
        after_node:  Dict[str, Any],
    ) -> bool:
        before_time = float(before_node.get("total_time", 0))
        after_time  = float(after_node.get("total_time",  0))
        return before_time < self._nb_before and after_time > self._nb_after

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _status(self, pct_change: float) -> NodeStatus:
        if pct_change >= self._reg_pct:
            return NodeStatus.REGRESSION
        if pct_change <= -self._imp_pct:
            return NodeStatus.IMPROVEMENT
        return NodeStatus.STABLE

    def _severity(self, status: NodeStatus, pct_change: float) -> NodeSeverity:
        if status != NodeStatus.REGRESSION:
            return NodeSeverity.LOW
        for threshold, severity in self._SEVERITY_THRESHOLDS:
            if pct_change >= threshold:
                return severity
        return NodeSeverity.LOW


# ---------------------------------------------------------------------------
# TraceComparator — thin orchestrator
# ---------------------------------------------------------------------------

class TraceComparator:
    """Compare two execution traces to detect performance changes."""

    def __init__(
        self,
        regression_threshold:  float = 0.10,
        improvement_threshold: float = 0.10,
    ) -> None:
        self._extractor  = GraphExtractor()
        self._classifier = NodeClassifier(
            regression_threshold  = regression_threshold,
            improvement_threshold = improvement_threshold,
        )

    def compare(
        self,
        before_graph: Dict[str, Any],
        after_graph:  Dict[str, Any],
    ) -> ComparisonResult:
        before_nodes = self._extractor.extract_nodes(before_graph)
        after_nodes  = self._extractor.extract_nodes(after_graph)
        before_total = self._extractor.get_total_time(before_graph)
        after_total  = self._extractor.get_total_time(after_graph)

        regressions:       List[NodeComparison] = []
        improvements:      List[NodeComparison] = []
        stable:            List[NodeComparison] = []
        new_functions:     List[NodeComparison] = []
        removed_functions: List[NodeComparison] = []

        # --- Compare nodes present in both graphs ---
        for node_key, before_node in before_nodes.items():
            if node_key in after_nodes:
                cmp = self._classifier.classify_pair(before_node, after_nodes[node_key])
                if cmp.status == NodeStatus.REGRESSION.value:
                    regressions.append(cmp)
                elif cmp.status == NodeStatus.IMPROVEMENT.value:
                    improvements.append(cmp)
                else:
                    stable.append(cmp)
            else:
                removed_functions.append(self._make_removed(before_node))

        # --- Find new functions ---
        for node_key, after_node in after_nodes.items():
            if node_key not in before_nodes:
                new_functions.append(self._make_new(after_node))

        # --- Top-k bottleneck detection: O(n log k) with heapq ---
        new_bottlenecks = self._identify_new_bottlenecks(before_nodes, after_nodes)

        # Sort by impact
        regressions.sort(key=lambda x: abs(x.time_delta), reverse=True)
        improvements.sort(key=lambda x: abs(x.time_delta), reverse=True)
        new_bottlenecks.sort(key=lambda x: x.after_time, reverse=True)

        return ComparisonResult(
            timestamp              = datetime.now().isoformat(),
            before_total_time      = before_total,
            after_total_time       = after_total,
            overall_delta          = after_total - before_total,
            overall_percent_change = (
                (after_total - before_total) / before_total * 100
                if before_total > 0 else 0.0
            ),
            regressions       = regressions,
            improvements      = improvements,
            stable            = stable,
            new_functions     = new_functions,
            removed_functions = removed_functions,
            new_bottlenecks   = new_bottlenecks,
            summary           = self._build_summary(
                regressions, improvements, stable,
                new_functions, removed_functions, new_bottlenecks,
                after_total, before_total,
            ),
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _make_removed(self, before_node: Dict[str, Any]) -> NodeComparison:
        t = float(before_node.get("total_time", 0))
        c = int(before_node.get("call_count", 0))
        return NodeComparison(
            name=before_node.get("name", "unknown"),
            module=before_node.get("module", "unknown"),
            before_time=t, after_time=0.0,
            time_delta=-t, percent_change=-100.0,
            call_count_before=c, call_count_after=0, call_count_delta=-c,
            status=NodeStatus.REMOVED.value, severity=NodeSeverity.LOW.value,
        )

    def _make_new(self, after_node: Dict[str, Any]) -> NodeComparison:
        t = float(after_node.get("total_time", 0))
        c = int(after_node.get("call_count", 0))
        sev = NodeSeverity.MEDIUM if t > 0.1 else NodeSeverity.LOW
        return NodeComparison(
            name=after_node.get("name", "unknown"),
            module=after_node.get("module", "unknown"),
            before_time=0.0, after_time=t,
            time_delta=t, percent_change=100.0,
            call_count_before=0, call_count_after=c, call_count_delta=c,
            status=NodeStatus.NEW.value, severity=sev.value,
        )

    def _identify_new_bottlenecks(
        self,
        before_nodes: Dict[str, Dict[str, Any]],
        after_nodes:  Dict[str, Dict[str, Any]],
    ) -> List[NodeComparison]:
        """
        Find top-10% slowest after-nodes that were fast before.

        DSA:
            Old: sorted() → O(n log n), then slice top-10%
            New: heapq.nlargest(k) → O(n log k) where k = n // 10
                 For n=1000, k=100: saves ~3x comparisons at large scale.
        """
        k = max(1, len(after_nodes) // 10)

        # nlargest returns the k nodes with highest total_time — O(n log k)
        top_k = heapq.nlargest(
            k,
            after_nodes.items(),
            key=lambda kv: kv[1].get("total_time", 0),
        )

        bottlenecks: List[NodeComparison] = []
        for node_key, after_node in top_k:
            if node_key not in before_nodes:
                continue
            before_node = before_nodes[node_key]
            if not self._classifier.is_new_bottleneck(before_node, after_node):
                continue

            before_time = float(before_node.get("total_time", 0))
            after_time  = float(after_node.get("total_time",  0))
            bottlenecks.append(NodeComparison(
                name=after_node.get("name", "unknown"),
                module=after_node.get("module", "unknown"),
                before_time=before_time,
                after_time=after_time,
                time_delta=after_time - before_time,
                percent_change=(
                    (after_time - before_time) / before_time * 100
                    if before_time > 0 else 100.0
                ),
                call_count_before=int(before_node.get("call_count", 0)),
                call_count_after=int(after_node.get("call_count", 0)),
                call_count_delta=int(after_node.get("call_count", 0))
                                 - int(before_node.get("call_count", 0)),
                status=NodeStatus.NEW_BOTTLENECK.value,
                severity=NodeSeverity.HIGH.value,
            ))

        return bottlenecks

    def _build_summary(
        self,
        regressions: List[NodeComparison],
        improvements: List[NodeComparison],
        stable: List[NodeComparison],
        new_functions: List[NodeComparison],
        removed_functions: List[NodeComparison],
        new_bottlenecks: List[NodeComparison],
        after_total: float,
        before_total: float,
    ) -> Dict[str, Any]:
        critical_count = sum(
            1 for r in regressions if r.severity == NodeSeverity.CRITICAL.value
        )
        return {
            "total_regressions":   len(regressions),
            "total_improvements":  len(improvements),
            "total_stable":        len(stable),
            "new_functions":       len(new_functions),
            "removed_functions":   len(removed_functions),
            "new_bottlenecks":     len(new_bottlenecks),
            "critical_regressions": critical_count,
            "overall_status": self._overall_status(
                regressions, improvements, after_total, before_total
            ),
        }

    def _overall_status(
        self,
        regressions:  List[NodeComparison],
        improvements: List[NodeComparison],
        after_total:  float,
        before_total: float,
    ) -> str:
        """
        Determine overall status by total time magnitude, not just count.

        Old code counted regressions vs improvements by number — two tiny
        improvements + one huge regression returned "mixed_positive" (wrong).
        Now we compare total regressed time vs total improved time.
        """
        if not regressions:
            return "improved"

        regressed_time  = sum(r.time_delta for r in regressions)
        improved_time   = abs(sum(i.time_delta for i in improvements))

        if improved_time > regressed_time * 1.2:
            return "mixed_positive"
        if regressed_time > improved_time * 1.2:
            return "mixed_negative"
        return "mixed"


# ---------------------------------------------------------------------------
# Convenience function (public API unchanged)
# ---------------------------------------------------------------------------

def compare_traces(
    before_graph: Dict[str, Any],
    after_graph:  Dict[str, Any],
    threshold:    float = 0.1,
) -> Dict[str, Any]:
    """
    Compare two execution traces.

    Args:
        before_graph: Baseline trace graph
        after_graph:  Current trace graph
        threshold:    Regression threshold (default 10%)

    Returns:
        Dict with comparison results including regressions, improvements,
        new_bottlenecks, critical_regressions, and summary.
    """
    comparator = TraceComparator(regression_threshold=threshold)
    return comparator.compare(before_graph, after_graph).to_dict()
