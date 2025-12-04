"""Minimal MCP server placeholder.

The real Model Context Protocol package may not be available in
restricted environments. This module provides a small shim that
explains how to enable MCP support while keeping the package
importable even when the dependency is missing.
"""
from __future__ import annotations

import sys
from typing import Any


def main(argv: list[str] | None = None) -> int:
    try:
        import mcp  # type: ignore
    except Exception:
        sys.stderr.write(
            "The `mcp` package is not installed. Install the optional 'mcp' extra to enable the server.\n"
        )
        return 1

    # If MCP is available, delegate to its CLI entrypoint. This keeps
    # our implementation tiny while still supporting real deployments.
    if hasattr(mcp, "serve"):
        mcp.serve(argv or [])  # type: ignore[attr-defined]
        return 0

    sys.stderr.write("MCP package is present but does not expose a 'serve' helper.\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
