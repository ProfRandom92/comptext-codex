#!/usr/bin/env python3
"""MedGemma-CompText-Impact — CLI Demo.

A rich terminal showcase that demonstrates CompText State Transfer:
compress raw patient text into a structured JSON state and visualise
the token savings.
"""

import json
import sys
import time

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import box

from src.core.comptext_mock import StateCompressor
from src.agents.nurse import NurseAgent
from src.agents.doctor import DoctorAgent

console = Console()

SAMPLE_INPUT = (
    "I have a headache and 39C fever since yesterday. "
    "I also feel nausea and body aches. My heart rate is 92 bpm."
)


def token_estimate(text: str) -> int:
    """Rough token count (words + punctuation)."""
    import re

    return len(re.findall(r"\w+|[^\w\s]", text))


def run_demo(raw_text: str) -> None:
    """Execute the full CompText State Transfer pipeline."""

    console.print()
    console.print(
        Panel(
            "[bold cyan]MedGemma-CompText-Impact[/bold cyan]\n"
            "[dim]Privacy-First · Edge-Compatible · Remote-Inference[/dim]",
            box=box.DOUBLE,
            expand=False,
        )
    )
    console.print()

    # --- Step 1: Intake -------------------------------------------------------
    console.print("[bold green]► Patient Input[/bold green]")
    console.print(Panel(raw_text, title="Raw Text", border_style="white"))

    # --- Step 2: Compression --------------------------------------------------
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("CompText Compression Running...", total=None)
        nurse = NurseAgent()
        state = nurse.intake(raw_text)
        time.sleep(0.8)  # visual pause
        progress.update(task, completed=True)

    state_json = state.model_dump_json(indent=2)

    console.print("[bold green]► Compressed State (JSON)[/bold green]")
    console.print(Panel(state_json, title="PatientState", border_style="cyan"))

    # --- Step 3: Size comparison ----------------------------------------------
    raw_size = len(raw_text)
    json_size = len(state_json)
    raw_tokens = token_estimate(raw_text)
    json_tokens = token_estimate(state_json)

    size_table = Table(
        title="Data Transfer Comparison",
        box=box.SIMPLE_HEAVY,
        show_lines=True,
    )
    size_table.add_column("Metric", style="bold")
    size_table.add_column("Raw Text", justify="right")
    size_table.add_column("CompText JSON", justify="right")
    size_table.add_column("Reduction", justify="right", style="green")
    size_table.add_row(
        "Characters",
        str(raw_size),
        str(json_size),
        f"{max(0, (1 - json_size / max(raw_size, 1)) * 100):.0f}%",
    )
    size_table.add_row(
        "Tokens (est.)",
        str(raw_tokens),
        str(json_tokens),
        f"{max(0, (1 - json_tokens / max(raw_tokens, 1)) * 100):.0f}%",
    )
    console.print(size_table)

    # --- Step 4: Token bar chart ----------------------------------------------
    # Simulate realistic context-window usage for multi-turn conversation
    standard_tokens = raw_tokens * 5  # 5-turn context history
    comptext_tokens = json_tokens  # single compressed state

    max_bar = 50
    standard_bar = max_bar
    comptext_bar = max(1, int(max_bar * comptext_tokens / max(standard_tokens, 1)))

    console.print()
    console.print("[bold yellow]► Token Usage Comparison[/bold yellow]")
    console.print(
        f"  Standard Context Tokens : [red]{'█' * standard_bar}[/red] "
        f"{standard_tokens}"
    )
    console.print(
        f"  CompText  State  Tokens : [green]{'█' * comptext_bar}[/green] "
        f"{comptext_tokens}"
    )
    savings_pct = max(0, (1 - comptext_tokens / max(standard_tokens, 1)) * 100)
    console.print(
        f"\n  [bold]Token savings: {savings_pct:.1f}%[/bold]"
    )

    # --- Step 5: Doctor response ----------------------------------------------
    console.print()
    console.print("[bold green]► Doctor Agent Response[/bold green]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("Remote LLM generating diagnosis...", total=None)
        doctor = DoctorAgent()
        diagnosis = doctor.diagnose(state)
        time.sleep(0.5)
        progress.update(task, completed=True)

    console.print(Panel(diagnosis, title="Diagnosis", border_style="magenta"))
    console.print()


def main() -> None:
    """Entry point for the demo CLI."""
    if len(sys.argv) > 1:
        raw_text = " ".join(sys.argv[1:])
    else:
        console.print(
            "[dim]No input provided — using sample scenario.[/dim]"
        )
        raw_text = SAMPLE_INPUT

    run_demo(raw_text)


if __name__ == "__main__":
    main()
