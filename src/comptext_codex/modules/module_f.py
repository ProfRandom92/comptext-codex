"""Module F: Documentation - API docs, tutorials, changelogs, design docs."""

from typing import Any, Dict

from comptext_codex.registry import codex_module, codex_command
from .base import BaseModule


@codex_module(
    code="F",
    name="Documentation",
    purpose="API docs, tutorials, changelogs, and design docs",
    token_priority="medium",
    security={"pii_safe": True, "threat_model": "content_sanitization"},
    privacy={"dp_budget": "epsilon<=0.2_per_call"},
)
class ModuleF(BaseModule):
    """Documentation module for generating various docs."""

    @codex_command(syntax="@DOC_GEN[type, format, ...]", description="Generate documentation", token_cost_hint=60)
    def execute_doc_gen(self, *args, context: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        return {"type": kwargs.get("type", "api"), "format": kwargs.get("format", "markdown"), "sections": ["Overview", "API Reference", "Examples"], "generated": True}

    @codex_command(syntax="@CHANGELOG[format, since, ...]", description="Generate changelog", token_cost_hint=50)
    def execute_changelog(self, *args, context: Dict[str, Any] = None, **kwargs) -> str:
        since = kwargs.get("since", "v1.0.0")
        return f"# Changelog\n\n## [Unreleased]\n\n### Added\n- New features since {since}\n\n### Changed\n- Updated components\n\n### Fixed\n- Bug fixes\n"


def get_module() -> ModuleF:
    return ModuleF()
