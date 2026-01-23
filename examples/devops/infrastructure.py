"""Example: Infrastructure as Code with Module J.

Demonstrates infrastructure provisioning and management.
"""

from comptext_codex import execute
import json


def main():
    """Configure infrastructure."""

    print("=== Infrastructure Configuration Examples ===\n")

    # Example 1: Kubernetes deployment
    print("1. Kubernetes Deployment:")
    result = execute("@K8S_DEPLOY[replicas=3, resources={'cpu':'500m','memory':'512Mi'}, autoscale=true]")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 2: Docker configuration
    print("2. Docker Configuration:")
    result = execute("@DOCKER_BUILD[base_image=python:3.9, optimize=true, multi_stage=true]")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 3: Terraform configuration
    print("3. Terraform Configuration:")
    result = execute("@TERRAFORM[provider=aws, resources=['ec2','rds','s3'], state_backend=s3]")
    print(json.dumps(result[0].result, indent=2))
    print()


if __name__ == "__main__":
    main()
