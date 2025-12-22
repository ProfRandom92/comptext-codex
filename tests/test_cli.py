from pathlib import Path

from click.testing import CliRunner

from comptext_codex.cli import main


def test_token_report_cli_text_output():
    codex_dir = Path(__file__).resolve().parents[1] / "codex"
    runner = CliRunner()
    result = runner.invoke(main, ["token-report", "--codex-dir", str(codex_dir)])
    assert result.exit_code == 0
    assert "Total commands" in result.output


def test_token_report_cli_json_output():
    """Test token-report command with JSON output format."""
    codex_dir = Path(__file__).resolve().parents[1] / "codex"
    runner = CliRunner()
    result = runner.invoke(
        main, ["token-report", "--codex-dir", str(codex_dir), "--format", "json"]
    )
    assert result.exit_code == 0
    assert "total_commands" in result.output
    assert "modules" in result.output


def test_token_report_cli_with_module_filter():
    """Test token-report command with module filter."""
    codex_dir = Path(__file__).resolve().parents[1] / "codex"
    runner = CliRunner()
    result = runner.invoke(
        main, ["token-report", "--codex-dir", str(codex_dir), "--module", "A"]
    )
    assert result.exit_code == 0
    assert "Total commands" in result.output


def test_token_report_cli_with_nonexistent_module():
    """Test token-report command with non-existent module filter."""
    codex_dir = Path(__file__).resolve().parents[1] / "codex"
    runner = CliRunner()
    result = runner.invoke(
        main, ["token-report", "--codex-dir", str(codex_dir), "--module", "NONEXISTENT"]
    )
    assert result.exit_code == 0
    assert "Total commands: 0" in result.output


def test_token_benchmark_cli_writes_report():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["token-benchmark", "--output", "bench.md"])
        assert result.exit_code == 0
        report_path = Path("bench.md")
        assert report_path.exists()
        assert "Token Reduction Results" in report_path.read_text(encoding="utf-8")


def test_cli_help():
    """Test that --help works for main command."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "CompText Codex" in result.output


def test_token_report_help():
    """Test that --help works for token-report subcommand."""
    runner = CliRunner()
    result = runner.invoke(main, ["token-report", "--help"])
    assert result.exit_code == 0
    assert "codex-dir" in result.output


def test_token_benchmark_help():
    """Test that --help works for token-benchmark subcommand."""
    runner = CliRunner()
    result = runner.invoke(main, ["token-benchmark", "--help"])
    assert result.exit_code == 0
    assert "output" in result.output.lower()
