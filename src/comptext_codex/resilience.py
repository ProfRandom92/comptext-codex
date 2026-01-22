"""Resilience utilities for CompText-Codex.

Provides retry logic, circuit breakers, timeouts, and fault tolerance features.
"""

import time
import functools
from typing import Callable, Any, Optional, Type, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    exceptions: Tuple[Type[Exception], ...] = (Exception,)


def retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """Decorator for automatic retry with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        exceptions: Tuple of exceptions to catch

    Returns:
        Decorated function

    Example:
        @retry(max_attempts=3, initial_delay=1.0)
        def unstable_function():
            # May fail occasionally
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < max_attempts - 1:
                        # Calculate delay with exponential backoff
                        delay = min(
                            initial_delay * (exponential_base ** attempt),
                            max_delay
                        )

                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )

                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func.__name__}: {e}"
                        )

            # All retries exhausted
            raise last_exception

        wrapper.retry_config = RetryConfig(
            max_attempts=max_attempts,
            initial_delay=initial_delay,
            max_delay=max_delay,
            exponential_base=exponential_base,
            exceptions=exceptions
        )

        return wrapper

    return decorator


def timeout(seconds: float):
    """Decorator for function timeout.

    Args:
        seconds: Timeout in seconds

    Returns:
        Decorated function

    Note:
        This is a simple timeout implementation. For production use,
        consider using signal-based timeouts or async timeouts.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError(f"Function {func.__name__} timed out after {seconds}s")

            # Set signal handler
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(seconds))

            try:
                result = func(*args, **kwargs)
            finally:
                # Restore old handler and cancel alarm
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

            return result

        return wrapper

    return decorator


class CircuitBreaker:
    """Circuit breaker pattern implementation.

    Protects against cascading failures by stopping requests
    to a failing service temporarily.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception
    ):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type to monitor
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half_open

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Call function through circuit breaker.

        Args:
            func: Function to call
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If circuit is open
        """
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half_open"
            else:
                raise Exception(
                    f"Circuit breaker is OPEN. Recovery in "
                    f"{self._time_to_recovery():.1f}s"
                )

        try:
            result = func(*args, **kwargs)

            # Success - reset if in half_open
            if self.state == "half_open":
                self._reset()

            return result

        except self.expected_exception as e:
            self._record_failure()
            raise e

    def _record_failure(self):
        """Record a failure."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(
                f"Circuit breaker opened after {self.failure_count} failures"
            )

    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset."""
        if self.last_failure_time is None:
            return True

        return (time.time() - self.last_failure_time) >= self.recovery_timeout

    def _time_to_recovery(self) -> float:
        """Get time remaining until recovery attempt."""
        if self.last_failure_time is None:
            return 0.0

        elapsed = time.time() - self.last_failure_time
        return max(0.0, self.recovery_timeout - elapsed)

    def _reset(self):
        """Reset circuit breaker."""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"
        logger.info("Circuit breaker reset to CLOSED state")

    def get_state(self) -> str:
        """Get current circuit breaker state."""
        return self.state


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    expected_exception: Type[Exception] = Exception
):
    """Decorator for circuit breaker pattern.

    Args:
        failure_threshold: Failures before opening circuit
        recovery_timeout: Recovery wait time in seconds
        expected_exception: Exception type to monitor

    Returns:
        Decorated function
    """
    breaker = CircuitBreaker(
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout,
        expected_exception=expected_exception
    )

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)

        wrapper.circuit_breaker = breaker
        return wrapper

    return decorator


class Bulkhead:
    """Bulkhead pattern for resource isolation.

    Limits concurrent execution to prevent resource exhaustion.
    """

    def __init__(self, max_concurrent: int = 10):
        """Initialize bulkhead.

        Args:
            max_concurrent: Maximum concurrent executions
        """
        self.max_concurrent = max_concurrent
        self.current_count = 0

    def __enter__(self):
        """Enter bulkhead context."""
        if self.current_count >= self.max_concurrent:
            raise RuntimeError(
                f"Bulkhead limit reached: {self.max_concurrent} concurrent executions"
            )

        self.current_count += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit bulkhead context."""
        self.current_count -= 1

    def is_available(self) -> bool:
        """Check if bulkhead has capacity."""
        return self.current_count < self.max_concurrent

    def get_current_load(self) -> int:
        """Get current concurrent execution count."""
        return self.current_count


# Global circuit breakers for common operations
_circuit_breakers = {}


def get_circuit_breaker(name: str, **kwargs) -> CircuitBreaker:
    """Get or create a named circuit breaker.

    Args:
        name: Circuit breaker name
        **kwargs: CircuitBreaker configuration

    Returns:
        CircuitBreaker instance
    """
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(**kwargs)

    return _circuit_breakers[name]
