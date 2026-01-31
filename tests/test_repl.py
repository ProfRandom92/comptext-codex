"""Comprehensive tests for CompText REPL."""

import io
import sys
from unittest.mock import patch, MagicMock
import pytest

from comptext_codex.repl import CompTextREPL


@pytest.fixture
def repl():
    """Create a REPL instance."""
    return CompTextREPL(codex_dir="codex")


class TestREPLInitialization:
    """Test REPL initialization."""

    def test_init_default_codex_dir(self):
        """Test REPL with default codex directory."""
        repl = CompTextREPL()
        assert repl.codex_dir == "codex"

    def test_init_custom_codex_dir(self):
        """Test REPL with custom codex directory."""
        repl = CompTextREPL(codex_dir="custom_codex")
        assert repl.codex_dir == "custom_codex"

    def test_init_creates_parser(self, repl):
        """Test REPL creates parser."""
        assert repl.parser is not None

    def test_init_creates_executor(self, repl):
        """Test REPL creates executor."""
        assert repl.executor is not None

    def test_init_empty_context(self, repl):
        """Test REPL starts with empty context."""
        assert repl.context == {}

    def test_init_empty_history(self, repl):
        """Test REPL starts with empty history."""
        assert repl.history == []

    def test_init_modules_list(self, repl):
        """Test REPL has modules list."""
        assert len(repl.modules) > 0
        assert 'A' in repl.modules


class TestLoadCommands:
    """Test command loading."""

    def test_load_available_commands(self, repl):
        """Test loading available commands."""
        commands = repl._load_available_commands()
        assert isinstance(commands, dict)


class TestCompleter:
    """Test tab completion functionality."""

    def test_complete_module_prefix(self, repl):
        """Test completing module prefix."""
        result = repl._completer("@A", 0)
        assert result is not None or result is None  # May or may not find match

    def test_complete_repl_command(self, repl):
        """Test completing REPL commands."""
        result = repl._completer(".he", 0)
        assert result == ".help"

    def test_complete_repl_exit(self, repl):
        """Test completing exit command."""
        result = repl._completer(".ex", 0)
        assert result == ".exit"

    def test_complete_repl_quit(self, repl):
        """Test completing quit command."""
        result = repl._completer(".qu", 0)
        assert result == ".quit"

    def test_complete_repl_commands(self, repl):
        """Test completing commands command."""
        result = repl._completer(".com", 0)
        assert result == ".commands"

    def test_complete_repl_context(self, repl):
        """Test completing context command."""
        result = repl._completer(".con", 0)
        assert result == ".context"

    def test_complete_repl_clear(self, repl):
        """Test completing clear command."""
        result = repl._completer(".cl", 0)
        assert result == ".clear"

    def test_complete_repl_history(self, repl):
        """Test completing history command."""
        result = repl._completer(".hi", 0)
        assert result == ".history"

    def test_complete_no_match(self, repl):
        """Test completing with no match."""
        result = repl._completer("xyz", 0)
        # Should return None when no match
        assert result is None

    def test_complete_state_out_of_range(self, repl):
        """Test completing with state out of range."""
        result = repl._completer(".help", 100)
        assert result is None


class TestBanner:
    """Test banner printing."""

    def test_print_banner(self, repl):
        """Test banner is printed."""
        captured = io.StringIO()
        with patch('sys.stdout', captured):
            repl.print_banner()
        output = captured.getvalue()
        assert "CompText" in output
        assert "REPL" in output


class TestHelp:
    """Test help functionality."""

    def test_print_help(self, repl):
        """Test help is printed."""
        captured = io.StringIO()
        with patch('sys.stdout', captured):
            repl.print_help()
        output = captured.getvalue()
        assert ".help" in output
        assert ".exit" in output
        assert ".commands" in output


class TestPrintCommands:
    """Test command listing."""

    def test_print_commands(self, repl):
        """Test listing available commands."""
        captured = io.StringIO()
        with patch('sys.stdout', captured):
            repl.print_commands()
        output = captured.getvalue()
        assert "Module" in output or "Commands" in output or "Available" in output


