#!/usr/bin/env python
"""Example 11: GDPR Compliance Check

Demonstrates GDPR compliance auditing using CompText.
"""

from comptext_codex.executor import CompTextExecutor
import json


def main():
    """Run GDPR compliance check example."""
    executor = CompTextExecutor()

    print("=" * 60)
    print("GDPR COMPLIANCE CHECK")
    print("=" * 60)

    # CompText command
    command = "@GDPR[audit=full, generate_report=true, remediation=suggest]"

    print(f"Command: {command}")
    print()

    # Execute
    results = executor.execute(command, context={'path': '/path/to/project'})

    print("=" * 60)
    print("COMPLIANCE REPORT")
    print("=" * 60)
    if results and results[0].success:
        report = results[0].result
        print(json.dumps(report, indent=2))

        if not report.get('compliant', True):
            print("\n⚠️  COMPLIANCE ISSUES FOUND")
            print("\nRecommendations:")
            for i, rec in enumerate(report.get('recommendations', []), 1):
                print(f"{i}. {rec}")
    else:
        print(f"Error: {results[0].error if results else 'Unknown error'}")


if __name__ == "__main__":
    main()
