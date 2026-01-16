"""Tests for CompText Parser."""

import pytest
from comptext_codex.parser import CompTextParser, CompTextCommand, parse


class TestCompTextParser:
    """Test cases for CompTextParser."""

    def test_simple_command(self):
        """Test parsing simple command format."""
        parser = CompTextParser()
        commands = parser.parse("@A:compress The quick brown fox")

        assert len(commands) == 1
        cmd = commands[0]
        assert cmd.module == 'A'
        assert cmd.command == 'compress'
        assert 'quick brown fox' in ' '.join(cmd.args)

    def test_parametric_command(self):
        """Test parsing parametric command format."""
        parser = CompTextParser()
        commands = parser.parse("@CODE_ANALYZE[perf_bottleneck, complexity]")

        assert len(commands) == 1
        cmd = commands[0]
        assert cmd.command == 'CODE_ANALYZE'
        assert 'perf_bottleneck' in cmd.args
        assert 'complexity' in cmd.args

    def test_key_value_command(self):
        """Test parsing key-value parameters."""
        parser = CompTextParser()
        commands = parser.parse("@AUTOML[task=classification, metric=f1, cv=5]")

        assert len(commands) == 1
        cmd = commands[0]
        assert cmd.kwargs['task'] == 'classification'
        assert cmd.kwargs['metric'] == 'f1'
        assert cmd.kwargs['cv'] == 5

    def test_chained_commands(self):
        """Test parsing chained commands."""
        parser = CompTextParser()
        commands = parser.parse("@EXTRACT[source=db] + @TRANSFORM[clean=true] + @LOAD[dest=warehouse]")

        assert len(commands) == 3
        assert commands[0].command == 'EXTRACT'
        assert commands[1].command == 'TRANSFORM'
        assert commands[2].command == 'LOAD'

    def test_boolean_parsing(self):
        """Test boolean value parsing."""
        parser = CompTextParser()
        commands = parser.parse("@TEST[enabled=true, verbose=false]")

        assert commands[0].kwargs['enabled'] is True
        assert commands[0].kwargs['verbose'] is False

    def test_list_parsing(self):
        """Test list value parsing."""
        parser = CompTextParser()
        commands = parser.parse("@AUTOML[models=[rf, xgb, lgbm]]")

        assert 'models' in commands[0].kwargs
        models = commands[0].kwargs['models']
        assert isinstance(models, list)
        assert len(models) == 3

    def test_format_command(self):
        """Test formatting command back to string."""
        parser = CompTextParser()
        cmd = CompTextCommand(
            module='A',
            command='compress',
            args=['text'],
            kwargs={},
            raw='@A:compress text'
        )

        formatted = parser.format_command(cmd)
        assert '@A:compress' in formatted

    def test_parse_convenience_function(self):
        """Test convenience parse function."""
        commands = parse("@A:compress text")
        assert len(commands) == 1
        assert commands[0].module == 'A'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
