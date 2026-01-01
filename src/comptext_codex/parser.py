"""Parser and executor for the CompText DSL."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional

from .registry import CommandMetadata, CommandRegistry

COMMAND_PATTERN = re.compile(r"@(?P<name>[A-Z0-9_]+)(?:\[(?P<options>[^\]]*)\])?$")


@dataclass
class CommandInvocation:
    """Represents a parsed command with its resolved metadata."""

    name: str
    options: Mapping[str, str | bool] = field(default_factory=dict)
    metadata: Optional[CommandMetadata] = None

    def as_dict(self) -> Dict[str, object]:
        payload: Dict[str, object] = {"name": self.name, "options": dict(self.options)}
        if self.metadata:
            payload["description"] = self.metadata.description
            payload["module"] = self.metadata.module
        return payload


class CompTextParser:
    """Parse and execute CompText command strings."""

    def __init__(self, registry: Optional[CommandRegistry] = None) -> None:
        self.registry = registry or CommandRegistry()

    def parse(self, command_string: str) -> List[CommandInvocation]:
        segments = [segment.strip() for segment in command_string.split("+") if segment.strip()]
        if not segments:
            raise ValueError("No commands found in input string")

        parsed: List[CommandInvocation] = []
        for segment in segments:
            match = COMMAND_PATTERN.match(segment)
            if not match:
                raise ValueError(f"Invalid command syntax: {segment}")
            name = match.group("name")
            options = self._parse_options(match.group("options"))
            metadata = self.registry.get(name)
            parsed.append(CommandInvocation(name=name, options=options, metadata=metadata))
        return parsed

    def execute(self, command_string: str, **context: object) -> Dict[str, object]:
        commands = [invocation.as_dict() for invocation in self.parse(command_string)]
        payload: Dict[str, object] = {"commands": commands}
        if context:
            payload["context"] = context
        payload["summary"] = self._summarize(commands)
        return payload

    def _parse_options(self, raw: Optional[str]) -> MutableMapping[str, str | bool]:
        if not raw:
            return {}
        options: MutableMapping[str, str | bool] = {}
        for token in [part.strip() for part in raw.split(",") if part.strip()]:
            if "=" in token:
                key, value = token.split("=", 1)
                options[key.strip()] = value.strip()
            else:
                options[token] = True
        return options

    def _summarize(self, commands: Iterable[Mapping[str, object]]) -> str:
        segments = []
        for command in commands:
            name = command.get("name", "?")
            options = command.get("options", {})
            if options:
                option_view = ", ".join(f"{key}={value}" if value is not True else key for key, value in options.items())
                segments.append(f"{name}({option_view})")
            else:
                segments.append(name)
        return " → ".join(segments)

    def to_json(self, command_string: str, **context: object) -> str:
        return json.dumps(self.execute(command_string, **context), indent=2)
