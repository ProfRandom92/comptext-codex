"""Token reporting utilities for the CompText codex."""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Any, Iterable, Mapping

import yaml


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"Failed to parse YAML file: {path}") from exc


def load_commands(codex_dir: Path) -> list[dict[str, Any]]:
    """Load command definitions from a codex directory."""
    commands: list[dict[str, Any]] = []
    aggregated = codex_dir / "commands.yaml"
    if aggregated.exists():
        commands.extend(_load_yaml(aggregated).get("commands", []))

    commands_dir = codex_dir / "commands"
    if commands_dir.exists():
        for path in sorted(commands_dir.glob("*.yaml")):
            commands.extend(_load_yaml(path).get("commands", []))

    return commands


def load_modules(codex_dir: Path) -> dict[str, dict[str, Any]]:
    """Load module definitions keyed by module code."""
    modules: dict[str, dict[str, Any]] = {}
    aggregated = codex_dir / "modules.yaml"
    if aggregated.exists():
        for item in _load_yaml(aggregated).get("modules", []):
            code = item.get("code")
            if not code:
                continue
            modules[code] = item

    modules_dir = codex_dir / "modules"
    if modules_dir.exists():
        for path in sorted(modules_dir.glob("*.yaml")):
            for item in _load_yaml(path).get("modules", []):
                code = item.get("code")
                if not code:
                    continue
                modules.setdefault(code, item)

    return modules


def build_token_report(
    commands: Iterable[dict[str, Any]], modules: Mapping[str, dict[str, Any]]
) -> dict[str, Any]:
    """Create an in-memory token report."""
    commands_list = list(commands)
    token_hints: list[int] = []
    for cmd in commands_list:
        hint = cmd.get("token_cost_hint")
        if hint is not None:
            token_hints.append(int(hint))

    module_summary: dict[str, dict[str, Any]] = {}
    for cmd in commands_list:
        code = cmd.get("module")
        if not code:
            continue
        summary = module_summary.setdefault(
            code,
            {
                "name": modules.get(code, {}).get("name", ""),
                "token_priority": modules.get(code, {}).get("token_priority", ""),
                "command_count": 0,
                "token_cost_hints": [],
            },
        )
        summary["command_count"] += 1
        if cmd.get("token_cost_hint") is not None:
            summary["token_cost_hints"].append(cmd["token_cost_hint"])

    for summary in module_summary.values():
        hints = summary["token_cost_hints"]
        summary["avg_token_cost"] = float(mean(hints)) if hints else 0.0

    return {
        "total_commands": len(commands_list),
        "commands_with_token_hint": len(token_hints),
        "avg_token_cost": float(mean(token_hints)) if token_hints else 0.0,
        "modules": module_summary,
    }


def render_text_report(report: Mapping[str, Any]) -> str:
    """Render a human-friendly text report."""
    lines = [
        f"Total commands: {report['total_commands']}",
        f"Commands with token hints: {report['commands_with_token_hint']}",
        f"Average token cost: {report['avg_token_cost']:.1f}",
        "",
        "Per-module summary:",
    ]
    modules: dict[str, Any] = report.get("modules", {})
    for code in sorted(modules.keys()):
        module = modules[code]
        lines.append(
            f"- {code} ({module.get('name', '').strip() or 'Unknown'}): "
            f"{module.get('command_count', 0)} commands, "
            f"avg token cost {module.get('avg_token_cost', 0.0):.1f} "
            f"(priority: {module.get('token_priority', 'n/a')})"
        )
    return "\n".join(lines)


def report_as_json(report: Mapping[str, Any]) -> str:
    """Return report as formatted JSON string."""
    return json.dumps(report, indent=2, sort_keys=True)
