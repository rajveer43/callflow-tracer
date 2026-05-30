"""
Plan verification tests for callflow_tracer/llm/

Test 1 — Unit:    Mock Anthropic SDK → assert LLMSpanRegistry entry + CallGraph edge
Test 2 — Flamegraph: Inject LLM span → generate HTML → assert gold node present
Test 3 — Cost:    analyze_costs on graph with LLM node → "api" category non-zero
Test 4 — Restore: After llm_instrumentation() exits → original method restored
"""

from __future__ import annotations

import importlib
import sys
import types
import unittest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_fake_anthropic():
    """Build a minimal fake anthropic module that mirrors the real SDK shape."""
    anthropic = types.ModuleType("anthropic")

    # resources.messages.Messages  (sync)
    resources = types.ModuleType("anthropic.resources")
    messages_mod = types.ModuleType("anthropic.resources.messages")

    class Messages:
        def create(self, *args, **kwargs):
            resp = MagicMock()
            resp.usage.input_tokens = 100
            resp.usage.output_tokens = 25
            resp.model = kwargs.get("model", "claude-sonnet-4-6")
            return resp

    class AsyncMessages:
        async def create(self, *args, **kwargs):
            resp = MagicMock()
            resp.usage.input_tokens = 80
            resp.usage.output_tokens = 20
            resp.model = kwargs.get("model", "claude-haiku-4-5")
            return resp

    messages_mod.Messages = Messages
    messages_mod.AsyncMessages = AsyncMessages
    resources.messages = messages_mod
    anthropic.resources = resources

    sys.modules["anthropic"] = anthropic
    sys.modules["anthropic.resources"] = resources
    sys.modules["anthropic.resources.messages"] = messages_mod
    return anthropic, Messages, AsyncMessages


def _cleanup_fake_anthropic():
    for key in list(sys.modules):
        if key.startswith("anthropic"):
            del sys.modules[key]


# ---------------------------------------------------------------------------
# Test 1 — Unit: LLMSpanRegistry + CallGraph edge after mocked SDK call
# ---------------------------------------------------------------------------

class TestLLMSpanAndCallGraphEdge(unittest.TestCase):

    def setUp(self):
        _make_fake_anthropic()
        import callflow_tracer.llm.span as _span_mod
        _span_mod.LLMSpanRegistry._instance = None
        _span_mod._registry = None

    def tearDown(self):
        _cleanup_fake_anthropic()
        import callflow_tracer.llm.span as _span_mod
        _span_mod.LLMSpanRegistry._instance = None
        _span_mod._registry = None

    def test_span_recorded_after_mock_create(self):
        from callflow_tracer.llm.anthropic_patch import AnthropicInstrumentor
        from callflow_tracer.llm.span import get_llm_registry
        from callflow_tracer.core.tracer import CallGraph, _thread_local

        # Wire up a real CallGraph so record_call has somewhere to write
        # get_current_graph() reads _thread_local.graph (not .active_graph)
        graph = CallGraph()
        _thread_local.graph = graph

        try:
            inst = AnthropicInstrumentor()
            inst.enable()

            import anthropic
            sdk_client = MagicMock()
            messages_cls = anthropic.resources.messages.Messages
            sdk_client.__class__ = messages_cls

            messages_cls.create(sdk_client, model="claude-sonnet-4-6", messages=[])

            # -- LLMSpanRegistry --
            registry = get_llm_registry()
            all_spans = registry.get_all()
            self.assertEqual(len(all_spans), 1, "Expected exactly one LLM span")

            key = "llm.anthropic.claude-sonnet-4-6"
            span = registry.get(key)
            self.assertIsNotNone(span, f"No span for key {key!r}")
            self.assertEqual(span.provider, "anthropic")
            self.assertEqual(span.model, "claude-sonnet-4-6")
            self.assertEqual(span.input_tokens, 100)
            self.assertEqual(span.output_tokens, 25)
            self.assertGreater(span.cost_usd, 0.0, "Cost should be non-zero")

            # -- CallGraph edge --
            callee_node = graph.nodes.get(key)
            self.assertIsNotNone(callee_node, f"CallGraph missing node {key!r}")
            self.assertGreaterEqual(callee_node.call_count, 1)

        finally:
            inst.disable()
            _thread_local.graph = None

    def test_span_aggregates_on_multiple_calls(self):
        from callflow_tracer.llm.anthropic_patch import AnthropicInstrumentor
        from callflow_tracer.llm.span import get_llm_registry
        from callflow_tracer.core.tracer import CallGraph, _thread_local

        graph = CallGraph()
        _thread_local.graph = graph

        try:
            inst = AnthropicInstrumentor()
            inst.enable()

            import anthropic
            sdk_client = MagicMock()
            messages_cls = anthropic.resources.messages.Messages
            sdk_client.__class__ = messages_cls

            messages_cls.create(sdk_client, model="claude-sonnet-4-6", messages=[])
            messages_cls.create(sdk_client, model="claude-sonnet-4-6", messages=[])

            span = get_llm_registry().get("llm.anthropic.claude-sonnet-4-6")
            self.assertEqual(span.input_tokens, 200, "Tokens should accumulate across calls")
            self.assertEqual(span.output_tokens, 50)

        finally:
            inst.disable()
            _thread_local.graph = None


