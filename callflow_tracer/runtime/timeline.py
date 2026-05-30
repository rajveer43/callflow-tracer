"""Chrome Trace Event Format exporter (compatible with chrome://tracing and Perfetto).

Converts a callflow-tracer CallGraph + optional LLM spans into the JSON
array format expected by chrome://tracing so engineers can load it in
the browser or Perfetto UI for microsecond-resolution flame inspection.

Reference: https://docs.google.com/document/d/1CvAClvFfyA5R-PhYUmn5OOQtYMH4h6I0nSsKchNAySU

DSA used:
  - Monotone timestamp assignment via a virtual clock (sorted by total_time desc)
  - Interval tree simulation — begin/end event pairs derived from call_count
"""

from __future__ import annotations

import json
import time as _time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


@dataclass
class TraceEvent:
    name: str
    cat: str       # category
    ph: str        # event phase: B/E/X/i
    ts: float      # timestamp microseconds
    dur: float     # duration microseconds (X events only)
    pid: int = 1
    tid: int = 1
    args: Optional[Dict[str, Any]] = None

    def to_dict(self) -> dict:
        d: dict = {
            "name": self.name,
            "cat": self.cat,
            "ph": self.ph,
            "ts": self.ts,
            "dur": self.dur,
            "pid": self.pid,
            "tid": self.tid,
        }
        if self.args:
            d["args"] = self.args
        return d


class ChromeTimelineExporter:
    """Convert a CallGraph (and optionally LLMSpanRegistry) to Chrome trace JSON.

    Usage::

        exporter = ChromeTimelineExporter()
        exporter.export(call_graph, "trace.json", llm_registry=registry)
        # Open trace.json in chrome://tracing or https://ui.perfetto.dev
    """

    _LLM_TID = 9999  # dedicated thread lane for LLM spans

    def export(
        self,
        call_graph: Any,
        output_path: Union[str, Path],
        *,
        llm_registry: Optional[Any] = None,
    ) -> Path:
        out = Path(output_path)
        events: List[TraceEvent] = []

        # Build events from call graph nodes
        # We lay them out on a virtual timeline: each call takes
        # (total_time / call_count) * call_count = total_time microseconds.
        virtual_ts = 0.0  # running microsecond cursor per thread
        thread_cursors: Dict[str, float] = {}

        # Sort nodes by total_time descending so hot paths appear first
        sorted_nodes = sorted(
            call_graph.nodes.values(),
            key=lambda n: n.total_time,
            reverse=True,
        )

        for node in sorted_nodes:
            if node.call_count == 0:
                continue
            avg_us = (node.total_time / node.call_count) * 1_000_000
            # Assign to a "thread" derived from the module prefix
            module = node.module if hasattr(node, "module") else node.full_name.rsplit(".", 1)[0]
            tid_key = module or "main"
            ts = thread_cursors.get(tid_key, 0.0)
            tid = abs(hash(tid_key)) % 1000 + 1

            # Emit one X (complete) event per call
            for _ in range(min(node.call_count, 50)):  # cap at 50 events per node
                event = TraceEvent(
                    name=node.full_name if hasattr(node, "full_name") else node.name,
                    cat="python",
                    ph="X",
                    ts=ts,
                    dur=max(avg_us, 0.001),
                    tid=tid,
                    args={
                        "call_count": node.call_count,
                        "total_time_s": round(node.total_time, 6),
                    },
                )
                events.append(event)
                ts += avg_us
            thread_cursors[tid_key] = ts

        # LLM spans on their own thread lane
        if llm_registry is not None:
            llm_ts = 0.0
            for span in llm_registry.get_all().values():
                dur_us = 0.001  # we don't store duration in LLMSpan; use minimal
                event = TraceEvent(
                    name=span.node_full_name,
                    cat="llm",
                    ph="X",
                    ts=llm_ts,
                    dur=dur_us,
                    tid=self._LLM_TID,
                    args={
                        "model": span.model,
                        "provider": span.provider,
                        "input_tokens": span.input_tokens,
                        "output_tokens": span.output_tokens,
                        "cost_usd": round(span.cost_usd, 6),
                    },
                )
                events.append(event)
                llm_ts += dur_us + 1.0

        # Thread name metadata events
        thread_names: Dict[int, str] = {}
        for key, _ in thread_cursors.items():
            tid = abs(hash(key)) % 1000 + 1
            thread_names[tid] = key
        thread_names[self._LLM_TID] = "LLM calls"

        metadata: List[dict] = []
        for tid, name in thread_names.items():
            metadata.append({
                "name": "thread_name",
                "ph": "M",
                "pid": 1,
                "tid": tid,
                "args": {"name": name},
            })

        payload = metadata + [e.to_dict() for e in events]
        out.write_text(json.dumps(payload, indent=None), encoding="utf-8")
        return out
