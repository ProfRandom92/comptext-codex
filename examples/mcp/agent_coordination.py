"""Example: Multi-agent coordination with Module M.

Demonstrates MCP (Model Context Protocol) integration.
"""

from comptext_codex import execute
import json


def main():
    """Configure multi-agent systems."""

    print("=== MCP Agent Coordination Examples ===\n")

    # Example 1: Agent messaging
    print("1. Agent Messaging:")
    result = execute("@AGENT_MSG[target=analyzer, message='Process data', priority=high]")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 2: Tool routing
    print("2. Tool Routing:")
    result = execute("@TOOL_ROUTE[tools=['search','calculate','format'], strategy=parallel]")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 3: Workflow orchestration
    print("3. Workflow Orchestration:")
    result = execute("@WORKFLOW[agents=['data_agent','ml_agent','output_agent'], coordination=sequential]")
    print(json.dumps(result[0].result, indent=2))
    print()


if __name__ == "__main__":
    main()
