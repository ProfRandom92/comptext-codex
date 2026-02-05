"""Comprehensive tests for CompText V5.0 ULTRA Parser."""

import pytest
from src.comptext_codex.parser_v5 import (
    CompTextParserV5,
    CompTextCommandV5,
    parse_v5,
    encode_v5
)


class TestParserV5Basic:
    """Test basic V5 parsing functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.parser = CompTextParserV5()

    def test_single_command_simple(self):
        """Test simple single command parsing."""
        result = self.parser.parse("C;P:FIB")
        assert len(result) == 1
        assert result[0].command == 'C'
        assert result[0].language == 'P'
        assert result[0].task == 'FIB'

    def test_single_command_with_modifiers(self):
        """Test command with modifiers."""
        result = self.parser.parse("T;P;R:FIB")
        assert len(result) == 1
        assert result[0].command == 'T'
        assert result[0].language == 'P'
        assert 'R' in result[0].modifiers
        assert result[0].task == 'FIB'

    def test_command_without_language(self):
        """Test command without language specification."""
        result = self.parser.parse("D:SUM")
        assert len(result) == 1
        assert result[0].command == 'D'
        assert result[0].language is None
        assert result[0].task == 'SUM'

    def test_command_with_multiple_modifiers(self):
        """Test command with multiple modifiers."""
        result = self.parser.parse("C;P;R;C:FAST")
        assert len(result) == 1
        assert result[0].command == 'C'
        assert result[0].language == 'P'
        assert 'R' in result[0].modifiers
        assert 'C' in result[0].modifiers

    def test_all_commands(self):
        """Test all single-char commands."""
        commands = ['C', 'F', 'M', 'T', 'D', 'E', 'O', 'A']
        for cmd in commands:
            result = self.parser.parse(f"{cmd}:TEST")
            assert result[0].command == cmd

    def test_all_languages(self):
        """Test all single-char languages."""
        languages = ['P', 'J', 'T', 'R', 'G', 'S', 'H']
        for lang in languages:
            result = self.parser.parse(f"C;{lang}:TEST")
            assert result[0].language == lang


class TestParserV5Batch:
    """Test V5 batch command parsing."""

    def setup_method(self):
        """Setup test fixtures."""
        self.parser = CompTextParserV5()

    def test_simple_batch(self):
        """Test simple batch with 3 commands."""
        result = self.parser.parse("B:[D:SUM]|[C;P:FIB]|[E;C:WHY]")
        assert len(result) == 3
        assert result[0].command == 'D'
        assert result[1].command == 'C'
        assert result[2].command == 'E'

    def test_complex_batch(self):
        """Test complex batch from benchmark."""
        result = self.parser.parse("B:[A:STRUCT]|[F;T:MEM]|[O;S:Q]|[D:API]")
        assert len(result) == 4
        assert result[0].task == 'STRUCT'
        assert result[1].language == 'T'
        assert result[2].command == 'O'
        assert result[3].task == 'API'

    def test_batch_with_modifiers(self):
        """Test batch commands with modifiers."""
        result = self.parser.parse("B:[T;P;R:FIB]|[C;J;N:UTIL]")
        assert len(result) == 2
        assert 'R' in result[0].modifiers
        assert 'N' in result[1].modifiers

    def test_empty_batch(self):
        """Test empty batch handling."""
        result = self.parser.parse("B:[]")
        assert len(result) == 1
        # Should create one empty command


class TestParserV5Encoding:
    """Test V5 command encoding."""

    def setup_method(self):
        """Setup test fixtures."""
        self.parser = CompTextParserV5()

    def test_encode_simple(self):
        """Test simple command encoding."""
        result = self.parser.encode('CODE', 'PYTHON', task='FIB')
        assert result == 'C;P:FIB'

    def test_encode_with_modifiers(self):
        """Test encoding with modifiers."""
        result = self.parser.encode('TEST', 'PYTHON', ['ROBUST'], 'FIB')
        assert result == 'T;P;R:FIB'

    def test_encode_without_language(self):
        """Test encoding without language."""
        result = self.parser.encode('DOCUMENT', task='SUM')
        assert result == 'D:SUM'

    def test_encode_batch(self):
        """Test batch encoding."""
        commands = [
            ('DOCUMENT', None, None, 'SUM'),
            ('CODE', 'PYTHON', None, 'FIB'),
            ('EXPLAIN', None, ['CONCISE'], 'WHY')
        ]
        result = self.parser.encode_batch(commands)
        assert result == 'B:[D:SUM]|[C;P:FIB]|[E;C:WHY]'

    def test_roundtrip_simple(self):
        """Test parse -> encode roundtrip."""
        original = "C;P:FIB"
        parsed = self.parser.parse(original)
        encoded = self.parser.encode(
            self.parser.COMMANDS[parsed[0].command],
            self.parser.LANGUAGES.get(parsed[0].language) if parsed[0].language else None,
            task=parsed[0].task
        )
        assert encoded == original

    def test_roundtrip_batch(self):
        """Test batch parse -> encode roundtrip."""
        original = "B:[D:SUM]|[C;P:FIB]|[E;C:WHY]"
        parsed = self.parser.parse(original)

        commands = []
        for cmd in parsed:
            commands.append((
                self.parser.COMMANDS[cmd.command],
                self.parser.LANGUAGES.get(cmd.language) if cmd.language else None,
                [self.parser.MODIFIERS[m] for m in cmd.modifiers] if cmd.modifiers else None,
                cmd.task
            ))

        encoded = self.parser.encode_batch(commands)
        assert encoded == original


class TestParserV5Conversion:
    """Test V5 to V4 conversion."""

    def setup_method(self):
        """Setup test fixtures."""
        self.parser = CompTextParserV5()

    def test_v5_to_v4_simple(self):
        """Test simple V5 to V4 conversion."""
        v5_cmd = self.parser.parse("C;P:FIB")[0]
        v4_format = self.parser.to_v4_format(v5_cmd)
        assert 'CMD:CODE' in v4_format
        assert 'LNG:PYTHON' in v4_format
        assert 'TSK:FIB' in v4_format

    def test_v5_to_v4_with_modifiers(self):
        """Test V5 to V4 conversion with modifiers."""
        v5_cmd = self.parser.parse("T;P;R:FIB")[0]
        v4_format = self.parser.to_v4_format(v5_cmd)
        assert 'CMD:TEST' in v4_format
        assert 'LNG:PYTHON' in v4_format
        assert 'STY:ROBUST' in v4_format
        assert 'TSK:FIB' in v4_format

    def test_v5_to_v4_batch(self):
        """Test batch V5 to V4 conversion."""
        v5_cmds = self.parser.parse("B:[D:SUM]|[C;P:FIB]|[E;C:WHY]")
        v4_formats = [self.parser.to_v4_format(cmd) for cmd in v5_cmds]

        assert 'CMD:DOCUMENT' in v4_formats[0]
        assert 'CMD:CODE' in v4_formats[1]
        assert 'CMD:EXPLAIN' in v4_formats[2]


class TestParserV5TokenReduction:
    """Test token reduction calculations."""

    def setup_method(self):
        """Setup test fixtures."""
        self.parser = CompTextParserV5()

    def test_calculate_reduction_simple(self):
        """Test token reduction calculation."""
        nl = "Write a Python function for Fibonacci"
        v5 = "C;P:FIB"

        stats = self.parser.calculate_token_reduction(nl, v5)

        assert stats['natural_tokens'] == 6
        assert stats['v5_tokens'] == 1
        assert stats['reduction_percent'] > 80

    def test_calculate_reduction_batch(self):
        """Test batch command reduction."""
        nl = "Summarize the repository then write Python Fibonacci and explain why it's fast"
        v5 = "B:[D:SUM]|[C;P:FIB]|[E;C:WHY]"

        stats = self.parser.calculate_token_reduction(nl, v5)

        assert stats['tokens_saved'] > 10
        assert stats['reduction_percent'] > 85

    def test_benchmark_examples(self):
        """Test all benchmark examples from V5 spec."""
        examples = [
            ("Write comprehensive unit tests for the Fibonacci function in Python with edge cases", "T;P;R:FIB"),
            ("Generate a Python FastAPI endpoint with PostgreSQL integration and proper error handling", "C;P;FA;PG;R"),
        ]

        for nl, v5 in examples:
            stats = self.parser.calculate_token_reduction(nl, v5)
            assert stats['reduction_percent'] > 80, f"Failed for: {nl}"


class TestParserV5EdgeCases:
    """Test edge cases and error handling."""

    def setup_method(self):
        """Setup test fixtures."""
        self.parser = CompTextParserV5()

    def test_empty_string(self):
        """Test empty string handling."""
        result = self.parser.parse("")
        assert len(result) >= 0

    def test_whitespace_handling(self):
        """Test whitespace in various positions."""
        result = self.parser.parse(" C ; P : FIB ")
        assert len(result) == 1
        assert result[0].command == 'C'

    def test_malformed_batch(self):
        """Test malformed batch command."""
        result = self.parser.parse("B:[C;P:FIB")
        # Should handle gracefully
        assert len(result) >= 0

    def test_unknown_command_char(self):
        """Test unknown command character."""
        result = self.parser.parse("X;P:TEST")
        assert len(result) == 1
        # Should still parse but command might be None

    def test_task_with_special_chars(self):
        """Test task names with special characters."""
        result = self.parser.parse("C;P:CALC_FIB_N")
        assert result[0].task == 'CALC_FIB_N'

    def test_nested_brackets(self):
        """Test nested brackets in batch."""
        # Should handle gracefully even if not typical usage
        result = self.parser.parse("B:[[C;P:FIB]]")
        assert len(result) >= 0


class TestParserV5RealWorld:
    """Test real-world usage scenarios."""

    def setup_method(self):
        """Setup test fixtures."""
        self.parser = CompTextParserV5()

    def test_original_mission_command(self):
        """Test the original mission command from the user."""
        original_v4 = "BATCH: [CMD:DOC; TSK:SUMMARY_OF_REPO; FMT:MD] || [CMD:CODE; LNG:PY; TSK:CALC_FIBONACCI] || [CMD:EXPL; STY:CONCISE; TSK:WHY_COMPTEXT_IS_FAST]"
        v5_equivalent = "B:[D:SUM]|[C;P:FIB]|[E;C:WHY]"

        result = self.parser.parse(v5_equivalent)
        assert len(result) == 3

    def test_test_generation_scenario(self):
        """Test the test generation use case."""
        v5_cmd = "T;P;R:FIB"
        result = self.parser.parse(v5_cmd)

        assert result[0].command == 'T'
        assert result[0].language == 'P'
        assert 'R' in result[0].modifiers

    def test_complex_workflow(self):
        """Test complex multi-step workflow."""
        v5_cmd = "B:[A:STRUCT]|[F;T:MEM]|[O;S:Q]|[D:API]"
        result = self.parser.parse(v5_cmd)

        assert len(result) == 4
        assert result[0].command == 'A'  # Analyze
        assert result[1].command == 'F'  # Fix
        assert result[2].command == 'O'  # Optimize
        assert result[3].command == 'D'  # Document


# Convenience function tests
class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_parse_v5_function(self):
        """Test parse_v5 convenience function."""
        result = parse_v5("C;P:FIB")
        assert len(result) == 1
        assert result[0].command == 'C'

    def test_encode_v5_function(self):
        """Test encode_v5 convenience function."""
        result = encode_v5('CODE', 'PYTHON', task='FIB')
        assert result == 'C;P:FIB'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
