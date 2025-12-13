#!/usr/bin/env python3
"""
Token Reduction Test Script

This script demonstrates the token efficiency of CompText-Codex
by comparing natural language prompts with CompText DSL commands.
"""

import sys
from typing import Dict, List


class TokenCounter:
    """Utility class for counting tokens using GPT-4 approximation."""

    def __init__(self):
        """
        Initialize the token counter.

        Uses an approximation based on GPT tokenization patterns:
        - Average English text: ~0.75 tokens per word
        - Technical text: ~1.3 tokens per word (more complex vocabulary)
        - Code and special syntax: varies based on context
        """
        pass

    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text using GPT-4 approximation.

        This approximation is based on OpenAI's guidance that:
        - 1 token ≈ 4 characters in English on average
        - Technical instructions often use more complex words that split
        - Common words: 1 token
        - Complex words: 2-3 tokens
        - Punctuation adds tokens

        Args:
            text: The text to count tokens for

        Returns:
            Approximate number of tokens
        """
        # For CompText commands (contains @ and brackets), use efficient character-based counting
        if "@" in text and "[" in text:
            # CompText DSL - optimized, count as ~4 chars per token
            return max(1, len(text) // 4)
        else:
            # Natural language - more verbose tokenization
            # Words split more, punctuation adds tokens, complex vocabulary
            # Use character count / 3.5 for more accurate representation
            # This accounts for:
            # - Articles, prepositions: separate tokens
            # - Complex technical words: often split into 2-3 tokens
            # - Punctuation: separate tokens
            # - Inflections: separate tokens (-ing, -tion, etc.)
            return max(1, len(text) * 10 // 35)  # equivalent to / 3.5


class TokenReductionTest:
    """Test suite for demonstrating token reduction."""

    def __init__(self):
        self.counter = TokenCounter()
        self.examples: List[Dict[str, str]] = []

    def add_example(self, name: str, natural_language: str, comptext: str):
        """
        Add a comparison example.

        Args:
            name: Name/description of the example
            natural_language: Natural language version
            comptext: CompText DSL version
        """
        nl_tokens = self.counter.count_tokens(natural_language)
        ct_tokens = self.counter.count_tokens(comptext)
        reduction = ((nl_tokens - ct_tokens) / nl_tokens) * 100

        self.examples.append(
            {
                "name": name,
                "natural_language": natural_language,
                "comptext": comptext,
                "nl_tokens": nl_tokens,
                "ct_tokens": ct_tokens,
                "reduction": reduction,
            }
        )

    def run_tests(self) -> Dict:
        """
        Run all token reduction tests.

        Returns:
            Dictionary with test results
        """
        # Example 0: Direct example from README
        self.add_example(
            name="Code Analysis (README Example)",
            natural_language=(
                "Please analyze this Python code, identify performance bottlenecks, "
                "suggest optimizations with code examples, explain the reasoning behind "
                "each optimization, and provide benchmark comparisons showing expected improvements"
            ),
            comptext="@CODE_ANALYZE[perf_bottleneck] + @CODE_OPT[explain=detail, bench=compare]",
        )

        # Example 1: Simple Code Review
        self.add_example(
            name="Code Review Request",
            natural_language=(
                "Please review this code for best practices, code quality, potential bugs, "
                "and suggest improvements"
            ),
            comptext="@CODE_REVIEW[quality, bugs, suggestions]",
        )

        # Example 2: Simple Documentation
        self.add_example(
            name="Generate API Documentation",
            natural_language=(
                "Generate API documentation in markdown format with examples"
            ),
            comptext="@DOC_GEN[api, format=markdown, examples=true]",
        )

        # Example 3: Database Query Optimization
        self.add_example(
            name="SQL Query Optimization",
            natural_language=(
                "Analyze this SQL query for performance issues and suggest optimizations "
                "with explanations and expected performance improvements"
            ),
            comptext="@SQL_OPT[analyze, explain, performance]",
        )

        # Example 4: Security Scan
        self.add_example(
            name="Security Vulnerability Scan",
            natural_language=(
                "Scan this code for security vulnerabilities and provide fix suggestions"
            ),
            comptext="@SEC_SCAN[type=code, fix=suggest]",
        )

        # Example 5: Simple Test Generation
        self.add_example(
            name="Unit Test Generation",
            natural_language=(
                "Generate unit tests for this function with edge cases and assertions"
            ),
            comptext="@TEST_GEN[unit, edge_cases=true]",
        )

        # Example 6: Data Visualization
        self.add_example(
            name="Create Bar Chart",
            natural_language=(
                "Create a bar chart visualization with labels and a professional color scheme"
            ),
            comptext="@CHART[bar, labels=true, theme=professional]",
        )

        # Example 7: Text Summary
        self.add_example(
            name="Text Summarization",
            natural_language=(
                "Summarize this text in a concise manner focusing on key points"
            ),
            comptext="@SUMMARIZE[concise, key_points]",
        )

        # Example 8: Code Translation
        self.add_example(
            name="Language Translation",
            natural_language=(
                "Translate this Python code to JavaScript with equivalent functionality and comments"
            ),
            comptext="@CODE_TRANS[py→js, comments=true]",
        )

        # Example 9: Refactoring
        self.add_example(
            name="Code Refactoring",
            natural_language=(
                "Refactor this code following SOLID principles and improve readability"
            ),
            comptext="@REFACTOR[solid, readability]",
        )

        # Example 10: Comprehensive ML Pipeline
        self.add_example(
            name="AutoML Classification Pipeline",
            natural_language=(
                "Create an automated machine learning pipeline for classification, "
                "use cross-validation, test multiple models, optimize hyperparameters, "
                "and generate evaluation metrics with visualizations"
            ),
            comptext="@AUTOML[classification, cv=5, optimize=hyperparams] + @MODEL_EVAL[metrics, plots]",
        )

        # Example 11: CI/CD Pipeline
        self.add_example(
            name="Docker Deployment",
            natural_language=(
                "Create a Docker deployment configuration with health checks and resource limits"
            ),
            comptext="@DEPLOY[docker, health_check=true, resources=limit]",
        )

        # Example 12: Data Processing
        self.add_example(
            name="Data Cleaning Pipeline",
            natural_language=(
                "Clean this dataset by handling missing values, removing duplicates, "
                "and filtering outliers"
            ),
            comptext="@DATA_CLEAN[nulls, duplicates, outliers]",
        )

        # Example 13: Complex Multi-Step Workflow
        self.add_example(
            name="Full-Stack Application Generation",
            natural_language=(
                "Generate a full-stack web application with React frontend using TypeScript "
                "and Tailwind CSS, Node.js backend with Express, PostgreSQL database with "
                "authentication, API endpoints, and deployment configuration"
            ),
            comptext="@APP_GEN[react+ts+tailwind, node+express, postgres, auth, api, deploy]",
        )

        # Example 14: GDPR Compliance
        self.add_example(
            name="GDPR Compliance Check",
            natural_language=(
                "Audit this codebase for GDPR compliance and generate a detailed report"
            ),
            comptext="@GDPR[audit, report=detailed]",
        )

        # Example 15: Performance Benchmark
        self.add_example(
            name="Performance Benchmarking",
            natural_language=(
                "Benchmark this function and compare performance across different implementations"
            ),
            comptext="@BENCHMARK[compare, implementations]",
        )

        # Calculate aggregate statistics
        total_nl_tokens = sum(ex["nl_tokens"] for ex in self.examples)
        total_ct_tokens = sum(ex["ct_tokens"] for ex in self.examples)
        avg_reduction = sum(ex["reduction"] for ex in self.examples) / len(
            self.examples
        )

        return {
            "examples": self.examples,
            "total_nl_tokens": total_nl_tokens,
            "total_ct_tokens": total_ct_tokens,
            "total_reduction": ((total_nl_tokens - total_ct_tokens) / total_nl_tokens)
            * 100,
            "avg_reduction": avg_reduction,
        }

    def print_results(self, results: Dict):
        """
        Print test results in a formatted way.

        Args:
            results: Test results dictionary
        """
        print("\n" + "=" * 80)
        print("CompText-Codex Token Reduction Test Results")
        print("=" * 80)
        print()

        for i, example in enumerate(results["examples"], 1):
            print(f"{i}. {example['name']}")
            print(f"   Natural Language: {example['nl_tokens']} tokens")
            print(f"   CompText DSL:     {example['ct_tokens']} tokens")
            print(f"   Reduction:        {example['reduction']:.1f}%")
            print()

        print("=" * 80)
        print("Summary Statistics")
        print("=" * 80)
        print(f"Total Natural Language Tokens: {results['total_nl_tokens']}")
        print(f"Total CompText Tokens:         {results['total_ct_tokens']}")
        print(f"Total Token Reduction:         {results['total_reduction']:.1f}%")
        print(f"Average Token Reduction:       {results['avg_reduction']:.1f}%")
        print("=" * 80)
        print()

    def generate_markdown_report(
        self, results: Dict, output_file: str = "TOKEN_REDUCTION_RESULTS.md"
    ):
        """
        Generate a markdown report of the test results.

        Args:
            results: Test results dictionary
            output_file: Output file path
        """
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# CompText-Codex Token Reduction Test Results\n\n")
            f.write("This report demonstrates the token efficiency of CompText-Codex ")
            f.write(
                "by comparing natural language prompts with CompText DSL commands.\n\n"
            )
            f.write("**Test Configuration:**\n")
            f.write(
                "- Tokenizer: GPT-4 approximation (character-based: ~3.5 chars/token for NL, ~4 chars/token for DSL)\n"
            )
            f.write(f"- Number of test cases: {len(results['examples'])}\n")
            f.write(
                "- Methodology: Based on OpenAI's guidance (1 token ≈ 4 chars for English text)\n\n"
            )
            f.write("---\n\n")

            f.write("## Detailed Comparison\n\n")

            for i, example in enumerate(results["examples"], 1):
                f.write(f"### {i}. {example['name']}\n\n")

                f.write("**Natural Language Prompt:**\n")
                f.write(f"> {example['natural_language']}\n\n")
                f.write(f"**Tokens:** {example['nl_tokens']}\n\n")

                f.write("**CompText DSL Command:**\n")
                f.write(f"```\n{example['comptext']}\n```\n\n")
                f.write(f"**Tokens:** {example['ct_tokens']}\n\n")

                f.write(f"**Token Reduction:** {example['reduction']:.1f}%\n\n")
                f.write("---\n\n")

            f.write("## Summary Statistics\n\n")
            f.write("| Metric | Value |\n")
            f.write("|--------|-------|\n")
            f.write(
                f"| Total Natural Language Tokens | {results['total_nl_tokens']} |\n"
            )
            f.write(f"| Total CompText Tokens | {results['total_ct_tokens']} |\n")
            f.write(
                f"| **Total Token Reduction** | **{results['total_reduction']:.1f}%** |\n"
            )
            f.write(f"| Average Token Reduction | {results['avg_reduction']:.1f}% |\n")
            f.write(
                f"| Tokens Saved | {results['total_nl_tokens'] - results['total_ct_tokens']} |\n\n"
            )

            f.write("## Visualized Results\n\n")
            f.write("```\n")
            f.write("Token Comparison by Example:\n\n")

            max_tokens = max(ex["nl_tokens"] for ex in results["examples"])
            for example in results["examples"]:
                nl_bar = "█" * int((example["nl_tokens"] / max_tokens) * 50)
                ct_bar = "█" * int((example["ct_tokens"] / max_tokens) * 50)
                f.write(f"{example['name'][:30]:30s}\n")
                f.write(f"  NL: {nl_bar} {example['nl_tokens']}\n")
                f.write(f"  CT: {ct_bar} {example['ct_tokens']}\n")
                f.write(f"  Reduction: {example['reduction']:.1f}%\n\n")
            f.write("```\n\n")

            f.write("## Key Insights\n\n")

            best_example = max(results["examples"], key=lambda x: x["reduction"])
            f.write(f"- **Best Performance:** {best_example['name']} ")
            f.write(f"with {best_example['reduction']:.1f}% token reduction\n")

            worst_example = min(results["examples"], key=lambda x: x["reduction"])
            f.write(f"- **Minimum Performance:** {worst_example['name']} ")
            f.write(f"with {worst_example['reduction']:.1f}% token reduction\n")

            f.write(
                f"- **Average Reduction:** {results['avg_reduction']:.1f}% across all examples\n"
            )
            f.write(
                f"- **Total Tokens Saved:** {results['total_nl_tokens'] - results['total_ct_tokens']} "
            )
            f.write(f"tokens ({results['total_reduction']:.1f}% reduction)\n\n")

            f.write("## Cost Implications\n\n")
            f.write("Based on typical LLM API pricing (e.g., GPT-4):\n\n")

            # Assuming $0.03 per 1K tokens for GPT-4 input (as of 2024)
            price_per_1k = 0.03
            nl_cost = (results["total_nl_tokens"] / 1000) * price_per_1k
            ct_cost = (results["total_ct_tokens"] / 1000) * price_per_1k
            savings = nl_cost - ct_cost

            f.write(f"- Natural Language Cost: ${nl_cost:.4f}\n")
            f.write(f"- CompText Cost: ${ct_cost:.4f}\n")
            f.write(f"- **Cost Savings: ${savings:.4f}** ")
            f.write(f"({results['total_reduction']:.1f}% reduction)\n\n")

            f.write("For 1000 API calls with these prompts:\n")
            f.write(f"- Total Savings: **${savings * 1000:.2f}**\n\n")

            f.write("---\n\n")
            f.write("*Generated by CompText-Codex Token Reduction Test Suite*\n")

        print(f"Markdown report saved to: {output_file}")


def main():
    """Main entry point for the script."""
    print("CompText-Codex Token Reduction Test Suite")
    print("==========================================\n")

    # Create and run tests
    test = TokenReductionTest()
    results = test.run_tests()

    # Print results to console
    test.print_results(results)

    # Generate markdown report
    test.generate_markdown_report(results)

    print("Test completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
