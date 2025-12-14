"""CLI entrypoint for CompText Codex utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import click

from .token_report import build_token_report, load_commands, load_modules, render_text_report, report_as_json


@click.group()
def main() -> None:
    """CompText Codex command-line tools."""


@main.command("token-report")
@click.option(
    "--codex-dir",
    default="codex",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Path to the codex directory.",
)
@click.option(
    "--module",
    "module_filter",
    default=None,
    help="Filter the report to a specific module code.",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help="Output format for the report.",
)
def token_report(
    codex_dir: Path, module_filter: Optional[str], output_format: str
) -> None:
    """Generate a token usage report for the codex."""
    commands = load_commands(codex_dir)
    if module_filter:
        commands = [cmd for cmd in commands if cmd.get("module") == module_filter]

    modules = load_modules(codex_dir)
    report = build_token_report(commands, modules)

    if output_format.lower() == "json":
        click.echo(report_as_json(report))
    else:
        click.echo(render_text_report(report))


if __name__ == "__main__":
    main()
