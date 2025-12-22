from pathlib import Path

from comptext_codex.token_report import (
    build_token_report,
    load_commands,
    load_modules,
    render_text_report,
    report_as_json,
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
    assert "Core Commands" in output
    assert "Analysis" in output


def test_modules_include_security_and_privacy_metadata():
    modules = load_modules(_codex_dir())
    assert len(modules) >= 13
    assert modules["A"]["security"]["pii_safe"] is True
    assert modules["A"]["privacy"]["dp_budget"].startswith("epsilon")
    assert "privacy" in modules["M"]
    assert modules["M"]["privacy"]["federated_ready"] is True


def test_build_token_report_with_empty_commands():
    """Test token report with empty command list."""
    report = build_token_report([], {})
    assert report["total_commands"] == 0
    assert report["commands_with_token_hint"] == 0
    assert report["avg_token_cost"] == 0.0
    assert report["modules"] == {}


def test_build_token_report_with_missing_token_hints():
    """Test token report with commands that lack token hints."""
    commands = [
        {"command": "test1", "module": "A"},
        {"command": "test2", "module": "A", "token_cost_hint": 50},
    ]
    modules = {"A": {"name": "Test Module", "token_priority": "high"}}
    report = build_token_report(commands, modules)
    assert report["total_commands"] == 2
    assert report["commands_with_token_hint"] == 1
    assert report["avg_token_cost"] == 50.0
    assert report["modules"]["A"]["command_count"] == 2


def test_build_token_report_with_commands_no_module():
    """Test token report with commands that have no module assigned."""
    commands = [
        {"command": "orphan_cmd"},
        {"command": "test", "module": "A", "token_cost_hint": 100},
    ]
    modules = {"A": {"name": "Test", "token_priority": "medium"}}
    report = build_token_report(commands, modules)
    assert report["total_commands"] == 2
    assert "A" in report["modules"]
    assert report["modules"]["A"]["command_count"] == 1


def test_report_as_json_output():
    """Test JSON output format."""
    commands = load_commands(_codex_dir())
    modules = load_modules(_codex_dir())
    report = build_token_report(commands, modules)
    json_output = report_as_json(report)
    assert "total_commands" in json_output
    assert "modules" in json_output
    assert json_output.startswith("{")
    assert json_output.endswith("}")


def test_render_text_report_with_empty_module_name():
    """Test rendering when module name is empty or missing."""
    report = {
        "total_commands": 1,
        "commands_with_token_hint": 1,
        "avg_token_cost": 10.0,
        "modules": {
            "X": {
                "name": "",
                "token_priority": "low",
                "command_count": 1,
                "avg_token_cost": 10.0,
            }
        },
    }
    output = render_text_report(report)
    assert "Unknown" in output or "X" in output
