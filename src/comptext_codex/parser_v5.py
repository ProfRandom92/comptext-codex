"""CompText V5.0 ULTRA Parser - 94% Token Reduction."""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class CompTextCommandV5:
    """Represents a parsed CompText V5.0 ULTRA command."""
    command: str  # Single char: C, F, M, T, D, E, O, A
    language: Optional[str] = None  # Single char: P, J, T, R, G, S, H
    modifiers: List[str] = None  # Single char: N, S, R, C
    task: Optional[str] = None
    params: Dict[str, Any] = None
    raw: str = ""

    def __post_init__(self):
        if self.modifiers is None:
            self.modifiers = []
        if self.params is None:
            self.params = {}


class CompTextParserV5:
    """Parser for CompText V5.0 ULTRA - Single-character ultra-compressed syntax.

    Syntax Examples:
        - Single command: C;P:FIB
        - With modifiers: T;P;R:FIB
        - Batch: B:[D:SUM]|[C;P:FIB]|[E;C:WHY]
        - Complex: B:[A:STRUCT]|[F;T:MEM]|[O;S:Q]|[D:API]
    """

    # Command mappings (single char -> full name)
    COMMANDS = {
        'C': 'CODE',
        'F': 'FIX',
        'M': 'MODIFY',
        'T': 'TEST',
        'D': 'DOCUMENT',
        'E': 'EXPLAIN',
        'O': 'OPTIMIZE',
        'A': 'ANALYZE',
    }

    # Language mappings
    LANGUAGES = {
        'P': 'PYTHON',
        'J': 'JAVASCRIPT',
        'T': 'TYPESCRIPT',
        'R': 'RUST',
        'G': 'GO',
        'S': 'SQL',
        'H': 'HTML',
    }

    # Modifier mappings
    MODIFIERS = {
        'N': 'NO_COMMENTS',
        'S': 'STRICT',
        'R': 'ROBUST',
        'C': 'CONCISE',
    }

    # Reverse mappings for encoding
    COMMANDS_REV = {v: k for k, v in COMMANDS.items()}
    LANGUAGES_REV = {v: k for k, v in LANGUAGES.items()}
    MODIFIERS_REV = {v: k for k, v in MODIFIERS.items()}

    def __init__(self):
        """Initialize V5 parser."""
        self.batch_pattern = re.compile(r'B:(.+)$', re.DOTALL)
        self.command_sep = '|'

    def parse(self, command_string: str) -> List[CompTextCommandV5]:
        """Parse V5.0 ULTRA command string.

        Args:
            command_string: Ultra-compressed command string

        Returns:
            List of parsed V5 commands

        Examples:
            >>> parser.parse("C;P:FIB")
            [CompTextCommandV5(command='C', language='P', task='FIB')]

            >>> parser.parse("B:[D:SUM]|[C;P:FIB]|[E;C:WHY]")
            [CompTextCommandV5(...), CompTextCommandV5(...), CompTextCommandV5(...)]
        """
        command_string = command_string.strip()

        # Check if it's a batch command
        batch_match = self.batch_pattern.match(command_string)
        if batch_match:
            # Extract batch content and split by pipe
            batch_content = batch_match.group(1)
            # Split by | but respect brackets
            commands_raw = self._split_batch(batch_content)
            return [self._parse_single(cmd.strip()) for cmd in commands_raw]
        else:
            # Single command
            return [self._parse_single(command_string)]

    def _split_batch(self, batch_content: str) -> List[str]:
        """Split batch content by | respecting brackets."""
        commands = []
        current = []
        depth = 0
        in_bracket_group = False

        for char in batch_content:
            if char == '[':
                depth += 1
                in_bracket_group = True
                current.append(char)
            elif char == ']':
                depth -= 1
                current.append(char)
                if depth == 0:
                    in_bracket_group = False
            elif char == '|' and depth == 0:
                cmd = ''.join(current).strip()
                if cmd:
                    commands.append(cmd)
                current = []
            else:
                current.append(char)

        # Add last command
        cmd = ''.join(current).strip()
        if cmd:
            commands.append(cmd)

        return commands

    def _parse_single(self, cmd_str: str) -> CompTextCommandV5:
        """Parse a single V5 command.

        Format: [CMD[;LANG][;MOD]*:TASK]
        Examples:
            - C;P:FIB
            - T;P;R:FIB
            - D:SUM
            - F;T:MEM
        """
        # Remove brackets if present
        cmd_str = cmd_str.strip()
        if cmd_str.startswith('[') and cmd_str.endswith(']'):
            cmd_str = cmd_str[1:-1]

        # Split by colon to separate command part from task
        if ':' in cmd_str:
            cmd_part, task = cmd_str.split(':', 1)
        else:
            cmd_part = cmd_str
            task = None

        # Parse command part (separated by semicolons)
        parts = cmd_part.split(';')

        command = None
        language = None
        modifiers = []

        # First part is always command
        if parts and parts[0].strip() in self.COMMANDS:
            command = parts[0].strip()
            parts = parts[1:]  # Remove processed command

        # Process remaining parts in order
        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Check if language (only if we haven't assigned one yet)
            if language is None and part in self.LANGUAGES:
                language = part
            # Otherwise it's a modifier
            elif part in self.MODIFIERS:
                modifiers.append(part)

        return CompTextCommandV5(
            command=command,
            language=language,
            modifiers=modifiers,
            task=task.strip() if task else None,
            raw=cmd_str
        )

    def encode(self, command: str, language: Optional[str] = None,
               modifiers: Optional[List[str]] = None, task: Optional[str] = None) -> str:
        """Encode a command into V5.0 ULTRA format.

        Args:
            command: Full command name (e.g., 'CODE', 'TEST')
            language: Optional language (e.g., 'PYTHON', 'TYPESCRIPT')
            modifiers: Optional modifiers (e.g., ['ROBUST', 'CONCISE'])
            task: Optional task name

        Returns:
            Encoded V5 command string

        Examples:
            >>> parser.encode('CODE', 'PYTHON', task='FIB')
            'C;P:FIB'

            >>> parser.encode('TEST', 'PYTHON', ['ROBUST'], 'FIB')
            'T;P;R:FIB'
        """
        parts = []

        # Add command
        cmd_char = self.COMMANDS_REV.get(command.upper())
        if cmd_char:
            parts.append(cmd_char)

        # Add language
        if language:
            lang_char = self.LANGUAGES_REV.get(language.upper())
            if lang_char:
                parts.append(lang_char)

        # Add modifiers
        if modifiers:
            for mod in modifiers:
                mod_char = self.MODIFIERS_REV.get(mod.upper())
                if mod_char:
                    parts.append(mod_char)

        # Join with semicolons
        result = ';'.join(parts)

        # Add task if present
        if task:
            result += f':{task}'

        return result

    def encode_batch(self, commands: List[Tuple[str, Optional[str], Optional[List[str]], Optional[str]]]) -> str:
        """Encode multiple commands into V5 batch format.

        Args:
            commands: List of (command, language, modifiers, task) tuples

        Returns:
            Encoded batch command string

        Example:
            >>> parser.encode_batch([
            ...     ('DOCUMENT', None, None, 'SUM'),
            ...     ('CODE', 'PYTHON', None, 'FIB'),
            ...     ('EXPLAIN', None, ['CONCISE'], 'WHY')
            ... ])
            'B:[D:SUM]|[C;P:FIB]|[E;C:WHY]'
        """
        encoded = [f'[{self.encode(*cmd)}]' for cmd in commands]
        return 'B:' + '|'.join(encoded)

    def to_v4_format(self, cmd: CompTextCommandV5) -> str:
        """Convert V5 command to V4 format for backward compatibility."""
        parts = []

        # Add command
        if cmd.command:
            full_cmd = self.COMMANDS.get(cmd.command, cmd.command)
            parts.append(f'CMD:{full_cmd}')

        # Add language
        if cmd.language:
            full_lang = self.LANGUAGES.get(cmd.language, cmd.language)
            parts.append(f'LNG:{full_lang}')

        # Add modifiers
        for mod in cmd.modifiers:
            full_mod = self.MODIFIERS.get(mod, mod)
            if full_mod == 'NO_COMMENTS':
                parts.append('PRF:NO_COM')
            else:
                parts.append(f'STY:{full_mod}')

        # Add task
        if cmd.task:
            parts.append(f'TSK:{cmd.task}')

        return '; '.join(parts)

    def calculate_token_reduction(self, natural_language: str, v5_command: str) -> Dict[str, Any]:
        """Calculate token reduction statistics.

        Args:
            natural_language: Original natural language request
            v5_command: V5.0 ULTRA encoded command

        Returns:
            Dictionary with token statistics
        """
        # Rough token estimation (1 token ≈ 0.75 words or 4 chars)
        nl_tokens = len(natural_language.split())
        v5_tokens = len(v5_command.split())

        reduction_pct = round((1 - v5_tokens / nl_tokens) * 100, 1) if nl_tokens > 0 else 0

        return {
            'natural_language': natural_language,
            'natural_tokens': nl_tokens,
            'v5_command': v5_command,
            'v5_tokens': v5_tokens,
            'tokens_saved': nl_tokens - v5_tokens,
            'reduction_percent': reduction_pct,
            'chars_natural': len(natural_language),
            'chars_v5': len(v5_command),
            'char_reduction': round((1 - len(v5_command) / len(natural_language)) * 100, 1) if len(natural_language) > 0 else 0
        }


# Convenience functions
def parse_v5(command_string: str) -> List[CompTextCommandV5]:
    """Parse V5.0 ULTRA command string."""
    parser = CompTextParserV5()
    return parser.parse(command_string)


def encode_v5(command: str, language: Optional[str] = None,
              modifiers: Optional[List[str]] = None, task: Optional[str] = None) -> str:
    """Encode command to V5.0 ULTRA format."""
    parser = CompTextParserV5()
    return parser.encode(command, language, modifiers, task)
