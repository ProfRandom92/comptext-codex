"""Example: API documentation generation with Module F.

Demonstrates automated documentation generation.
"""

from comptext_codex import execute


def main():
    """Generate API documentation."""

    print("=== Documentation Generation Examples ===\n")

    # Example 1: API documentation
    print("1. API Documentation:")
    api_code = """
@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify(users)
"""
    result = execute(f"@DOC_GEN[format=openapi, style=rest] {api_code}")
    print(result[0].result)
    print()

    # Example 2: Changelog generation
    print("2. Changelog Generation:")
    commits = "feat: add user authentication, fix: resolve memory leak, docs: update README"
    result = execute(f"@CHANGELOG[format=markdown, group_by=type] {commits}")
    print(result[0].result)
    print()

    # Example 3: README generation
    print("3. README Generation:")
    result = execute("@DOC_GEN[format=readme, sections=['install','usage','api','contributing']]")
    print(result[0].result)
    print()


if __name__ == "__main__":
    main()
