// Force-directed call graph rendered on a Canvas element.
// Pure vanilla JS — no external deps so the dashboard loads offline.
//
// DSA: spring-force simulation
//   - Repulsion: O(n^2) Coulomb force between all node pairs
//   - Attraction: Hooke's law along each edge
//   - Velocity Verlet integration, dt=0.016 (60 fps target)

(function () {
  const canvas = document.getElementById("graph-canvas");
  const ctx = canvas.getContext("2d");

  let nodes = [];    // { id, x, y, vx, vy, radius, color, label }
  let edges = [];    // { source, target, width }
  let indexMap = {}; // id → array index
  let animFrame = null;

  const PALETTE = [
    "#e8a838","#38e8a8","#a838e8","#e83881","#38a8e8",
    "#81e838","#e86038","#3860e8","#e83860","#60e838"
  ];

  function nodeColor(name, isGod, communityId) {
    if (name.startsWith("llm.")) return "#ffd700";
    if (isGod) return "#f85149";
    if (communityId !== undefined) return PALETTE[communityId % PALETTE.length];
    return "#4c9be8";
  }

  function resize() {
    const parent = canvas.parentElement;
    canvas.width = parent.clientWidth;
    canvas.height = parent.clientHeight;
  }

  window.updateGraph = function (graphData, godNodeList, communities) {
    resize();
    const godSet = new Set(godNodeList.map(g => g.full_name || g));
    const communityMap = {};
    (communities || []).forEach(c => c.members.forEach(m => communityMap[m] = c.id));

    const existingPositions = {};
    nodes.forEach(n => { existingPositions[n.id] = { x: n.x, y: n.y }; });

    indexMap = {};
    nodes = graphData.nodes.map((n, i) => {
      const ex = existingPositions[n.full_name];
      indexMap[n.full_name] = i;
      return {
        id: n.full_name,
        label: n.full_name.split(".").pop(),
        x: ex ? ex.x : (Math.random() - 0.5) * canvas.width * 0.8 + canvas.width / 2,
        y: ex ? ex.y : (Math.random() - 0.5) * canvas.height * 0.8 + canvas.height / 2,
        vx: 0, vy: 0,
        radius: Math.max(6, Math.min(20, (n.call_count || 1) * 1.5)),
        color: nodeColor(n.full_name, godSet.has(n.full_name), communityMap[n.full_name]),
        label: n.full_name.split(".").pop(),
      };
    });

    edges = graphData.edges.map(e => ({
      source: indexMap[e.caller],
      target: indexMap[e.callee],
      width: Math.max(1, Math.min(4, (e.call_count || 1) / 3)),
    })).filter(e => e.source !== undefined && e.target !== undefined);

    if (animFrame) cancelAnimationFrame(animFrame);
    animate();
  };

  // ------------------------------------------------------------------
  // Spring simulation
  // ------------------------------------------------------------------

  const K_REPEL = 3000;
  const K_ATTRACT = 0.04;
  const DAMPING = 0.85;
  const MAX_V = 8;

  function step() {
    const w = canvas.width, h = canvas.height;
    const cx = w / 2, cy = h / 2;

    // Repulsion
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx = nodes[j].x - nodes[i].x;
        const dy = nodes[j].y - nodes[i].y;
        const dist2 = Math.max(dx*dx + dy*dy, 1);
        const f = K_REPEL / dist2;
        const dist = Math.sqrt(dist2);
        nodes[i].vx -= f * dx / dist;
        nodes[i].vy -= f * dy / dist;
        nodes[j].vx += f * dx / dist;
        nodes[j].vy += f * dy / dist;
      }
    }

    // Attraction along edges
    edges.forEach(e => {
      if (e.source === undefined || e.target === undefined) return;
      const a = nodes[e.source], b = nodes[e.target];
      if (!a || !b) return;
      const dx = b.x - a.x, dy = b.y - a.y;
      a.vx += K_ATTRACT * dx;
      a.vy += K_ATTRACT * dy;
      b.vx -= K_ATTRACT * dx;
      b.vy -= K_ATTRACT * dy;
    });

    // Gravity toward centre
    nodes.forEach(n => {
      n.vx += (cx - n.x) * 0.002;
      n.vy += (cy - n.y) * 0.002;
      n.vx *= DAMPING;
      n.vy *= DAMPING;
      const speed = Math.sqrt(n.vx*n.vx + n.vy*n.vy);
      if (speed > MAX_V) { n.vx = n.vx/speed*MAX_V; n.vy = n.vy/speed*MAX_V; }
      n.x += n.vx;
      n.y += n.vy;
      n.x = Math.max(n.radius, Math.min(w - n.radius, n.x));
      n.y = Math.max(n.radius, Math.min(h - n.radius, n.y));
    });
  }

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Edges
    edges.forEach(e => {
      const a = nodes[e.source], b = nodes[e.target];
      if (!a || !b) return;
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.lineTo(b.x, b.y);
      ctx.strokeStyle = "rgba(136,170,255,0.35)";
      ctx.lineWidth = e.width;
      ctx.stroke();

      // Arrowhead
      const angle = Math.atan2(b.y - a.y, b.x - a.x);
      const tipX = b.x - Math.cos(angle) * b.radius;
      const tipY = b.y - Math.sin(angle) * b.radius;
      ctx.beginPath();
      ctx.moveTo(tipX, tipY);
      ctx.lineTo(tipX - 7*Math.cos(angle-0.4), tipY - 7*Math.sin(angle-0.4));
      ctx.lineTo(tipX - 7*Math.cos(angle+0.4), tipY - 7*Math.sin(angle+0.4));
      ctx.closePath();
      ctx.fillStyle = "rgba(136,170,255,0.5)";
      ctx.fill();
    });

    // Nodes
    nodes.forEach(n => {
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.radius, 0, 2 * Math.PI);
      ctx.fillStyle = n.color;
      ctx.fill();
      ctx.strokeStyle = "rgba(255,255,255,0.15)";
      ctx.lineWidth = 1;
      ctx.stroke();

      if (n.radius > 8) {
        ctx.fillStyle = "#ffffff";
        ctx.font = `${Math.min(11, n.radius)}px monospace`;
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(n.label.slice(0, 12), n.x, n.y + n.radius + 8);
      }
    });
  }

  function animate() {
    step();
    draw();
    animFrame = requestAnimationFrame(animate);
  }

  window.addEventListener("resize", () => {
    resize();
  });
})();
