#!/usr/bin/env python
"""Example 6: API Documentation Generation

Demonstrates automatic generation of OpenAPI specifications and API documentation.
"""

from comptext_codex.executor import CompTextExecutor
import json


def main():
    """Run API documentation generation example."""
    executor = CompTextExecutor()

    print("=" * 60)
    print("API DOCUMENTATION GENERATION")
    print("=" * 60)

    # API specification
    api_spec = {
        'endpoints': [
            {'path': '/users', 'method': 'GET', 'description': 'List all users'},
            {'path': '/users/{id}', 'method': 'GET', 'description': 'Get user by ID'},
            {'path': '/users', 'method': 'POST', 'description': 'Create new user'},
        ],
        'models': [
            {'name': 'User', 'fields': ['id', 'name', 'email', 'created_at']}
        ]
    }

    # CompText command
    command = """@DOC_GENERATE[format=openapi, version=3.0, include_examples=true]"""

    print(f"Command: {command}")
    print()
    print("Spec:")
    print(json.dumps(api_spec, indent=2))
    print()

    # Execute
    results = executor.execute(command, context={'api_spec': api_spec})

    print("=" * 60)
    print("GENERATED DOCUMENTATION")
    print("=" * 60)
    if results and results[0].success:
        print(json.dumps(results[0].result, indent=2))
    else:
        print(f"Error: {results[0].error if results else 'Unknown error'}")

    print()
    print("Token Savings vs Natural Language:")
    print("Natural Language: ~45 tokens")
    print("CompText: ~12 tokens")
    print("Savings: ~73%")


if __name__ == "__main__":
    main()
