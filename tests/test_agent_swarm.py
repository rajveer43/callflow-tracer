"""
tests/test_agent_swarm.py — Unit tests for the swarm agent system.

Covers:
  - ProviderChain failover and backoff
  - BindingStore persistence and merge precedence
  - SkillRegistry (bundled + workspace)
  - configure_from_task: effective tool registry and system prompt
  - HookBus subscribe/fire and NullHookBus no-op
  - JsonlMemoryStore compaction and rotation
  - DispatchPlan parsing with skills + tools (nested JSON)
  - Full SwarmBuilder construction (no LLM calls made)

All tests are pure unit tests — no LLM API calls, no filesystem side effects
beyond tempdir, no network required.
"""

from __future__ import annotations

import json
import os
import tempfile
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ── Feature 1: ProviderChain failover ─────────────────────────────────────────

class TestProviderChain:
    def test_first_provider_success(self):
        from callflow_tracer.ai.failover import ProviderChain

        p1 = MagicMock()
        p1.generate.return_value = "answer from p1"
        p1.is_available.return_value = True

        chain = ProviderChain([p1])
        assert chain.generate("q") == "answer from p1"
        p1.generate.assert_called_once()

    def test_failover_to_second_on_rate_limit(self):
        from callflow_tracer.ai.failover import ProviderChain

        p1 = MagicMock()
        p1.generate.side_effect = Exception("429 rate limit exceeded")
        p1.is_available.return_value = True

        p2 = MagicMock()
        p2.generate.return_value = "answer from p2"
        p2.is_available.return_value = True

        chain = ProviderChain([p1, p2])
        result = chain.generate("q")
        assert result == "answer from p2"

    def test_all_fail_raises(self):
        from callflow_tracer.ai.failover import ProviderChain, ProviderChainExhaustedError

        p1 = MagicMock()
        p1.generate.side_effect = Exception("503 overloaded")
        p1.is_available.return_value = True

        chain = ProviderChain([p1], max_attempts=1)
        with pytest.raises(ProviderChainExhaustedError):
            chain.generate("q")

    def test_permanent_skip_on_403(self):
        from callflow_tracer.ai.failover import ProviderChain, ProviderChainExhaustedError
        from callflow_tracer.ai.error_classifier import ProviderErrorKind

        p1 = MagicMock()
        p1.generate.side_effect = Exception("403 forbidden access denied")
        p1.is_available.return_value = True

        chain = ProviderChain([p1], max_attempts=3)
        with pytest.raises(ProviderChainExhaustedError):
            chain.generate("q")

        slot = list(chain._slots)[0]
        assert slot.permanent_skip is True

    def test_is_available_true_when_slot_available(self):
        from callflow_tracer.ai.failover import ProviderChain

        p = MagicMock()
        p.is_available.return_value = True
        chain = ProviderChain([p])
        assert chain.is_available() is True

    def test_null_provider_returns_error_string(self):
        from callflow_tracer.ai.failover import NullProvider

        np = NullProvider()
        result = np.generate("anything")
        assert "ERROR" in result
        assert np.is_available() is False


# ── Feature 1: error classifier ───────────────────────────────────────────────

class TestErrorClassifier:
    def test_classify_rate_limit(self):
        from callflow_tracer.ai.error_classifier import classify, ProviderErrorKind
        assert classify(Exception("429 too many requests")) == ProviderErrorKind.RATE_LIMIT

    def test_classify_auth(self):
        from callflow_tracer.ai.error_classifier import classify, ProviderErrorKind
        assert classify(Exception("401 unauthorized invalid api key")) == ProviderErrorKind.AUTH

    def test_classify_auth_perm(self):
        from callflow_tracer.ai.error_classifier import classify, ProviderErrorKind
        assert classify(Exception("403 forbidden")) == ProviderErrorKind.AUTH_PERM

    def test_classify_billing(self):
        from callflow_tracer.ai.error_classifier import classify, ProviderErrorKind
        assert classify(Exception("402 payment required insufficient_quota")) == ProviderErrorKind.BILLING

    def test_classify_overloaded(self):
        from callflow_tracer.ai.error_classifier import classify, ProviderErrorKind
        assert classify(Exception("503 service unavailable overloaded")) == ProviderErrorKind.OVERLOADED

    def test_classify_timeout(self):
        from callflow_tracer.ai.error_classifier import classify, ProviderErrorKind
        assert classify(Exception("read timeout")) == ProviderErrorKind.TIMEOUT

    def test_classify_unknown(self):
        from callflow_tracer.ai.error_classifier import classify, ProviderErrorKind
        assert classify(Exception("something completely random")) == ProviderErrorKind.UNKNOWN


