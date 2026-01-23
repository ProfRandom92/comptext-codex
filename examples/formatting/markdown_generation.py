"""Example: Markdown document generation with CompText.

Demonstrates Module C (Formatting) capabilities for generating
structured markdown documents efficiently.
"""

from comptext_codex import execute


def main():
    """Generate various markdown formats."""

    print("=== Markdown Generation Examples ===\n")

    # Example 1: Basic markdown formatting
    print("1. Basic Markdown:")
    result = execute("@C:markdown[style=standard] Project Documentation")
    print(result[0].result)
    print()

    # Example 2: GitHub-flavored markdown
    print("2. GitHub Markdown:")
    result = execute("@C:markdown[style=github] CompText Codex Overview")
    print(result[0].result)
    print()

    # Example 3: Markdown table
    print("3. Markdown Table:")
    result = execute("@C:table[format=markdown, headers=['Name','Age','City']] John,30,NYC\\nJane,25,SF\\nBob,35,LA")
    print(result[0].result)
    print()

    # Example 4: Code block formatting
    print("4. Code Block:")
    code = "def hello():\\n    print('Hello, World!')"
    result = execute(f"@C:code[lang=python] {code}")
    print(result[0].result)
    print()

    # Example 5: List formatting
    print("5. Ordered List:")
    result = execute("@C:list[ordered=true] Planning Design Implementation Testing Deployment")
    print(result[0].result)
    print()

    # Token comparison
    natural_language = "Please create a markdown document with the project documentation including a title, description, and a table showing team members with their names, ages, and cities. Also include a code example and an ordered list of project phases."
    comptext_command = "@C:markdown[style=github] + @C:table[format=markdown] + @C:code[lang=python] + @C:list[ordered=true]"

    print(f"\n=== Token Savings ===")
    print(f"Natural language tokens: ~{len(natural_language.split()) * 1.3:.0f}")
    print(f"CompText tokens: ~{len(comptext_command.split()) * 1.3:.0f}")
    print(f"Reduction: ~{(1 - len(comptext_command.split()) / len(natural_language.split())) * 100:.0f}%")


if __name__ == "__main__":
    main()
