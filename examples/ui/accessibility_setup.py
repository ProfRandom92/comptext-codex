"""Example: Accessibility configuration for web applications.

Demonstrates Module K accessibility features for WCAG compliance.
"""

from comptext_codex import execute
import json


def main():
    """Configure accessibility features."""

    print("=== Accessibility Configuration Examples ===\n")

    # Example 1: WCAG AA compliance
    print("1. WCAG AA Configuration:")
    result = execute("@ACCESSIBILITY[level=wcag_aa, captions=true]")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 2: Animation configuration
    print("2. Accessible Animations:")
    result = execute("@ANIMATION[type=fade, duration=300, easing=ease-in-out]")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 3: Responsive breakpoints
    print("3. Responsive Configuration:")
    result = execute("@RESPONSIVE[mobile_first=true, gestures=true]")
    print(json.dumps(result[0].result, indent=2))
    print()


if __name__ == "__main__":
    main()
