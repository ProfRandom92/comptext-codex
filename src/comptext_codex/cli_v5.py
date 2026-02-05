"""CompText V5.0 ULTRA CLI - Interactive Command Line Interface."""

import sys
import json
from typing import Optional
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich import print as rprint

from .parser_v5 import CompTextParserV5, CompTextCommandV5


console = Console()


@click.group()
@click.version_option(version="5.0.0", prog_name="CompText ULTRA")
def cli():
    """CompText V5.0 ULTRA - 94% Token Reduction Protocol"""
    pass


@cli.command()
@click.argument('command', required=False)
@click.option('--format', '-f', type=click.Choice(['json', 'table', 'text']), default='table',
              help='Output format')
@click.option('--v4', is_flag=True, help='Show V4 equivalent')
@click.option('--stats', is_flag=True, help='Show token statistics')
@click.option('--natural', '-n', help='Natural language for comparison')
def parse(command: Optional[str], format: str, v4: bool, stats: bool, natural: Optional[str]):
    """Parse a V5.0 ULTRA command.

    Examples:
        comptext parse "C;P:FIB"
        comptext parse "B:[D:SUM]|[C;P:FIB]|[E;C:WHY]" --v4
        comptext parse "T;P;R:FIB" --stats --natural "Write unit tests"
    """
    if not command:
        console.print("[red]Error: Command required[/red]")
        sys.exit(1)

    parser = CompTextParserV5()

    try:
        results = parser.parse(command)

        if format == 'json':
            output = []
            for cmd in results:
                output.append({
                    'command': cmd.command,
                    'language': cmd.language,
                    'modifiers': cmd.modifiers,
                    'task': cmd.task,
                    'raw': cmd.raw
                })
            console.print_json(json.dumps(output, indent=2))

        elif format == 'table':
            table = Table(title="Parsed V5.0 ULTRA Commands")
            table.add_column("Command", style="cyan")
            table.add_column("Language", style="magenta")
            table.add_column("Modifiers", style="yellow")
            table.add_column("Task", style="green")

            for cmd in results:
                table.add_row(
                    parser.COMMANDS.get(cmd.command, cmd.command),
                    parser.LANGUAGES.get(cmd.language, cmd.language) if cmd.language else "-",
                    ", ".join([parser.MODIFIERS.get(m, m) for m in cmd.modifiers]) if cmd.modifiers else "-",
                    cmd.task or "-"
                )

            console.print(table)

            if v4:
                console.print("\n[bold]V4.0 Format:[/bold]")
                for i, cmd in enumerate(results):
                    v4_format = parser.to_v4_format(cmd)
                    console.print(f"  [{i+1}] {v4_format}")

            if stats and natural:
                console.print("\n[bold]Token Statistics:[/bold]")
                token_stats = parser.calculate_token_reduction(natural, command)
                stats_table = Table(show_header=False)
                stats_table.add_row("Natural Language", f"{token_stats['natural_tokens']} tokens")
                stats_table.add_row("V5.0 ULTRA", f"{token_stats['v5_tokens']} tokens")
                stats_table.add_row("Tokens Saved", f"{token_stats['tokens_saved']} tokens")
                stats_table.add_row("Reduction", f"[green bold]{token_stats['reduction_percent']}%[/green bold]")
                console.print(stats_table)

        else:  # text
            for i, cmd in enumerate(results):
                console.print(f"[{i+1}] {cmd.command} - {cmd.task}")

    except Exception as e:
        console.print(f"[red]Parse Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('command')
@click.option('--language', '-l', help='Language (PYTHON, JAVASCRIPT, etc.)')
@click.option('--modifiers', '-m', multiple=True, help='Modifiers (ROBUST, CONCISE, etc.)')
@click.option('--task', '-t', help='Task name')
def encode(command: str, language: Optional[str], modifiers: tuple, task: Optional[str]):
    """Encode a command to V5.0 ULTRA format.

    Examples:
        comptext encode CODE --language PYTHON --task FIB
        comptext encode TEST --language PYTHON --modifiers ROBUST --task FIB
    """
    parser = CompTextParserV5()

    try:
        result = parser.encode(
            command.upper(),
            language.upper() if language else None,
            [m.upper() for m in modifiers] if modifiers else None,
            task
        )
        console.print(Panel(result, title="V5.0 ULTRA Encoded", border_style="green"))
    except Exception as e:
        console.print(f"[red]Encode Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--natural', '-n', required=True, help='Natural language command')
@click.option('--v5', required=True, help='V5.0 ULTRA command')
def benchmark(natural: str, v5: str):
    """Benchmark token reduction.

    Example:
        comptext benchmark -n "Write Python Fibonacci" -v "C;P:FIB"
    """
    parser = CompTextParserV5()

    stats = parser.calculate_token_reduction(natural, v5)

    table = Table(title="Token Reduction Benchmark", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Natural Language", natural)
    table.add_row("Natural Tokens", str(stats['natural_tokens']))
    table.add_row("V5.0 ULTRA Command", v5)
    table.add_row("V5 Tokens", str(stats['v5_tokens']))
    table.add_row("Tokens Saved", f"[yellow]{stats['tokens_saved']}[/yellow]")
    table.add_row("Reduction", f"[green bold]{stats['reduction_percent']}%[/green bold]")
    table.add_row("Char Reduction", f"{stats['char_reduction']}%")

    console.print(table)


@cli.command()
def reference():
    """Display V5.0 ULTRA syntax reference."""

    console.print(Panel.fit(
        "[bold cyan]CompText V5.0 ULTRA - Quick Reference[/bold cyan]",
        border_style="cyan"
    ))

    # Commands
    cmd_table = Table(title="Commands (Single Char)", show_header=True)
    cmd_table.add_column("Char", style="cyan")
    cmd_table.add_column("Command", style="white")

    parser = CompTextParserV5()
    for char, full in parser.COMMANDS.items():
        cmd_table.add_row(char, full)

    console.print(cmd_table)

    # Languages
    lang_table = Table(title="Languages (Single Char)", show_header=True)
    lang_table.add_column("Char", style="magenta")
    lang_table.add_column("Language", style="white")

    for char, full in parser.LANGUAGES.items():
        lang_table.add_row(char, full)

    console.print(lang_table)

    # Modifiers
    mod_table = Table(title="Modifiers (Single Char)", show_header=True)
    mod_table.add_column("Char", style="yellow")
    mod_table.add_column("Modifier", style="white")

    for char, full in parser.MODIFIERS.items():
        mod_table.add_row(char, full)

    console.print(mod_table)

    # Examples
    console.print("\n[bold]Examples:[/bold]")
    examples = [
        ("C;P:FIB", "Code Python Fibonacci"),
        ("T;P;R:FIB", "Test Python (Robust) Fibonacci"),
        ("B:[D:SUM]|[C;P:FIB]|[E;C:WHY]", "Batch: Document + Code + Explain"),
        ("B:[A:STRUCT]|[F;T:MEM]|[O;S:Q]|[D:API]", "Batch: Analyze + Fix + Optimize + Document"),
    ]

    for v5, desc in examples:
        console.print(f"  [cyan]{v5}[/cyan]")
        console.print(f"    {desc}\n")


@cli.command()
def interactive():
    """Start interactive V5.0 ULTRA shell."""

    parser = CompTextParserV5()

    console.print(Panel.fit(
        "[bold cyan]CompText V5.0 ULTRA - Interactive Shell[/bold cyan]\n"
        "Type V5 commands or 'help' for reference\n"
        "Type 'exit' to quit",
        border_style="cyan"
    ))

    while True:
        try:
            cmd = console.input("\n[bold green]v5>[/bold green] ")

            if not cmd.strip():
                continue

            if cmd.lower() in ['exit', 'quit', 'q']:
                console.print("[yellow]Goodbye![/yellow]")
                break

            if cmd.lower() == 'help':
                console.print("\n[bold]Quick Commands:[/bold]")
                console.print("  help      - Show this help")
                console.print("  ref       - Show syntax reference")
                console.print("  exit      - Exit shell")
                console.print("\n[bold]Try these:[/bold]")
                console.print("  C;P:FIB")
                console.print("  B:[D:SUM]|[C;P:FIB]|[E;C:WHY]")
                continue

            if cmd.lower() == 'ref':
                reference.invoke(click.Context(reference))
                continue

            # Parse command
            results = parser.parse(cmd)

            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Command")
            table.add_column("Language")
            table.add_column("Modifiers")
            table.add_column("Task")

            for result in results:
                table.add_row(
                    parser.COMMANDS.get(result.command, result.command or "?"),
                    parser.LANGUAGES.get(result.language, result.language) if result.language else "-",
                    ", ".join([parser.MODIFIERS.get(m, m) for m in result.modifiers]) if result.modifiers else "-",
                    result.task or "-"
                )

            console.print(table)

            # Show V4 equivalent
            console.print("\n[dim]V4.0 Equivalent:[/dim]")
            for i, r in enumerate(results):
                console.print(f"  [{i+1}] [dim]{parser.to_v4_format(r)}[/dim]")

        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'exit' to quit[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


@cli.command()
def examples():
    """Show real-world V5.0 ULTRA examples with benchmarks."""

    parser = CompTextParserV5()

    console.print(Panel.fit(
        "[bold cyan]CompText V5.0 ULTRA - Real-World Examples[/bold cyan]",
        border_style="cyan"
    ))

    examples = [
        {
            "name": "Simple Code Generation",
            "natural": "Write a Python function for Fibonacci",
            "v5": "C;P:FIB"
        },
        {
            "name": "Test Generation with Modifiers",
            "natural": "Write comprehensive unit tests for the Fibonacci function in Python with edge cases",
            "v5": "T;P;R:FIB"
        },
        {
            "name": "Multi-Task Batch",
            "natural": "Summarize the repository, write Python Fibonacci, and explain why CompText is fast",
            "v5": "B:[D:SUM]|[C;P:FIB]|[E;C:WHY]"
        },
        {
            "name": "Complex Workflow",
            "natural": "Analyze the codebase structure, fix TypeScript memory leaks, optimize database queries, and generate API documentation",
            "v5": "B:[A:STRUCT]|[F;T:MEM]|[O;S:Q]|[D:API]"
        }
    ]

    for ex in examples:
        stats = parser.calculate_token_reduction(ex['natural'], ex['v5'])

        console.print(f"\n[bold yellow]{ex['name']}[/bold yellow]")
        console.print(f"[dim]Natural:[/dim] {ex['natural']}")
        console.print(f"[dim]V5.0:[/dim] [cyan]{ex['v5']}[/cyan]")
        console.print(f"[green]Reduction: {stats['reduction_percent']}% ({stats['natural_tokens']} -> {stats['v5_tokens']} tokens)[/green]")


def main():
    """Main CLI entry point."""
    cli()


if __name__ == '__main__':
    main()
