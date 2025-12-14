#!/usr/bin/env python3
"""Run the token reduction test suite and generate a markdown report."""

import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
src_path = repo_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from comptext_codex.token_reduction import main as run_suite  # noqa: E402


def main() -> None:
    output_path = repo_root / "TOKEN_REDUCTION_RESULTS.md"
    run_suite(output_path=output_path)


if __name__ == "__main__":
    main()
