from pathlib import Path

from comptext_codex.token_report import (
    build_token_report,
    load_commands,
    load_modules,
    render_text_report,
)


def _codex_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "codex"


def test_token_report_counts():
    commands = load_commands(_codex_dir())
    modules = load_modules(_codex_dir())

    report = build_token_report(commands, modules)
    assert report["total_commands"] == 6
    assert report["commands_with_token_hint"] == 6
    assert report["modules"]["A"]["command_count"] == 4
    assert report["modules"]["B"]["command_count"] == 1
    assert report["modules"]["C"]["command_count"] == 1


def test_render_text_report_includes_module_names():
    commands = load_commands(_codex_dir())
    modules = load_modules(_codex_dir())
    report = build_token_report(commands, modules)
    output = render_text_report(report)
    assert "Total commands" in output
    assert "Core Commands" in output or "Analysis" in output
