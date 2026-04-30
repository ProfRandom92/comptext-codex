"""Real subprocess-based MCP integration tests.

These tests start mcp_server_v5.py as an actual child process and communicate
via the stdio transport — no mocks, no fakes.  They complement (not replace)
the unit-test mocks in test_mcp_server.py that verify parser / business logic.

Run with:  pytest tests/test_mcp_integration.py -v
Skipped automatically when mcp[cli] is not installed.
"""

import json
import sys

import pytest

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    _SERVER_PARAMS = StdioServerParameters(
        command=sys.executable,
        args=["-m", "comptext_codex.mcp_server_v5"],
    )
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    _SERVER_PARAMS = None  # type: ignore[assignment]


pytestmark = pytest.mark.skipif(
    not MCP_AVAILABLE,
    reason="mcp[cli] package not installed — skipping real-transport integration tests",
)

_EXPECTED_TOOLS = {
    "parse_v5",
    "encode_v5",
    "encode_batch_v5",
    "calculate_token_reduction",
    "convert_v5_to_v4",
    "get_v5_reference",
    "benchmark_v5",
}


@pytest.mark.asyncio
async def test_initialize_returns_correct_server_info() -> None:
    """Server must respond to initialize with correct name and version."""
    async with stdio_client(_SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            result = await session.initialize()
    assert result.serverInfo.name == "comptext-v5-ultra"
    assert result.serverInfo.version == "5.0.0"


@pytest.mark.asyncio
async def test_list_tools_contains_all_expected_tools() -> None:
    """All seven CompText tools must be advertised by the server."""
    async with stdio_client(_SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools_response = await session.list_tools()
    tool_names = {t.name for t in tools_response.tools}
    missing = _EXPECTED_TOOLS - tool_names
    assert not missing, f"Tools missing from server: {missing}"


@pytest.mark.asyncio
async def test_call_parse_v5_simple_command() -> None:
    """parse_v5 must parse 'C;P:FIB' correctly over real stdio transport."""
    async with stdio_client(_SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("parse_v5", {"command": "C;P:FIB"})
    data = json.loads(result.content[0].text)
    assert data["success"] is True
    assert data["count"] >= 1
    cmd = data["commands"][0]
    assert cmd["command_char"] == "C", f"Expected command_char='C', got {cmd['command_char']!r}"
    assert cmd["language_char"] == "P", f"Expected language_char='P', got {cmd['language_char']!r}"
    assert cmd["task"] == "FIB", f"Expected task='FIB', got {cmd['task']!r}"


@pytest.mark.asyncio
async def test_call_parse_v5_batch_command() -> None:
    """parse_v5 must handle a batch command string."""
    async with stdio_client(_SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "parse_v5", {"command": "B:[D:SUM]|[C;P:FIB]|[E;C:WHY]"}
            )
    data = json.loads(result.content[0].text)
    assert data["success"] is True
    assert data["count"] == 3


@pytest.mark.asyncio
async def test_call_get_v5_reference_returns_full_catalogue() -> None:
    """get_v5_reference must return version and non-empty command/language/modifier dicts."""
    async with stdio_client(_SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("get_v5_reference", {})
    data = json.loads(result.content[0].text)
    assert data["success"] is True
    assert data["version"] == "5.0.0"
    assert len(data["commands"]) > 0
    assert len(data["languages"]) > 0
    assert len(data["modifiers"]) > 0


@pytest.mark.asyncio
async def test_call_tool_unknown_tool_returns_error() -> None:
    """Calling a nonexistent tool must return an error, not crash the server."""
    async with stdio_client(_SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            with pytest.raises(Exception):
                await session.call_tool("nonexistent_tool", {})
