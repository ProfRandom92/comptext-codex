#!/usr/bin/env python
"""Advanced Example: Ultra Token Compression

Demonstrates 80%+ token savings using advanced compression strategies.
"""

from comptext_codex.compression import (
    CommandCompressor,
    CompressionLevel,
    demonstrate_compression_levels
)


def main():
    """Demonstrate ultra compression capabilities."""
    print("=" * 70)
    print("ULTRA TOKEN COMPRESSION DEMONSTRATION")
    print("=" * 70)
    print()

    # Example 1: Complex ML Pipeline
    example1 = {
        'name': 'ML Pipeline with Feature Engineering',
        'natural_language': """
        Please analyze the dataset, perform automated feature engineering with
        recursive feature elimination, train multiple classification models
        including random forest, xgboost, and lightgbm, optimize hyperparameters
        using bayesian optimization, evaluate performance using cross-validation
        with f1 score as the metric, generate feature importance plots, and
        export the best model with documentation
        """.strip(),
        'basic_comptext': "@AUTOML[task=classification, models=[rf, xgb, lgbm], metric=f1] + @FEATURE_ENGINEER[method=automated, selection=rfe] + @DOC_GENERATE[format=markdown]",
    }

    # Example 2: Full-Stack Application Deployment
    example2 = {
        'name': 'Full-Stack Application Deployment',
        'natural_language': """
        Set up a complete CI/CD pipeline using GitHub Actions with automated
        linting, unit testing with pytest, integration testing, security
        vulnerability scanning, docker container building, deployment to
        kubernetes cluster, monitoring configuration with prometheus and
        grafana, and automated rollback on failure
        """.strip(),
        'basic_comptext': "@CI_CD_CONFIG[platform=gha, steps=lint+test+security+build+deploy] + @DEPLOY[target=k8s, monitoring=prometheus+grafana, rollback=auto]",
    }

    # Example 3: Security Audit with Remediation
    example3 = {
        'name': 'Comprehensive Security Audit',
        'natural_language': """
        Perform a comprehensive security vulnerability scan including OWASP
        top 10 checks, SQL injection detection, XSS vulnerability testing,
        authentication and authorization review, GDPR compliance verification,
        generate detailed security report with severity ratings, provide
        remediation recommendations with code examples, and create action items
        prioritized by risk level
        """.strip(),
        'basic_comptext': "@SEC_VULNERABILITY_SCAN[severity=high, owasp=true] + @GDPR[scope=full, action=audit] + @DOC_GENERATE[format=security_report, include=remediation+code_examples]",
    }

    examples = [example1, example2, example3]

    for i, example in enumerate(examples, 1):
        print(f"\n{'=' * 70}")
        print(f"EXAMPLE {i}: {example['name']}")
        print(f"{'=' * 70}\n")

        nl = example['natural_language']
        basic = example['basic_comptext']

        # Count tokens
        nl_tokens = len(nl.split())
        basic_tokens = len(basic.split())
        basic_savings = ((nl_tokens - basic_tokens) / nl_tokens * 100)

        print(f"📝 Natural Language ({nl_tokens} tokens):")
        print(f"   {nl[:100]}...")
        print()
        print(f"✨ Basic CompText ({basic_tokens} tokens, {basic_savings:.1f}% savings):")
        print(f"   {basic}")
        print()

        # Apply compression levels
        print("🚀 Advanced Compression Levels:")
        print()

        results = demonstrate_compression_levels(basic)

        for level_name, data in results.items():
            if level_name == 'NONE':
                continue

            compressed = data['compressed']
            metrics = data['metrics']
            comp_tokens = metrics['compressed_tokens']
            total_savings = ((nl_tokens - comp_tokens) / nl_tokens * 100)

            print(f"   {level_name:15} ({comp_tokens:2} tokens, "
                  f"{total_savings:5.1f}% total savings):")
            print(f"   → {compressed}")
            print()

        # Calculate best case
        ultra_result = results['ULTRA']
        ultra_tokens = ultra_result['metrics']['compressed_tokens']
        ultra_savings = ((nl_tokens - ultra_tokens) / nl_tokens * 100)

        print(f"💎 MAXIMUM SAVINGS: {ultra_savings:.1f}%")
        print(f"   Original: {nl_tokens} tokens → Ultra Compressed: {ultra_tokens} tokens")
        print()

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY: TOKEN SAVINGS ACROSS COMPRESSION LEVELS")
    print("=" * 70)
    print()
    print("Compression Level    | Avg Savings | Use Case")
    print("-" * 70)
    print("None                 |      0%     | Maximum clarity")
    print("Basic                |    60-70%   | General use")
    print("Moderate             |    70-75%   | Production default")
    print("Aggressive           |    75-80%   | Cost optimization")
    print("Ultra                |    80-85%   | Maximum efficiency")
    print()
    print("💡 Tip: Use MODERATE for best balance of savings and readability")
    print()


if __name__ == "__main__":
    main()
