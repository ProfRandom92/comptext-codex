"""Parsing utilities for the CompText DSL.

The parser translates DSL command strings such as
```
@CODE_ANALYZE[perf_bottleneck] + @CODE_OPT[explain=detail]
```
into structured :class:`Command` instances. It is intentionally
forgiving and aims to provide meaningful error messages so that
users can iterate quickly when crafting commands.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Command:
    """Represents a single CompText command."""

    name: str
    parameters: Dict[str, object] = field(default_factory=dict)
    raw: str = ""


class ParseError(ValueError):
    """Raised when the DSL string cannot be parsed."""


class CompTextParser:
    """Parse and execute CompText commands.

    The parser exposes both :meth:`parse` for turning raw DSL strings
    into structured commands and :meth:`execute` for running them with
    a provided executor.
    """

    command_pattern = re.compile(r"@(?P<name>[A-Z0-9_]+)\[(?P<body>[^\]]*)\]")

    def __init__(self, executor=None):
        # The executor is defined in a separate module to keep parsing
        # responsibilities isolated. Import lazily to avoid circular
        # imports when the parser is used standalone.
        if executor is None:
            from .executor import CommandExecutor

            self.executor = CommandExecutor()
        else:
            self.executor = executor

    def parse(self, text: str) -> List[Command]:
        """Parse the DSL text into a list of commands.

        Parameters
        ----------
        text:
            The raw DSL string, e.g. ``"@SUMMARIZE[len=short] + @CHART[type=bar]"``.

        Returns
        -------
        list[Command]
            Structured command objects in the order they appear.
        """

        if not text or not text.strip():
            raise ParseError("No command provided")

        commands: List[Command] = []
        for raw_cmd in [part.strip() for part in text.split("+") if part.strip()]:
            match = self.command_pattern.fullmatch(raw_cmd)
            if not match:
                raise ParseError(f"Invalid command syntax: '{raw_cmd}'")

            name = match.group("name").upper()
            parameters = self._parse_parameters(match.group("body"))
            commands.append(Command(name=name, parameters=parameters, raw=raw_cmd))
        return commands

    def _parse_parameters(self, body: str) -> Dict[str, object]:
        """Parse a command parameter block into a dictionary."""

        parameters: Dict[str, object] = {}
        body = body.strip()
        if not body:
            return parameters

        for raw_param in [part.strip() for part in body.split(",") if part.strip()]:
            if "=" in raw_param:
                key, value = [piece.strip() for piece in raw_param.split("=", 1)]
                parameters[key] = self._coerce_value(value)
            else:
                # Flag-style parameters become booleans.
                parameters[raw_param] = True
        return parameters

    @staticmethod
    def _coerce_value(value: str):
        """Convert textual parameter values to pythonic types when possible."""

        lowered = value.lower()
        if lowered in {"true", "yes"}:
            return True
        if lowered in {"false", "no"}:
            return False

        # Try to cast numeric values.
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            return value

    def execute(self, text: str, **context):
        """Convenience wrapper combining parsing and execution."""

        commands = self.parse(text)
        return self.executor.run(commands, **context)


__all__ = ["Command", "CompTextParser", "ParseError"]
