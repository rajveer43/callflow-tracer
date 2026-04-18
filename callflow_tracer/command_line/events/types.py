"""Typed event definitions for the CLI event bus."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class EventType(Enum):
    COMMAND_STARTED    = auto()   # fired before execute()
    COMMAND_SUCCEEDED  = auto()   # fired when exit_code == 0
    COMMAND_FAILED     = auto()   # fired when exit_code != 0
    COMMAND_ERROR      = auto()   # fired when execute() raises unexpectedly
    MIDDLEWARE_BLOCKED = auto()   # middleware short-circuited the chain
    PLUGIN_REGISTERED  = auto()   # a plugin added a new command
    TRACE_RECORDED     = auto()   # a trace was captured (feeds agent runtime)


@dataclass
class CLIEvent:
    """
    Value object emitted to all subscribers.

    payload is a HashMap — flexible enough to carry any event-specific data
    without requiring a new class per event type.
    """
    type: EventType
    command_name: str
    payload: dict[str, Any] = field(default_factory=dict)
