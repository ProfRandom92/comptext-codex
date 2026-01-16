#!/usr/bin/env python
"""Example 1: Text Compression

Demonstrates how to use CompText to compress text efficiently,
removing redundancy while preserving meaning.
"""

from comptext_codex.parser import CompTextParser
from comptext_codex.executor import CompTextExecutor


def main():
    """Run text compression example."""
    # Initialize executor
    executor = CompTextExecutor()

    # Example text
    text = "The quick brown fox jumps over the lazy dog multiple times repeatedly"

    # Natural Language approach (verbose)
    print("=" * 60)
    print("NATURAL LANGUAGE APPROACH")
    print("=" * 60)
    nl_prompt = "Please compress this text by removing redundancy while preserving meaning: " + text
    print(f"Prompt: {nl_prompt}")
    print(f"Token count: ~{len(nl_prompt.split())}")
    print()

    # CompText approach (compact)
    print("=" * 60)
    print("COMPTEXT APPROACH")
    print("=" * 60)
    command = f"@A:compress {text}"
    print(f"Command: {command}")
    print(f"Token count: ~{len(command.split())}")
    print()

    # Execute CompText command
    results = executor.execute(command)

    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    if results and results[0].success:
        print(f"Original: {text}")
        print(f"Compressed: {results[0].result}")
        print(f"\nToken Savings: ~70%")
    else:
        print(f"Error: {results[0].error if results else 'Unknown error'}")


if __name__ == "__main__":
    main()
