"""Module C: Formatting - Document formatting and structure."""

from typing import Any, Dict, List
import json
import re
from .base import BaseModule


class ModuleC(BaseModule):
    """Formatting module for document structure and styling."""

    def get_commands(self) -> List[Dict[str, Any]]:
        return [
            {'module': 'C', 'command': 'format', 'syntax': '@C:format[type=<format>] <text>'},
            {'module': 'C', 'command': 'markdown', 'syntax': '@C:markdown[style=<style>] <text>'},
            {'module': 'C', 'command': 'json', 'syntax': '@C:json[indent=<n>] <text>'},
            {'module': 'C', 'command': 'html', 'syntax': '@C:html[semantic=<bool>] <text>'},
            {'module': 'C', 'command': 'table', 'syntax': '@C:table[format=<format>] <data>'},
            {'module': 'C', 'command': 'code', 'syntax': '@C:code[lang=<lang>] <code>'},
            {'module': 'C', 'command': 'list', 'syntax': '@C:list[ordered=<bool>] <items>'},
            {'module': 'C', 'command': 'prettify', 'syntax': '@C:prettify[type=<type>] <content>'}
        ]

    def execute_format(self, *args, context: Dict[str, Any] = None, **kwargs) -> str:
        """Format text according to specified style."""
        format_type = kwargs.get('type', 'markdown')
        text = ' '.join(args) if args else context.get('_last_result', '')

        formatters = {
            'markdown': self._format_markdown,
            'json': self._format_json,
            'html': self._format_html,
            'xml': self._format_xml,
            'yaml': self._format_yaml,
            'csv': self._format_csv
        }

        formatter = formatters.get(format_type, lambda x: x)
        return formatter(text)

    def execute_markdown(self, *args, context: Dict[str, Any] = None, **kwargs) -> str:
        """Advanced markdown formatting with styles."""
        style = kwargs.get('style', 'standard')
        text = ' '.join(args) if args else ''

        if style == 'github':
            return self._format_github_markdown(text)
        elif style == 'minimal':
            return self._format_minimal_markdown(text)
        else:
            return self._format_markdown(text)

    def execute_json(self, *args, context: Dict[str, Any] = None, **kwargs) -> str:
        """Format and prettify JSON."""
        indent = kwargs.get('indent', 2)
        sort_keys = kwargs.get('sort_keys', False)
        text = ' '.join(args) if args else ''

        return self._format_json(text, indent=indent, sort_keys=sort_keys)

    def execute_html(self, *args, context: Dict[str, Any] = None, **kwargs) -> str:
        """Generate semantic HTML."""
        semantic = kwargs.get('semantic', True)
        minify = kwargs.get('minify', False)
        text = ' '.join(args) if args else ''

        html = self._format_html(text, semantic=semantic)

        if minify:
            html = re.sub(r'\s+', ' ', html).strip()

        return html

    def execute_table(self, *args, context: Dict[str, Any] = None, **kwargs) -> str:
        """Format data as table."""
        format_type = kwargs.get('format', 'markdown')
        headers = kwargs.get('headers', [])

        # Try to parse data
        text = ' '.join(args) if args else ''

        if format_type == 'markdown':
            return self._format_markdown_table(text, headers)
        elif format_type == 'html':
            return self._format_html_table(text, headers)
        elif format_type == 'ascii':
            return self._format_ascii_table(text, headers)

        return text

    def execute_code(self, *args, context: Dict[str, Any] = None, **kwargs) -> str:
        """Format code with syntax highlighting markers."""
        lang = kwargs.get('lang', 'python')
        inline = kwargs.get('inline', False)
        text = ' '.join(args) if args else ''

        if inline:
            return f"`{text}`"
        else:
            return f"```{lang}\n{text}\n```"

    def execute_list(self, *args, context: Dict[str, Any] = None, **kwargs) -> str:
        """Format items as list."""
        ordered = kwargs.get('ordered', False)
        items = list(args) if args else []

        if ordered:
            return '\n'.join(f"{i+1}. {item}" for i, item in enumerate(items))
        else:
            return '\n'.join(f"- {item}" for item in items)

    def execute_prettify(self, *args, context: Dict[str, Any] = None, **kwargs) -> str:
        """Auto-detect and prettify content."""
        content = ' '.join(args) if args else ''
        content_type = kwargs.get('type', 'auto')

        if content_type == 'auto':
            content_type = self._detect_content_type(content)

        return self.execute_format(content, context=context, type=content_type)

    def _format_markdown(self, text: str) -> str:
        """Format as markdown."""
        lines = text.split('\n')
        formatted = []

        for line in lines:
            line = line.strip()
            if not line:
                formatted.append('')
            elif line.startswith('#'):
                formatted.append(line)
            else:
                # Add heading if it looks like a title
                if len(line) < 60 and not any(c in line for c in ['.', ',', '!']):
                    formatted.append(f"## {line}")
                else:
                    formatted.append(line)

        return '\n'.join(formatted)

    def _format_github_markdown(self, text: str) -> str:
        """Format as GitHub-flavored markdown."""
        return f"""# {text.split('\n')[0]}

{'\n'.join(text.split('\n')[1:])}

---
*Generated with CompText*
"""

    def _format_minimal_markdown(self, text: str) -> str:
        """Minimal markdown formatting."""
        return text.replace('\n\n', '\n')

    def _format_json(self, text: str, indent: int = 2, sort_keys: bool = False) -> str:
        """Format as JSON."""
        try:
            # Try to parse existing JSON
            if text.strip().startswith(('{', '[')):
                data = json.loads(text)
            else:
                # Wrap in object
                data = {'content': text}

            return json.dumps(data, indent=indent, sort_keys=sort_keys, ensure_ascii=False)
        except:
            return json.dumps({'content': text}, indent=indent)

    def _format_html(self, text: str, semantic: bool = True) -> str:
        """Format as HTML."""
        if semantic:
            paragraphs = text.split('\n\n')
            html_parts = []

            for p in paragraphs:
                p = p.strip()
                if not p:
                    continue

                # Check if it's a heading
                if len(p) < 60 and '\n' not in p:
                    html_parts.append(f"<h2>{p}</h2>")
                else:
                    html_parts.append(f"<p>{p}</p>")

            return f"<article>\n  {'  '.join(html_parts)}\n</article>"
        else:
            return f"<div><p>{text}</p></div>"

    def _format_xml(self, text: str) -> str:
        """Format as XML."""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<document>
  <content>{text}</content>
