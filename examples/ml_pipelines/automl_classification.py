#!/usr/bin/env python
"""Example 4: AutoML Classification

Demonstrates AutoML pipeline with hyperparameter optimization.
"""

from comptext_codex.executor import CompTextExecutor
import json


def main():
    """Run AutoML classification example."""
    executor = CompTextExecutor()

    print("=" * 60)
    print("AUTOML CLASSIFICATION EXAMPLE")
    print("=" * 60)

    # CompText command for AutoML
    command = """@AUTOML[task=classification, metric=f1, cv=5, models=[rf, xgb, lgbm], optimize=hyperparams]"""

    print(f"Command: {command}")
    print()
    print("Natural Language Equivalent:")
    print("-" * 60)
    print("Please run an automated machine learning pipeline for a classification")
    print("task. Use F1 score as the evaluation metric with 5-fold cross-validation.")
    print("Compare Random Forest, XGBoost, and LightGBM models. Optimize")
    print("hyperparameters for the best model and provide detailed results.")
    print()
    print("Token Savings: ~65%")
    print()

    # Execute
    results = executor.execute(command, context={'dataset': 'customer_churn.csv', 'target': 'churned'})

    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    if results and results[0].success:
        print(json.dumps(results[0].result, indent=2))
    else:
        print(f"Error: {results[0].error if results else 'Unknown error'}")


if __name__ == "__main__":
    main()
