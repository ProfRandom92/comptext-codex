"""Batch processing for high-performance command execution.

Enables efficient execution of multiple commands with parallel processing,
result caching, and optimized resource usage.
"""

from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from dataclasses import dataclass
import time


@dataclass
class BatchResult:
    """Result from batch command execution."""
    command: str
    success: bool
    result: Any
    duration_ms: float
    error: Optional[str] = None
    cached: bool = False


class BatchExecutor:
    """High-performance batch executor for CompText commands."""

    def __init__(self,
                 executor_instance,
                 max_workers: int = 4,
                 use_cache: bool = True,
                 parallel: bool = True):
        """Initialize batch executor.

        Args:
            executor_instance: CompTextExecutor instance
            max_workers: Maximum parallel workers
            use_cache: Enable result caching
            parallel: Enable parallel execution
        """
        self.executor = executor_instance
        self.max_workers = max_workers
        self.use_cache = use_cache
        self.parallel = parallel
        self._cache: Dict[str, BatchResult] = {}

    def execute_batch(self,
                      commands: List[str],
                      context: Optional[Dict[str, Any]] = None,
                      progress_callback: Optional[Callable[[int, int], None]] = None
                      ) -> List[BatchResult]:
        """Execute batch of commands.

        Args:
            commands: List of CompText commands
            context: Shared execution context
            progress_callback: Optional callback(completed, total)

        Returns:
            List of batch results
        """
        if self.parallel and len(commands) > 1:
            return self._execute_parallel(commands, context, progress_callback)
        else:
            return self._execute_sequential(commands, context, progress_callback)

    def _execute_sequential(self,
                           commands: List[str],
                           context: Optional[Dict[str, Any]],
                           progress_callback: Optional[Callable[[int, int], None]]
                           ) -> List[BatchResult]:
        """Execute commands sequentially.

        Args:
            commands: Commands to execute
            context: Execution context
            progress_callback: Progress callback

        Returns:
            List of results
        """
        results = []
        total = len(commands)

        for i, cmd in enumerate(commands):
            # Check cache
            if self.use_cache and cmd in self._cache:
                cached_result = self._cache[cmd]
                results.append(BatchResult(
                    command=cmd,
                    success=cached_result.success,
                    result=cached_result.result,
                    duration_ms=0.0,
                    error=cached_result.error,
                    cached=True
                ))
            else:
                # Execute command
                start = time.time()
                try:
                    exec_results = self.executor.execute(cmd, context=context)
                    duration_ms = (time.time() - start) * 1000

                    if exec_results and len(exec_results) > 0:
                        first_result = exec_results[0]
                        result = BatchResult(
                            command=cmd,
                            success=first_result.success,
                            result=first_result.result,
                            duration_ms=duration_ms,
                            error=first_result.error,
                            cached=False
                        )
                    else:
                        result = BatchResult(
                            command=cmd,
                            success=False,
                            result=None,
                            duration_ms=duration_ms,
                            error="No results returned",
                            cached=False
                        )

                    # Cache successful results
                    if self.use_cache and result.success:
                        self._cache[cmd] = result

                    results.append(result)

                except Exception as e:
                    duration_ms = (time.time() - start) * 1000
                    results.append(BatchResult(
                        command=cmd,
                        success=False,
                        result=None,
                        duration_ms=duration_ms,
                        error=str(e),
                        cached=False
                    ))

            # Progress callback
            if progress_callback:
                progress_callback(i + 1, total)

        return results

    def _execute_parallel(self,
                         commands: List[str],
                         context: Optional[Dict[str, Any]],
                         progress_callback: Optional[Callable[[int, int], None]]
                         ) -> List[BatchResult]:
        """Execute commands in parallel.

        Args:
            commands: Commands to execute
            context: Execution context
            progress_callback: Progress callback

        Returns:
            List of results (in original order)
        """
        results: Dict[int, BatchResult] = {}
        total = len(commands)
        completed = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            # Submit all tasks
            future_to_idx = {}
            for idx, cmd in enumerate(commands):
                # Check cache
                if self.use_cache and cmd in self._cache:
                    cached_result = self._cache[cmd]
                    results[idx] = BatchResult(
                        command=cmd,
                        success=cached_result.success,
                        result=cached_result.result,
                        duration_ms=0.0,
                        error=cached_result.error,
                        cached=True
                    )
                    completed += 1
                    if progress_callback:
                        progress_callback(completed, total)
                else:
                    future = pool.submit(self._execute_single, cmd, context)
                    future_to_idx[future] = idx

            # Collect results
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    result = future.result()
                    results[idx] = result

                    # Cache successful results
                    if self.use_cache and result.success:
                        self._cache[result.command] = result

                except Exception as e:
                    results[idx] = BatchResult(
                        command=commands[idx],
                        success=False,
                        result=None,
                        duration_ms=0.0,
                        error=str(e),
                        cached=False
                    )

                completed += 1
                if progress_callback:
                    progress_callback(completed, total)

        # Return in original order
        return [results[i] for i in range(len(commands))]

    def _execute_single(self, cmd: str, context: Optional[Dict[str, Any]]) -> BatchResult:
        """Execute a single command.

        Args:
            cmd: Command to execute
            context: Execution context

        Returns:
            Batch result
        """
        start = time.time()
        try:
            exec_results = self.executor.execute(cmd, context=context)
            duration_ms = (time.time() - start) * 1000

            if exec_results and len(exec_results) > 0:
                first_result = exec_results[0]
                return BatchResult(
                    command=cmd,
                    success=first_result.success,
                    result=first_result.result,
                    duration_ms=duration_ms,
                    error=first_result.error,
                    cached=False
                )
            else:
                return BatchResult(
                    command=cmd,
                    success=False,
                    result=None,
                    duration_ms=duration_ms,
                    error="No results returned",
                    cached=False
                )

        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            return BatchResult(
                command=cmd,
                success=False,
                result=None,
                duration_ms=duration_ms,
                error=str(e),
                cached=False
            )

    def get_stats(self) -> Dict[str, Any]:
        """Get batch execution statistics.

        Returns:
            Statistics dictionary
        """
        return {
            'cache_size': len(self._cache),
            'max_workers': self.max_workers,
            'cache_enabled': self.use_cache,
            'parallel_enabled': self.parallel
        }

    def clear_cache(self):
        """Clear the result cache."""
        self._cache.clear()


def create_batch_executor(executor_instance,
                         max_workers: int = 4,
                         use_cache: bool = True,
                         parallel: bool = True) -> BatchExecutor:
    """Factory function to create batch executor.

    Args:
        executor_instance: CompTextExecutor instance
        max_workers: Maximum parallel workers
        use_cache: Enable caching
        parallel: Enable parallel execution

    Returns:
        BatchExecutor instance
    """
    return BatchExecutor(
        executor_instance=executor_instance,
        max_workers=max_workers,
        use_cache=use_cache,
        parallel=parallel
    )