# ── Feature 2: BindingStore ────────────────────────────────────────────────────

class TestBindingStore:
    def test_save_and_load(self, tmp_path):
        from callflow_tracer.agent.core.bindings import BindingStore, CwdBinding

        store = BindingStore(path=tmp_path / "bindings.json")
        store.save("/my/project", CwdBinding(trace="tests/test_api.py", scope="payment/"))

        loaded = store.load("/my/project")
        assert loaded.trace == "tests/test_api.py"
        assert loaded.scope == "payment/"
        assert loaded.provider is None

    def test_load_missing_returns_empty(self, tmp_path):
        from callflow_tracer.agent.core.bindings import BindingStore, CwdBinding

        store = BindingStore(path=tmp_path / "bindings.json")
        b = store.load("/nonexistent/path")
        assert b == CwdBinding()

    def test_merge_cli_wins(self, tmp_path):
        from callflow_tracer.agent.core.bindings import BindingStore, CwdBinding

        store = BindingStore(path=tmp_path / "bindings.json")
        stored = CwdBinding(trace="old.py", scope="old/", provider="openai")

        merged = store.merge(stored, {"trace": "new.py", "scope": None, "provider": None})
        assert merged.trace == "new.py"       # CLI wins
        assert merged.scope == "old/"         # stored preserved (CLI was None)
        assert merged.provider == "openai"    # stored preserved (CLI was None)

    def test_atomic_write_survives_existing_file(self, tmp_path):
        from callflow_tracer.agent.core.bindings import BindingStore, CwdBinding

        path = tmp_path / "bindings.json"
        store = BindingStore(path=path)
        store.save("/proj/a", CwdBinding(scope="a/"))
        store.save("/proj/b", CwdBinding(scope="b/"))

        assert store.load("/proj/a").scope == "a/"
        assert store.load("/proj/b").scope == "b/"

    def test_uses_realpath_for_key(self, tmp_path):
        from callflow_tracer.agent.core.bindings import BindingStore, CwdBinding

        store = BindingStore(path=tmp_path / "bindings.json")
        real = os.path.realpath(str(tmp_path))
        store.save(str(tmp_path), CwdBinding(scope="x/"))

        loaded = store.load(real)
        assert loaded.scope == "x/"


# ── Feature 3: Skill system ────────────────────────────────────────────────────

