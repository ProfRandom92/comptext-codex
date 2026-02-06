#!/usr/bin/env python3
"""
CompText MCP Server - High-Speed Context Analyzer
Optimized for Claude Agent Teams
"""
import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("CompText Speed Server")


@mcp.tool()
def comptext_analyze(file_path: str, query: str) -> str:
    """
    High-speed file analysis tool for Agent Teams.
    
    Searches a file for lines containing the query string and returns
    ONLY the matching lines with line numbers. This prevents context
    pollution by avoiding full file dumps.
    
    Args:
        file_path: Absolute path to the file to analyze
        query: Search term to find in the file
        
    Returns:
        Formatted results with [FILE:LINE] markers
        
    Example:
        comptext_analyze("/path/to/code.py", "def fibonacci")
        Returns: "[code.py:42] def fibonacci(n):"
    """
    try:
        # Resolve absolute path
        path = Path(file_path).resolve()
        
        if not path.exists():
            return f"❌ Error: File not found: {file_path}"
        
        if not path.is_file():
            return f"❌ Error: Not a file: {file_path}"
        
        # Read and search file
        results = []
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, start=1):
                if query.lower() in line.lower():
                    # Strip but preserve indentation info
                    clean_line = line.rstrip()
                    results.append(f"[{path.name}:{line_num}] {clean_line}")
        
        if not results:
            return f"🔍 No matches found for '{query}' in {path.name}"
        
        # Add summary header
        summary = f"✅ Found {len(results)} match(es) in {path.name}:\n\n"
        return summary + "\n".join(results)
        
    except Exception as e:
        return f"❌ Error analyzing file: {str(e)}"


@mcp.tool()
def comptext_parse(command: str) -> str:
    """
    Parse a CompText protocol command into human-readable format.
    
    Args:
        command: CompText command string (e.g., "C;P:FIB")
        
    Returns:
        Parsed command structure with full descriptions
        
    Example:
        comptext_parse("C;P:FIB")
        Returns: "Command: CODE, Language: PYTHON, Task: FIB"
    """
    try:
        from comptext_codex.parser_v5 import CompTextParserV5
        
        parser = CompTextParserV5()
        result = parser.parse(command)
        
        # Handle list result from parser
        if isinstance(result, list) and len(result) > 0:
            cmd = result[0]
        else:
            return f"❌ Parse Error: Unexpected result format"
        
        # Format output
        output = []
        output.append(f"✅ Parsed CompText Command: {command}")
        output.append(f"   Command: {cmd.command}")
        output.append(f"   Language: {cmd.language}")
        
        if cmd.task:
            output.append(f"   Task: {cmd.task}")
        
        if cmd.modifiers:
            output.append(f"   Modifiers: {', '.join(cmd.modifiers)}")
        
        if cmd.params:
            output.append("   Parameters:")
            for key, value in cmd.params.items():
                output.append(f"     {key}: {value}")
        
        return "\n".join(output)
        
    except ImportError:
        return "❌ Error: comptext_codex not installed. Run: pip install comptext-codex"
    except Exception as e:
        return f"❌ Error parsing command: {str(e)}"


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
