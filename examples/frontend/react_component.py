#!/usr/bin/env python
"""Example 12: React Component Generation

Demonstrates UI component generation with TypeScript and tests.
"""

from comptext_codex.executor import CompTextExecutor
import json


def main():
    """Run React component generation example."""
    executor = CompTextExecutor()

    print("=" * 60)
    print("REACT COMPONENT GENERATION")
    print("=" * 60)

    # CompText command
    command = """@COMPONENT[framework=react, styling=tailwind, typescript=true, props_validation=true, tests=jest, accessibility=wcag_aa]"""

    print(f"Command: {command}")
    print()
    print("Generates:")
    print("- UserCard.tsx - Component implementation")
    print("- UserCard.test.tsx - Jest unit tests")
    print("- UserCard.stories.tsx - Storybook stories")
    print()

    # Component specification
    spec = {
        'name': 'UserCard',
        'props': ['name', 'email', 'avatar', 'role'],
        'actions': ['onEdit', 'onDelete'],
        'variants': ['default', 'compact', 'detailed']
    }

    # Execute
    results = executor.execute(command, context={'spec': spec})

    print("=" * 60)
    print("GENERATION RESULTS")
    print("=" * 60)
    if results and results[0].success:
        print(json.dumps(results[0].result, indent=2))
    else:
        print(f"Error: {results[0].error if results else 'Unknown error'}")


if __name__ == "__main__":
    main()
