"""Read-only CompText Codex catalog server (MCP stdio, research profile).

This MCP server provides discovery and inspection only. No command execution,
filesystem mutations, approval grants, signed identity, or Notion dependency.
The caller must pin the expected SHA-256 from the separately reviewed catalog.
"""
from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

from .catalog_index import (
    open_search_index, search_catalog, lookup_catalog, CatalogIndexError
)


mcp = FastMCP("comptext-codex-catalog-research")


def _source():
    path=os.environ.get("COMPTEXT_CODEX_INDEX_PATH")
    expected=os.environ.get("COMPTEXT_CODEX_EXPECTED_SHA256")
    if not path or not expected:
        raise CatalogIndexError("missing pinned index configuration")
    return path,expected


@mcp.tool()
def catalog_stats() -> dict:
    """List counts and review status of the non-executable command catalog."""
    try:
        path,expected=_source()
        with open_search_index(path,expected_catalog_sha256=expected) as db:
            total=db.execute("SELECT count(*) FROM commands").fetchone()[0]
            approved=db.execute(
                "SELECT count(*) FROM commands WHERE quality='unreviewed'"
            ).fetchone()[0]
            quarantined=total-approved
        return {
            "status":"available",
            "commands_total":total,
            "unreviewed_commands":approved,
            "quarantined_commands":quarantined,
            "executable_commands":0,
            "runtime_authority":False,
        }
    except (CatalogIndexError,ValueError):
        return {"status":"unavailable","executable_commands":0}


@mcp.tool()
def catalog_search(query: str, limit: int=5) -> dict:
    """Search human-readable unreviewed definitions; never executes a command."""
    try:
        if type(limit) is not int or not 1<=limit<=20:
            return {"status":"invalid_query","results":[]}
        path,expected=_source()
        with open_search_index(path,expected_catalog_sha256=expected) as db:
            rows=search_catalog(db,query,limit=limit)
        return {
            "status":"available",
            "results":rows,
            "runtime_authority":False,
        }
    except (CatalogIndexError,ValueError):
        return {"status":"unavailable","results":[]}


@mcp.tool()
def catalog_lookup(module: str, command: str) -> dict:
    """Inspect one uniquely identifiable command without tool permissions."""
    try:
        path,expected=_source()
        with open_search_index(path,expected_catalog_sha256=expected) as db:
            entry=lookup_catalog(db,module=module,command=command)
        if entry is None:
            return {"found":False,"reason":"UNAVAILABLE_OR_AMBIGUOUS"}
        return {"found":True,"record":entry}
    except (CatalogIndexError,ValueError):
        return {"found":False,"reason":"UNAVAILABLE_OR_AMBIGUOUS"}


if __name__=="__main__":
    mcp.run(transport="stdio")
