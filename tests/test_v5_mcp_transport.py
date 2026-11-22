"""Real MCP 1.x stdio compatibility and security tests for the V5 CLI."""
import json
import sys
import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@pytest.mark.asyncio
async def test_v5_mcp_cli_starts_on_real_stdio_without_stdout_banner():
    p=StdioServerParameters(command=sys.executable,
                            args=["-m","comptext_codex.mcp_server_v5"])
    async with stdio_client(p) as (read,write):
        async with ClientSession(read,write) as session:
            info=await session.initialize()
            tools=await session.list_tools()
            valid=await session.call_tool("parse_v5",{"command":"C;P:FIB"})
            invalid=await session.call_tool("parse_v5",{"command":"Z;P:EXEC"})
    names={tool.name for tool in tools.tools}
    assert "parse_v5" in names and "encode_v5" in names
    assert all("execute" not in name and "approve" not in name for name in names)
    a=json.loads(valid.content[0].text)
    b=json.loads(invalid.content[0].text)
    assert a["success"] is True
    assert a["commands"][0]["command"]=="CODE"
    assert a["can_execute"] is False
    assert b["success"] is False
    assert info.serverInfo.name=="comptext-v5-compat-readonly"


@pytest.mark.asyncio
async def test_v5_mcp_encoder_refuses_unknown_opcode_instead_of_empty_string():
    p=StdioServerParameters(command=sys.executable,
                           args=["-m","comptext_codex.mcp_server_v5"])
    async with stdio_client(p) as (read,write):
        async with ClientSession(read,write) as session:
            await session.initialize()
            res=await session.call_tool("encode_v5",{"command":"SECRET_ADMIN_DELETE"})
    x=json.loads(res.content[0].text)
    assert x["success"] is False
    assert x["can_execute"] is False