# ---------------------------------------------------------------------------
# Test 2 — Flamegraph: Gold LLM node in generated HTML
# ---------------------------------------------------------------------------

class TestFlamegraphLLMNode(unittest.TestCase):

    def setUp(self):
        import callflow_tracer.llm.span as _span_mod
        _span_mod.LLMSpanRegistry._instance = None
        _span_mod._registry = None

    def tearDown(self):
        import callflow_tracer.llm.span as _span_mod
        _span_mod.LLMSpanRegistry._instance = None
        _span_mod._registry = None

    def test_llm_node_type_in_flamegraph_data(self):
        """LLM span injected into registry → flamegraph child dict has type=llm."""
        from callflow_tracer.llm.span import LLMSpan, get_llm_registry
        from callflow_tracer.core.tracer import CallGraph, CallNode
        from callflow_tracer.visualization.flamegraph import _build_flame_children

        # Seed registry with a known span
        span = LLMSpan(
            node_full_name="llm.anthropic.claude-sonnet-4-6",
            provider="anthropic",
            model="claude-sonnet-4-6",
            input_tokens=500,
            output_tokens=150,
            cost_usd=0.0038,
        )
        get_llm_registry().record(span)

        # Build a minimal CallGraph: root → llm.anthropic.claude-sonnet-4-6
        graph = CallGraph()
        graph.record_call(
            caller="app.main",
            callee="llm.anthropic.claude-sonnet-4-6",
            duration=0.45,
        )

        graph_dict = graph.to_dict()
        # _build_flame_children expects nodes keyed by full_name, same as _process_for_flamegraph does
        nodes = {n["full_name"]: n for n in graph_dict["nodes"] if "full_name" in n}
        edges = graph_dict["edges"]

        root_data = {"name": "app.main", "value": 450, "children": []}
        _build_flame_children(root_data, nodes, edges)

        children = root_data["children"]
        self.assertTrue(len(children) > 0, "Expected at least one child node")

        llm_child = next(
            (c for c in children if "anthropic" in c.get("name", "")), None
        )
        self.assertIsNotNone(llm_child, "LLM child node not found in flamegraph data")
        self.assertEqual(llm_child.get("type"), "llm")
        self.assertEqual(llm_child.get("provider"), "anthropic")
        self.assertEqual(llm_child.get("input_tokens"), 500)
        self.assertEqual(llm_child.get("output_tokens"), 150)
        self.assertAlmostEqual(llm_child.get("cost_usd"), 0.0038, places=5)

    def test_llm_gold_color_in_html_output(self):
        """Full HTML output must contain the gold color marker for LLM spans."""
        from callflow_tracer.llm.span import LLMSpan, get_llm_registry
        from callflow_tracer.core.tracer import CallGraph
        from callflow_tracer.visualization.flamegraph import generate_flamegraph
        import tempfile, os

        span = LLMSpan(
            node_full_name="llm.openai.gpt-4o",
            provider="openai",
            model="gpt-4o",
            input_tokens=200,
            output_tokens=80,
            cost_usd=0.0013,
        )
        get_llm_registry().record(span)

        graph = CallGraph()
        graph.record_call(
            caller="service.handler",
            callee="llm.openai.gpt-4o",
            duration=0.9,
        )

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            out_path = f.name

        try:
            generate_flamegraph(graph, output_file=out_path)
            html = open(out_path).read()
            self.assertIn("f59e0b", html, "Gold color #f59e0b must appear in HTML output")
            self.assertIn("llm", html.lower(), "HTML must reference LLM nodes")
        finally:
            os.unlink(out_path)