class TestSkillRegistry:
    def test_bundled_skills_present(self):
        from callflow_tracer.agent.skills import build_skill_registry

        reg = build_skill_registry()
        assert set(reg.names()) == {
            "StaticAnalysis", "DependencyTrace", "CostProfiling", "SecurityScan"
        }

    def test_get_returns_skill(self):
        from callflow_tracer.agent.skills import build_skill_registry

        reg = build_skill_registry()
        sec = reg.get("SecurityScan")
        assert sec is not None
        assert "grep_codebase" in [t.name for t in sec.tools]
        assert sec.prompt_fragment.strip() != ""

    def test_get_unknown_returns_none(self):
        from callflow_tracer.agent.skills import build_skill_registry

        reg = build_skill_registry()
        assert reg.get("NonExistentSkill") is None

    def test_descriptions_for_router_contains_all_names(self):
        from callflow_tracer.agent.skills import build_skill_registry

        reg = build_skill_registry()
        desc = reg.descriptions_for_router()
        for name in reg.names():
            assert name in desc

    def test_workspace_skill_loaded(self, tmp_path):
        from callflow_tracer.agent.skills import build_skill_registry

        skill_file = tmp_path / "custom_skill.py"
        skill_file.write_text(textwrap.dedent("""
            from callflow_tracer.agent.skills import Skill
            from callflow_tracer.agent.tools import GrepCodebaseTool
            SKILLS = [Skill(
                name="CustomSkill",
                tools=(GrepCodebaseTool(),),
                description="custom",
            )]
        """), encoding="utf-8")

        reg = build_skill_registry(skill_dir=tmp_path)
        assert reg.get("CustomSkill") is not None
        assert reg.get("StaticAnalysis") is not None  # bundled still present

    def test_workspace_skill_overrides_bundled(self, tmp_path):
        from callflow_tracer.agent.skills import build_skill_registry

        skill_file = tmp_path / "override.py"
        skill_file.write_text(textwrap.dedent("""
            from callflow_tracer.agent.skills import Skill
            from callflow_tracer.agent.tools import GrepCodebaseTool
            SKILLS = [Skill(
                name="SecurityScan",
                tools=(GrepCodebaseTool(),),
                description="overridden version",
            )]
        """), encoding="utf-8")

        reg = build_skill_registry(skill_dir=tmp_path)
        skill = reg.get("SecurityScan")
        assert skill.description == "overridden version"


# ── Feature 3: configure_from_task ────────────────────────────────────────────

class TestConfigureFromTask:
    def test_skills_inject_tools(self):
        from callflow_tracer.agent.skills import build_skill_registry
        from callflow_tracer.agent.core.types import AgentTask
        from callflow_tracer.agent.agents.grep import GrepAgent

        reg = build_skill_registry()
        agent = GrepAgent(MagicMock())

        base_tools = set(agent._tool_registry.names())
        task = AgentTask("GrepAgent", skills=["SecurityScan"])
        agent.configure_from_task(task, reg)

        eff_tools = set(agent._effective_tool_registry().names())
        security_tools = {t.name for t in reg.get("SecurityScan").tools}
        assert security_tools.issubset(eff_tools)

    def test_extra_tools_added(self):
        from callflow_tracer.agent.skills import build_skill_registry
        from callflow_tracer.agent.core.types import AgentTask
        from callflow_tracer.agent.agents.grep import GrepAgent

        reg = build_skill_registry()
        agent = GrepAgent(MagicMock())
        task = AgentTask("GrepAgent", extra_tools=["run_context"])
        agent.configure_from_task(task, reg)

        assert "run_context" in agent._effective_tool_registry().names()

    def test_no_duplicate_tools(self):
        from callflow_tracer.agent.skills import build_skill_registry
        from callflow_tracer.agent.core.types import AgentTask
        from callflow_tracer.agent.agents.grep import GrepAgent

        reg = build_skill_registry()
        agent = GrepAgent(MagicMock())
        # StaticAnalysis includes grep_codebase — GrepAgent already has it
        task = AgentTask("GrepAgent", skills=["StaticAnalysis"])
        agent.configure_from_task(task, reg)

        names = agent._effective_tool_registry().names()
        assert names.count("grep_codebase") == 1

    def test_skill_prompt_fragment_appended(self):
        from callflow_tracer.agent.skills import build_skill_registry
        from callflow_tracer.agent.core.types import AgentTask
        from callflow_tracer.agent.core.context import SwarmContext
        from callflow_tracer.agent.agents.grep import GrepAgent

        reg = build_skill_registry()
        agent = GrepAgent(MagicMock())
        task = AgentTask("GrepAgent", skills=["SecurityScan"])
        agent.configure_from_task(task, reg)

        ctx = SwarmContext(question="test", cwd=".")
        prompt = agent._effective_system_prompt(ctx)
        assert "Active Skills" in prompt
        assert "SecurityScan" in prompt
        assert "OWASP" in prompt

    def test_no_skills_prompt_unchanged(self):
        from callflow_tracer.agent.skills import build_skill_registry
        from callflow_tracer.agent.core.types import AgentTask
        from callflow_tracer.agent.core.context import SwarmContext
        from callflow_tracer.agent.agents.grep import GrepAgent

        reg = build_skill_registry()
        agent = GrepAgent(MagicMock())
        task = AgentTask("GrepAgent")
        agent.configure_from_task(task, reg)

        ctx = SwarmContext(question="test", cwd=".")
        base = agent._build_system_prompt(ctx)
        effective = agent._effective_system_prompt(ctx)
        assert effective == base  # no extra sections when no skills


