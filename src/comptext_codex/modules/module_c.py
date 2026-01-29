"""Module C: Formatting - Document formatting and structure."""

import json
import re
from typing import Any, Dict, List

from comptext_codex.registry import codex_module, codex_command
from .base import BaseModule


@codex_module(
    code="C",
    name="Formatting",
    purpose="Document formatting and structure",
    token_priority="medium",
    security={"pii_safe": True, "threat_model": "template_injection_controls"},
)
class ModuleC(BaseModule):
    """Formatting module for document structure and styling."""

    @codex_command(syntax="@C:format[type=<format>] <text>", description="Format text according to specified style", aliases=["style"], token_cost_hint=40)
    def execute_format(self, *args, context: Dict[str, Any] = None, **kwargs) -> str:
        fmt = kwargs.get("type", "markdown")
        text = " ".join(args) if args else (context or {}).get("_last_result", "")
        formatters = {"markdown": self._format_markdown, "json": self._format_json, "html": self._format_html, "xml": self._format_xml, "yaml": self._format_yaml, "csv": self._format_csv}
        return formatters.get(fmt, lambda x: x)(text)

    @codex_command(syntax="@C:markdown[style=<style>] <text>", description="Advanced markdown formatting with styles", token_cost_hint=40)
    def execute_markdown(self, *args, context: Dict[str, Any] = None, **kwargs) -> str:
        style = kwargs.get("style", "standard")
        text = " ".join(args) if args else ""
        if style == "github":
            return self._format_github_markdown(text)
        if style == "minimal":
            return self._format_minimal_markdown(text)
        return self._format_markdown(text)

    @codex_command(syntax="@C:json[indent=<n>] <text>", description="Format and prettify JSON", token_cost_hint=30)
    def execute_json(self, *args, context: Dict[str, Any] = None, **kwargs) -> str:
        indent = kwargs.get("indent", 2)
        sort_keys = kwargs.get("sort_keys", False)
        text = " ".join(args) if args else ""
        return self._format_json(text, indent=indent, sort_keys=sort_keys)

    @codex_command(syntax="@C:html[semantic=<bool>] <text>", description="Generate semantic HTML", token_cost_hint=40)
    def execute_html(self, *args, context: Dict[str, Any] = None, **kwargs) -> str:
        semantic = kwargs.get("semantic", True)
        minify = kwargs.get("minify", False)
        text = " ".join(args) if args else ""
        html = self._format_html(text, semantic=semantic)
        if minify:
            html = re.sub(r"\s+", " ", html).strip()
        return html

    @codex_command(syntax="@C:table[format=<format>] <data>", description="Format data as table", token_cost_hint=50)
    def execute_table(self, *args, context: Dict[str, Any] = None, **kwargs) -> str:
        fmt = kwargs.get("format", "markdown")
        headers = kwargs.get("headers", [])
        text = " ".join(args) if args else ""
        if fmt == "markdown":
            return self._format_markdown_table(text, headers)
        if fmt == "html":
            return self._format_html_table(text, headers)
        if fmt == "ascii":
            return self._format_ascii_table(text, headers)
        return text

    @codex_command(syntax="@C:code[lang=<lang>] <code>", description="Format code with syntax highlighting markers", token_cost_hint=20)
    def execute_code(self, *args, context: Dict[str, Any] = None, **kwargs) -> str:
        lang = kwargs.get("lang", "python")
        inline = kwargs.get("inline", False)
        text = " ".join(args) if args else ""
        return f"`{text}`" if inline else f"```{lang}\n{text}\n```"

    @codex_command(syntax="@C:list[ordered=<bool>] <items>", description="Format items as list", token_cost_hint=20)
    def execute_list(self, *args, context: Dict[str, Any] = None, **kwargs) -> str:
        ordered = kwargs.get("ordered", False)
        items = list(args) if args else []
        if ordered:
            return "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))
        return "\n".join(f"- {item}" for item in items)

    @codex_command(syntax="@C:prettify[type=<type>] <content>", description="Auto-detect and prettify content", token_cost_hint=40)
    def execute_prettify(self, *args, context: Dict[str, Any] = None, **kwargs) -> str:
        content = " ".join(args) if args else ""
        ctype = kwargs.get("type", "auto")
        if ctype == "auto":
            ctype = self._detect_content_type(content)
        return self.execute_format(content, context=context, type=ctype)

    # -- helpers ---------------------------------------------------------------

    def _format_markdown(self, text: str) -> str:
        lines = text.split("\n")
        out = []
        for line in lines:
            line = line.strip()
            if not line:
                out.append("")
            elif line.startswith("#"):
                out.append(line)
            elif len(line) < 60 and not any(c in line for c in [".", ",", "!"]):
                out.append(f"## {line}")
            else:
                out.append(line)
        return "\n".join(out)

    def _format_github_markdown(self, text: str) -> str:
        parts = text.split("\n")
        return f"# {parts[0]}\n\n{chr(10).join(parts[1:])}\n\n---\n*Generated with CompText*\n"

    def _format_minimal_markdown(self, text: str) -> str:
        return text.replace("\n\n", "\n")

    def _format_json(self, text: str, indent: int = 2, sort_keys: bool = False) -> str:
        try:
            data = json.loads(text) if text.strip().startswith(("{", "[")) else {"content": text}
            return json.dumps(data, indent=indent, sort_keys=sort_keys, ensure_ascii=False)
        except Exception:
            return json.dumps({"content": text}, indent=indent)

    def _format_html(self, text: str, semantic: bool = True) -> str:
        if semantic:
            parts = [p.strip() for p in text.split("\n\n") if p.strip()]
            html = [f"<h2>{p}</h2>" if len(p) < 60 and "\n" not in p else f"<p>{p}</p>" for p in parts]
            return f"<article>\n  {'  '.join(html)}\n</article>"
        return f"<div><p>{text}</p></div>"

    def _format_xml(self, text: str) -> str:
        return f'<?xml version="1.0" encoding="UTF-8"?>\n<document>\n  <content>{text}</content>\n</document>'

    def _format_yaml(self, text: str) -> str:
        return "\n".join(line if ":" in line else f"content: {line}" for line in text.split("\n"))

    def _format_csv(self, text: str) -> str:
        return "\n".join(f'"{line}"' for line in text.split("\n") if line.strip())

    def _format_markdown_table(self, text: str, headers: List[str]) -> str:
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        if not headers and lines:
            headers = ["Column 1", "Column 2", "Column 3"]
        h = "| " + " | ".join(headers) + " |"
        s = "| " + " | ".join(["---"] * len(headers)) + " |"
        rows = []
        for line in lines:
            cells = line.split(",")[:len(headers)]
            cells += [""] * (len(headers) - len(cells))
            rows.append("| " + " | ".join(cells) + " |")
        return "\n".join([h, s] + rows)

    def _format_html_table(self, text: str, headers: List[str]) -> str:
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        parts = ["<table>"]
        if headers:
            parts += ["  <thead>", "    <tr>"] + [f"      <th>{h}</th>" for h in headers] + ["    </tr>", "  </thead>"]
        parts.append("  <tbody>")
        for line in lines:
            parts.append("    <tr>")
            for cell in line.split(","):
                parts.append(f"      <td>{cell.strip()}</td>")
            parts.append("    </tr>")
        parts += ["  </tbody>", "</table>"]
        return "\n".join(parts)

    def _format_ascii_table(self, text: str, headers: List[str]) -> str:
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        cw = [len(h) for h in headers] if headers else [10, 10, 10]
        for line in lines:
            for i, cell in enumerate(line.split(",")):
                if i < len(cw):
                    cw[i] = max(cw[i], len(cell.strip()))
        out = ["\u250c" + "\u252c".join("\u2500" * (w + 2) for w in cw) + "\u2510"]
        if headers:
            out.append("\u2502" + "\u2502".join(f" {h:<{w}} " for h, w in zip(headers, cw)) + "\u2502")
            out.append("\u251c" + "\u253c".join("\u2500" * (w + 2) for w in cw) + "\u2524")
        for line in lines:
            cells = line.split(",")
            cells += [""] * (len(cw) - len(cells))
            out.append("\u2502" + "\u2502".join(f" {c.strip():<{w}} " for c, w in zip(cells, cw)) + "\u2502")
        out.append("\u2514" + "\u2534".join("\u2500" * (w + 2) for w in cw) + "\u2518")
        return "\n".join(out)

    def _detect_content_type(self, content: str) -> str:
        c = content.strip()
        if c.startswith(("{", "[")):
            return "json"
        if c.startswith("<"):
            return "html"
        if "<?xml" in c:
            return "xml"
        if c.count("\n") > 2 and all(":" in l for l in c.split("\n")[:3]):
            return "yaml"
        if "," in c and c.count(",") > 3:
            return "csv"
        return "markdown"


def get_module() -> ModuleC:
    return ModuleC()
