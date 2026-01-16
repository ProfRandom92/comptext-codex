"""Module C: Formatting - Document formatting and structure.

This module provides comprehensive text and document formatting capabilities
including markdown, JSON, HTML, XML, CSV, and code formatting.
"""

from typing import Any, Dict, List
import json
import html as html_module
from .base import BaseModule


class ModuleC(BaseModule):
    """Formatting module for document structure and styling.

    Supports formats:
    - Markdown: Documentation and text formatting
    - JSON: Structured data formatting
    - HTML: Web content formatting
    - XML: Structured document formatting
    - CSV: Tabular data formatting
    - Code: Source code formatting (Python, JavaScript, etc.)
    """

    def get_commands(self) -> List[Dict[str, Any]]:
        """Return available formatting commands."""
        return [
            {
                'module': 'C',
                'command': 'format',
                'description': 'Format text in specified style',
                'syntax': '@C:format <style> <text>'
            },
            {
                'module': 'C',
                'command': 'beautify',
                'description': 'Auto-format and beautify code',
                'syntax': '@C:beautify <code>'
            },
            {
                'module': 'C',
                'command': 'minify',
                'description': 'Minify code or data',
                'syntax': '@C:minify <content>'
            }
        ]

    def execute_format(self, *args, context: Dict[str, Any] = None, **kwargs) -> str:
        """Format text according to specified style.

        Args:
            args[0]: Format style (markdown, json, html, xml, csv, code)
            args[1:]: Text content to format
            context: Optional execution context
            **kwargs: Additional formatting options (indent, sort_keys, etc.)

        Returns:
            Formatted text string
        """
        if not args:
            return ""

        style = kwargs.get('style', args[0] if args else 'text')
        text = kwargs.get('text', ' '.join(args[1:]) if len(args) > 1 else args[0])

        formatters = {
            'markdown': self._format_markdown,
            'md': self._format_markdown,
            'json': self._format_json,
            'html': self._format_html,
            'xml': self._format_xml,
            'csv': self._format_csv,
            'code': self._format_code,
            'python': lambda t: self._format_code(t, 'python'),
            'javascript': lambda t: self._format_code(t, 'javascript'),
            'yaml': self._format_yaml
        }

        formatter = formatters.get(style.lower())
        if formatter:
            return formatter(text)

        return text

    def execute_beautify(self, text: str = '', context: Dict[str, Any] = None, **kwargs) -> str:
        """Auto-format and beautify code or data.

        Args:
            text: Code or data to beautify
            context: Execution context
            **kwargs: Language hint, indent size, etc.

        Returns:
            Beautified text
        """
        language = kwargs.get('language', kwargs.get('lang', 'python'))

        if language == 'json':
            try:
                data = json.loads(text)
                return json.dumps(data, indent=2, sort_keys=True)
            except:
                pass

        return self._format_code(text, language)

    def execute_minify(self, text: str = '', context: Dict[str, Any] = None, **kwargs) -> str:
        """Minify code or data by removing whitespace.

        Args:
            text: Content to minify
            context: Execution context
            **kwargs: Additional options

        Returns:
            Minified text
        """
        # For JSON
        try:
            data = json.loads(text)
            return json.dumps(data, separators=(',', ':'))
        except:
            pass

        # Generic: remove extra whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return ' '.join(lines)

    def _format_markdown(self, text: str) -> str:
        """Format text as markdown.

        Args:
            text: Plain text to format

        Returns:
            Markdown-formatted text
        """
        # Simple markdown enhancement
        lines = text.split('\n')
        formatted = []

        for line in lines:
            line = line.strip()
            if not line:
                formatted.append('')
                continue

            # Detect headers
            if line.startswith('#'):
                formatted.append(line)
            # Detect lists
            elif line.startswith(('-', '*', '+')):
                formatted.append(line)
            # Regular paragraphs
            else:
                formatted.append(line)
                formatted.append('')  # Add blank line after paragraphs

        return '\n'.join(formatted).strip()

    def _format_json(self, text: str) -> str:
        """Format text as JSON.

        Args:
            text: Text or dict-like string to format

        Returns:
            Pretty-printed JSON
        """
        try:
            # Try to parse as JSON
            if isinstance(text, str):
                data = json.loads(text)
            else:
                data = text
            return json.dumps(data, indent=2, sort_keys=True)
        except (json.JSONDecodeError, TypeError):
            # Wrap plain text as JSON
            return json.dumps({'content': text}, indent=2)

    def _format_html(self, text: str) -> str:
        """Format text as HTML.

        Args:
            text: Text to format

        Returns:
            HTML-formatted text
        """
        # Escape HTML entities
        escaped = html_module.escape(text)

        # Convert newlines to <br>
        escaped = escaped.replace('\n', '<br>\n')

        # Wrap in basic HTML structure
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Document</title>
</head>
<body>
    <div class="content">
        {escaped}
    </div>
</body>
</html>"""

    def _format_xml(self, text: str) -> str:
        """Format text as XML.

        Args:
            text: Text to format

        Returns:
            XML-formatted text
        """
        escaped = html_module.escape(text)
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<document>
    <content>{escaped}</content>
</document>"""

    def _format_csv(self, text: str) -> str:
        """Format text as CSV.

        Args:
            text: Comma or tab separated text

        Returns:
            Properly formatted CSV
        """
        lines = text.strip().split('\n')
        formatted = []

        for line in lines:
            # Handle both comma and tab separators
            if '\t' in line:
                fields = line.split('\t')
            else:
                fields = line.split(',')

            # Quote fields that contain commas or quotes
            quoted_fields = []
            for field in fields:
                field = field.strip()
                if ',' in field or '"' in field:
                    field = field.replace('"', '""')
                    field = f'"{field}"'
                quoted_fields.append(field)

            formatted.append(','.join(quoted_fields))

        return '\n'.join(formatted)

    def _format_code(self, text: str, language: str = 'python') -> str:
        """Format source code.

        Args:
            text: Source code
            language: Programming language

        Returns:
            Formatted code
        """
        # Basic code formatting (indentation)
        lines = text.split('\n')
        formatted = []
        indent_level = 0

        for line in lines:
            stripped = line.strip()

            # Decrease indent for closing brackets
            if stripped.startswith(('}', ')', ']', 'end', 'else:', 'elif', 'except:', 'finally:')):
                indent_level = max(0, indent_level - 1)

            # Add indentation
            if stripped:
                formatted.append('    ' * indent_level + stripped)
            else:
                formatted.append('')

            # Increase indent for opening brackets
            if stripped.endswith((':', '{', '(', '[')):
                indent_level += 1

        return '\n'.join(formatted)

    def _format_yaml(self, text: str) -> str:
        """Format text as YAML.

        Args:
            text: Text to format

        Returns:
            YAML-formatted text
        """
        try:
            # If it's JSON, convert to YAML-like format
            data = json.loads(text)
            return self._dict_to_yaml(data)
        except:
            return text

    def _dict_to_yaml(self, data: Any, indent: int = 0) -> str:
        """Convert dict to YAML-like format."""
        if isinstance(data, dict):
            lines = []
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    lines.append(f"{'  ' * indent}{key}:")
                    lines.append(self._dict_to_yaml(value, indent + 1))
                else:
                    lines.append(f"{'  ' * indent}{key}: {value}")
            return '\n'.join(lines)
        elif isinstance(data, list):
            lines = []
            for item in data:
                lines.append(f"{'  ' * indent}- {item}")
            return '\n'.join(lines)
        else:
            return str(data)


def get_module() -> ModuleC:
    """Factory function to get module instance."""
    return ModuleC()