# ── Feature 4: HookBus ────────────────────────────────────────────────────────

class TestHookBus:
    def test_subscribe_and_fire(self):
        from callflow_tracer.agent.core.hooks import HookBus, HookKind

        bus = HookBus()
        received = []
        bus.subscribe(HookKind.TOOL_CALLED, lambda k, p: received.append(p["tool"]))
        bus.fire(HookKind.TOOL_CALLED, {"tool": "grep_codebase"})

        assert received == ["grep_codebase"]

    def test_multiple_subscribers_all_called(self):
        from callflow_tracer.agent.core.hooks import HookBus, HookKind

        bus = HookBus()
        calls = []
        bus.subscribe(HookKind.AGENT_START, lambda k, p: calls.append("s1"))
        bus.subscribe(HookKind.AGENT_START, lambda k, p: calls.append("s2"))
        bus.fire(HookKind.AGENT_START, {"agent": "GrepAgent"})

        assert calls == ["s1", "s2"]

    def test_exception_in_callback_does_not_propagate(self):
        from callflow_tracer.agent.core.hooks import HookBus, HookKind

        bus = HookBus()
        bus.subscribe(HookKind.TOOL_CALLED, lambda k, p: 1 / 0)  # raises
        # must not raise
        bus.fire(HookKind.TOOL_CALLED, {"tool": "anything"})

    def test_no_subscribers_fire_is_noop(self):
        from callflow_tracer.agent.core.hooks import HookBus, HookKind

        bus = HookBus()
        bus.fire(HookKind.SWARM_COMPLETE, {"elapsed_ms": 42})  # no subscribers

    def test_null_hook_bus_is_noop(self):
        from callflow_tracer.agent.core.hooks import NullHookBus, HookKind

        null = NullHookBus()
        called = []
        null.subscribe(HookKind.TOOL_CALLED, lambda k, p: called.append(1))
        null.fire(HookKind.TOOL_CALLED, {"tool": "x"})
        assert called == []  # subscription was silently dropped


# ── Feature 5: JsonlMemoryStore compaction ────────────────────────────────────

