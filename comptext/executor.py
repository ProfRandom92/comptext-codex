"""Command execution layer for the CompText DSL."""
from __future__ import annotations

from typing import Callable, Dict, Iterable, List

from .parser import Command
from .modules import registry

Handler = Callable[[Command, Dict[str, object]], str]


def _format_header(title: str) -> str:
    return f"=== {title} ==="


class CommandExecutor:
    """Execute parsed commands using a registry of handlers."""

    def __init__(self, command_registry: Dict[str, Handler] | None = None):
        self.registry: Dict[str, Handler] = command_registry or registry

    def run(self, commands: Iterable[Command], **context) -> str:
        outputs: List[str] = []
        for command in commands:
            handler = self.registry.get(command.name, self._unknown_command)
            outputs.append(handler(command, context))
        return "\n\n".join(outputs)

    def _unknown_command(self, command: Command, context: Dict[str, object]) -> str:
        suggestion = (
            "Command not recognized. Available commands include: "
            + ", ".join(sorted(self.registry.keys()))
        )
        return "\n".join([
            _format_header(f"{command.name} (unimplemented)"),
            suggestion,
            "Provide a supported command or extend the registry in `comptext.modules`.",
        ])


__all__ = ["CommandExecutor"]
