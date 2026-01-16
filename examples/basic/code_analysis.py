#!/usr/bin/env python
"""Example 2: Code Analysis

Demonstrates performance bottleneck detection using CompText.
"""

from comptext_codex.executor import CompTextExecutor


def main():
    """Run code analysis example."""
    executor = CompTextExecutor()

    # Sample code with performance issues
    code = """
def process_data(items):
    result = []
    for item in items:
        for other in items:
            if item != other:
                result.append(item + other)
    return result
"""

    print("=" * 60)
    print("CODE ANALYSIS EXAMPLE")
    print("=" * 60)
    print("Code to analyze:")
    print(code)
    print()

    # CompText command
    command = "@CODE_ANALYZE[perf_bottleneck, complexity]"
    print(f"CompText Command: {command}")
    print()

    # Execute with code context
    results = executor.execute(command, context={'code': code})

    print("=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)
    if results and results[0].success:
        import json
        print(json.dumps(results[0].result, indent=2))
    else:
        print(f"Error: {results[0].error if results else 'Unknown error'}")


if __name__ == "__main__":
    main()
