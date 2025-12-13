"""AI control and prompt-engineering commands."""
from __future__ import annotations

from typing import Dict, Iterable

from ..parser import Command


def model_config(command: Command, context: Dict[str, object]) -> str:
    temperature = command.parameters.get("temperature", 0.7)
    max_tokens = command.parameters.get("max_tokens", 500)
    system = command.parameters.get("system", "analysis")
    return "\n".join(
        [
            "=== MODEL CONFIG ===",
            f"Temperature: {temperature}",
            f"Max tokens: {max_tokens}",
            f"System profile: {system}",
            "Use these settings when calling your preferred LLM backend.",
        ]
    )


def chain(command: Command, context: Dict[str, object]) -> str:
    steps: Iterable[str] = command.parameters.get("steps") or []
    if isinstance(steps, str):
        steps = [step.strip() for step in steps.split(";") if step.strip()]
    lines = ["=== CHAIN ==="]
    if steps:
        lines.append(" -> ".join(steps))
    else:
        lines.append("No steps defined; add steps=[analyze, summarize, format]")
    return "\n".join(lines)


def prompt_optimize(command: Command, context: Dict[str, object]) -> str:
    goal = command.parameters.get("goal", "concise")
    preserve = command.parameters.get("preserve_meaning", True)
    return "\n".join(
        [
            "=== PROMPT OPTIMIZATION ===",
            f"Goal: {goal}",
            f"Preserve meaning: {preserve}",
            "Tip: prefer explicit bullet points and constraints over prose.",
        ]
    )


AI_CONTROL_COMMANDS = {
    "MODEL_CONFIG": model_config,
    "CHAIN": chain,
    "PROMPT_OPT": prompt_optimize,
}

__all__ = ["AI_CONTROL_COMMANDS"]
