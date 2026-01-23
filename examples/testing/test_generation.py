"""Example: Automated test generation with Module G.

Demonstrates test generation and coverage analysis.
"""

from comptext_codex import execute
import json


def main():
    """Generate automated tests."""

    print("=== Test Generation Examples ===\n")

    # Example 1: Unit test generation
    print("1. Unit Test Generation:")
    function_code = """
def calculate_total(items):
    return sum(item['price'] for item in items)
"""
    result = execute(f"@TEST_GEN[type=unit, framework=pytest, coverage=branch] {function_code}")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 2: Integration test generation
    print("2. Integration Test Generation:")
    result = execute("@TEST_GEN[type=integration, framework=pytest, fixtures=true]")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 3: Coverage analysis
    print("3. Coverage Analysis:")
    result = execute("@COVERAGE[target=80, report_format=html, include_branches=true]")
    print(json.dumps(result[0].result, indent=2))
    print()


if __name__ == "__main__":
    main()
