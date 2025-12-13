import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from comptext import CompTextParser, estimate_tokens, token_reduction


NATURAL_PROMPT = (
    "Please analyze this Python code, identify performance bottlenecks, "
    "suggest optimizations with code examples, explain the reasoning behind "
    "each optimization, and provide benchmark comparisons showing expected improvements"
)
DSL_PROMPT = "@CODE_ANALYZE[perf_bottleneck] + @CODE_OPT[explain=detail, bench=compare]"


def test_estimate_tokens_matches_expectations():
    assert estimate_tokens(NATURAL_PROMPT) == 26
    assert estimate_tokens(DSL_PROMPT) == 4


def test_token_reduction_is_above_seventy_percent():
    natural_tokens, dsl_tokens, reduction = token_reduction(NATURAL_PROMPT, DSL_PROMPT)

    assert natural_tokens == 26
    assert dsl_tokens == 4
    assert reduction >= 0.7


def test_parser_execution_still_works_with_token_reduction_example():
    parser = CompTextParser()
    output = parser.execute(DSL_PROMPT, code="def slow():\n    return [i*i for i in range(3)]")

    assert "CODE ANALYZE" in output
    assert "CODE OPTIMIZATION" in output


def test_cli_reports_token_counts(tmp_path):
    natural_file = tmp_path / "natural.txt"
    natural_file.write_text(NATURAL_PROMPT)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "comptext.cli",
            DSL_PROMPT,
            "--natural-file",
            str(natural_file),
            "--show-tokens",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Token counts" in result.stdout
    assert "dsl: 4" in result.stdout
