"""Tests for the KVTC (Key-Value Transform Coding) compression strategy.

Validates that the KVTCCompressor preserves Attention Sinks (start of text)
and the Sliding Window (end of text) while compressing the middle section.
"""

import pytest

from comptext_codex.kvtc import KVTCCompressor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_text(length: int, *, char: str = "x") -> str:
    """Create a deterministic text string of exactly *length* characters."""
    return char * length


def _make_varied_text(length: int) -> str:
    """Create text with repeated words suitable for compression."""
    base = "the quick brown fox jumps over the lazy dog again and again "
    reps = (length // len(base)) + 1
    return (base * reps)[:length]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestKVTCStrategy:
    """Test suite for the KVTCCompressor."""

    def test_sink_integrity(self) -> None:
        """Verify the first 500 chars remain absolutely unchanged."""
        text = _make_varied_text(3000)
        compressor = KVTCCompressor(sink_chars=500, window_chars=1000)
        result = compressor.compress(text)

        assert result[:500] == text[:500]

    def test_window_integrity(self) -> None:
        """Verify the last 1000 chars remain absolutely unchanged."""
        text = _make_varied_text(3000)
        compressor = KVTCCompressor(sink_chars=500, window_chars=1000)
        result = compressor.compress(text)

        assert result[-1000:] == text[-1000:]

    def test_middle_compression(self) -> None:
        """Verify overall length is reduced compared to the original."""
        text = _make_varied_text(3000)
        compressor = KVTCCompressor(sink_chars=500, window_chars=1000)
        result = compressor.compress(text)

        assert len(result) < len(text)

    def test_short_text_bypass(self) -> None:
        """Verify that short texts are not touched."""
        short_text = _make_varied_text(1200)
        compressor = KVTCCompressor(sink_chars=500, window_chars=1000)
        result = compressor.compress(short_text)

        assert result == short_text

    # ------------------------------------------------------------------
    # Additional edge-case coverage
    # ------------------------------------------------------------------

    def test_exact_boundary_text_unchanged(self) -> None:
        """Text with exactly sink+window length is returned unchanged."""
        text = _make_text(1500, char="a")
        compressor = KVTCCompressor(sink_chars=500, window_chars=1000)
        result = compressor.compress(text)

        assert result == text

    def test_empty_text(self) -> None:
        """Empty string is returned unchanged."""
        compressor = KVTCCompressor()
        assert compressor.compress("") == ""

    def test_custom_sink_window_sizes(self) -> None:
        """Custom sink/window sizes are honoured."""
        text = _make_varied_text(500)
        compressor = KVTCCompressor(sink_chars=50, window_chars=100)
        result = compressor.compress(text)

        assert result[:50] == text[:50]
        assert result[-100:] == text[-100:]
        assert len(result) < len(text)