# ---------------------------------------------------------------------------
# Test 3 — Cost: analyze_costs includes non-zero "api" category for LLM nodes
# ---------------------------------------------------------------------------

class TestLLMCostClassifier(unittest.TestCase):

    def setUp(self):
        import callflow_tracer.llm.span as _span_mod
        _span_mod.LLMSpanRegistry._instance = None
        _span_mod._registry = None

    def tearDown(self):
        import callflow_tracer.llm.span as _span_mod
        _span_mod.LLMSpanRegistry._instance = None
        _span_mod._registry = None

    def test_api_cost_non_zero_when_llm_span_present(self):
        from callflow_tracer.llm.span import LLMSpan, get_llm_registry
        from callflow_tracer.core.tracer import CallGraph
        from callflow_tracer.ai.cost_analyzer import analyze_costs

        span = LLMSpan(
            node_full_name="llm.anthropic.claude-sonnet-4-6",
            provider="anthropic",
            model="claude-sonnet-4-6",
            input_tokens=1000,
            output_tokens=300,
            cost_usd=0.0075,  # 1000 * 3/1M + 300 * 15/1M
        )
        get_llm_registry().record(span)

        graph = CallGraph()
        graph.record_call(
            caller="app.main",
            callee="llm.anthropic.claude-sonnet-4-6",
            duration=1.2,
        )

        result = analyze_costs(graph.to_dict())

        self.assertIn("cost_breakdown", result)
        breakdown = result["cost_breakdown"]
        api_cost = breakdown.get("api", 0.0)
        self.assertGreater(api_cost, 0.0, f"API cost should be > 0, got {api_cost}. Breakdown: {breakdown}")

    def test_no_llm_spans_means_zero_api_cost(self):
        """Without LLM spans the api bucket should be 0."""
        from callflow_tracer.core.tracer import CallGraph
        from callflow_tracer.ai.cost_analyzer import analyze_costs

        graph = CallGraph()
        graph.record_call(caller="app.main", callee="app.helper", duration=0.1)

        result = analyze_costs(graph.to_dict())
        breakdown = result.get("cost_breakdown", {})
        api_cost = breakdown.get("api", 0.0)
        self.assertEqual(api_cost, 0.0, f"Expected 0 API cost without LLM spans, got {api_cost}")


# ---------------------------------------------------------------------------
# Test 4 — Restore: Original SDK method is restored after context exit
# ---------------------------------------------------------------------------

class TestRestoreAfterContext(unittest.TestCase):

    def setUp(self):
        _make_fake_anthropic()
        import callflow_tracer.llm.span as _span_mod
        _span_mod.LLMSpanRegistry._instance = None
        _span_mod._registry = None

    def tearDown(self):
        _cleanup_fake_anthropic()
        import callflow_tracer.llm.span as _span_mod
        _span_mod.LLMSpanRegistry._instance = None
        _span_mod._registry = None

    def test_original_method_restored_after_context(self):
        import anthropic
        from callflow_tracer.llm.manager import LLMInstrumentationManager

        messages_cls = anthropic.resources.messages.Messages
        original_create = messages_cls.create

        mgr = LLMInstrumentationManager()

        with _ctx(mgr):
            patched_create = messages_cls.create
            self.assertIsNot(
                patched_create, original_create,
                "Inside context: method should be patched"
            )

        restored_create = messages_cls.create
        self.assertIs(
            restored_create, original_create,
            "After context: original method must be restored"
        )

    def test_enable_disable_roundtrip(self):
        import anthropic
        from callflow_tracer.llm.anthropic_patch import AnthropicInstrumentor

        messages_cls = anthropic.resources.messages.Messages
        original = messages_cls.create

        inst = AnthropicInstrumentor()
        inst.enable()
        self.assertIsNot(messages_cls.create, original, "Should be patched after enable()")

        inst.disable()
        self.assertIs(messages_cls.create, original, "Should be original after disable()")

        # Second enable/disable cycle — idempotency
        inst.enable()
        inst.enable()  # double enable should be safe
        inst.disable()
        self.assertIs(messages_cls.create, original, "Idempotent enable/disable must still restore")


# Helper — plain context manager without using the module-level singleton
from contextlib import contextmanager

@contextmanager
def _ctx(mgr):
    mgr.instrumentors["anthropic"].enable()
    try:
        yield
    finally:
        mgr.instrumentors["anthropic"].disable()


if __name__ == "__main__":
    unittest.main(verbosity=2)
