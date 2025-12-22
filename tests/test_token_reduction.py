from pathlib import Path

from comptext_codex.token_reduction import (
    DEFAULT_CASES,
    TokenReductionCase,
    calculate_reduction,
    generate_markdown_report,
    main,
    token_count,
    write_report,
)


def test_token_count_simple():
    assert token_count("  a   b c ") == 3


def test_token_count_empty():
    """Test token count with empty string."""
    assert token_count("") == 0
    assert token_count("   ") == 0


def test_token_count_single_word():
    """Test token count with single word."""
    assert token_count("hello") == 1


def test_calculate_reduction_has_positive_delta():
    metrics = calculate_reduction(DEFAULT_CASES[0])
    assert metrics["original_tokens"] > metrics["comptext_tokens"]
    assert (
        metrics["token_reduction"]
        == metrics["original_tokens"] - metrics["comptext_tokens"]
    )
    assert metrics["reduction_pct"] > 0


def test_calculate_reduction_with_equal_tokens():
    """Test reduction when original and comptext have same token count."""
    case = TokenReductionCase(
        name="Equal",
        original="hello world",
        comptext="test case",
    )
    metrics = calculate_reduction(case)
    assert metrics["token_reduction"] == 0
    assert metrics["reduction_pct"] == 0.0


def test_calculate_reduction_with_more_comptext_tokens():
    """Test reduction when comptext has more tokens than original."""
    case = TokenReductionCase(
        name="Negative",
        original="one",
        comptext="two three four",
    )
    metrics = calculate_reduction(case)
    assert metrics["token_reduction"] == 0
    assert metrics["reduction_pct"] == 0.0


def test_calculate_reduction_with_empty_original():
    """Test reduction with empty original text."""
    case = TokenReductionCase(
        name="Empty",
        original="",
        comptext="test",
    )
    metrics = calculate_reduction(case)
    assert metrics["original_tokens"] == 0
    assert metrics["reduction_pct"] == 0.0


def test_generate_markdown_report_includes_cases(tmp_path: Path):
    content = generate_markdown_report(DEFAULT_CASES)
    assert "Token Reduction Results" in content
    for case in DEFAULT_CASES:
        assert case.name in content

    # ensure report can be written
    report_path = tmp_path / "report.md"
    report_path.write_text(content, encoding="utf-8")
    assert report_path.read_text(encoding="utf-8").startswith("# Token Reduction")


def test_generate_markdown_report_with_empty_cases():
    """Test report generation with empty case list."""
    content = generate_markdown_report([])
    assert "Token Reduction Results" in content


def test_write_report_creates_parent_dirs(tmp_path: Path):
    """Test that write_report creates parent directories."""
    nested_path = tmp_path / "nested" / "dir" / "report.md"
    write_report(nested_path, "test content")
    assert nested_path.exists()
    assert nested_path.read_text(encoding="utf-8") == "test content"


def test_main_function(tmp_path: Path):
    """Test the main entry point function."""
    output_path = tmp_path / "output.md"
    main(output_path=output_path)
    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8")
    assert "Token Reduction Results" in content
