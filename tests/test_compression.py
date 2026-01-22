"""Tests for compression module."""

import pytest
from comptext_codex.compression import (
    CommandCompressor,
    CompressionLevel,
    BatchOptimizer,
    demonstrate_compression_levels
)


class TestCommandCompressor:
    """Test cases for CommandCompressor."""

    def test_no_compression(self):
        """Test NONE compression level."""
        compressor = CommandCompressor(CompressionLevel.NONE)
        command = "@AUTOML[task=classification]"
        compressed = compressor.compress_command(command)

        assert compressed == command

    def test_basic_compression(self):
        """Test BASIC compression level."""
        compressor = CommandCompressor(CompressionLevel.BASIC)
        command = "@ANALYZE[performance=high]"
        compressed = compressor.compress_command(command)

        # Should have abbreviations
        assert "perf" in compressed or "anlz" in compressed

    def test_moderate_compression(self):
        """Test MODERATE compression level."""
        compressor = CommandCompressor(CompressionLevel.MODERATE)
        command = "@CMD[framework=react, language=python]"
        compressed = compressor.compress_command(command)

        # Should have parameter shortcuts
        assert "fw=" in compressed or "lang=" in compressed

    def test_aggressive_compression(self):
        """Test AGGRESSIVE compression level."""
        compressor = CommandCompressor(CompressionLevel.AGGRESSIVE)
        command = "@CMD[param = value, test = true]"
        compressed = compressor.compress_command(command)

        # Should remove spaces around =
        assert " = " not in compressed

    def test_ultra_compression(self):
        """Test ULTRA compression level."""
        compressor = CommandCompressor(CompressionLevel.ULTRA)
        command = "@AUTOML[include=features, test=true]"
        compressed = compressor.compress_command(command)

        # Should convert true to 1
        assert "1" in compressed or "=1" in compressed

    def test_estimate_savings(self):
        """Test savings estimation."""
        compressor = CommandCompressor(CompressionLevel.MODERATE)
        original = "@ANALYZE[performance=high, optimization=enabled]"
        compressed = compressor.compress_command(original)

        savings = compressor.estimate_savings(original, compressed)

        assert 'original_tokens' in savings
        assert 'compressed_tokens' in savings
        assert 'savings_percent' in savings
        assert savings['savings_percent'] >= 0

    def test_real_world_command(self):
        """Test with real-world command."""
        compressor = CommandCompressor(CompressionLevel.AGGRESSIVE)
        command = "@CODE_ANALYZE[performance_bottleneck, complexity] + @CODE_OPTIMIZE[explain=detail]"
        compressed = compressor.compress_command(command)

        savings = compressor.estimate_savings(command, compressed)

        # Aggressive should have savings (removes spaces)
        assert savings['savings_percent'] >= 0  # At least not negative
        # Compressed should be different
        assert compressed != command


class TestBatchOptimizer:
    """Test cases for BatchOptimizer."""

    def test_optimize_batch(self):
        """Test batch optimization."""
        optimizer = BatchOptimizer()
        commands = [
            "@A:compress text one",
            "@A:compress text two",
            "@B:analyze data"
        ]

        optimized, metrics = optimizer.optimize_batch(commands)

        assert len(optimized) == len(commands)
        assert 'batch_size' in metrics
        assert 'savings_percent' in metrics
        assert metrics['batch_size'] == 3

    def test_merge_similar_commands(self):
        """Test merging similar commands."""
        optimizer = BatchOptimizer()
        commands = [
            "@A:compress text1",
            "@A:expand text2",
            "@B:analyze data"
        ]

        merged = optimizer.merge_similar_commands(commands)

        # Should have some merging
        assert len(merged) <= len(commands)


class TestDemonstrateCompressionLevels:
    """Test compression level demonstration."""

    def test_demonstrate_all_levels(self):
        """Test demonstrating all compression levels."""
        command = "@AUTOML[task=classification, metric=accuracy]"
        results = demonstrate_compression_levels(command)

        # Should have results for all levels
        assert len(results) == 5  # NONE, BASIC, MODERATE, AGGRESSIVE, ULTRA

        # All levels should have results
        for level in CompressionLevel:
            assert level.name in results
            assert 'compressed' in results[level.name]
            assert 'metrics' in results[level.name]

    def test_progressive_compression(self):
        """Test that higher levels compress more."""
        command = "@ANALYZE[performance=high, optimization=enabled]"
        results = demonstrate_compression_levels(command)

        # Extract token counts
        none_tokens = results['NONE']['metrics']['compressed_tokens']
        basic_tokens = results['BASIC']['metrics']['compressed_tokens']
        ultra_tokens = results['ULTRA']['metrics']['compressed_tokens']

        # Higher compression should result in fewer tokens
        assert ultra_tokens <= basic_tokens <= none_tokens


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
