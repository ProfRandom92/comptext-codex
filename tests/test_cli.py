from pathlib import Path

from click.testing import CliRunner

from comptext_codex.cli import main


def test_token_report_cli_text_output():
    codex_dir = Path(__file__).resolve().parents[1] / "codex"
    runner = CliRunner()
    result = runner.invoke(main, ["token-report", "--codex-dir", str(codex_dir)])
    assert result.exit_code == 0
    assert "Total commands" in result.output


def test_token_benchmark_cli_writes_report():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["token-benchmark", "--output", "bench.md"])
        assert result.exit_code == 0
        report_path = Path("bench.md")
        assert report_path.exists()
        assert "Token Reduction Results" in report_path.read_text(encoding="utf-8")
