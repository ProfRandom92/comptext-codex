"""Command-line interface for CompText-Codex."""

from __future__ import annotations

import json
from typing import Dict

import click

from .catalog import iter_catalog
from .parser import CompTextParser
from .registry import CommandRegistry


@click.command()
@click.argument("command")
@click.option(
    "--context",
    multiple=True,
    help="Optional context key=value pairs added to the execution payload.",
)
@click.option(
    "--list-catalog",
    is_flag=True,
    help="List bundled catalog entries before executing the command.",
)
def main(command: str, context: tuple[str, ...], list_catalog: bool) -> None:
    parser = CompTextParser(CommandRegistry())

    if list_catalog:
        click.echo("# CompText Catalog")
        for entry in iter_catalog():
            title = entry.get("Titel", "<unbenannt>")
            description = entry.get("Beschreibung", "")
            module = entry.get("Modul", "")
            click.echo(f"- {title} ({module}) — {description}")
        click.echo()

    parsed_context: Dict[str, object] = {}
    for item in context:
        if "=" not in item:
            raise click.BadParameter("Context values must be in key=value format.")
        key, value = item.split("=", 1)
        parsed_context[key] = value

    result = parser.execute(command, **parsed_context)
    click.echo(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":  # pragma: no cover - manual CLI entry point
    main()
