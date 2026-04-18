"""
CommandFactory — Factory Pattern for dynamic command creation.

Responsibility: given a command name string, produce a command instance.
This decouples the dispatcher (which knows names) from the concrete classes
(which know how to execute).

Two modes:
  1. Eager registration: call register_class(name, cls) at bootstrap.
     The factory holds a dict[str, type[BaseCommand]].
  2. Lazy discovery: call discover_plugins(path) to scan a directory and
     import any module that exports a class with a `name` attribute.
     This is the plugin system entry point.

DSA: creator_map is a dict — O(1) factory resolution.
     Plugin discovery uses os.scandir (O(d) where d = directory entries).
"""

from __future__ import annotations

import importlib
import importlib.util
import logging
import os
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..interfaces.command import BaseCommand

log = logging.getLogger(__name__)


class CommandFactory:
    """
    Produces BaseCommand instances from registered class references.

    Usage:
        factory = CommandFactory()
        factory.register_class("trace", TraceCommand)
        factory.register_class("flamegraph", FlamegraphCommand)

        cmd = factory.create("trace")   # → TraceCommand()
    """

    def __init__(self) -> None:
        # HashMap: command name → class (not instance)
        # Commands are instantiated on create(), keeping the factory stateless
        self._creator_map: dict[str, type] = {}

    def register_class(self, name: str, cls: type) -> None:
        """Register a command class under a given name."""
        self._creator_map[name] = cls

    def create(self, name: str) -> "BaseCommand":
        """
        Instantiate and return the named command.
        Raises KeyError if name is not registered.
        """
        cls = self._creator_map.get(name)
        if cls is None:
            raise KeyError(f"No command class registered for '{name}'")
        return cls()

    def registered_names(self) -> list[str]:
        return list(self._creator_map.keys())

    # ── Plugin discovery ───────────────────────────────────────────────────────

    def discover_plugins(self, plugin_dir: str) -> list[str]:
        """
        Scan `plugin_dir` for Python files/packages that export a BaseCommand
        subclass. Any module that defines a class with a `.name` attribute and
        an `execute` method is registered automatically.

        Returns list of successfully registered command names.

        This is how third-party plugins add commands at runtime without
        modifying the registry or main.py — the agent runtime calls
        discover_plugins("~/.callflow/plugins/") on startup.
        """
        from ..interfaces.command import BaseCommand as _BaseCommand

        registered: list[str] = []

        if not os.path.isdir(plugin_dir):
            return registered

        for entry in os.scandir(plugin_dir):
            if not (entry.name.endswith(".py") or (entry.is_dir() and
                    os.path.isfile(os.path.join(entry.path, "__init__.py")))):
                continue
            try:
                module_name = f"_callflow_plugin_{entry.name.replace('.py', '')}"
                spec = importlib.util.spec_from_file_location(
                    module_name,
                    entry.path if entry.is_dir()
                    else entry.path,
                )
                if spec is None or spec.loader is None:
                    continue
                mod = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = mod
                spec.loader.exec_module(mod)  # type: ignore[union-attr]

                # Find all BaseCommand subclasses defined in this module
                for attr_name in dir(mod):
                    obj = getattr(mod, attr_name)
                    if (
                        isinstance(obj, type)
                        and issubclass(obj, _BaseCommand)
                        and obj is not _BaseCommand
                        and hasattr(obj, "name")
                    ):
                        instance = obj()
                        self.register_class(instance.name, obj)
                        registered.append(instance.name)
                        log.info("Plugin command registered: %s (from %s)", instance.name, entry.path)

            except Exception as exc:
                # Plugin load failure = degraded mode (warn + skip, not crash)
                log.warning("Failed to load plugin %s: %s", entry.path, exc)

        return registered
