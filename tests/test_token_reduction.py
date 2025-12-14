from pathlib import Path

from comptext_codex.token_reduction import (
    DEFAULT_CASES,
    calculate_reduction,
    generate_markdown_report,
    token_count,
)


def test_token_count_simple():
    assert token_count("  a   b c ") == 3


def test_calculate_reduction_has_positive_delta():
    metrics = calculate_reduction(DEFAULT_CASES[0])
    assert metrics["original_tokens"] > metrics["comptext_tokens"]
    assert metrics["token_reduction"] == metrics["original_tokens"] - metrics["comptext_tokens"]
    assert metrics["reduction_pct"] > 0


def test_generate_markdown_report_includes_cases(tmp_path: Path):
    content = generate_markdown_report(DEFAULT_CASES)
    assert "Token Reduction Results" in content
    for case in DEFAULT_CASES:
        assert case.name in content

    # ensure report can be written
    report_path = tmp_path / "report.md"
    report_path.write_text(content, encoding="utf-8")
    assert report_path.read_text(encoding="utf-8").startswith("# Token Reduction Results")