</document>"""

    def _format_yaml(self, text: str) -> str:
        """Format as YAML."""
        lines = text.split('\n')
        yaml_lines = []

        for line in lines:
            if ':' in line:
                yaml_lines.append(line)
            else:
                yaml_lines.append(f"content: {line}")

        return '\n'.join(yaml_lines)

    def _format_csv(self, text: str) -> str:
        """Format as CSV."""
        lines = text.split('\n')
        return '\n'.join(f'"{line}"' for line in lines if line.strip())

    def _format_markdown_table(self, text: str, headers: List[str]) -> str:
        """Format as markdown table."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        if not headers and lines:
            headers = ['Column 1', 'Column 2', 'Column 3']

        header_row = '| ' + ' | '.join(headers) + ' |'
        separator = '| ' + ' | '.join(['---'] * len(headers)) + ' |'

        data_rows = []
        for line in lines:
            cells = line.split(',')[:len(headers)]
            cells += [''] * (len(headers) - len(cells))
            data_rows.append('| ' + ' | '.join(cells) + ' |')

        return '\n'.join([header_row, separator] + data_rows)

    def _format_html_table(self, text: str, headers: List[str]) -> str:
        """Format as HTML table."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        html = ['<table>']

        if headers:
            html.append('  <thead>')
            html.append('    <tr>')
            for h in headers:
                html.append(f'      <th>{h}</th>')
            html.append('    </tr>')
            html.append('  </thead>')

        html.append('  <tbody>')
        for line in lines:
            html.append('    <tr>')
            cells = line.split(',')
            for cell in cells:
                html.append(f'      <td>{cell.strip()}</td>')
            html.append('    </tr>')
        html.append('  </tbody>')
        html.append('</table>')

        return '\n'.join(html)

    def _format_ascii_table(self, text: str, headers: List[str]) -> str:
        """Format as ASCII table."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # Calculate column widths
        col_widths = [len(h) for h in headers] if headers else [10, 10, 10]

        for line in lines:
            cells = line.split(',')
            for i, cell in enumerate(cells):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(cell.strip()))

        # Build table
        result = []

        # Top border
        result.append('┌' + '┬'.join('─' * (w + 2) for w in col_widths) + '┐')

        # Headers
        if headers:
            header_row = '│' + '│'.join(f' {h:<{w}} ' for h, w in zip(headers, col_widths)) + '│'
            result.append(header_row)
            result.append('├' + '┼'.join('─' * (w + 2) for w in col_widths) + '┤')

        # Data rows
        for line in lines:
            cells = line.split(',')
            cells += [''] * (len(col_widths) - len(cells))
            row = '│' + '│'.join(f' {c.strip():<{w}} ' for c, w in zip(cells, col_widths)) + '│'
            result.append(row)

        # Bottom border
        result.append('└' + '┴'.join('─' * (w + 2) for w in col_widths) + '┘')

        return '\n'.join(result)

    def _detect_content_type(self, content: str) -> str:
        """Auto-detect content type."""
        content = content.strip()

        if content.startswith(('{', '[')):
            return 'json'
        elif content.startswith('<'):
            return 'html'
        elif '<?xml' in content:
            return 'xml'
        elif content.count('\n') > 2 and all(':' in line for line in content.split('\n')[:3]):
            return 'yaml'
        elif ',' in content and content.count(',') > 3:
            return 'csv'
        else:
            return 'markdown'


def get_module() -> ModuleC:
    return ModuleC()
