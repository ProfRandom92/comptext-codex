"""Tests for MCP Server."""

import pytest
from comptext_mcp.server import CompTextMCPServer, create_server


class TestMCPServer:
    """Test cases for CompText MCP Server."""

    def test_server_initialization(self):
        """Test server initializes correctly."""
        server = CompTextMCPServer()
        assert server is not None
        assert server.parser is not None
        assert server.executor is not None

    def test_list_tools(self):
        """Test listing available tools."""
        server = CompTextMCPServer()
        tools = server.list_tools()

        assert isinstance(tools, list)
        assert len(tools) > 0
        assert all('name' in tool for tool in tools)
        assert all('description' in tool for tool in tools)

    def test_call_tool(self):
        """Test calling a tool."""
        server = CompTextMCPServer()

        # Get first available tool
        tools = server.list_tools()
        if tools:
            tool_name = tools[0]['name']
            result = server.call_tool(tool_name, {'command': '@A:compress test text'})

            assert 'success' in result
            assert 'result' in result

    def test_call_nonexistent_tool(self):
        """Test calling non-existent tool raises error."""
        server = CompTextMCPServer()

        with pytest.raises(ValueError):
            server.call_tool('nonexistent_tool', {})

    def test_handle_tools_list_request(self):
        """Test handling tools/list request."""
        server = CompTextMCPServer()
        response = server.handle_request('tools/list', {})

        assert 'tools' in response
        assert isinstance(response['tools'], list)

    def test_handle_tools_call_request(self):
        """Test handling tools/call request."""
        server = CompTextMCPServer()
        tools = server.list_tools()

        if tools:
            tool_name = tools[0]['name']
            response = server.handle_request('tools/call', {
                'name': tool_name,
                'arguments': {'command': '@A:compress text'}
            })

            assert 'success' in response

    def test_handle_initialize_request(self):
        """Test handling initialize request."""
        server = CompTextMCPServer()
        response = server.handle_request('initialize', {})

        assert 'protocolVersion' in response
        assert 'serverInfo' in response
        assert 'capabilities' in response

    def test_handle_unknown_method(self):
        """Test handling unknown method."""
        server = CompTextMCPServer()
        response = server.handle_request('unknown_method', {})

        assert 'error' in response

    def test_create_server_factory(self):
        """Test server factory function."""
        server = create_server()
        assert isinstance(server, CompTextMCPServer)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
