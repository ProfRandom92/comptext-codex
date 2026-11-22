"""Actual MCP stdio integration for the non-executable vNext Codex catalog."""
import json
import os
import sys

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from experiments.vnext.catalog import build_catalog,save_catalog
from experiments.vnext.catalog_index import build_search_index
from test_vnext_catalog import fixture as source_fixture


def make_params(tmp_path):
    db,yamls=source_fixture(tmp_path)
    catalog=build_catalog(db,yamls)
    source=tmp_path/"catalog.json"
    index=tmp_path/"index.sqlite"
    save_catalog(catalog,source)
    build_search_index(source,index)
    env={
        **os.environ,
        "COMPTEXT_CODEX_INDEX_PATH":str(index),
        "COMPTEXT_CODEX_EXPECTED_SHA256":catalog["sha256"],
    }
    return StdioServerParameters(
        command=sys.executable,
        args=["-m","experiments.vnext.catalog_mcp_server"],
        env=env,
    )


@pytest.mark.asyncio
async def test_mcp_catalog_service_exposes_only_three_readonly_tools(tmp_path):
    params=make_params(tmp_path)
    async with stdio_client(params) as (read,write):
        async with ClientSession(read,write) as session:
            info=await session.initialize()
            tools=await session.list_tools()
            result=await session.call_tool("catalog_stats",{})
    assert info.serverInfo.name=="comptext-codex-catalog-research"
    assert {x.name for x in tools.tools}=={
        "catalog_stats","catalog_search","catalog_lookup"
    }
    assert result.isError is False
    payload=json.loads(result.content[0].text)
    assert payload["commands_total"]==3
    assert payload["executable_commands"]==0
    assert "database_path" not in payload


@pytest.mark.asyncio
async def test_mcp_catalog_queries_return_only_redacted_metadata_and_never_execute(tmp_path):
    params=make_params(tmp_path)
    async with stdio_client(params) as (read,write):
        async with ClientSession(read,write) as session:
            await session.initialize()
            searched=await session.call_tool("catalog_search",{"query":"summarize"})
            found=await session.call_tool("catalog_lookup",{"module":"A","command":"@sum"})
            ambiguous=await session.call_tool("catalog_lookup",{"module":"J","command":"deploy"})
            suspicious=await session.call_tool("catalog_search",{"query":"'; DROP TABLE commands;--"})
    a=json.loads(searched.content[0].text)
    b=json.loads(found.content[0].text)
    c=json.loads(ambiguous.content[0].text)
    d=json.loads(suspicious.content[0].text)
    assert a["results"][0]["command"]=="@sum"
    assert b["found"] is True
    assert b["record"]["can_execute"] is False
    assert c=={"found":False,"reason":"UNAVAILABLE_OR_AMBIGUOUS"}
    assert d["results"]==[]
    assert not any("approval_ref" in str(x) for x in [a,b,c,d])
