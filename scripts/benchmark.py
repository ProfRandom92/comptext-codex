#!/usr/bin/env python
"""Performance benchmarks for CompText-Codex.

Measures performance of:
- Parser (commands/second)
- Executor (commands/second)
- End-to-end (commands/second)
"""

import time
from typing import List, Tuple
import statistics

from comptext_codex.parser import CompTextParser
from comptext_codex.executor import CompTextExecutor


def benchmark_parser(iterations: int = 10000) -> Tuple[float, float]:
    """Benchmark parser performance.

    Args:
        iterations: Number of iterations to run

    Returns:
        Tuple of (commands_per_second, avg_time_ms)
    """
    parser = CompTextParser()

    commands = [
        "@A:compress text",
        "@B:analyze sentiment",
        "@CODE_ANALYZE[perf_bottleneck, complexity]",
        "@AUTOML[task=classification, metric=f1]",
        "@EXTRACT[source=db] + @TRANSFORM[clean=true] + @LOAD[dest=warehouse]",
        "@COMPONENT[framework=react, styling=tailwind]"
    ]

    times = []

    for _ in range(iterations):
        cmd = commands[_ % len(commands)]
        start = time.time()
        parser.parse(cmd)
        end = time.time()
        times.append((end - start) * 1000)  # Convert to ms

    avg_time_ms = statistics.mean(times)
    commands_per_sec = 1000 / avg_time_ms if avg_time_ms > 0 else 0

    return commands_per_sec, avg_time_ms


def benchmark_executor(iterations: int = 5000) -> Tuple[float, float]:
    """Benchmark executor performance.

    Args:
        iterations: Number of iterations to run

    Returns:
        Tuple of (commands_per_second, avg_time_ms)
    """
    executor = CompTextExecutor()

    commands = [
        "@A:compress text",
        "@B:analyze sentiment analysis",
        "@C:format json {}",
    ]

    times = []

    for _ in range(iterations):
        cmd = commands[_ % len(commands)]
        start = time.time()
        executor.execute(cmd)
        end = time.time()
        times.append((end - start) * 1000)  # Convert to ms

    avg_time_ms = statistics.mean(times)
    commands_per_sec = 1000 / avg_time_ms if avg_time_ms > 0 else 0

    return commands_per_sec, avg_time_ms


def benchmark_end_to_end(iterations: int = 3000) -> Tuple[float, float]:
    """Benchmark end-to-end performance including parsing and execution.

    Args:
        iterations: Number of iterations to run

    Returns:
        Tuple of (commands_per_second, avg_time_ms)
    """
    executor = CompTextExecutor()

    commands = [
        "@A:compress The quick brown fox jumps over the lazy dog",
        "@B:analyze Customer feedback shows positive sentiment",
        "@C:format json {\"key\": \"value\"}",
        "@EXTRACT[source=db] + @TRANSFORM[clean=true]",
    ]

    times = []

    for _ in range(iterations):
        cmd = commands[_ % len(commands)]
        start = time.time()
        results = executor.execute(cmd)
        # Ensure execution completed
        assert results is not None
        end = time.time()
        times.append((end - start) * 1000)  # Convert to ms

    avg_time_ms = statistics.mean(times)
    commands_per_sec = 1000 / avg_time_ms if avg_time_ms > 0 else 0

    return commands_per_sec, avg_time_ms


def print_benchmark_results(name: str, commands_per_sec: float, avg_time_ms: float):
    """Print benchmark results in a formatted way."""
    print(f"\n{name}")
    print("=" * 60)
    print(f"Commands/second:   {commands_per_sec:,.0f}")
    print(f"Avg time per cmd:  {avg_time_ms:.3f} ms")
    print(f"Throughput:        {commands_per_sec * 60:,.0f} commands/minute")


def main():
    """Run all benchmarks and display results."""
    print("=" * 60)
    print("CompText-Codex Performance Benchmarks")
    print("=" * 60)

    # Parser benchmark
    print("\n[1/3] Running parser benchmark...")
    parser_cps, parser_avg = benchmark_parser(iterations=10000)
    print_benchmark_results("PARSER PERFORMANCE", parser_cps, parser_avg)

    # Executor benchmark
    print("\n[2/3] Running executor benchmark...")
    executor_cps, executor_avg = benchmark_executor(iterations=5000)
    print_benchmark_results("EXECUTOR PERFORMANCE", executor_cps, executor_avg)

    # End-to-end benchmark
    print("\n[3/3] Running end-to-end benchmark...")
    e2e_cps, e2e_avg = benchmark_end_to_end(iterations=3000)
    print_benchmark_results("END-TO-END PERFORMANCE", e2e_cps, e2e_avg)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Parser:      {parser_cps:>10,.0f} cmd/s  ({parser_avg:>6.3f} ms/cmd)")
    print(f"Executor:    {executor_cps:>10,.0f} cmd/s  ({executor_avg:>6.3f} ms/cmd)")
    print(f"End-to-End:  {e2e_cps:>10,.0f} cmd/s  ({e2e_avg:>6.3f} ms/cmd)")
    print("=" * 60)

    # Performance rating
    if e2e_cps >= 5000:
        rating = "⭐⭐⭐⭐⭐ EXCELLENT"
    elif e2e_cps >= 3000:
        rating = "⭐⭐⭐⭐ VERY GOOD"
    elif e2e_cps >= 1000:
        rating = "⭐⭐⭐ GOOD"
    elif e2e_cps >= 500:
        rating = "⭐⭐ FAIR"
    else:
        rating = "⭐ NEEDS IMPROVEMENT"

    print(f"\nPerformance Rating: {rating}")
    print()


if __name__ == "__main__":
    main()
