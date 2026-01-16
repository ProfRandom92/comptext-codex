"""Advanced caching mechanisms for CompText-Codex.

Implements LRU caching for parser results and executor results to dramatically
improve performance for repeated commands.
"""

from functools import lru_cache
from typing import Dict, List, Tuple, Any, Optional
import hashlib
import time


class ParserCache:
    """LRU cache for parser results with TTL support."""

    def __init__(self, maxsize: int = 1000, ttl: int = 3600):
        """Initialize parser cache.

        Args:
            maxsize: Maximum number of cached entries
            ttl: Time-to-live in seconds (default: 1 hour)
        """
        self.maxsize = maxsize
        self.ttl = ttl
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._access_times: Dict[str, float] = {}
        self._hits = 0
        self._misses = 0

    def get(self, command_string: str) -> Optional[List]:
        """Get cached parse result.

        Args:
            command_string: Command to look up

        Returns:
            Cached parse result or None if not found/expired
        """
        key = self._hash_command(command_string)

        if key in self._cache:
            result, timestamp = self._cache[key]

            # Check if expired
            if time.time() - timestamp > self.ttl:
                del self._cache[key]
                del self._access_times[key]
                self._misses += 1
                return None

            # Update access time
            self._access_times[key] = time.time()
            self._hits += 1
            return result

        self._misses += 1
        return None

    def set(self, command_string: str, result: List):
        """Cache parse result.

        Args:
            command_string: Command string
            result: Parse result to cache
        """
        key = self._hash_command(command_string)

        # Evict oldest if at capacity
        if len(self._cache) >= self.maxsize:
            oldest_key = min(self._access_times, key=self._access_times.get)
            del self._cache[oldest_key]
            del self._access_times[oldest_key]

        self._cache[key] = (result, time.time())
        self._access_times[key] = time.time()

    def clear(self):
        """Clear all cached entries."""
        self._cache.clear()
        self._access_times.clear()
        self._hits = 0
        self._misses = 0

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0

        return {
            'size': len(self._cache),
            'maxsize': self.maxsize,
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': hit_rate,
            'total_requests': total
        }

    def _hash_command(self, command_string: str) -> str:
        """Generate hash for command string.

        Args:
            command_string: Command to hash

        Returns:
            Hash string
        """
        return hashlib.md5(command_string.encode()).hexdigest()


class ExecutorCache:
    """Cache for executor results with context-awareness."""

    def __init__(self, maxsize: int = 500):
        """Initialize executor cache.

        Args:
            maxsize: Maximum number of cached entries
        """
        self.maxsize = maxsize
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._hits = 0
        self._misses = 0

    def get(self, command_string: str, context_hash: str) -> Optional[List]:
        """Get cached execution result.

        Args:
            command_string: Command string
            context_hash: Hash of execution context

        Returns:
            Cached result or None
        """
        key = self._make_key(command_string, context_hash)

        if key in self._cache:
            result, timestamp = self._cache[key]
            self._hits += 1
            return result

        self._misses += 1
        return None

    def set(self, command_string: str, context_hash: str, result: List):
        """Cache execution result.

        Args:
            command_string: Command string
            context_hash: Hash of execution context
            result: Execution result
        """
        key = self._make_key(command_string, context_hash)

        # Simple FIFO eviction
        if len(self._cache) >= self.maxsize:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        self._cache[key] = (result, time.time())

    def clear(self):
        """Clear all cached entries."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0

        return {
            'size': len(self._cache),
            'maxsize': self.maxsize,
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': hit_rate,
            'total_requests': total
        }

    def _make_key(self, command_string: str, context_hash: str) -> str:
        """Create cache key from command and context.

        Args:
            command_string: Command string
            context_hash: Context hash

        Returns:
            Cache key
        """
        combined = f"{command_string}:{context_hash}"
        return hashlib.md5(combined.encode()).hexdigest()


@lru_cache(maxsize=2048)
def cache_module_inference(command_name: str) -> str:
    """Cache module inference results.

    Args:
        command_name: Command name to infer module for

    Returns:
        Module code (A-M)
    """
    # This will be populated by the actual inference logic
    module_map = {
        'CODE_': 'B',
        'ANALYZE': 'B',
        'FORMAT': 'C',
        'MODEL_': 'D',
        'AUTOML': 'E',
        'FEATURE_': 'E',
        'DOC_': 'F',
        'CHANGELOG': 'F',
        'TEST_': 'G',
        'DB_': 'H',
        'SEC_': 'I',
        'GDPR': 'I',
        'DEPLOY': 'J',
        'CI_CD': 'J',
        'COMPONENT': 'K',
        'DASHBOARD': 'K',
        'EXTRACT': 'L',
        'TRANSFORM': 'L',
        'LOAD': 'L',
        'AGENT_': 'M',
        'TASK_': 'M',
    }

    for prefix, module in module_map.items():
        if command_name.upper().startswith(prefix):
            return module

    return 'A'


def hash_context(context: Optional[Dict[str, Any]]) -> str:
    """Generate hash for execution context.

    Args:
        context: Execution context dictionary

    Returns:
        Context hash string
    """
    if not context:
        return "empty"

    # Create stable hash from context
    context_str = str(sorted(context.items()))
    return hashlib.md5(context_str.encode()).hexdigest()[:16]
