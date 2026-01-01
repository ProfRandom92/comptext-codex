"""Command registry and metadata for CompText-Codex."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Mapping, Optional


@dataclass(frozen=True)
class CommandMetadata:
    """Represents a CompText command and its optional parameters."""

    name: str
    description: str
    module: str
    options: Mapping[str, str] = field(default_factory=dict)
    example: Optional[str] = None


class CommandRegistry:
    """Lightweight registry to resolve CompText commands."""

    def __init__(self, commands: Optional[Iterable[CommandMetadata]] = None) -> None:
        default_commands = commands if commands is not None else _DEFAULT_COMMANDS
        self._commands: Dict[str, CommandMetadata] = {cmd.name: cmd for cmd in default_commands}

    def get(self, name: str) -> Optional[CommandMetadata]:
        return self._commands.get(name)

    def list(self) -> Iterable[CommandMetadata]:
        return self._commands.values()

    def describe(self, name: str) -> str:
        command = self.get(name)
        if command is None:
            raise KeyError(f"Unknown command: {name}")
        return command.description


_DEFAULT_COMMANDS = [
    CommandMetadata(
        name="CODE_ANALYZE",
        description="Inspect code for readability, structure, and performance hotspots.",
        module="Module B - Programming",
        options={"perf_bottleneck": "Highlight performance bottlenecks", "style": "Target style guideline"},
        example="@CODE_ANALYZE[perf_bottleneck]",
    ),
    CommandMetadata(
        name="CODE_OPT",
        description="Suggest concrete improvements for the provided code snippet.",
        module="Module B - Programming",
        options={"explain": "explain=detail for verbose reasoning", "bench": "bench=compare to include benchmarks"},
        example="@CODE_OPT[explain=detail, bench=compare]",
    ),
    CommandMetadata(
        name="DOC_GEN",
        description="Generate API documentation or tutorials from a code base.",
        module="Module F - Documentation",
        options={"format": "Choose markdown or rst", "include_examples": "true to add runnable snippets"},
        example="@DOC_GEN[api, format=markdown, include_examples=true]",
    ),
    CommandMetadata(
        name="AUTOML",
        description="Configure an AutoML pipeline with sensible defaults.",
        module="Module E - ML Pipelines",
        options={"task": "classification or regression", "metric": "primary evaluation metric", "budget": "time budget in minutes"},
        example="@AUTOML[task=classification, metric=f1, budget=30]",
    ),
    CommandMetadata(
        name="MODEL_EVAL",
        description="Evaluate trained models with cross-validation and reporting.",
        module="Module E - ML Pipelines",
        options={"cv": "number of folds", "report": "set to full for confusion matrix and metrics"},
        example="@MODEL_EVAL[cv=5, report=full]",
    ),
    CommandMetadata(
        name="DOC_SUMMARY",
        description="Summarize documents with configurable tone and depth.",
        module="Module A - General",
        options={"style": "target voice such as executive or technical", "length": "short, medium, or long"},
        example="@DOC_SUMMARY[style=executive, length=short]",
    ),
]
