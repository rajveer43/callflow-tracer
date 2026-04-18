"""
orchestration/plugin_loader.py — Discovers and loads custom agent plugins.

Users place .py files in ~/.callflow/agents/ that call api.register_agent(MyAgentClass).
Each plugin file must define a top-level `register(api)` function.

Design patterns:
  Plugin + Registry — AgentPluginApi is the single registration surface
  Factory           — load_agent_plugins() returns name→agent instances
  Adapter           — user agents subclass BaseAgent (same ABC, no new interface)

DSA:
  importlib.util dynamic import — no sys.path pollution
  dict[str, type[BaseAgent]]    — O(1) duplicate-name detection at registration time
  sorted(glob("*.py"))          — deterministic load order across platforms
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from ..agents.base import BaseAgent
from ..core.exceptions import AgentError
from ..core.types import AGENT_NAMES

if TYPE_CHECKING:
    from ...ai.llm_provider import LLMProvider


class PluginError(AgentError):
    """Raised when a plugin fails to load or registers a conflicting agent name."""


def _get_agent_name(cls: type) -> str:
    """
    Retrieve the agent name from a BaseAgent subclass.

    Creates a minimal stub instance (provider=None) to call the name property.
    Falls back to cls.__name__ if anything goes wrong.
    """
    try:
        obj = cls.__new__(cls)
        obj._provider = None      # type: ignore[attr-defined]
        obj._max_turns = 4        # type: ignore[attr-defined]
        obj._temperature = 0.1    # type: ignore[attr-defined]
        return obj.name           # type: ignore[return-value]
    except Exception:
        return cls.__name__


class AgentPluginApi:
    """
    Registration surface exposed to user plugin files.

    User plugins call api.register_agent(MyAgentClass) from their
    module-level register(api) function.
    """

    def __init__(self) -> None:
        self._registered: dict[str, type[BaseAgent]] = {}

    def register_agent(self, cls: type[BaseAgent]) -> None:
        """
        Register a custom agent class.

        Raises PluginError if the name conflicts with a built-in agent or
        another already-registered plugin.
        """
        name = _get_agent_name(cls)
        if name in AGENT_NAMES:
            raise PluginError(
                f"Plugin agent name '{name}' conflicts with built-in agent. "
                "Choose a different name."
            )
        if name in self._registered:
            raise PluginError(f"Duplicate plugin agent name: '{name}'")
        self._registered[name] = cls

    @property
    def registered(self) -> dict[str, type[BaseAgent]]:
        return dict(self._registered)


def _load_one_plugin(py_file: Path, api: AgentPluginApi) -> None:
    """Dynamically import one plugin file and call its register(api) function."""
    module_name = f"_callflow_plugin_{py_file.stem}"
    spec = importlib.util.spec_from_file_location(module_name, py_file)
    if spec is None or spec.loader is None:
        return
    module = importlib.util.module_from_spec(spec)
    # Don't add to sys.modules to avoid pollution; but we need a temporary entry
    # so relative imports within the plugin can resolve if needed
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)  # type: ignore[attr-defined]
        register_fn = getattr(module, "register", None)
        if callable(register_fn):
            register_fn(api)
    except PluginError:
        raise
    except Exception as exc:
        raise PluginError(f"Failed to load plugin '{py_file.name}': {exc}") from exc
    finally:
        sys.modules.pop(module_name, None)


def load_agent_plugins(
    provider: "LLMProvider",
    plugin_dir: Path | None = None,
) -> dict[str, BaseAgent]:
    """
    Discover and load all .py plugin files from plugin_dir.

    Returns a dict mapping agent name → instantiated agent.
    Files are loaded in sorted order for deterministic behaviour.
    Returns an empty dict if plugin_dir does not exist.
    """
    plugin_dir = plugin_dir or (Path.home() / ".callflow" / "agents")
    if not plugin_dir.is_dir():
        return {}

    api = AgentPluginApi()
    for py_file in sorted(plugin_dir.glob("*.py")):
        _load_one_plugin(py_file, api)

    return {name: cls(provider) for name, cls in api.registered.items()}