class TestJsonlMemoryStore:
    def _make_store(self, tmp_path):
        from callflow_tracer.agent.core.memory import JsonlMemoryStore
        return JsonlMemoryStore(str(tmp_path))

    def test_append_and_load(self, tmp_path):
        from callflow_tracer.agent.core.memory import RunMemory

        store = self._make_store(tmp_path)
        store.append(RunMemory("q1", "a1", {}, str(tmp_path)))
        store.append(RunMemory("q2", "a2", {}, str(tmp_path)))

        mems = store.load_recent(limit=10)
        assert len(mems) == 2
        assert mems[-1].question == "q2"

    def test_load_recent_respects_limit(self, tmp_path):
        from callflow_tracer.agent.core.memory import RunMemory

        store = self._make_store(tmp_path)
        for i in range(10):
            store.append(RunMemory(f"q{i}", f"a{i}", {}, str(tmp_path)))

        mems = store.load_recent(limit=3)
        assert len(mems) == 3
        assert mems[-1].question == "q9"  # newest last

    def test_entry_count(self, tmp_path):
        from callflow_tracer.agent.core.memory import RunMemory

        store = self._make_store(tmp_path)
        assert store.entry_count() == 0
        for i in range(5):
            store.append(RunMemory(f"q{i}", "a", {}, str(tmp_path)))
        assert store.entry_count() == 5

    def test_compact_below_threshold_returns_false(self, tmp_path):
        from callflow_tracer.agent.core.memory import RunMemory

        store = self._make_store(tmp_path)
        store.append(RunMemory("q", "a", {}, str(tmp_path)))
        assert store.compact() is False

    def test_compact_above_threshold_returns_true(self, tmp_path):
        from callflow_tracer.agent.core.memory import RunMemory, _COMPACT_THRESHOLD, _KEEP_RECENT

        store = self._make_store(tmp_path)
        for i in range(_COMPACT_THRESHOLD + 5):
            store.append(RunMemory(f"q{i}", f"a{i}", {}, str(tmp_path)))

        compacted = store.compact()
        assert compacted is True
        assert store.entry_count() == _KEEP_RECENT

    def test_compact_creates_bak_file(self, tmp_path):
        from callflow_tracer.agent.core.memory import RunMemory, _COMPACT_THRESHOLD

        store = self._make_store(tmp_path)
        for i in range(_COMPACT_THRESHOLD + 1):
            store.append(RunMemory(f"q{i}", "a", {}, str(tmp_path)))

        store.compact()
        baks = list(Path(str(tmp_path)).rglob("*.bak.*"))
        assert len(baks) >= 1

    def test_rotate_renames_file(self, tmp_path):
        from callflow_tracer.agent.core.memory import RunMemory

        store = self._make_store(tmp_path)
        store.append(RunMemory("q", "a", {}, str(tmp_path)))
        assert store.path.exists()

        store.rotate()
        assert not store.path.exists()
        baks = list(Path(str(tmp_path)).rglob("*.bak.*"))
        assert len(baks) == 1


# ── RouterAgent dispatch plan parsing ─────────────────────────────────────────

