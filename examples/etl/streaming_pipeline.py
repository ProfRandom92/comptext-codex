"""Example: Streaming data pipeline with Kafka.

Demonstrates real-time data processing with Module L.
"""

from comptext_codex import execute
import json


def main():
    """Configure streaming ETL pipeline."""

    print("=== Streaming Pipeline Examples ===\n")

    # Example 1: Kafka extraction
    print("1. Kafka Stream Extraction:")
    result = execute("@EXTRACT[source=kafka, topic=events, consumer_group=etl-processor]")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 2: Real-time transformation
    print("2. Streaming Transformation:")
    result = execute("@TRANSFORM[operations=['clean','enrich'], parallel=true]")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 3: Load to data lake
    print("3. Data Lake Loading:")
    result = execute("@LOAD[destination=lake, platform=delta_lake, format=delta, partition_by=['year','month']]")
    print(json.dumps(result[0].result, indent=2))
    print()

    # Example 4: Complete streaming pipeline
    print("4. Complete Pipeline Configuration:")
    result = execute("@PIPELINE[steps=['extract','transform','load'], schedule=real-time, parallel=true]")
    print(json.dumps(result[0].result, indent=2))
    print()


if __name__ == "__main__":
    main()
