"""Example: Data encryption and security with Module I.

Demonstrates encryption and secure data handling.
"""

from comptext_codex import execute
import json


def main():
    """Configure encryption and security."""

    print("=== Encryption & Security Examples ===\n")

    # Example 1: Encryption setup
    print("1. Encryption Configuration:")
    result = execute("@ENCRYPT[algorithm=aes256, key_rotation=true, mode=gcm]")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 2: Access control
    print("2. Access Control Setup:")
    result = execute("@ACCESS_CONTROL[model=rbac, roles=['admin','user','guest'], audit=true]")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 3: Security headers
    print("3. Security Headers:")
    result = execute("@SECURITY_HEADERS[hsts=true, csp=strict, xss_protection=true]")
    print(json.dumps(result[0].result, indent=2))
    print()


if __name__ == "__main__":
    main()
