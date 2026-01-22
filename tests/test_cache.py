"""Tests for cache module."""

import pytest
import time
from comptext_codex.cache import (
    ParserCache,
    ExecutorCache,
    cache_module_inference,
    hash_context
)


class TestParserCache:
    """Test cases for ParserCache."""

    def test_cache_miss(self):
        """Test cache miss."""
        cache = ParserCache()
        result = cache.get("@A:compress text")

        assert result is None

    def test_cache_hit(self):
        """Test cache hit."""
        cache = ParserCache()
        command = "@A:compress text"
        data = ["parsed", "data"]

        cache.set(command, data)
        result = cache.get(command)

        assert result == data

    def test_cache_expiry(self):
        """Test cache entry expiry."""
        cache = ParserCache(ttl=1)
        command = "@A:compress text"

        cache.set(command, ["data"])

        # Should hit immediately
        assert cache.get(command) is not None

        # Wait for expiry
        time.sleep(1.1)

        # Should miss after expiry
        assert cache.get(command) is None

    def test_cache_maxsize(self):
        """Test cache respects maxsize."""
        cache = ParserCache(maxsize=2)

        cache.set("cmd1", ["data1"])
        cache.set("cmd2", ["data2"])
        cache.set("cmd3", ["data3"])

        # Should have evicted oldest (cmd1)
        assert cache.get("cmd1") is None
        assert cache.get("cmd2") is not None
        assert cache.get("cmd3") is not None

    def test_cache_stats(self):
        """Test cache statistics."""
        cache = ParserCache()

        # Initial stats
        stats = cache.stats()
        assert stats['size'] == 0
        assert stats['hits'] == 0
        assert stats['misses'] == 0

        # Add entry
        cache.set("cmd1", ["data"])

        # Hit
        cache.get("cmd1")

        # Miss
        cache.get("cmd2")

        stats = cache.stats()
        assert stats['size'] == 1
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 0.5

    def test_cache_clear(self):
        """Test cache clearing."""
        cache = ParserCache()

        cache.set("cmd1", ["data1"])
        cache.set("cmd2", ["data2"])

        assert cache.stats()['size'] == 2

        cache.clear()

        assert cache.stats()['size'] == 0
        assert cache.stats()['hits'] == 0
        assert cache.stats()['misses'] == 0


class TestExecutorCache:
    """Test cases for ExecutorCache."""

    def test_cache_with_context(self):
        """Test caching with context hash."""
        cache = ExecutorCache()
        command = "@A:compress text"
        context_hash = "abc123"

        cache.set(command, context_hash, ["result"])
        result = cache.get(command, context_hash)

        assert result == ["result"]

    def test_different_context_miss(self):
        """Test cache miss with different context."""
        cache = ExecutorCache()
        command = "@A:compress text"

        cache.set(command, "context1", ["result1"])

        # Different context should miss
        result = cache.get(command, "context2")
        assert result is None

    def test_executor_cache_stats(self):
        """Test executor cache statistics."""
        cache = ExecutorCache()

        cache.set("cmd", "ctx", ["data"])
        cache.get("cmd", "ctx")  # Hit
        cache.get("cmd", "different")  # Miss

        stats = cache.stats()
        assert stats['hits'] == 1
        assert stats['misses'] == 1

    def test_executor_cache_maxsize(self):
        """Test executor cache respects maxsize."""
        cache = ExecutorCache(maxsize=2)

        cache.set("cmd1", "ctx", ["data1"])
        cache.set("cmd2", "ctx", ["data2"])
        cache.set("cmd3", "ctx", ["data3"])

        # Should have evicted first
        assert cache.get("cmd1", "ctx") is None
        assert cache.get("cmd2", "ctx") is not None


class TestCacheModuleInference:
    """Test module inference caching."""

    def test_cache_hit(self):
        """Test that module inference is cached."""
        # First call
        result1 = cache_module_inference("CODE_ANALYZE")

        # Second call (should be cached)
        result2 = cache_module_inference("CODE_ANALYZE")

        assert result1 == result2
        assert result1 == 'B'

    def test_different_commands(self):
        """Test different command names."""
        assert cache_module_inference("CODE_") == 'B'
        assert cache_module_inference("AUTOML") == 'E'
        assert cache_module_inference("DEPLOY") == 'J'

    def test_default_module(self):
        """Test default module for unknown commands."""
        result = cache_module_inference("UNKNOWN_COMMAND")
        assert result == 'A'


class TestHashContext:
    """Test context hashing."""

    def test_empty_context(self):
        """Test hashing empty context."""
        result = hash_context(None)
        assert result == "empty"

        result = hash_context({})
        assert result == "empty"

    def test_consistent_hash(self):
        """Test context produces consistent hash."""
        context = {'key': 'value', 'num': 42}

        hash1 = hash_context(context)
        hash2 = hash_context(context)

        assert hash1 == hash2

    def test_different_contexts(self):
        """Test different contexts produce different hashes."""
        context1 = {'key': 'value1'}
        context2 = {'key': 'value2'}

        hash1 = hash_context(context1)
        hash2 = hash_context(context2)

        assert hash1 != hash2

    def test_order_independent(self):
        """Test hash is order-independent."""
        context1 = {'a': 1, 'b': 2}
        context2 = {'b': 2, 'a': 1}

        hash1 = hash_context(context1)
        hash2 = hash_context(context2)

        # Should be same due to sorting
        assert hash1 == hash2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
