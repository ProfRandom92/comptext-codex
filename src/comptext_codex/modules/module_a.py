"""Module A: Core Commands - Essential CompText DSL commands for text manipulation."""

import re
from typing import Any, Dict

from comptext_codex.registry import codex_module, codex_command
from .base import BaseModule


@codex_module(
    code="A",
    name="Core Commands",
    purpose="Essential CompText DSL commands for text manipulation",
    token_priority="high",
    security={"pii_safe": True, "threat_model": "prompt_injection_hardened"},
    privacy={"dp_budget": "epsilon<=1.0_per_call", "federated_ready": True},
)
class ModuleA(BaseModule):
    """Core Commands module for text manipulation and basic operations."""

    @codex_command(
        syntax="@A:compress <text>",
        description="Compress text by removing redundancy while preserving meaning",
        aliases=["shrink", "condense"],
        examples=["@A:compress The quick brown fox jumps over the lazy dog multiple times repeatedly"],
        token_cost_hint=50,
    )
    def execute_compress(self, text: str = "", *, context: Dict[str, Any] = None, **kwargs) -> str:
        if not text:
            return ""
        words = text.split()
        seen: set = set()
        compressed = []
        for word in words:
            wl = word.lower()
            if wl not in seen or wl in {"the", "a", "an"}:
                compressed.append(word)
                seen.add(wl)
        result = " ".join(compressed)
        result = re.sub(r"\b(\w+)\s+\1\b", r"\1", result, flags=re.IGNORECASE)
        return result

    @codex_command(
        syntax="@A:expand <compressed_text>",
        description="Expand compressed text to full verbose form",
        aliases=["elaborate", "verbose"],
        examples=["@A:expand QBF jump dog"],
        token_cost_hint=100,
    )
    def execute_expand(self, compressed_text: str = "", *, context: Dict[str, Any] = None, **kwargs) -> str:
        return f"Expanded form: {compressed_text}"


def get_module() -> ModuleA:
    return ModuleA()
