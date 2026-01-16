#!/usr/bin/env python
"""Advanced Example: High-Performance Batch Processing

Demonstrates batch processing with parallel execution, caching, and
massive performance improvements for handling multiple commands.
"""

from comptext_codex.executor import CompTextExecutor
from comptext_codex.batch import create_batch_executor
import time


def progress_callback(completed: int, total: int):
    """Progress callback for batch execution."""
    percent = (completed / total) * 100
    bar_length = 40
    filled = int(bar_length * completed / total)
    bar = '█' * filled + '░' * (bar_length - filled)
    print(f'\r  Progress: [{bar}] {percent:5.1f}% ({completed}/{total})', end='', flush=True)


def main():
    """Demonstrate batch processing capabilities."""
    print("=" * 70)
    print("HIGH-PERFORMANCE BATCH PROCESSING")
    print("=" * 70)
    print()

    # Create executor
    executor = CompTextExecutor()

    # Prepare batch of commands
    commands = [
        "@A:compress The quick brown fox jumps over the lazy dog repeatedly",
        "@B:analyze Customer feedback shows very positive sentiment overall",
        "@C:format json {\"name\": \"value\", \"data\": [1, 2, 3]}",
        "@A:compress Remove redundant information from this long text passage",
        "@B:analyze This product review indicates negative user experience",
        "@C:format markdown # Heading\n\nParagraph text here",
        "@A:compress Eliminate duplicate words in this sentence with many many duplicates",
        "@B:analyze The sentiment expressed here is neutral and balanced",
        "@C:format json {\"users\": [{\"id\": 1, \"name\": \"Alice\"}]}",
        "@A:compress Shorten this verbose explanation into concise format",
    ] * 5  # 50 commands total

    print(f"📦 Batch Size: {len(commands)} commands")
    print()

    # Test 1: Sequential execution (no batch)
    print("=" * 70)
    print("TEST 1: Sequential Execution (Baseline)")
    print("=" * 70)

    start = time.time()
    sequential_results = []
    for i, cmd in enumerate(commands):
        results = executor.execute(cmd)
        sequential_results.extend(results)
        progress_callback(i + 1, len(commands))

    sequential_time = time.time() - start
    print(f"\n  ✓ Completed in {sequential_time:.3f} seconds")
    print(f"  Throughput: {len(commands) / sequential_time:.1f} commands/sec")
    print()

    # Test 2: Batch execution with caching (sequential)
    print("=" * 70)
    print("TEST 2: Batch with Caching (Sequential)")
    print("=" * 70)

    batch_executor = create_batch_executor(
        executor_instance=executor,
        max_workers=4,
        use_cache=True,
        parallel=False
    )

    start = time.time()
    batch_results = batch_executor.execute_batch(
        commands,
        progress_callback=progress_callback
    )
    batch_time = time.time() - start

    # Count cache hits
    cache_hits = sum(1 for r in batch_results if r.cached)

    print(f"\n  ✓ Completed in {batch_time:.3f} seconds")
    print(f"  Throughput: {len(commands) / batch_time:.1f} commands/sec")
    print(f"  Cache hits: {cache_hits}/{len(commands)} ({cache_hits/len(commands)*100:.1f}%)")
    print(f"  🚀 Speedup: {sequential_time / batch_time:.2f}x faster")
    print()

    # Clear cache for fair comparison
    batch_executor.clear_cache()

    # Test 3: Batch execution with parallel processing
    print("=" * 70)
    print("TEST 3: Batch with Parallel Execution")
    print("=" * 70)

    parallel_executor = create_batch_executor(
        executor_instance=executor,
        max_workers=8,
        use_cache=True,
        parallel=True
    )

    start = time.time()
    parallel_results = parallel_executor.execute_batch(
        commands,
        progress_callback=progress_callback
    )
    parallel_time = time.time() - start

    cache_hits = sum(1 for r in parallel_results if r.cached)

    print(f"\n  ✓ Completed in {parallel_time:.3f} seconds")
    print(f"  Throughput: {len(commands) / parallel_time:.1f} commands/sec")
    print(f"  Cache hits: {cache_hits}/{len(commands)} ({cache_hits/len(commands)*100:.1f}%)")
    print(f"  🚀 Speedup: {sequential_time / parallel_time:.2f}x faster")
    print()

    # Test 4: Cached parallel execution (best case)
    print("=" * 70)
    print("TEST 4: Cached Parallel Execution (Best Case)")
    print("=" * 70)

    start = time.time()
    cached_results = parallel_executor.execute_batch(
        commands,
        progress_callback=progress_callback
    )
    cached_time = time.time() - start

    cache_hits = sum(1 for r in cached_results if r.cached)

    print(f"\n  ✓ Completed in {cached_time:.3f} seconds")
    print(f"  Throughput: {len(commands) / cached_time:.1f} commands/sec")
    print(f"  Cache hits: {cache_hits}/{len(commands)} ({cache_hits/len(commands)*100:.1f}%)")
    print(f"  🚀 Speedup: {sequential_time / cached_time:.2f}x faster")
    print()

    # Summary
    print("=" * 70)
    print("PERFORMANCE SUMMARY")
    print("=" * 70)
    print()
    print(f"{'Method':<30} {'Time (s)':<12} {'Throughput':<20} {'Speedup':<10}")
    print("-" * 70)
    print(f"{'Sequential (Baseline)':<30} {sequential_time:<12.3f} "
          f"{len(commands)/sequential_time:<20.1f} {'1.0x':<10}")
    print(f"{'Batch + Caching':<30} {batch_time:<12.3f} "
          f"{len(commands)/batch_time:<20.1f} {sequential_time/batch_time:<10.2f}x")
    print(f"{'Batch + Parallel':<30} {parallel_time:<12.3f} "
          f"{len(commands)/parallel_time:<20.1f} {sequential_time/parallel_time:<10.2f}x")
    print(f"{'Cached + Parallel':<30} {cached_time:<12.3f} "
          f"{len(commands)/cached_time:<20.1f} {sequential_time/cached_time:<10.2f}x")
    print()

    # Results verification
    print("=" * 70)
    print("RESULTS VERIFICATION")
    print("=" * 70)
    print()
    success_count = sum(1 for r in parallel_results if r.success)
    print(f"  ✓ Successful: {success_count}/{len(commands)}")
    print(f"  ✗ Failed: {len(commands) - success_count}/{len(commands)}")
    print()

    # Show sample results
    print("  Sample Results:")
    for i in range(min(3, len(parallel_results))):
        result = parallel_results[i]
        print(f"    [{i+1}] {result.command[:50]}...")
        print(f"        → Success: {result.success}, Cached: {result.cached}, "
              f"Duration: {result.duration_ms:.2f}ms")

    print()
    print("💡 Key Takeaways:")
    print("   • Caching provides significant speedup for repeated commands")
    print("   • Parallel execution scales with number of workers")
    print("   • Combined (cached + parallel) offers best performance")
    print(f"   • Maximum speedup achieved: {sequential_time/cached_time:.1f}x")
    print()


if __name__ == "__main__":
    main()
