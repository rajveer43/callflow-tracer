"""
CommandRegistry — HashMap-based command store with O(1) lookup.

DSA rationale:
  - Primary store: dict[str, BaseCommand] — O(1) average case for register/resolve.
  - Alias map: secondary dict[str, str] mapping alias → primary name.
    Two-level lookup: alias_map[alias] → name → registry[name].
    Still O(1) but keeps the primary map clean (one entry per command).
  - Ordered iteration via insertion order (Python 3.7+ dict guarantee).
    Commands appear in --help in registration order, not alphabetical chaos.

  Optional Trie extension (not implemented here, flagged for REPL auto-complete):
    A prefix Trie over all registered names + aliases gives O(k) prefix search
    where k = query length, enabling tab-completion with negligible memory cost
    for the typical 10–30 command vocabulary.

Registry is NOT a Singleton. The dispatcher owns one instance and passes it
where needed. This makes testing trivial: build a registry with only the
commands under test, no global state.
"""

from __future__ import annotations

from typing import Iterator

from ..interfaces.command import BaseCommand


class DuplicateCommandError(ValueError):
    pass


class CommandNotFoundError(KeyError):
    pass


class CommandRegistry:
    """
    Central command store. Supports:
      - register(command): add a command; error on duplicate primary name
      - resolve(name): return command by primary name or alias in O(1)
      - all(): iterate commands in registration order
      - names(): all primary names (for argparse subparser setup)

    Supports dynamic registration at runtime — plugins call register() after
    bootstrap to inject new commands without touching main.py.
    """

    def __init__(self) -> None:
        # Primary map: command name → command instance
        self._commands: dict[str, BaseCommand] = {}
        # Alias map: alias → primary name (two-hop lookup, still O(1))
        self._aliases: dict[str, str] = {}

    def register(self, command: BaseCommand) -> None:
        """
        Register a command. Raises DuplicateCommandError if primary name or
        any alias conflicts with an existing entry.
        """
        name = command.name
        if name in self._commands or name in self._aliases:
            raise DuplicateCommandError(
                f"Command '{name}' is already registered"
            )
        for alias in command.aliases:
            if alias in self._commands or alias in self._aliases:
                raise DuplicateCommandError(
                    f"Alias '{alias}' for command '{name}' conflicts with existing entry"
                )

        self._commands[name] = command
        for alias in command.aliases:
            self._aliases[alias] = name

    def resolve(self, name: str) -> BaseCommand:
        """
        Resolve name or alias → command in O(1).
        Raises CommandNotFoundError if not found.
        """
        # Direct hit (primary name)
        if name in self._commands:
            return self._commands[name]
        # Two-hop via alias
        primary = self._aliases.get(name)
        if primary:
            return self._commands[primary]
        raise CommandNotFoundError(
            f"Unknown command: '{name}'. "
            f"Available: {', '.join(self._commands)}"
        )

    def contains(self, name: str) -> bool:
        return name in self._commands or name in self._aliases

    def all(self) -> Iterator[BaseCommand]:
        """Yield all commands in registration order."""
        yield from self._commands.values()

    def names(self) -> list[str]:
        """Primary names only, in registration order."""
        return list(self._commands.keys())

    def __len__(self) -> int:
        return len(self._commands)

    def __repr__(self) -> str:
        return f"<CommandRegistry commands={self.names()}>"
