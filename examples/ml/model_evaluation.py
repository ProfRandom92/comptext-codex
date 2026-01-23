"""Example: Model evaluation and comparison.

Demonstrates ML model evaluation with Module E.
"""

from comptext_codex import execute
import json


def main():
    """Evaluate ML models."""

    print("=== Model Evaluation Examples ===\n")

    # Example 1: Model training
    print("1. Model Training:")
    result = execute("@MODEL_TRAIN[algorithm=random_forest, params={'n_estimators': 100, 'max_depth': 10}]")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 2: Cross-validation
    print("2. Cross-Validation:")
    result = execute("@CROSS_VALIDATE[cv_strategy=stratified_kfold, n_splits=5, metrics=['accuracy','f1','roc_auc']]")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 3: Hyperparameter tuning
    print("3. Hyperparameter Tuning:")
    result = execute("@HYPERPARAM_TUNE[method=bayesian, n_trials=50, metric=f1]")
    print(json.dumps(result[0].result, indent=2))
    print()


if __name__ == "__main__":
    main()
