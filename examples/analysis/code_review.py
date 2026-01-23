"""Example: Automated code review with Module B.

Demonstrates code analysis capabilities for quality assessment.
"""

from comptext_codex import execute


def main():
    """Perform automated code review."""

    print("=== Code Review Examples ===\n")

    # Sample code for analysis
    sample_code = """
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
"""

    # Example 1: Complexity analysis
    print("1. Complexity Analysis:")
    result = execute(f"@B:analyze[complexity, maintainability] {sample_code}")
    print(result[0].result)
    print()

    # Example 2: Performance analysis
    print("2. Performance Analysis:")
    result = execute(f"@B:analyze[performance, memory] {sample_code}")
    print(result[0].result)
    print()

    # Example 3: Security analysis
    print("3. Security Scan:")
    vulnerable_code = "query = 'SELECT * FROM users WHERE id = ' + user_input"
    result = execute(f"@SEC_SCAN[owasp_top10=true] {vulnerable_code}")
    print(result[0].result)
    print()


if __name__ == "__main__":
    main()
