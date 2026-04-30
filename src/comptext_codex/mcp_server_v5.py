"""CompText V5.0 ULTRA MCP Server Implementation."""

import asyncio
import json
import sys
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, asdict

try:
    from mcp.server import Server
    from mcp.types import Tool
    import mcp.types as types
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    # Fallback stubs so the module remains importable without mcp installed
    class Server:  # type: ignore[no-redef]
        def __init__(self, *a, **kw): pass
        def tool(self, *a, **kw):
            def decorator(fn): return fn
            return decorator
    class Tool:  # type: ignore[no-redef]
        pass
    class types:  # type: ignore[no-redef]
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
    """MCP Server for CompText V5.0 ULTRA Protocol."""

    def __init__(self):
        """Initialize MCP server."""
        if not MCP_AVAILABLE:
            raise ImportError("MCP package not installed. Install with: pip install mcp")

        self.parser = CompTextParserV5()
        self.server = Server("comptext-v5-ultra")

        # Internal registries for testability
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._tool_handlers: Dict[str, Callable] = {}

        self._register_tools()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_tools(self) -> List[Dict[str, Any]]:
        """Return list of registered tool definitions."""
        return list(self._tools.values())

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a registered tool by name synchronously."""
        if name not in self._tool_handlers:
            raise ValueError(f"Unknown tool: {name}")
        handler = self._tool_handlers[name]
        result = asyncio.run(handler(**arguments))
        return {"success": True, "result": result}

    def handle_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a JSON-RPC style MCP request."""
        if method == "initialize":
            return {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "comptext-v5-ultra", "version": "5.0.0"},
                "capabilities": {"tools": {}},
            }
        if method == "tools/list":
            return {"tools": self.list_tools()}
        if method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            try:
                return self.call_tool(tool_name, arguments)
            except ValueError as exc:
                return {"error": str(exc)}
        return {"error": f"Unknown method: {method}"}

    # ------------------------------------------------------------------
    # Internal tool registration
    # ------------------------------------------------------------------

    def _add_tool(self, name: str, description: str,
                  parameters: Dict[str, Any], handler: Callable) -> None:
        """Register a tool in internal registry and with MCP server."""
        self._tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
        }
        self._tool_handlers[name] = handler
        # Register with the real MCP transport layer when available
        try:
            self.server.tool(
                name=name, description=description, parameters=parameters
            )(handler)
        except Exception:  # MagicMock or real server may differ
            pass

    def _register_tools(self) -> None:
        """Register all CompText MCP tools."""

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
                        "raw": cmd.raw,
                    })
                return {"success": True, "count": len(commands), "commands": commands}
            except Exception as exc:
                return {"success": False, "error": str(exc)}

        self._add_tool(
            "parse_v5",
            "Parse a CompText V5.0 ULTRA command into structured format",
            {"command": {"type": "string",
                         "description": "V5.0 ULTRA command to parse (e.g., 'C;P:FIB')"}},
            parse_v5,
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
                    task,
                )
                return {"success": True, "v5_command": result,
                        "input": {"command": command, "language": language,
                                  "modifiers": modifiers, "task": task}}
            except Exception as exc:
                return {"success": False, "error": str(exc)}

        self._add_tool(
            "encode_v5",
            "Encode a command to V5.0 ULTRA format",
            {"command": {"type": "string", "description": "Command name"},
             "language": {"type": "string", "optional": True},
             "modifiers": {"type": "array", "optional": True},
             "task": {"type": "string", "optional": True}},
            encode_v5,
        )

        async def encode_batch_v5(commands: List[Dict[str, Any]]) -> Dict[str, Any]:
            """Encode batch of commands to V5.0 ULTRA format."""
            try:
                batch_input = []
                for cmd_dict in commands:
                    batch_input.append((
                        cmd_dict.get("command", "").upper(),
                        cmd_dict.get("language", "").upper() if cmd_dict.get("language") else None,
                        [m.upper() for m in cmd_dict.get("modifiers", [])] if cmd_dict.get("modifiers") else None,
                        cmd_dict.get("task"),
                    ))
                result = self.parser.encode_batch(batch_input)
                return {"success": True, "v5_batch": result, "count": len(commands)}
            except Exception as exc:
                return {"success": False, "error": str(exc)}

        self._add_tool(
            "encode_batch_v5",
            "Encode multiple commands to V5.0 ULTRA batch format",
            {"commands": {"type": "array",
                          "description": "Array of command objects"}},
            encode_batch_v5,
        )

        async def calculate_token_reduction(natural_language: str,
                                            v5_command: str) -> Dict[str, Any]:
            """Calculate token reduction statistics."""
            try:
                stats = self.parser.calculate_token_reduction(natural_language, v5_command)
                return {"success": True, "statistics": stats}
            except Exception as exc:
                return {"success": False, "error": str(exc)}

        self._add_tool(
            "calculate_token_reduction",
            "Calculate token reduction statistics for V5.0 ULTRA",
            {"natural_language": {"type": "string"},
             "v5_command": {"type": "string"}},
            calculate_token_reduction,
        )

        async def convert_v5_to_v4(v5_command: str) -> Dict[str, Any]:
            """Convert V5 to V4 format."""
            try:
                results = self.parser.parse(v5_command)
                v4_commands = [self.parser.to_v4_format(cmd) for cmd in results]
                return {"success": True, "v5_input": v5_command,
                        "v4_output": v4_commands, "count": len(v4_commands)}
            except Exception as exc:
                return {"success": False, "error": str(exc)}

        self._add_tool(
            "convert_v5_to_v4",
            "Convert V5.0 ULTRA command to V4.0 format",
            {"v5_command": {"type": "string"}},
            convert_v5_to_v4,
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
                    "batch": "B:[CMD1]|[CMD2]|[CMD3]",
                },
                "examples": [
                    {"v5": "C;P:FIB", "description": "Code Python Fibonacci"},
                    {"v5": "T;P;R:FIB", "description": "Test Python (Robust) Fibonacci"},
                    {"v5": "B:[D:SUM]|[C;P:FIB]|[E;C:WHY]",
                     "description": "Batch: Document + Code + Explain"},
                ],
            }

        self._add_tool("get_v5_reference",
                       "Get V5.0 ULTRA syntax reference", {}, get_v5_reference)

        async def benchmark_v5(examples: List[Dict[str, str]]) -> Dict[str, Any]:
            """Run V5 benchmark."""
            try:
                results = []
                total_natural_tokens = 0
                total_v5_tokens = 0
                for example in examples:
                    stats = self.parser.calculate_token_reduction(
                        example["natural"], example["v5"]
                    )
                    results.append(stats)
                    total_natural_tokens += stats["natural_tokens"]
                    total_v5_tokens += stats["v5_tokens"]
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
                        "average_reduction_percent": avg_reduction,
                    },
                }
            except Exception as exc:
                return {"success": False, "error": str(exc)}

        self._add_tool(
            "benchmark_v5",
            "Run benchmark comparing natural language to V5.0 ULTRA",
            {"examples": {"type": "array"}},
            benchmark_v5,
        )

    async def start(self, transport: str = "stdio") -> None:
        """Start the MCP server."""
        await self.server.run(transport)


def create_server() -> CompTextMCPServer:
    """Create and return a new CompText MCP server instance."""
    return CompTextMCPServer()


def main() -> None:
    """Main entry point for MCP server."""
    if not MCP_AVAILABLE:
        print("Error: MCP package not installed")
        print("Install with: pip install mcp")
        sys.exit(1)

    server = create_server()
    print("CompText V5.0 ULTRA MCP Server")
    print("Listening on stdio...")
    asyncio.run(server.start("stdio"))


if __name__ == "__main__":
    main()
