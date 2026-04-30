"""Tests for CompText MCP Server.

MCP_AVAILABLE is patched to True for every test via the autouse fixture so
these tests always run — no skips, regardless of whether the mcp package
is installed in the test environment.

Note: the old `Server` mock is intentionally removed — the module no longer
exposes a `Server` symbol after the FastMCP refactor.  Only MCP_AVAILABLE
needs patching for environments where mcp is not installed.
"""
import pytest
from unittest.mock import MagicMock


@pytest.fixture(autouse=True)
def mock_mcp(monkeypatch):
    """Patch MCP_AVAILABLE=True for every test."""
    monkeypatch.setattr("comptext_codex.mcp_server_v5.MCP_AVAILABLE", True)


from comptext_codex.mcp_server_v5 import CompTextMCPServer, create_server  # noqa: E402


class TestMCPServer:
    """Test cases for CompText MCP Server."""

    def test_server_initialization(self):
        """Test server initialises correctly."""
        server = CompTextMCPServer()
        assert server is not None
        assert server.parser is not None

    def test_list_tools(self):
        """Test listing available tools."""
        server = CompTextMCPServer()
        tools = server.list_tools()

        assert isinstance(tools, list)
        assert len(tools) > 0
        assert all("name" in tool for tool in tools)
        assert all("description" in tool for tool in tools)

    def test_call_tool(self):
        """Test calling a tool."""
        server = CompTextMCPServer()
        result = server.call_tool("parse_v5", {"command": "C;P:FIB"})

        assert "success" in result
        assert result["success"] is True
        assert "result" in result

    def test_call_nonexistent_tool(self):
        """Test calling non-existent tool raises ValueError."""
        server = CompTextMCPServer()

        with pytest.raises(ValueError, match="Unknown tool"):
            server.call_tool("nonexistent_tool", {})

    def test_handle_tools_list_request(self):
        """Test handling tools/list request."""
        server = CompTextMCPServer()
        response = server.handle_request("tools/list", {})

        assert "tools" in response
        assert isinstance(response["tools"], list)

    def test_handle_tools_call_request(self):
        """Test handling tools/call request."""
        server = CompTextMCPServer()
        response = server.handle_request(
            "tools/call",
            {"name": "parse_v5", "arguments": {"command": "C;P:FIB"}},
        )

        assert "success" in response
        assert response["success"] is True

    def test_handle_initialize_request(self):
        """Test handling initialize request."""
        server = CompTextMCPServer()
        response = server.handle_request("initialize", {})

        assert "protocolVersion" in response
        assert "serverInfo" in response
        assert "capabilities" in response

    def test_handle_unknown_method(self):
        """Test handling unknown method returns error."""
        server = CompTextMCPServer()
        response = server.handle_request("unknown_method", {})

        assert "error" in response

    def test_create_server_factory(self):
        """Test server factory function."""
        server = create_server()
        assert isinstance(server, CompTextMCPServer)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