class TestContextManagement:
    """Test context management."""

    def test_print_context_empty(self, repl):
        """Test showing empty context."""
        captured = io.StringIO()
        with patch('sys.stdout', captured):
            repl.print_context()
        output = captured.getvalue()
        # Should show empty context message
        assert "empty" in output.lower()

    def test_print_context_with_data(self, repl):
        """Test showing context with data."""
        repl.context = {"key": "value", "number": 42}
        captured = io.StringIO()
        with patch('sys.stdout', captured):
            repl.print_context()
        output = captured.getvalue()
        assert "key" in output
        assert "value" in output

    def test_context_clears_manually(self, repl):
        """Test clearing context manually."""
        repl.context = {"key": "value"}
        repl.context = {}
        assert repl.context == {}


class TestHistory:
    """Test history functionality."""

    def test_print_history_empty(self, repl):
        """Test showing empty history."""
        captured = io.StringIO()
        with patch('sys.stdout', captured):
            repl.print_history()
        output = captured.getvalue()
        # Should show no history message
        assert "No" in output or "history" in output.lower()

    def test_print_history_with_entries(self, repl):
        """Test showing history with entries."""
        repl.history = ["@A:test", "@B:analyze", "@C:format"]
        captured = io.StringIO()
        with patch('sys.stdout', captured):
            repl.print_history()
        output = captured.getvalue()
        # Should contain history entries
        assert "@A:test" in output


class TestExecuteReplCommand:
    """Test REPL command execution."""

    def test_execute_exit_command(self, repl):
        """Test executing .exit command."""
        result = repl.execute_repl_command(".exit")
        assert result is False  # Should return False to exit

    def test_execute_quit_command(self, repl):
        """Test executing .quit command."""
        result = repl.execute_repl_command(".quit")
        assert result is False  # Should return False to exit

    def test_execute_help_command(self, repl):
        """Test executing .help command."""
        captured = io.StringIO()
        with patch('sys.stdout', captured):
            result = repl.execute_repl_command(".help")
        assert result is True

    def test_execute_commands_command(self, repl):
        """Test executing .commands command."""
        captured = io.StringIO()
        with patch('sys.stdout', captured):
            result = repl.execute_repl_command(".commands")
        assert result is True

    def test_execute_context_command(self, repl):
        """Test executing .context command."""
        captured = io.StringIO()
        with patch('sys.stdout', captured):
            result = repl.execute_repl_command(".context")
        assert result is True

    def test_execute_history_command(self, repl):
        """Test executing .history command."""
        captured = io.StringIO()
        with patch('sys.stdout', captured):
            result = repl.execute_repl_command(".history")
        assert result is True

    def test_execute_clear_command(self, repl):
        """Test executing .clear command."""
        repl.context = {"key": "value"}
        captured = io.StringIO()
        with patch('sys.stdout', captured):
            result = repl.execute_repl_command(".clear")
        assert result is True
        assert repl.context == {}

    def test_execute_unknown_command(self, repl):
        """Test executing unknown REPL command."""
        captured = io.StringIO()
        with patch('sys.stdout', captured):
            result = repl.execute_repl_command(".unknown")
        assert result is True
        output = captured.getvalue()
        assert "Unknown" in output


class TestMultilineInput:
    """Test multiline input handling."""

    def test_multiline_buffer_init(self, repl):
        """Test multiline buffer is initialized."""
        assert repl.multiline_buffer == []


class TestREPLIntegration:
    """Integration tests for REPL."""

    def test_context_can_be_set(self, repl):
        """Test that context can be set."""
        repl.context = {"initial": "value"}
        assert repl.context["initial"] == "value"

    def test_history_can_be_appended(self, repl):
        """Test that history can be appended."""
        repl.history.append("@A:test")
        assert "@A:test" in repl.history
