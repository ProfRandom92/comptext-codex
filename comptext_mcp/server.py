"""MCP Server implementation for CompText DSL."""

import json
from typing import Any, Dict, List, Optional
import logging

from comptext_codex.parser import CompTextParser
from comptext_codex.executor import CompTextExecutor
from comptext_codex.kvtc import KVTCCompressor

logger = logging.getLogger(__name__)


class CompTextMCPServer:
    """MCP Server for CompText DSL commands.

    Provides Model Context Protocol interface for CompText commands,
    enabling multi-agent communication and tool routing.
    """

    def __init__(self, codex_dir: Optional[str] = None):
        """Initialize MCP server.

        Args:
            codex_dir: Path to codex directory
        """
        self.codex_dir = codex_dir
        self.parser = CompTextParser(codex_dir=codex_dir)
        self.executor = CompTextExecutor(codex_dir=codex_dir)
        self.kvtc = KVTCCompressor()
        self.tools: Dict[str, Dict[str, Any]] = {}
        self._register_tools()

    def _register_tools(self):
        """Register CompText commands as MCP tools."""
        commands = self.executor.get_available_commands()

        for cmd in commands:
            tool_name = f"comptext_{cmd['module'].lower()}_{cmd['command']}"
            self.tools[tool_name] = {
                'name': tool_name,
                'description': cmd.get('description', f"Execute {cmd['command']}"),
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'command': {
                            'type': 'string',
                            'description': f"CompText command: {cmd.get('syntax', '')}"
                        },
                        'context': {
                            'type': 'object',
                            'description': 'Execution context'
                        }
                    },
                    'required': ['command']
                },
                'module': cmd['module'],
                'command': cmd['command']
            }

        # Register KVTC-based compress_content tool
        self.tools['compress_content'] = {
            'name': 'compress_content',
            'description': (
                'Compress content using the KVTC strategy. '
                'Preserves system instructions (Attention Sinks at the start) '
                'and recent context (Sliding Window at the end) while '
                'compressing the middle section.'
            ),
            'input_schema': {
                'type': 'object',
                'properties': {
                    'text': {
                        'type': 'string',
                        'description': 'Text content to compress'
                    }
                },
                'required': ['text']
            },
            'module': 'A',
            'command': 'compress_content'
        }

    def list_tools(self) -> List[Dict[str, Any]]:
        """List available MCP tools.

        Returns:
            List of tool definitions
        """
        return list(self.tools.values())

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an MCP tool.

        Uses the KVTC strategy by default for ``compress_content``, which
        preserves system instructions (Sinks) and recent context (Window).

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments including 'command' and optional 'context'

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool not found
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")

        # Handle compress_content via KVTC compressor
        if tool_name == 'compress_content':
            text = arguments.get('text', '')
            try:
                compressed = self.kvtc.compress(text)
                return {
                    'success': True,
                    'result': compressed,
                    'error': None,
                    'metadata': {'strategy': 'kvtc'}
                }
            except Exception as e:
                logger.error("Error in compress_content: %s", e)
                return {
                    'success': False,
                    'result': None,
                    'error': str(e)
                }

        command = arguments.get('command', '')
        context = arguments.get('context', {})

        try:
            results = self.executor.execute(command, context=context)

            # Return first result for single commands
            if len(results) == 1:
                result = results[0]
                return {
                    'success': result.success,
                    'result': result.result,
                    'error': result.error,
                    'metadata': result.metadata
                }

            # Return all results for chained commands
            return {
                'success': all(r.success for r in results),
                'results': [
                    {
                        'success': r.success,
                        'result': r.result,
                        'error': r.error,
                        'metadata': r.metadata
                    }
                    for r in results
                ],
                'chain_length': len(results)
            }

        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {
                'success': False,
                'result': None,
                'error': str(e)
            }

    def handle_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP protocol request.

        Args:
            method: MCP method name (e.g., 'tools/list', 'tools/call')
            params: Method parameters

        Returns:
            Response dictionary
        """
        if method == 'tools/list':
            return {
                'tools': self.list_tools()
            }

        elif method == 'tools/call':
            tool_name = params.get('name')
            arguments = params.get('arguments', {})

            if not tool_name:
                return {
                    'error': 'Missing tool name'
                }

            try:
                result = self.call_tool(tool_name, arguments)
                return result
            except Exception as e:
                return {
                    'error': str(e)
                }

        elif method == 'initialize':
            return {
                'protocolVersion': '1.0',
                'serverInfo': {
                    'name': 'CompText MCP Server',
                    'version': '1.0.0'
                },
                'capabilities': {
                    'tools': {
                        'listChanged': False
                    }
                }
            }

        else:
            return {
                'error': f'Unknown method: {method}'
            }

    def start(self, host: str = '0.0.0.0', port: int = 8765):
        """Start MCP server (stub for future implementation).

        Args:
            host: Server host
            port: Server port
        """
        logger.info(f"CompText MCP Server would start on {host}:{port}")
        logger.info(f"Registered {len(self.tools)} tools")

        # In a real implementation, this would start a WebSocket or HTTP server
        # For now, this is a synchronous API that can be used directly
        pass


def create_server(codex_dir: Optional[str] = None) -> CompTextMCPServer:
    """Factory function to create MCP server instance.

    Args:
        codex_dir: Path to codex directory

    Returns:
        CompTextMCPServer instance
    """
    return CompTextMCPServer(codex_dir=codex_dir)
