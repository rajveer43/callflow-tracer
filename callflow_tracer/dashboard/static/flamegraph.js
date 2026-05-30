// Flame graph renderer — currently a placeholder.
// The full flame graph uses the existing callflow_tracer visualization
// module rendered server-side; this stub reserves the panel for
// future inline client-side rendering.
(function () {
  window.renderFlamegraph = function (data) {
    // TODO: render collapsed flame rectangles from sampler hot_paths
  };
})();
