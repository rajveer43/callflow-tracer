"""Interactive HTML graph exporter using vis.js (embedded via CDN).

Produces a single self-contained HTML file with:
  - Force-directed call graph (vis.js Network)
  - God nodes highlighted in red
  - Community clusters colour-coded
  - LLM nodes in gold
  - Hover tooltip: call_count, total_time, z-score
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Union

from .base_exporter import BaseExporter

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>callflow-tracer — Call Graph</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
  body {{ margin: 0; background: #1a1a2e; font-family: monospace; color: #e0e0e0; }}
  #graph {{ width: 100vw; height: 90vh; border: none; }}
  #legend {{ padding: 8px 16px; font-size: 12px; display: flex; gap: 20px; }}
  .dot {{ display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 4px; }}
</style>
</head>
<body>
<div id="legend">
  <span><span class="dot" style="background:#ff4c4c"></span>God Node</span>
  <span><span class="dot" style="background:#ffd700"></span>LLM Call</span>
  <span><span class="dot" style="background:#4c9be8"></span>Regular</span>
  <span><span class="dot" style="background:#7fff7f"></span>Static-only</span>
</div>
<div id="graph"></div>
<script>
const GRAPH_DATA = {graph_data};

const god_set = new Set(GRAPH_DATA.god_nodes || []);
const community_colors = {community_colors};

const palette = [
  "#e8a838","#38e8a8","#a838e8","#e83881","#38a8e8",
  "#81e838","#e86038","#3860e8","#e83860","#60e838"
];

function nodeColor(n) {{
  if (n.full_name.startsWith("llm.")) return "#ffd700";
  if (god_set.has(n.full_name)) return "#ff4c4c";
  if (n.in_static && !n.in_runtime) return "#7fff7f";
  const cid = community_colors[n.full_name];
  if (cid !== undefined) return palette[cid % palette.length];
  return "#4c9be8";
}}

const nodes = new vis.DataSet(
  GRAPH_DATA.call_graph.nodes.map(n => ({{
    id: n.full_name,
    label: n.full_name.split(".").pop(),
    title: `<b>${{n.full_name}}</b><br>calls: ${{n.call_count}}<br>time: ${{n.total_time?.toFixed(4)}}s`,
    color: nodeColor(n),
    size: Math.max(8, Math.min(40, (n.call_count || 1) * 2)),
    font: {{ color: "#ffffff", size: 11 }},
  }}))
);

const edges = new vis.DataSet(
  GRAPH_DATA.call_graph.edges.map(e => ({{
    from: e.caller,
    to: e.callee,
    arrows: "to",
    width: Math.max(1, Math.min(5, (e.call_count || 1) / 3)),
    color: {{ color: e.is_static_only ? "#7fff7f55" : "#88aaff66" }},
    title: `calls: ${{e.call_count}}<br>avg: ${{e.avg_time?.toFixed(4)}}s`,
  }}))
);

const container = document.getElementById("graph");
const network = new vis.Network(container, {{ nodes, edges }}, {{
  physics: {{ solver: "forceAtlas2Based", stabilization: {{ iterations: 150 }} }},
  interaction: {{ hover: true, tooltipDelay: 150 }},
  edges: {{ smooth: {{ type: "dynamic" }} }},
}});
</script>
</body>
</html>
"""


class HTMLExporter(BaseExporter):
    def export(
        self,
        unified_graph: "UnifiedCallGraph",  # noqa: F821
        output_path: Union[str, Path],
        *,
        knowledge_graph: Optional["KnowledgeGraph"] = None,  # noqa: F821
        communities: Optional[list] = None,
        god_nodes: Optional[list] = None,
    ) -> Path:
        out = Path(output_path)

        graph_data = unified_graph.to_dict()
        graph_data["god_nodes"] = [g.full_name for g in (god_nodes or [])]

        # Map node → community id for colour coding
        community_colors: dict = {}
        for community in (communities or []):
            for member in community.members:
                community_colors[member] = community.id

        html = _HTML_TEMPLATE.format(
            graph_data=json.dumps(graph_data),
            community_colors=json.dumps(community_colors),
        )
        out.write_text(html, encoding="utf-8")
        return out
