from pathlib import Path

from click.testing import CliRunner

from comptext_codex.cli import main


def test_token_report_cli_text_output():
    codex_dir = Path(__file__).resolve().parents[1] / "codex"
    runner = CliRunner()
    result = runner.invoke(main, ["token-report", "--codex-dir", str(codex_dir)])
    assert result.exit_code == 0
    assert "Total commands" in result.output
