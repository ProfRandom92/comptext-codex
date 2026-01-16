"""CompText DSL Parser - Parses CompText commands into structured format."""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class CompTextCommand:
    """Represents a parsed CompText command."""
    module: str
    command: str
    args: List[str]
    kwargs: Dict[str, Any]
    raw: str


class CompTextParser:
    """Parser for CompText Domain-Specific Language.

    Supports multiple syntax patterns:
    - Simple: @A:compress <text>
    - Parametric: @CODE_ANALYZE[perf_bottleneck, complexity]
    - Key-value: @AUTOML[task=classification, metric=f1]
    - Chained: @EXTRACT[source=db] + @TRANSFORM[clean=true] + @LOAD[dest=warehouse]
    """

    # Regex patterns for different command formats
    SIMPLE_PATTERN = re.compile(r'@([A-M]):(\w+)\s*(.*?)(?=\s*(?:@|$))', re.DOTALL)
    PARAMETRIC_PATTERN = re.compile(r'@(\w+)\[', re.DOTALL)  # Match opening, extract content manually
    CHAIN_SEPARATOR = re.compile(r'\s*\+\s*')

    def __init__(self, codex_dir: Optional[str] = None):
        """Initialize parser with optional codex directory."""
        self.codex_dir = codex_dir
        self._command_registry: Dict[str, Dict[str, Any]] = {}
        self._load_command_definitions()

    def _load_command_definitions(self):
        """Load command definitions from codex YAML files."""
        if not self.codex_dir:
            return

        try:
            import yaml
            from pathlib import Path

            commands_file = Path(self.codex_dir) / "commands.yaml"
            if commands_file.exists():
                with open(commands_file, 'r') as f:
                    data = yaml.safe_load(f)
                    for cmd in data.get('commands', []):
                        key = f"{cmd['module']}:{cmd['command']}"
                        self._command_registry[key] = cmd
        except Exception as e:
            # Silent fallback if codex files not available
            pass

    def parse(self, command_string: str) -> List[CompTextCommand]:
        """Parse a CompText command string into structured commands.

        Args:
            command_string: Raw CompText command(s)

        Returns:
            List of parsed CompTextCommand objects

        Examples:
            >>> parser.parse("@A:compress The quick brown fox")
            [CompTextCommand(module='A', command='compress', ...)]

            >>> parser.parse("@CODE_ANALYZE[perf_bottleneck] + @CODE_OPT[explain=detail]")
            [CompTextCommand(...), CompTextCommand(...)]
        """
        # Split by chain operator if present
        parts = self.CHAIN_SEPARATOR.split(command_string.strip())

        commands = []
        for part in parts:
            cmd = self._parse_single_command(part.strip())
            if cmd:
                commands.append(cmd)

        return commands

    def _parse_single_command(self, command_str: str) -> Optional[CompTextCommand]:
        """Parse a single CompText command."""
        # Try parametric pattern first (e.g., @CODE_ANALYZE[...])
        param_match = self.PARAMETRIC_PATTERN.match(command_str)
        if param_match:
            # Extract content between balanced brackets
            command_name = param_match.group(1)
            start_idx = param_match.end()  # Position after '['
            params_content = self._extract_bracketed_content(command_str, start_idx)
            if params_content is not None:
                return self._parse_parametric_with_content(command_name, params_content, command_str)

        # Try simple pattern (e.g., @A:compress text)
        simple_match = self.SIMPLE_PATTERN.match(command_str)
        if simple_match:
            return self._parse_simple(simple_match, command_str)

        return None

    def _extract_bracketed_content(self, text: str, start_idx: int) -> Optional[str]:
        """Extract content between balanced brackets starting from start_idx."""
        bracket_depth = 1
        content = []

        for i in range(start_idx, len(text)):
            char = text[i]
            if char == '[':
                bracket_depth += 1
                content.append(char)
            elif char == ']':
                bracket_depth -= 1
                if bracket_depth == 0:
                    return ''.join(content)
                content.append(char)
            else:
                content.append(char)

        return None  # Unbalanced brackets

    def _parse_parametric_with_content(self, command_name: str, params_str: str, raw: str) -> CompTextCommand:
        """Parse parametric command with pre-extracted content."""
        args = []
        kwargs = {}

        # Parse comma-separated parameters (respecting nested brackets)
        if params_str:
            params = self._split_params(params_str)
            for param in params:
                if '=' in param and not param.startswith('['):
                    key, value = param.split('=', 1)
                    kwargs[key.strip()] = self._parse_value(value.strip())
                else:
                    args.append(param)

        # Infer module from command name or use generic
        module = self._infer_module(command_name)

        return CompTextCommand(
            module=module,
            command=command_name,
            args=args,
            kwargs=kwargs,
            raw=raw
        )

    def _parse_parametric(self, match: re.Match, raw: str) -> CompTextCommand:
        """Parse parametric command format: @COMMAND[param1, key=value]."""
        command_name = match.group(1)
        params_str = match.group(2)

        args = []
        kwargs = {}

        # Parse comma-separated parameters (respecting nested brackets)
        if params_str:
            params = self._split_params(params_str)
            for param in params:
                if '=' in param and not param.startswith('['):
                    key, value = param.split('=', 1)
                    kwargs[key.strip()] = self._parse_value(value.strip())
                else:
                    args.append(param)

        # Infer module from command name or use generic
        module = self._infer_module(command_name)

        return CompTextCommand(
            module=module,
            command=command_name,
            args=args,
            kwargs=kwargs,
            raw=raw
        )

    def _split_params(self, params_str: str) -> List[str]:
        """Split parameters by comma, respecting nested brackets."""
        params = []
        current = []
        bracket_depth = 0

        for char in params_str:
            if char == '[':
                bracket_depth += 1
                current.append(char)
            elif char == ']':
                bracket_depth -= 1
                current.append(char)
            elif char == ',' and bracket_depth == 0:
                params.append(''.join(current).strip())
                current = []
            else:
                current.append(char)

        if current:
            params.append(''.join(current).strip())

        return params

    def _parse_simple(self, match: re.Match, raw: str) -> CompTextCommand:
        """Parse simple command format: @A:command text."""
        module = match.group(1)
        command = match.group(2)
        text = match.group(3).strip()

        return CompTextCommand(
            module=module,
            command=command,
            args=[text] if text else [],
            kwargs={},
            raw=raw
        )

    def _parse_value(self, value: str) -> Any:
        """Parse parameter value with type inference."""
        # Boolean
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'

        # Number
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass

        # List
        if value.startswith('[') and value.endswith(']'):
            items = value[1:-1].split(',')
            return [item.strip() for item in items if item.strip()]

        # String (strip quotes if present)
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return value[1:-1]

        return value

    def _infer_module(self, command_name: str) -> str:
        """Infer module code from command name."""
        # Common command name patterns
        module_map = {
            'CODE_': 'B',
            'ANALYZE': 'B',
            'FORMAT': 'C',
            'MODEL_': 'D',
            'AUTOML': 'E',
            'FEATURE_': 'E',
            'DOC_': 'F',
            'CHANGELOG': 'F',
            'TEST_': 'G',
            'DB_': 'H',
            'SEC_': 'I',
            'GDPR': 'I',
            'DEPLOY': 'J',
            'CI_CD': 'J',
            'COMPONENT': 'K',
            'DASHBOARD': 'K',
            'EXTRACT': 'L',
            'TRANSFORM': 'L',
            'LOAD': 'L',
            'AGENT_': 'M',
            'TASK_': 'M',
        }

        for prefix, module in module_map.items():
            if command_name.upper().startswith(prefix):
                return module

        return 'A'  # Default to core commands

    def validate(self, commands: List[CompTextCommand]) -> Tuple[bool, List[str]]:
        """Validate parsed commands against registry.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        for cmd in commands:
            key = f"{cmd.module}:{cmd.command}"
            if key not in self._command_registry:
                # Check if it's a generic command pattern
                if cmd.command.upper() not in ['ANALYZE', 'FORMAT', 'OPTIMIZE', 'GENERATE']:
                    errors.append(f"Unknown command: {key}")

        return len(errors) == 0, errors

    def format_command(self, cmd: CompTextCommand) -> str:
        """Format a CompTextCommand back to string representation."""
        if cmd.kwargs:
            params = []
            params.extend(cmd.args)
            params.extend([f"{k}={v}" for k, v in cmd.kwargs.items()])
            return f"@{cmd.command}[{', '.join(params)}]"
        elif cmd.args:
            if cmd.module and len(cmd.module) == 1:
                return f"@{cmd.module}:{cmd.command} {' '.join(cmd.args)}"
            return f"@{cmd.command}[{', '.join(cmd.args)}]"
        else:
            return f"@{cmd.module}:{cmd.command}" if len(cmd.module) == 1 else f"@{cmd.command}"


# Convenience functions
def parse(command_string: str, codex_dir: Optional[str] = None) -> List[CompTextCommand]:
    """Parse CompText command string.

    Args:
        command_string: Raw CompText command(s)
        codex_dir: Optional path to codex directory

    Returns:
        List of parsed commands
    """
    parser = CompTextParser(codex_dir=codex_dir)
    return parser.parse(command_string)


def format_command(cmd: CompTextCommand) -> str:
    """Format command back to string."""
    parser = CompTextParser()
    return parser.format_command(cmd)
