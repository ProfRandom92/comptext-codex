"""CompText V5.0 ULTRA MCP Server Implementation."""

import json
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict

try:
    from mcp import Server, Tool, types
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    # Fallback for when MCP is not installed
    class Server:
        pass
    class Tool:
        pass

from .parser_v5 import CompTextParserV5, CompTextCommandV5


@dataclass
class MCPToolResult:
    """Result from an MCP tool execution."""
    success: bool
    data: Any
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CompTextMCPServer:
    """MCP Server for CompText V5.0 ULTRA Protocol.

    Provides tools for parsing, encoding, and analyzing V5.0 ULTRA commands
    through the Model Context Protocol.
    """

    def __init__(self):
        """Initialize MCP server."""
        if not MCP_AVAILABLE:
            raise ImportError("MCP package not installed. Install with: pip install mcp")

        self.parser = CompTextParserV5()
        self.server = Server("comptext-v5-ultra")

        # Register tools
        self._register_tools()

    def _register_tools(self):
        """Register MCP tools."""

        @self.server.tool(
            name="parse_v5",
            description="Parse a CompText V5.0 ULTRA command into structured format",
            parameters={
                "command": {
                    "type": "string",
                    "description": "V5.0 ULTRA command to parse (e.g., 'C;P:FIB' or 'B:[D:SUM]|[C;P:FIB]')"
                }
            }
        )
        async def parse_v5(command: str) -> Dict[str, Any]:
            """Parse V5.0 ULTRA command."""
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
            description="Encode a command to V5.0 ULTRA format",
            parameters={
                "command": {
                    "type": "string",
                    "description": "Command name (e.g., 'CODE', 'TEST', 'DOCUMENT')"
                },
                "language": {
                    "type": "string",
                    "description": "Optional language (e.g., 'PYTHON', 'JAVASCRIPT')",
                    "optional": True
                },
                "modifiers": {
                    "type": "array",
                    "description": "Optional modifiers (e.g., ['ROBUST', 'CONCISE'])",
                    "optional": True
                },
                "task": {
                    "type": "string",
                    "description": "Optional task name",
                    "optional": True
                }
            }
        )
        async def encode_v5(command: str, language: Optional[str] = None,
                           modifiers: Optional[List[str]] = None,
                           task: Optional[str] = None) -> Dict[str, Any]:
            """Encode command to V5.0 ULTRA format."""
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
            description="Encode multiple commands to V5.0 ULTRA batch format",
            parameters={
                "commands": {
                    "type": "array",
                    "description": "Array of command objects with command, language, modifiers, task"
                }
            }
        )
        async def encode_batch_v5(commands: List[Dict[str, Any]]) -> Dict[str, Any]:
            """Encode batch of commands to V5.0 ULTRA format."""
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
            description="Calculate token reduction statistics for V5.0 ULTRA",
            parameters={
                "natural_language": {
                    "type": "string",
                    "description": "Original natural language request"
                },
                "v5_command": {
                    "type": "string",
                    "description": "V5.0 ULTRA encoded command"
                }
            }
        )
        async def calculate_token_reduction(natural_language: str, v5_command: str) -> Dict[str, Any]:
            """Calculate token reduction statistics."""
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
            description="Convert V5.0 ULTRA command to V4.0 format",
            parameters={
                "v5_command": {
                    "type": "string",
                    "description": "V5.0 ULTRA command to convert"
                }
            }
        )
        async def convert_v5_to_v4(v5_command: str) -> Dict[str, Any]:
            """Convert V5 to V4 format."""
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
            description="Get V5.0 ULTRA syntax reference (commands, languages, modifiers)",
            parameters={}
        )
        async def get_v5_reference() -> Dict[str, Any]:
            """Get V5.0 ULTRA reference."""
            return {
                "success": True,
                "version": "5.0.0",
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
            description="Run benchmark comparing natural language to V5.0 ULTRA",
            parameters={
                "examples": {
                    "type": "array",
                    "description": "Array of {natural, v5} example pairs"
                }
            }
        )
        async def benchmark_v5(examples: List[Dict[str, str]]) -> Dict[str, Any]:
            """Run V5 benchmark."""
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

    async def start(self, transport: str = "stdio"):
        """Start the MCP server.

        Args:
            transport: Transport type ("stdio", "sse", etc.)
        """
        await self.server.run(transport)


def create_server() -> CompTextMCPServer:
    """Create and return a new CompText MCP server instance."""
    return CompTextMCPServer()


# CLI entry point for MCP server
def main():
    """Main entry point for MCP server."""
    import asyncio

    if not MCP_AVAILABLE:
        print("Error: MCP package not installed")
        print("Install with: pip install mcp")
        sys.exit(1)

    server = create_server()

    print("CompText V5.0 ULTRA MCP Server")
    print("Listening on stdio...")

    asyncio.run(server.start("stdio"))


if __name__ == '__main__':
    main()
