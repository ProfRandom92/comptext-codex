"""CLI entrypoint for CompText Codex utilities."""

from __future__ import annotations

from pathlib import Path

import click

from .token_reduction import main as run_token_benchmark
from .token_report import (
    build_token_report,
    load_commands,
    load_modules,
    render_text_report,
    report_as_json,
)


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
    codex_dir: Path, module_filter: str | None, output_format: str
) -> None:
    """Generate a token usage report for the codex."""
    commands = load_commands(codex_dir)
    if module_filter:
        commands = [cmd for cmd in commands if cmd.get("module") == module_filter]
        if not commands:
            click.echo(
                f"No commands found for module filter '{module_filter}'.", err=True
            )
            raise SystemExit(1)

    modules = load_modules(codex_dir)
    report = build_token_report(commands, modules)

    if output_format.lower() == "json":
        click.echo(report_as_json(report))
    else:
        click.echo(render_text_report(report))


@main.command("token-benchmark")
@click.option(
    "--output",
    default="TOKEN_REDUCTION_RESULTS.md",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Where to write the token reduction benchmark report.",
)
def token_benchmark(output: Path) -> None:
    """Run the token reduction benchmark suite and write the markdown report."""
    run_token_benchmark(output_path=output)


if __name__ == "__main__":
    main()
