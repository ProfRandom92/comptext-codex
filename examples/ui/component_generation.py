"""Example: UI Component generation with Module K.

Demonstrates comprehensive component scaffolding with
accessibility and responsive design.
"""

from comptext_codex import execute
import json


def main():
    """Generate UI components with various configurations."""

    print("=== UI Component Generation Examples ===\n")

    # Example 1: React component with TypeScript
    print("1. React TypeScript Component:")
    result = execute("@COMPONENT[framework=react, typescript=true, styling=styled-components, type=functional]")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 2: Dashboard layout
    print("2. Dashboard Layout:")
    result = execute("@DASHBOARD[layout=grid, theme=dark, responsive=true, charts=['line','bar','pie']]")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 3: Form with validation
    print("3. Form with Validation:")
    result = execute("@FORM[fields=['email','password','username'], validation=yup]")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 4: Responsive layout
    print("4. Responsive Grid Layout:")
    result = execute("@LAYOUT[type=grid, columns=12, responsive=true, gap=16]")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 5: Theme configuration
    print("5. Theme Configuration:")
    result = execute("@THEME[primary_color=#8b5cf6, dark_mode=true]")
    print(json.dumps(result[0].result, indent=2))
    print()


if __name__ == "__main__":
    main()
