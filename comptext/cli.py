"""Console interface for executing CompText commands."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

from .parser import CompTextParser, ParseError
from .utils import estimate_tokens, token_reduction


def _load_text(path: str | None) -> str:
    if not path:
        return ""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    return file_path.read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run CompText commands from the CLI")
    parser.add_argument("command", help="CompText command string, e.g. '@SUMMARIZE[len=short]' ")
    parser.add_argument("--code-file", help="Path to a code file to analyze", default=None)
    parser.add_argument("--text-file", help="Path to a text file for summarization/translation", default=None)
    parser.add_argument("--data", help="JSON string with additional context data", default=None)
    parser.add_argument("--natural", help="Natural language prompt to compare token usage against", default=None)
    parser.add_argument(
        "--natural-file",
        help="Path to a file containing the natural language prompt for token comparison",
        default=None,
    )
    parser.add_argument(
        "--show-tokens",
        action="store_true",
        help="Print token counts for the DSL command and optional natural prompt",
    )

    args = parser.parse_args(argv)

    context: Dict[str, Any] = {}
    natural_prompt: str | None = None
    try:
        if args.code_file:
            context["code"] = _load_text(args.code_file)
        if args.text_file:
            context["text"] = _load_text(args.text_file)
        if args.data:
            context.update(json.loads(args.data))
        natural_prompt = args.natural or _load_text(args.natural_file) if args.natural_file else args.natural
    except FileNotFoundError as exc:
        parser.error(str(exc))
        return 1
    except json.JSONDecodeError:
        parser.error("Unable to parse --data as JSON")
        return 1

    dsl_parser = CompTextParser()
    try:
        output = dsl_parser.execute(args.command, **context)
    except ParseError as exc:
        parser.error(str(exc))
        return 1

    token_lines: list[str] = []
    if args.show_tokens:
        if natural_prompt:
            natural_tokens, dsl_tokens, reduction = token_reduction(natural_prompt, args.command)
            token_lines.append(
                f"Token counts -> natural: {natural_tokens}, dsl: {dsl_tokens}, reduction: {reduction:.2%}"
            )
        else:
            dsl_tokens = estimate_tokens(args.command)
            token_lines.append(f"Token count (DSL): {dsl_tokens}")

    if token_lines:
        sys.stdout.write("\n".join(token_lines) + "\n\n")

    sys.stdout.write(str(output) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
