"""Example: Feature engineering for ML with Module E.

Demonstrates automated feature engineering capabilities.
"""

from comptext_codex import execute
import json


def main():
    """Perform feature engineering operations."""

    print("=== Feature Engineering Examples ===\n")

    # Example 1: AutoML configuration
    print("1. AutoML Classification:")
    result = execute("@AUTOML[task=classification, metric=f1, cv_folds=5, models=['rf','xgb','lgbm']]")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 2: Feature selection
    print("2. Feature Selection:")
    result = execute("@FEATURE_SELECT[method=mutual_info, n_features=20, threshold=0.1]")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 3: Feature transformation
    print("3. Feature Engineering:")
    result = execute("@FEATURE_ENG[operations=['scale','encode','polynomial'], degree=2]")
    print(json.dumps(result[0].result, indent=2))
    print()


if __name__ == "__main__":
    main()
