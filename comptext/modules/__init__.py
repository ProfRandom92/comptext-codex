"""Command registry for CompText modules."""
from __future__ import annotations

from .ai_control import AI_CONTROL_COMMANDS
from .general import GENERAL_COMMANDS
from .programming import PROGRAMMING_COMMANDS
from .visualization import VISUALIZATION_COMMANDS

registry = {}
registry.update(GENERAL_COMMANDS)
registry.update(PROGRAMMING_COMMANDS)
registry.update(VISUALIZATION_COMMANDS)
registry.update(AI_CONTROL_COMMANDS)

__all__ = ["registry"]
