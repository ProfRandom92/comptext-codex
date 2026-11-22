"""CompText V5 legacy compatibility MCP server, strictly read-only.

The old module used an API that never matched the installed MCP SDK,
and printed a protocol-breaking banner to stdout. This implementation
supports MCP SDK 1.x, preserves legacy read-only tool names, and NEVER
executes arbitrary agent commands or promotes syntax to authorization.
"""
from __future__ import annotations

from typing import Any
from mcp.server.fastmcp import FastMCP

from .parser_v5 import CompTextParserV5

MAX_INPUT = 16384
MAX_BATCH = 100


class _ReadOnlyExecutor:
    """Compatibility boundary: no execution capability is exposed."""

    def execute(self, *_: Any, **__: Any) -> None:
        raise PermissionError("legacy Codex MCP is read-only")


class CompTextMCPServer:
    """Compat layer with seven read-only V5 tools and a working stdio server."""

    def __init__(self) -> None:
        self.parser = CompTextParserV5()
        self.executor = _ReadOnlyExecutor()
        self.server = FastMCP("comptext-v5-compat-readonly")
        self._callbacks: dict[str, Any] = {}
        self._register_tools()

    def _registered(self, name: str, function: Any) -> None:
        self._callbacks[name] = function

    def _safe_parse(self, command: str) -> dict[str, Any]:
        if type(command) is not str or not 1 <= len(command) <= MAX_INPUT:
            return {"success": False, "reason": "INVALID_COMMAND", "can_execute": False}
        if any(ord(x) < 32 for x in command):
            return {"success": False, "reason": "INVALID_CONTROL_CHAR", "can_execute": False}
        try:
            parsed = self.parser.parse(command)
        except (ValueError, TypeError, IndexError):
            return {"success": False, "reason": "INVALID_COMMAND", "can_execute": False}
        if not parsed or len(parsed) > MAX_BATCH or any(x.command not in self.parser.COMMANDS for x in parsed):
            return {"success": False, "reason": "UNKNOWN_OPCODE", "can_execute": False}
        for item in parsed:
            # The historic parser silently ignores unknown/duplicated tokens.
            # Such lossy normalization must not be treated as a valid command.
            parts = item.raw.split(":", 1)[0].split(";")
            if not parts or parts[0] != item.command:
                return {"success": False, "reason": "UNKNOWN_OPCODE", "can_execute": False}
            seen_language = False
            for part in parts[1:]:
                if part in self.parser.LANGUAGES and not seen_language:
                    seen_language = True
                elif part in self.parser.MODIFIERS:
                    continue
                else:
                    return {"success": False, "reason": "UNKNOWN_OR_DUPLICATE_TOKEN", "can_execute": False}
        return {
            "success": True,
            "commands": [
                {
                    "command": self.parser.COMMANDS[x.command],
                    "command_char": x.command,
                    "language": self.parser.LANGUAGES.get(x.language) if x.language else None,
                    "modifiers": [self.parser.MODIFIERS.get(m, m) for m in x.modifiers],
                    "task": x.task,
                    "raw": x.raw,
                }
                for x in parsed
            ],
            "can_execute": False,
            "authorization": "EXTERNAL_VERIFIER_REQUIRED",
        }

    def _safe_encode(
        self, command: str, language: str | None = None,
        modifiers: list[str] | None = None,
        task: str | None = None,
    ) -> dict[str, Any]:
        if type(command) is not str or command.upper() not in self.parser.COMMANDS_REV:
            return {"success": False, "reason": "UNKNOWN_OPCODE", "can_execute": False}
        if language is not None and (
            type(language) is not str or language.upper() not in self.parser.LANGUAGES_REV
        ):
            return {"success": False, "reason": "UNKNOWN_LANGUAGE", "can_execute": False}
        if modifiers is not None and (
            type(modifiers) is not list or len(modifiers)>16 or
            any(type(x) is not str or x.upper() not in self.parser.MODIFIERS_REV for x in modifiers)
        ):
            return {"success": False, "reason": "UNKNOWN_MODIFIER", "can_execute": False}
        if task is not None and (
            type(task) is not str or len(task)>1024 or any(ord(x)<32 for x in task)
        ):
            return {"success": False, "reason": "INVALID_TASK", "can_execute": False}
        result=self.parser.encode(
            command.upper(),
            language.upper() if language else None,
            [x.upper() for x in modifiers] if modifiers else None,
            task,
        )
        return {"success": True, "v5_command": result, "can_execute": False}

    def _register_tools(self) -> None:
        @self.server.tool()
        def parse_v5(command: str) -> dict[str, Any]:
            """Parse V5 mnemonic into metadata; no command execution."""
            return self._safe_parse(command)
        self._registered("parse_v5",parse_v5)

        @self.server.tool()
        def encode_v5(
            command: str, language: str | None = None,
            modifiers: list[str] | None = None,
            task: str | None = None,
        ) -> dict[str, Any]:
            """Encode supported V5 mnemonic names as text only."""
            return self._safe_encode(command,language,modifiers,task)
        self._registered("encode_v5",encode_v5)

        @self.server.tool()
        def encode_batch_v5(commands: list[dict[str, Any]]) -> dict[str, Any]:
            """Encode a bounded, validated batch of mnemonics without execution."""
            if type(commands) is not list or not 1 <= len(commands) <= MAX_BATCH:
                return {"success": False, "reason": "INVALID_BATCH", "can_execute": False}
            output=[]
            for item in commands:
                if type(item) is not dict or set(item)-{"command","language","modifiers","task"}:
                    return {"success": False, "reason": "INVALID_BATCH_ENTRY", "can_execute": False}
                value=self._safe_encode(**item)
                if not value["success"]:
                    return value
                output.append(value["v5_command"])
            return {"success": True, "v5_batch":"B:"+"|".join("["+x+"]" for x in output),
                    "count":len(output),"can_execute":False}
        self._registered("encode_batch_v5",encode_batch_v5)

        @self.server.tool()
        def calculate_token_reduction(natural_language: str, v5_command: str) -> dict[str, Any]:
            """Compute BPE token lengths of provided strings, not semantic equivalence."""
            if any(type(x) is not str or len(x)>MAX_INPUT for x in (natural_language,v5_command)):
                return {"success":False,"reason":"INVALID_INPUT","can_execute":False}
            if not self._safe_parse(v5_command)["success"]:
                return {"success":False,"reason":"INVALID_OPCODE","can_execute":False}
            metrics=self.parser.calculate_token_reduction(natural_language,v5_command)
            return {"success":True,"statistics":metrics,"semantic_equivalence_verified":False,
                    "can_execute":False}
        self._registered("calculate_token_reduction",calculate_token_reduction)

        @self.server.tool()
        def convert_v5_to_v4(v5_command: str) -> dict[str, Any]:
            """Return legacy V4 mnemonic strings; no tool execution."""
            parsed=self._safe_parse(v5_command)
            if not parsed["success"]:
                return parsed
            converted=[self.parser.to_v4_format(c) for c in self.parser.parse(v5_command)]
            return {"success":True,"v4_output":converted,"can_execute":False}
        self._registered("convert_v5_to_v4",convert_v5_to_v4)

        @self.server.tool()
        def get_v5_reference() -> dict[str, Any]:
            """Return supported V5 opcode vocabulary, without authority claims."""
            return {
                "success":True,
                "version":"5.0.4-compat",
                "commands":dict(self.parser.COMMANDS),
                "languages":dict(self.parser.LANGUAGES),
                "modifiers":dict(self.parser.MODIFIERS),
                "can_execute":False,
            }
        self._registered("get_v5_reference",get_v5_reference)

        @self.server.tool()
        def benchmark_v5(examples: list[dict[str,str]]) -> dict[str, Any]:
            """Benchmark BPE string lengths; no semantic fidelity assertion."""
            if type(examples) is not list or not 1<=len(examples)<=MAX_BATCH:
                return {"success":False,"reason":"INVALID_BENCHMARK","can_execute":False}
            results=[]
            for item in examples:
                if type(item) is not dict or set(item)!={"natural","v5"}:
                    return {"success":False,"reason":"INVALID_EXAMPLE","can_execute":False}
                measured=calculate_token_reduction(item["natural"],item["v5"])
                if not measured["success"]:
                    return measured
                results.append(measured["statistics"])
            return {"success":True,"count":len(results),"examples":results,
                    "semantic_equivalence_verified":False,"can_execute":False}
        self._registered("benchmark_v5",benchmark_v5)

    def list_tools(self) -> list[dict[str, str]]:
        return [{"name":t.name,"description":t.description or ""}
                for t in self.server._tool_manager.list_tools()]

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Local compatibility helper, explicitly no external tool execution."""
        fn=self._callbacks.get(name)
        if fn is None:
            raise ValueError("unknown read-only tool")
        if type(arguments) is not dict:
            return {"success":False,"result":None,"can_execute":False}
        try:
            payload=fn(**arguments)
            return {"success":bool(payload.get("success")), "result":payload,"can_execute":False}
        except (TypeError,ValueError,KeyError) as exc:
            return {"success":False,"result":None,"reason":"INVALID_ARGUMENTS",
                    "can_execute":False}

    def handle_request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        """Legacy test adapter. Actual MCP JSON-RPC is owned by FastMCP."""
        if method=="tools/list":
            return {"tools":self.list_tools()}
        if method=="tools/call":
            return self.call_tool(params.get("name",""),params.get("arguments",{}))
        if method=="initialize":
            return {"protocolVersion":"2025-06-18",
                    "serverInfo":{"name":"comptext-v5-compat-readonly","version":"5.0.4"},
                    "capabilities":{"tools":{"listChanged":False}}}
        return {"error":{"code":-32601,"message":"Method not found"}}

    async def start(self, transport: str="stdio") -> None:
        if transport!="stdio":
            raise ValueError("only stdio supported")
        await self.server.run_stdio_async()


def create_server() -> CompTextMCPServer:
    return CompTextMCPServer()


def main() -> None:
    """MCP stdio CLI entrypoint. Write no banners or debug output to stdout."""
    create_server().server.run(transport="stdio")


if __name__=="__main__":
    main()
