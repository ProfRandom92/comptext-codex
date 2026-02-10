"""CompText V5.0 ULTRA MCP Server Implementation.

Exposes the CompText V5.0 ULTRA protocol through the `Model Context Protocol
<https://modelcontextprotocol.io/>`_ so that AI agent teams can parse, encode,
and benchmark ultra-compact commands without leaving their tool loop.

Available MCP Tools
-------------------
+----------------------------+---------------------------------------------------+
| Tool                       | Description                                       |
+============================+===================================================+
| ``parse_v5``               | Decompress a V5 command string into structured    |
|                            | command/language/modifier/task components.         |
+----------------------------+---------------------------------------------------+
| ``encode_v5``              | Compress a natural command description into V5.0  |
|                            | ULTRA single-character format.                    |
+----------------------------+---------------------------------------------------+
| ``encode_batch_v5``        | Compress multiple commands into a V5 batch string |
|                            | (``B:[...]|[...]``).                             |
+----------------------------+---------------------------------------------------+
| ``calculate_token_reduction``| Measure token savings between natural language   |
|                            | and V5 encoding using tiktoken BPE.               |
+----------------------------+---------------------------------------------------+
| ``convert_v5_to_v4``       | Convert a V5 command to legacy V4.0 format.       |
+----------------------------+---------------------------------------------------+
| ``get_v5_reference``       | Return the full V5 syntax reference (commands,    |
|                            | languages, modifiers, examples).                  |
+----------------------------+---------------------------------------------------+
| ``benchmark_v5``           | Run a multi-example benchmark and return          |
|                            | aggregate token reduction statistics.             |
+----------------------------+---------------------------------------------------+

Quick start::

    # Install with MCP support
    pip install comptext-codex[mcp]

    # Run the server (stdio transport)
    comptext-mcp
"""

import json
import sys
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict

try:
    from mcp import Server, Tool, types
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    # Fallback for when MCP is not installed
    class Server:  # type: ignore[no-redef]
        pass
    class Tool:  # type: ignore[no-redef]
        pass

from .parser_v5 import CompTextParserV5, CompTextCommandV5


