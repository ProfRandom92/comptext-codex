"""Example: Database schema design with Module H.

Demonstrates schema design and optimization.
"""

from comptext_codex import execute
import json


def main():
    """Design database schemas."""

    print("=== Database Schema Examples ===\n")

    # Example 1: Schema design
    print("1. Schema Design:")
    result = execute("@DB_SCHEMA[tables=['users','posts','comments'], relationships=true, indexes=auto]")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 2: Query optimization
    print("2. Query Optimization:")
    query = "SELECT * FROM users WHERE email LIKE '%@example.com%'"
    result = execute(f"@QUERY_OPT[analyze=true, suggest_indexes=true] {query}")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 3: Migration generation
    print("3. Migration Generation:")
    result = execute("@DB_MIGRATION[from_schema=v1, to_schema=v2, preserve_data=true]")
    print(json.dumps(result[0].result, indent=2))
    print()


if __name__ == "__main__":
    main()
