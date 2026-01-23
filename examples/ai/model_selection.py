"""Example: AI model selection and configuration with Module D.

Demonstrates AI control and model management.
"""

from comptext_codex import execute
import json


def main():
    """Configure AI models."""

    print("=== AI Model Configuration Examples ===\n")

    # Example 1: Model selection
    print("1. Model Selection:")
    result = execute("@MODEL_SELECT[task=classification, performance_level=high, cost_constraint=medium]")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 2: Safety filters
    print("2. Safety Filter Configuration:")
    result = execute("@SAFETY_FILTER[level=strict, categories=['violence','hate','sexual'], threshold=0.8]")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 3: Prompt optimization
    print("3. Prompt Optimization:")
    result = execute("@PROMPT_OPT[strategy=few_shot, examples=3, temperature=0.7]")
    print(json.dumps(result[0].result, indent=2))
    print()


if __name__ == "__main__":
    main()