class TestDispatchPlanParsing:
    def _ctx(self):
        from callflow_tracer.agent.core.context import SwarmContext
        return SwarmContext(question="test question", cwd=".")

    def test_basic_agents_parsed(self):
        from callflow_tracer.agent.agents.router import _extract_dispatch_plan

        text = 'DISPATCH_PLAN:\n{"agents": ["GrepAgent", "ContextAgent"], "mode": "parallel", "hints": {}}'
        plan = _extract_dispatch_plan(text, self._ctx())
        assert plan.agent_names() == ["GrepAgent", "ContextAgent"]
        assert plan.mode == "parallel"

    def test_skills_parsed(self):
        from callflow_tracer.agent.agents.router import _extract_dispatch_plan

        text = (
            'DISPATCH_PLAN:\n'
            '{"agents": ["GrepAgent"], "mode": "parallel",'
            ' "skills": {"GrepAgent": ["SecurityScan", "StaticAnalysis"]},'
            ' "tools": {}, "hints": {}}'
        )
        plan = _extract_dispatch_plan(text, self._ctx())
        task = plan.tasks[0]
        assert task.skills == ["SecurityScan", "StaticAnalysis"]

    def test_extra_tools_parsed(self):
        from callflow_tracer.agent.agents.router import _extract_dispatch_plan

        text = (
            'DISPATCH_PLAN:\n'
            '{"agents": ["GrepAgent"], "mode": "sequential",'
            ' "skills": {}, "tools": {"GrepAgent": ["read_file", "run_context"]},'
            ' "hints": {}}'
        )
        plan = _extract_dispatch_plan(text, self._ctx())
        assert plan.tasks[0].extra_tools == ["read_file", "run_context"]
        assert plan.mode == "sequential"

    def test_nested_json_parsed_correctly(self):
        """Regression: non-greedy regex used to stop at first nested }."""
        from callflow_tracer.agent.agents.router import _extract_dispatch_plan

        text = (
            'DISPATCH_PLAN:\n'
            '{"agents": ["GrepAgent", "CostAgent"], "mode": "parallel",'
            ' "skills": {"GrepAgent": ["SecurityScan"], "CostAgent": ["CostProfiling"]},'
            ' "tools": {"GrepAgent": ["read_file"]},'
            ' "hints": {"GrepAgent": {"query": "auth"}}}'
        )
        plan = _extract_dispatch_plan(text, self._ctx())
        assert len(plan.tasks) == 2
        grep_task = next(t for t in plan.tasks if t.agent_name == "GrepAgent")
        cost_task = next(t for t in plan.tasks if t.agent_name == "CostAgent")
        assert grep_task.skills == ["SecurityScan"]
        assert grep_task.extra_tools == ["read_file"]
        assert cost_task.skills == ["CostProfiling"]

    def test_fallback_on_invalid_json(self):
        from callflow_tracer.agent.agents.router import _extract_dispatch_plan
        from callflow_tracer.agent.core.context import SwarmContext

        ctx = SwarmContext(question="find slow code", cwd=".")
        text = "DISPATCH_PLAN:\n{not valid json at all"
        plan = _extract_dispatch_plan(text, ctx)
        # should fall back to keyword-based dispatch, not raise
        assert len(plan.tasks) > 0
        assert plan.reasoning == "fallback: keyword-based dispatch"

    def test_unknown_agents_filtered(self):
        from callflow_tracer.agent.agents.router import _extract_dispatch_plan

        text = (
            'DISPATCH_PLAN:\n'
            '{"agents": ["GrepAgent", "FakeAgent", "AnotherFake"], "mode": "parallel", "hints": {}}'
        )
        plan = _extract_dispatch_plan(text, self._ctx())
        assert plan.agent_names() == ["GrepAgent"]


# ── SwarmBuilder construction ──────────────────────────────────────────────────

class TestSwarmBuilder:
    def test_build_returns_swarm(self):
        from callflow_tracer.agent.orchestration import SwarmBuilder, Swarm

        swarm = SwarmBuilder(MagicMock()).build()
        assert isinstance(swarm, Swarm)

    def test_skill_registry_populated(self):
        from callflow_tracer.agent.orchestration import SwarmBuilder

        swarm = SwarmBuilder(MagicMock()).build()
        assert "StaticAnalysis" in swarm._skill_registry.names()
        assert "SecurityScan" in swarm._skill_registry.names()

    def test_with_skill_dir_loads_workspace_skills(self, tmp_path):
        from callflow_tracer.agent.orchestration import SwarmBuilder

        skill_file = tmp_path / "my_skill.py"
        skill_file.write_text(textwrap.dedent("""
            from callflow_tracer.agent.skills import Skill
            from callflow_tracer.agent.tools import GrepCodebaseTool
            SKILLS = [Skill(name="MyCustom", tools=(GrepCodebaseTool(),), description="x")]
        """), encoding="utf-8")

        swarm = SwarmBuilder(MagicMock()).with_skill_dir(tmp_path).build()
        assert swarm._skill_registry.get("MyCustom") is not None

    def test_with_plugin_dir_empty_dir_ok(self, tmp_path):
        from callflow_tracer.agent.orchestration import SwarmBuilder

        swarm = SwarmBuilder(MagicMock()).with_plugin_dir(tmp_path).build()
        assert swarm is not None

    def test_fluent_api_returns_builder(self):
        from callflow_tracer.agent.orchestration import SwarmBuilder

        builder = SwarmBuilder(MagicMock())
        assert builder.with_mode("sequential") is builder
        assert builder.with_timeout(30) is builder
        assert builder.with_max_workers(2) is builder
        assert builder.verbose() is builder
