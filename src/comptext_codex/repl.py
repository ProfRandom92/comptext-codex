"""Interactive REPL for CompText Codex.

Provides an interactive shell with:
- Command history and editing
- Tab completion for modules and commands
- Syntax highlighting
- Multi-line input support
- Built-in help system
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any

try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False

from .parser import CompTextParser, CompTextCommand
from .executor import CompTextExecutor, ExecutionResult


class CompTextREPL:
    """Interactive REPL for CompText DSL."""

    def __init__(self, codex_dir: Optional[str] = None):
        """Initialize REPL.

        Args:
            codex_dir: Path to codex directory (defaults to ./codex)
        """
        self.codex_dir = codex_dir or "codex"
        self.parser = CompTextParser(codex_dir=self.codex_dir)
        self.executor = CompTextExecutor(codex_dir=self.codex_dir)
        self.context: Dict[str, Any] = {}
        self.history: List[str] = []
        self.multiline_buffer: List[str] = []

        # Available modules and commands for autocomplete
        self.modules = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M']
        self.commands_by_module = self._load_available_commands()

        # Setup readline if available
        if READLINE_AVAILABLE:
            self._setup_readline()

    def _load_available_commands(self) -> Dict[str, List[str]]:
        """Load available commands from executor."""
        commands_by_module = {}
        available = self.executor.get_available_commands()

        for cmd_info in available:
            module = cmd_info.get('module', 'A')
            command = cmd_info.get('command', '')

            if module not in commands_by_module:
                commands_by_module[module] = []

            if command and command not in commands_by_module[module]:
                commands_by_module[module].append(command)

        return commands_by_module

    def _setup_readline(self):
        """Setup readline for history and completion."""
        # Enable tab completion
        readline.parse_and_bind('tab: complete')
        readline.set_completer(self._completer)

        # Load history file
        history_file = Path.home() / '.comptext_history'
        if history_file.exists():
            try:
                readline.read_history_file(history_file)
            except Exception:
                pass

        # Save history on exit
        import atexit
        atexit.register(lambda: self._save_history(history_file))

    def _save_history(self, history_file: Path):
        """Save command history to file."""
        try:
            readline.write_history_file(history_file)
        except Exception:
            pass

    def _completer(self, text: str, state: int) -> Optional[str]:
        """Readline completer for tab completion."""
        options = []

        # Complete module codes
        if text.startswith('@') and ':' not in text and '[' not in text:
            module_prefix = text[1:]
            options = [f"@{m}:" for m in self.modules if m.startswith(module_prefix.upper())]

        # Complete commands after module:
        elif ':' in text:
            parts = text.split(':')
            if len(parts) == 2:
                module = parts[0].strip('@')
                cmd_prefix = parts[1]

                if module in self.commands_by_module:
                    options = [
                        f"@{module}:{cmd}"
                        for cmd in self.commands_by_module[module]
                        if cmd.startswith(cmd_prefix.lower())
                    ]

        # Complete REPL commands
        elif text.startswith('.'):
            repl_commands = ['.help', '.commands', '.context', '.clear', '.history', '.exit', '.quit']
            options = [cmd for cmd in repl_commands if cmd.startswith(text)]

        if state < len(options):
            return options[state]
        return None

    def print_banner(self):
        """Print welcome banner."""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║           CompText Codex Interactive REPL v3.5.0             ║
║                                                              ║
║  Efficient LLM communication through DSL commands            ║
║  70-88% token reduction | Modular architecture               ║
╚══════════════════════════════════════════════════════════════╝

Type .help for available commands | .exit to quit
"""
        print(banner)

    def print_help(self):
        """Print help message."""
        help_text = """
CompText REPL Commands:
  .help              Show this help message
  .commands          List all available CompText commands
  .context           Show current execution context
  .clear             Clear execution context
  .history           Show command history
  .exit, .quit       Exit the REPL

CompText Syntax Examples:
  @A:compress The quick brown fox jumps over the lazy dog
  @B:analyze[complexity, maintainability] def foo(): pass
  @C:format[type=markdown] # My Title\\nContent here
  @AUTOML[task=classification, metric=f1]
  @EXTRACT[source=db] + @TRANSFORM[clean=true] + @LOAD[dest=warehouse]

Module Codes:
  A - Core Commands        │  H - Database
  B - Analysis            │  I - Security
  C - Formatting          │  J - DevOps
  D - AI Control          │  K - Frontend/UI
  E - ML Pipelines        │  L - ETL
  F - Documentation       │  M - MCP Integration
  G - Testing             │

Tips:
  - Press Tab for autocomplete
  - Use arrow keys to navigate history
  - Chain commands with + operator
  - Multi-line input: end line with \\ to continue
"""
        print(help_text)

    def print_commands(self):
        """Print all available commands."""
        print("\n═══ Available Commands ═══\n")

        for module in sorted(self.commands_by_module.keys()):
            commands = self.commands_by_module[module]
            if commands:
                print(f"Module {module}:")
                for cmd in sorted(commands):
                    print(f"  @{module}:{cmd}")
                print()

    def print_context(self):
        """Print current execution context."""
        if not self.context:
            print("Context is empty")
            return

        print("\n═══ Execution Context ═══\n")
        for key, value in self.context.items():
            # Truncate long values
            value_str = str(value)
            if len(value_str) > 100:
                value_str = value_str[:97] + "..."
            print(f"{key}: {value_str}")
        print()

    def print_history(self):
        """Print command history."""
        if not self.history:
            print("No command history")
            return

        print("\n═══ Command History ═══\n")
        for i, cmd in enumerate(self.history, 1):
            print(f"{i:3d}: {cmd}")
        print()

    def format_result(self, result: ExecutionResult, command: CompTextCommand) -> str:
        """Format execution result for display."""
        if not result.success:
            return f"❌ Error: {result.error}"

        # Check if simulated
        if result.metadata.get('simulated'):
            return f"🔸 [Simulated] {result.result.get('message', 'Command executed')}"

        # Format result based on type
        result_data = result.result

        if isinstance(result_data, dict):
            # Pretty print dict results
            lines = []
            for key, value in result_data.items():
                value_str = str(value)
                if len(value_str) > 200:
                    value_str = value_str[:197] + "..."
                lines.append(f"  {key}: {value_str}")
            return "✓ Result:\n" + "\n".join(lines)

        elif isinstance(result_data, (list, tuple)):
            if len(result_data) <= 5:
                return f"✓ Result: {result_data}"
            else:
                preview = result_data[:5]
                return f"✓ Result: {preview}... ({len(result_data)} items)"

        else:
            result_str = str(result_data)
            if len(result_str) > 500:
                result_str = result_str[:497] + "..."
            return f"✓ Result: {result_str}"

    def execute_repl_command(self, command: str) -> bool:
        """Execute REPL meta-command.

        Returns:
            True to continue REPL, False to exit
        """
        command = command.strip()

        if command in ['.exit', '.quit']:
            return False

        elif command == '.help':
            self.print_help()

        elif command == '.commands':
            self.print_commands()

        elif command == '.context':
            self.print_context()

        elif command == '.clear':
            self.context.clear()
            print("✓ Context cleared")

        elif command == '.history':
            self.print_history()

        else:
            print(f"Unknown command: {command}")
            print("Type .help for available commands")

        return True

    def execute_comptext_command(self, command: str):
        """Execute CompText DSL command."""
        try:
            # Parse and execute
            commands = self.parser.parse(command)

            if not commands:
                print("❌ Failed to parse command")
                return

            # Execute all commands
            results = self.executor.execute(command, context=self.context)

            # Display results
            for cmd, result in zip(commands, results):
                print(self.format_result(result, cmd))

                # Update context with successful results
                if result.success and result.result:
                    self.context['_last_result'] = result.result

        except Exception as e:
            print(f"❌ Error: {e}")

    def read_input(self) -> Optional[str]:
        """Read input from user, supporting multi-line input.

        Returns:
            Complete command string, or None if EOF
        """
        try:
            # Primary prompt
            prompt = "comptext> " if not self.multiline_buffer else "      ... "

            line = input(prompt)

            # Check for multi-line continuation
            if line.endswith('\\'):
                self.multiline_buffer.append(line[:-1])  # Remove trailing \
                return self.read_input()  # Recursive read

            # Complete multi-line input
            if self.multiline_buffer:
                self.multiline_buffer.append(line)
                complete = ' '.join(self.multiline_buffer)
                self.multiline_buffer.clear()
                return complete

            return line

        except EOFError:
            return None
        except KeyboardInterrupt:
            # Clear multi-line buffer on Ctrl+C
            if self.multiline_buffer:
                self.multiline_buffer.clear()
                print("\n(Multi-line input cancelled)")
                return ""
            print()  # New line
            return None

    def run(self):
        """Run the REPL main loop."""
        self.print_banner()

        while True:
            try:
                # Read command
                command = self.read_input()

                # Handle EOF (Ctrl+D) or exit
                if command is None:
                    print("\nGoodbye!")
                    break

                # Skip empty lines
                command = command.strip()
                if not command:
                    continue

                # Add to history
                self.history.append(command)

                # Execute REPL command
                if command.startswith('.'):
                    should_continue = self.execute_repl_command(command)
                    if not should_continue:
                        print("\nGoodbye!")
                        break

                # Execute CompText command
                elif command.startswith('@'):
                    self.execute_comptext_command(command)

                else:
                    print("Commands must start with @ or .")
                    print("Type .help for usage information")

            except KeyboardInterrupt:
                print("\n(Use .exit or Ctrl+D to quit)")
                continue

            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                import traceback
                traceback.print_exc()


def main():
    """Entry point for REPL."""
    import argparse

    parser = argparse.ArgumentParser(
        description="CompText Codex Interactive REPL"
    )
    parser.add_argument(
        '--codex-dir',
        default='codex',
        help='Path to codex directory (default: ./codex)'
    )

    args = parser.parse_args()

    # Create and run REPL
    repl = CompTextREPL(codex_dir=args.codex_dir)
    repl.run()


if __name__ == '__main__':
    main()