@dataclass
class MCPToolResult:
    """Result from an MCP tool execution.

    Attributes:
        success: Whether the tool call completed without errors.
        data: The tool's return payload (tool-specific).
        error: Human-readable error message when ``success`` is False.
        metadata: Optional extra metadata (timing, version, etc.).
    """
    success: bool
    data: Any
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CompTextMCPServer:
    """MCP Server for CompText V5.0 ULTRA Protocol.

    Provides 7 tools for parsing, encoding, and analysing V5.0 ULTRA
    commands through the Model Context Protocol.  The server is
    transport-agnostic and defaults to ``stdio``.

    Example::

        server = CompTextMCPServer()
        import asyncio
        asyncio.run(server.start("stdio"))
    """

    def __init__(self) -> None:
        """Initialise the MCP server and register all tool endpoints.

        Raises:
            ImportError: If the ``mcp`` package is not installed.
        """
        if not MCP_AVAILABLE:
            raise ImportError(
                "MCP package not installed. Install with: pip install comptext-codex[mcp]"
            )

        self.parser = CompTextParserV5()
        self.server = Server("comptext-v5-ultra")

        # Register tools
        self._register_tools()

    def _register_tools(self) -> None:
        """Register all MCP tool endpoints on ``self.server``."""

        @self.server.tool(
            name="parse_v5",
            description=(
                "Parse a CompText V5.0 ULTRA command into structured format. "
                "Accepts single commands (e.g. 'C;P:FIB') or batch commands "
                "(e.g. 'B:[D:SUM]|[C;P:FIB]|[E;C:WHY]'). Returns an array of "
                "decomposed command objects with full-name expansions."
            ),
            parameters={
                "command": {
                    "type": "string",
                    "description": (
                        "V5.0 ULTRA command string. Examples: "
                        "'C;P:FIB' (single), 'B:[D:SUM]|[C;P:FIB]' (batch)"
                    ),
                }
            }
        )
        async def parse_v5(command: str) -> Dict[str, Any]:
            """Parse V5.0 ULTRA command string into structured components."""
            try:
                results = self.parser.parse(command)

                commands = []
                for cmd in results:
                    commands.append({
                        "command": self.parser.COMMANDS.get(cmd.command, cmd.command),
                        "command_char": cmd.command,
                        "language": self.parser.LANGUAGES.get(cmd.language, cmd.language) if cmd.language else None,
                        "language_char": cmd.language,
                        "modifiers": [self.parser.MODIFIERS.get(m, m) for m in cmd.modifiers] if cmd.modifiers else [],
                        "modifier_chars": cmd.modifiers,
                        "task": cmd.task,
                        "raw": cmd.raw
                    })

                return {
                    "success": True,
                    "count": len(commands),
                    "commands": commands
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }

        @self.server.tool(
            name="encode_v5",
            description=(
                "Encode a human-readable command specification into V5.0 ULTRA "
                "single-character format. E.g. command='CODE', language='PYTHON', "
                "task='FIB' -> 'C;P:FIB'."
            ),
            parameters={
                "command": {
                    "type": "string",
                    "description": "Command name: CODE, FIX, MODIFY, TEST, DOCUMENT, EXPLAIN, OPTIMIZE, or ANALYZE"
                },
                "language": {
                    "type": "string",
                    "description": "Optional language: PYTHON, JAVASCRIPT, TYPESCRIPT, RUST, GO, SQL, or HTML",
                    "optional": True
                },
                "modifiers": {
                    "type": "array",
                    "description": "Optional modifiers: NO_COMMENTS, STRICT, ROBUST, CONCISE",
                    "optional": True
                },
                "task": {
                    "type": "string",
                    "description": "Optional task identifier (e.g. 'FIB', 'AUTH', 'API')",
                    "optional": True
                }
            }
        )
        async def encode_v5(command: str, language: Optional[str] = None,
                           modifiers: Optional[List[str]] = None,
                           task: Optional[str] = None) -> Dict[str, Any]:
            """Encode a command specification into V5.0 ULTRA format."""
            try:
                result = self.parser.encode(
                    command.upper(),
                    language.upper() if language else None,
                    [m.upper() for m in modifiers] if modifiers else None,
                    task
                )

                return {
                    "success": True,
                    "v5_command": result,
                    "input": {
                        "command": command,
                        "language": language,
                        "modifiers": modifiers,
                        "task": task
                    }
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }

        @self.server.tool(
            name="encode_batch_v5",
            description=(
                "Encode multiple commands into a single V5.0 ULTRA batch string. "
                "Returns the 'B:[...]|[...]' format for parallel execution."
            ),
            parameters={
                "commands": {
                    "type": "array",
                    "description": (
                        "Array of command objects, each with keys: "
                        "command (required), language, modifiers, task"
                    ),
                }
            }
        )
        async def encode_batch_v5(commands: List[Dict[str, Any]]) -> Dict[str, Any]:
            """Encode a batch of commands into V5.0 ULTRA batch format."""
            try:
                batch_input = []
                for cmd_dict in commands:
                    batch_input.append((
                        cmd_dict.get('command', '').upper(),
                        cmd_dict.get('language', '').upper() if cmd_dict.get('language') else None,
                        [m.upper() for m in cmd_dict.get('modifiers', [])] if cmd_dict.get('modifiers') else None,
                        cmd_dict.get('task')
                    ))

                result = self.parser.encode_batch(batch_input)

                return {
                    "success": True,
                    "v5_batch": result,
                    "count": len(commands)
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }

        @self.server.tool(
            name="calculate_token_reduction",
            description=(
                "Calculate token reduction statistics between a natural-language "
                "prompt and its V5.0 ULTRA equivalent.  Uses tiktoken BPE "
                "(cl100k_base) for deterministic counting."
            ),
            parameters={
                "natural_language": {
                    "type": "string",
                    "description": "The original verbose natural language request"
                },
                "v5_command": {
                    "type": "string",
                    "description": "The V5.0 ULTRA encoded command"
                }
            }
        )
        async def calculate_token_reduction(natural_language: str, v5_command: str) -> Dict[str, Any]:
            """Calculate token reduction statistics between NL and V5 encoding."""
            try:
                stats = self.parser.calculate_token_reduction(natural_language, v5_command)

                return {
                    "success": True,
                    "statistics": stats
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }

        @self.server.tool(
            name="convert_v5_to_v4",
            description=(
                "Convert a V5.0 ULTRA command to the legacy V4.0 format. "
                "Useful for backward compatibility with older integrations."
            ),
            parameters={
                "v5_command": {
                    "type": "string",
                    "description": "V5.0 ULTRA command to convert (e.g. 'C;P:FIB')"
                }
            }
        )
        async def convert_v5_to_v4(v5_command: str) -> Dict[str, Any]:
            """Convert V5 command to legacy V4 format."""
            try:
                results = self.parser.parse(v5_command)

                v4_commands = []
                for cmd in results:
                    v4_format = self.parser.to_v4_format(cmd)
                    v4_commands.append(v4_format)

                return {
                    "success": True,
                    "v5_input": v5_command,
                    "v4_output": v4_commands,
                    "count": len(v4_commands)
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }

        @self.server.tool(
            name="get_v5_reference",
            description=(
                "Return the complete V5.0 ULTRA syntax reference including "
                "all command codes, language codes, modifier codes, syntax "
                "patterns, and annotated examples."
            ),
            parameters={}
        )
        async def get_v5_reference() -> Dict[str, Any]:
            """Return the full V5.0 ULTRA syntax reference card."""
            return {
                "success": True,
                "version": "5.0.3",
                "commands": {char: full for char, full in self.parser.COMMANDS.items()},
                "languages": {char: full for char, full in self.parser.LANGUAGES.items()},
                "modifiers": {char: full for char, full in self.parser.MODIFIERS.items()},
                "syntax": {
                    "simple": "CMD;LANG:TASK",
                    "with_modifiers": "CMD;LANG;MOD:TASK",
                    "batch": "B:[CMD1]|[CMD2]|[CMD3]"
                },
                "examples": [
                    {"v5": "C;P:FIB", "description": "Code Python Fibonacci"},
                    {"v5": "T;P;R:FIB", "description": "Test Python (Robust) Fibonacci"},
                    {"v5": "B:[D:SUM]|[C;P:FIB]|[E;C:WHY]", "description": "Batch: Document + Code + Explain"}
                ]
            }

        @self.server.tool(
            name="benchmark_v5",
            description=(
                "Run a token-reduction benchmark over one or more example pairs. "
                "Each pair provides a natural-language prompt and its V5 encoding. "
                "Returns per-example and aggregate statistics."
            ),
            parameters={
                "examples": {
                    "type": "array",
                    "description": (
                        "Array of objects, each with 'natural' (str) and 'v5' (str) keys"
                    ),
                }
            }
        )
        async def benchmark_v5(examples: List[Dict[str, str]]) -> Dict[str, Any]:
            """Run a multi-example token reduction benchmark."""
            try:
                results = []
                total_natural_tokens = 0
                total_v5_tokens = 0

                for example in examples:
                    stats = self.parser.calculate_token_reduction(
                        example['natural'],
                        example['v5']
                    )
                    results.append(stats)
                    total_natural_tokens += stats['natural_tokens']
                    total_v5_tokens += stats['v5_tokens']

                avg_reduction = round(
                    (1 - total_v5_tokens / total_natural_tokens) * 100, 1
                ) if total_natural_tokens > 0 else 0

                return {
                    "success": True,
                    "examples": results,
                    "aggregate": {
                        "total_natural_tokens": total_natural_tokens,
                        "total_v5_tokens": total_v5_tokens,
                        "total_saved": total_natural_tokens - total_v5_tokens,
                        "average_reduction_percent": avg_reduction
                    }
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }

    async def start(self, transport: str = "stdio") -> None:
        """Start the MCP server.

        Args:
            transport: Transport type (``"stdio"``, ``"sse"``, etc.).
        """
        await self.server.run(transport)


def create_server() -> CompTextMCPServer:
    """Create and return a new CompText MCP server instance.

    Raises:
        ImportError: If the ``mcp`` package is not installed.
    """
    return CompTextMCPServer()


# CLI entry point for MCP server
def main() -> None:
    """Main entry point for the ``comptext-mcp`` CLI command."""
    import asyncio

    if not MCP_AVAILABLE:
        print("Error: MCP package not installed")
        print("Install with: pip install comptext-codex[mcp]")
        sys.exit(1)

    server = create_server()

    print("CompText V5.0 ULTRA MCP Server")
    print("Listening on stdio...")

    asyncio.run(server.start("stdio"))


if __name__ == '__main__':
    main()
