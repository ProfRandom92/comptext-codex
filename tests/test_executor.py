"""Tests for CompText Executor."""

import pytest
from comptext_codex.executor import CompTextExecutor, ExecutionResult, execute


class TestCompTextExecutor:
    """Test cases for CompTextExecutor."""

    def test_simple_execution(self):
        """Test executing simple command."""
        executor = CompTextExecutor()
        results = executor.execute("@A:compress The quick brown fox jumps repeatedly")

        assert len(results) == 1
        assert results[0].success is True
        assert results[0].result is not None

    def test_execution_with_context(self):
        """Test execution with context."""
        executor = CompTextExecutor()
        code = "def test(): pass"
        results = executor.execute(
            "@CODE_ANALYZE[perf_bottleneck]",
            context={'code': code}
        )

        assert len(results) == 1
        assert results[0].success is True

    def test_chained_execution(self):
        """Test chained command execution."""
        executor = CompTextExecutor()
        results = executor.execute("@EXTRACT[source=db] + @TRANSFORM[clean=true] + @LOAD[dest=warehouse]")

        assert len(results) == 3
        assert all(r.success for r in results)

    def test_module_b_analyze(self):
        """Test Module B analysis command."""
        executor = CompTextExecutor()
        results = executor.execute("@B:analyze This is a positive and great message")

        assert results[0].success is True
        result = results[0].result
        assert 'word_count' in result
        assert 'sentiment' in result

    def test_module_e_automl(self):
        """Test Module E AutoML command."""
        executor = CompTextExecutor()
        results = executor.execute("@AUTOML[task=classification, metric=f1]")

        assert results[0].success is True
        result = results[0].result
        assert result['task'] == 'classification'
        assert result['metric'] == 'f1'
        assert 'best_model' in result

    def test_module_i_security_scan(self):
        """Test Module I security scan."""
        executor = CompTextExecutor()
        results = executor.execute("@SEC_SCAN[type=code, severity=high]")

        assert results[0].success is True
        result = results[0].result
        assert 'vulnerabilities_found' in result
        assert 'recommendations' in result

    def test_get_available_commands(self):
        """Test getting available commands."""
        executor = CompTextExecutor()
        commands = executor.get_available_commands()

        assert len(commands) > 0
        assert any(cmd['module'] == 'A' for cmd in commands)

    def test_fallback_execution(self):
        """Test fallback for unimplemented commands."""
        executor = CompTextExecutor()
        results = executor.execute("@UNKNOWN_COMMAND[param=value]")

        assert len(results) == 1
        # Should not fail, but return simulated result
        assert results[0].success is True

    def test_execute_convenience_function(self):
        """Test convenience execute function."""
        results = execute("@A:compress text")
        assert len(results) == 1
        assert results[0].success is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
