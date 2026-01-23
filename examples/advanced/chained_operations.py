"""Example: Complex chained operations.

Demonstrates advanced command chaining across multiple modules.
"""

from comptext_codex import execute
import json


def main():
    """Execute complex chained operations."""

    print("=== Advanced Chaining Examples ===\n")

    # Example 1: ETL + Analysis chain
    print("1. ETL + Analysis Chain:")
    result = execute("""
        @EXTRACT[source=api, endpoint=/data] +
        @TRANSFORM[operations=['clean','normalize']] +
        @VALIDATE[rules=['not_null','format']] +
        @LOAD[destination=warehouse]
    """)
    print(f"Executed {len(result)} steps successfully")
    for i, r in enumerate(result):
        print(f"\nStep {i+1}: {r.metadata.get('module')}:{r.metadata.get('command')}")
        if isinstance(r.result, dict):
            print(json.dumps(r.result, indent=2)[:200] + "...")
    print()

    # Example 2: Full stack development chain
    print("2. Full Stack Development Chain:")
    result = execute("""
        @COMPONENT[framework=react, typescript=true] +
        @FORM[fields=['name','email'], validation=yup] +
        @THEME[primary_color=#8b5cf6] +
        @ACCESSIBILITY[level=wcag_aa]
    """)
    print(f"Generated {len(result)} components")
    print()

    # Example 3: ML pipeline chain
    print("3. ML Pipeline Chain:")
    result = execute("""
        @EXTRACT[source=database, table=training_data] +
        @FEATURE_ENG[operations=['scale','encode']] +
        @AUTOML[task=classification, metric=f1] +
        @MODEL_EVALUATE[metrics=['accuracy','precision','recall']]
    """)
    print(f"ML pipeline with {len(result)} stages completed")
    print()


if __name__ == "__main__":
    main()
