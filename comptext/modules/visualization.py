"""Visualization-related CompText commands."""
from __future__ import annotations

from typing import Dict

from ..parser import Command


def chart(command: Command, context: Dict[str, object]) -> str:
    chart_type = command.parameters.get("type", "bar")
    style = command.parameters.get("style", "professional")
    export = command.parameters.get("export", "png")
    return "\n".join(
        [
            "=== CHART SPEC ===",
            f"Type: {chart_type}",
            f"Style: {style}",
            f"Export format: {export}",
            "Ready to render using matplotlib or Vega-Lite.",
        ]
    )


def diagram(command: Command, context: Dict[str, object]) -> str:
    diagram_type = command.parameters.get("type", "flowchart")
    notation = command.parameters.get("notation", "uml")
    subject = command.parameters.get("subject", "process")
    return "\n".join(
        [
            "=== DIAGRAM PLAN ===",
            f"Diagram: {diagram_type} ({notation})",
            f"Subject: {subject}",
            "Nodes: start -> task -> validate -> done",
            "Edges: start->task, task->validate, validate->done",
        ]
    )


def dashboard(command: Command, context: Dict[str, object]) -> str:
    layout = command.parameters.get("layout", "grid")
    theme = command.parameters.get("theme", "professional")
    responsive = command.parameters.get("responsive", True)
    data = context.get("data") or {}
    metrics = ", ".join(data.keys()) if isinstance(data, dict) and data else "no metrics provided"
    return "\n".join(
        [
            "=== DASHBOARD BLUEPRINT ===",
            f"Layout: {layout} | Theme: {theme} | Responsive: {responsive}",
            f"Metrics available: {metrics}",
            "Generates a React + Tailwind starter with cards and charts.",
        ]
    )


VISUALIZATION_COMMANDS = {
    "CHART": chart,
    "DIAGRAM": diagram,
    "DASHBOARD": dashboard,
}

__all__ = ["VISUALIZATION_COMMANDS"]
