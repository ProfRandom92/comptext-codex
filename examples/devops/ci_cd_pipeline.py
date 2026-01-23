"""Example: CI/CD pipeline configuration with Module J.

Demonstrates DevOps automation and pipeline setup.
"""

from comptext_codex import execute
import json


def main():
    """Configure CI/CD pipelines."""

    print("=== CI/CD Pipeline Examples ===\n")

    # Example 1: CI pipeline
    print("1. CI Pipeline Configuration:")
    result = execute("@CI_CD[platform=github_actions, stages=['build','test','lint'], parallel=true]")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 2: Deployment configuration
    print("2. Deployment Configuration:")
    result = execute("@DEPLOY[environment=production, strategy=blue_green, rollback=auto]")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 3: Monitoring setup
    print("3. Monitoring Configuration:")
    result = execute("@MONITOR[metrics=['cpu','memory','response_time'], alerts=true, dashboard=grafana]")
    print(json.dumps(result[0].result, indent=2))
    print()


if __name__ == "__main__":
    main()
