"""CompText V5.0 ULTRA MCP Server — FastMCP Edition."""

import asyncio
import sys
from typing import Any, Callable, Dict, List, Optional

try:
    from mcp.server.fastmcp import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

    class FastMCP:  # type: ignore[no-redef]
        def __init__(self, *a: Any, **kw: Any) -> None: pass

        def tool(self, *a: Any, **kw: Any) -> Callable:
            def decorator(fn: Callable) -> Callable:
                return fn
            return decorator

        def run(self, transport: str = "stdio") -> None: pass

from .parser_v5 import CompTextParserV5, CompTextCommandV5

# ---------------------------------------------------------------------------
# Module-level FastMCP instance — used by stdio transport / Hermes / real MCP
# ---------------------------------------------------------------------------
mcp = FastMCP("comptext-v5-ultra")
_parser = CompTextParserV5()


@mcp.tool()
async def parse_v5(command: str) -> Dict[str, Any]:
    """Parse a CompText V5.0 ULTRA command into structured format."""
    try:
        results = _parser.parse(command)
        commands = []
        for cmd in results:
            commands.append({
                "command": _parser.COMMANDS.get(cmd.command, cmd.command),
                "command_char": cmd.command,
                "language": _parser.LANGUAGES.get(cmd.language, cmd.language) if cmd.language else None,
                "language_char": cmd.language,
                "modifiers": [_parser.MODIFIERS.get(m, m) for m in cmd.modifiers] if cmd.modifiers else [],
                "modifier_chars": cmd.modifiers,
                "task": cmd.task,
                "raw": cmd.raw,
            })
        return {"success": True, "count": len(commands), "commands": commands}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


@mcp.tool()
async def encode_v5(
    command: str,
    language: Optional[str] = None,
    modifiers: Optional[List[str]] = None,
    task: Optional[str] = None,
) -> Dict[str, Any]:
    """Encode a command to V5.0 ULTRA format."""
    try:
        result = _parser.encode(
            command.upper(),
            language.upper() if language else None,
            [m.upper() for m in modifiers] if modifiers else None,
            task,
        )
        return {
            "success": True,
            "v5_command": result,
            "input": {"command": command, "language": language, "modifiers": modifiers, "task": task},
        }
    except Exception as exc:
        return {"success": False, "error": str(exc)}


@mcp.tool()
async def encode_batch_v5(commands: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Encode multiple commands to V5.0 ULTRA batch format."""
    try:
        batch_input = [
            (
                c.get("command", "").upper(),
                c.get("language", "").upper() if c.get("language") else None,
                [m.upper() for m in c.get("modifiers", [])] if c.get("modifiers") else None,
                c.get("task"),
            )
            for c in commands
        ]
        result = _parser.encode_batch(batch_input)
        return {"success": True, "v5_batch": result, "count": len(commands)}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


@mcp.tool()
async def calculate_token_reduction(natural_language: str, v5_command: str) -> Dict[str, Any]:
    """Calculate token reduction statistics for V5.0 ULTRA."""
    try:
        stats = _parser.calculate_token_reduction(natural_language, v5_command)
        return {"success": True, "statistics": stats}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


@mcp.tool()
async def convert_v5_to_v4(v5_command: str) -> Dict[str, Any]:
    """Convert V5.0 ULTRA command to V4.0 format."""
    try:
        results = _parser.parse(v5_command)
        v4_commands = [_parser.to_v4_format(cmd) for cmd in results]
        return {"success": True, "v5_input": v5_command, "v4_output": v4_commands, "count": len(v4_commands)}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


@mcp.tool()
async def get_v5_reference() -> Dict[str, Any]:
    """Get V5.0 ULTRA syntax reference and command catalogue."""
    return {
        "success": True,
        "version": "5.0.0",
        "commands": dict(_parser.COMMANDS),
        "languages": dict(_parser.LANGUAGES),
        "modifiers": dict(_parser.MODIFIERS),
        "syntax": {
            "simple": "CMD;LANG:TASK",
            "with_modifiers": "CMD;LANG;MOD:TASK",
            "batch": "B:[CMD1]|[CMD2]|[CMD3]",
        },
        "examples": [
            {"v5": "C;P:FIB", "description": "Code Python Fibonacci"},
            {"v5": "T;P;R:FIB", "description": "Test Python (Robust) Fibonacci"},
            {"v5": "B:[D:SUM]|[C;P:FIB]|[E;C:WHY]", "description": "Batch: Document + Code + Explain"},
        ],
    }


@mcp.tool()
async def benchmark_v5(examples: List[Dict[str, str]]) -> Dict[str, Any]:
    """Run benchmark comparing natural language to V5.0 ULTRA commands."""
    try:
        results = []
        total_natural = 0
        total_v5 = 0
        for ex in examples:
            stats = _parser.calculate_token_reduction(ex["natural"], ex["v5"])
            results.append(stats)
            total_natural += stats["natural_tokens"]
            total_v5 += stats["v5_tokens"]
        avg_reduction = round((1 - total_v5 / total_natural) * 100, 1) if total_natural > 0 else 0
        return {
            "success": True,
            "examples": results,
            "aggregate": {
                "total_natural_tokens": total_natural,
                "total_v5_tokens": total_v5,
                "total_saved": total_natural - total_v5,
                "average_reduction_percent": avg_reduction,
            },
        }
    except Exception as exc:
        return {"success": False, "error": str(exc)}


# ---------------------------------------------------------------------------
# CompTextMCPServer — thin class wrapper kept for unit-test backward compat
# ---------------------------------------------------------------------------

_TOOL_FUNCS: Dict[str, Callable] = {
    "parse_v5": parse_v5,
    "encode_v5": encode_v5,
    "encode_batch_v5": encode_batch_v5,
    "calculate_token_reduction": calculate_token_reduction,
    "convert_v5_to_v4": convert_v5_to_v4,
    "get_v5_reference": get_v5_reference,
    "benchmark_v5": benchmark_v5,
}


class CompTextMCPServer:
    """Thin wrapper around the module-level FastMCP instance.

    Exposes the same list_tools / call_tool / handle_request API used by
    existing unit tests so they continue passing without modification.
    The actual MCP transport (stdio) is handled by the module-level `mcp`
    instance — not by this class.
    """

    def __init__(self) -> None:
        """Initialise server wrapper."""
        if not MCP_AVAILABLE:
            raise ImportError(
                "MCP package not installed. Install with: pip install 'mcp[cli]'"
            )
        self.parser = CompTextParserV5()

    # ------------------------------------------------------------------
    # Public API (unchanged — existing unit tests rely on this interface)
    # ------------------------------------------------------------------

    def list_tools(self) -> List[Dict[str, Any]]:
        """Return list of registered tool names."""
        return [{"name": name} for name in _TOOL_FUNCS]

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool by name (synchronous shim for unit tests)."""
        if name not in _TOOL_FUNCS:
            raise ValueError(f"Unknown tool: {name}")
        result = asyncio.run(_TOOL_FUNCS[name](**arguments))
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


def create_server() -> CompTextMCPServer:
    """Create and return a new CompTextMCPServer instance."""
    return CompTextMCPServer()


def main() -> None:
    """Entry point: start MCP server over stdio (required for Hermes Phase 1)."""
    if not MCP_AVAILABLE:
        print("Error: MCP package not installed. Run: pip install 'mcp[cli]'")
        sys.exit(1)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
