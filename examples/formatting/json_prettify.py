"""Example: JSON formatting and prettification.

Demonstrates Module C JSON formatting capabilities.
"""

from comptext_codex import execute


def main():
    """Demonstrate JSON formatting."""

    print("=== JSON Formatting Examples ===\n")

    # Example 1: Basic JSON formatting
    print("1. Basic JSON:")
    result = execute("@C:json[indent=2] {\"name\": \"CompText\", \"version\": \"3.5.0\"}")
    print(result[0].result)
    print()

    # Example 2: Sorted keys
    print("2. Sorted JSON:")
    result = execute("@C:json[indent=2, sort_keys=true] {\"z_field\": 1, \"a_field\": 2, \"m_field\": 3}")
    print(result[0].result)
    print()

    # Example 3: Auto-detect and prettify
    print("3. Auto-prettify:")
    result = execute("@C:prettify[type=auto] {\"data\": [1, 2, 3]}")
    print(result[0].result)
    print()


if __name__ == "__main__":
    main()
