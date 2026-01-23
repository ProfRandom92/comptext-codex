"""Example: Complete ETL pipeline with Module L.

Demonstrates extract, transform, load operations with
comprehensive data processing.
"""

from comptext_codex import execute
import json


def main():
    """Run complete ETL pipeline."""

    print("=== ETL Pipeline Examples ===\n")

    # Example 1: Simple ETL chain
    print("1. Basic ETL Chain:")
    result = execute("@EXTRACT[source=database, table=users] + @TRANSFORM[operations=['clean','normalize']] + @LOAD[destination=warehouse, mode=append]")

    for i, r in enumerate(result):
        print(f"\nStep {i+1} Result:")
        print(json.dumps(r.result, indent=2))
    print()

    # Example 2: Data validation
    print("2. Data Validation:")
    result = execute("@VALIDATE[rules=['email','not_null'], strict=false]")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 3: Deduplication
    print("3. Deduplication:")
    result = execute("@DEDUPE[strategy=key_based, keys=['email','phone']]")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 4: Data enrichment
    print("4. Data Enrichment:")
    result = execute("@ENRICH[sources=['geo_api','demographics'], fields=['location','age_group']]")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 5: Data aggregation
    print("5. Data Aggregation:")
    result = execute("@AGGREGATE[operations=['sum','avg','count'], group_by=['category','region']]")
    print(json.dumps(result[0].result, indent=2))
    print()


if __name__ == "__main__":
    main()
