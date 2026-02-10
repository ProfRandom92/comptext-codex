"""Integration tests for real-world CompText workflows.

These tests exercise end-to-end paths across the parser, executor,
modules, and token reduction subsystems to verify that the components
work together correctly under realistic usage patterns.
"""

import warnings
import pytest

from comptext_codex.parser_v5 import CompTextParserV5, parse_v5, encode_v5
from comptext_codex.executor import CompTextExecutor, execute
from comptext_codex.token_reduction import token_count, calculate_reduction, DEFAULT_CASES
from comptext_codex.exceptions import CompTextError


# ---------------------------------------------------------------------------
# V5 Parser round-trip tests
# ---------------------------------------------------------------------------

class TestV5RoundTrip:
    """Encode -> parse round-trip must be lossless."""

    @pytest.mark.parametrize("command,language,modifiers,task", [
        ("CODE", "PYTHON", None, "FIB"),
        ("TEST", "PYTHON", ["ROBUST"], "AUTH"),
        ("DOCUMENT", None, None, "API"),
        ("FIX", "TYPESCRIPT", None, "MEM"),
        ("OPTIMIZE", "SQL", None, "ANALYTICS"),
        ("EXPLAIN", None, ["CONCISE"], "PARSER"),
        ("ANALYZE", "RUST", ["STRICT"], "PERF"),
    ])
    def test_encode_parse_roundtrip(self, command, language, modifiers, task):
        parser = CompTextParserV5()
        encoded = parser.encode(command, language, modifiers, task)
        parsed = parser.parse(encoded)
        assert len(parsed) == 1
        cmd = parsed[0]
        assert parser.COMMANDS.get(cmd.command) == command
        if language:
            assert parser.LANGUAGES.get(cmd.language) == language
        if task:
            assert cmd.task == task

    def test_batch_encode_parse_roundtrip(self):
        parser = CompTextParserV5()
        batch = [
            ("DOCUMENT", None, None, "SUM"),
            ("CODE", "PYTHON", None, "FIB"),
            ("EXPLAIN", None, ["CONCISE"], "WHY"),
        ]
        encoded = parser.encode_batch(batch)
        assert encoded.startswith("B:")
        parsed = parser.parse(encoded)
        assert len(parsed) == 3
        assert parsed[0].task == "SUM"
        assert parsed[1].task == "FIB"
        assert parsed[2].task == "WHY"


# ---------------------------------------------------------------------------
# Executor end-to-end tests
# ---------------------------------------------------------------------------

class TestExecutorWorkflows:
    """End-to-end executor tests covering multi-module scenarios."""

    def test_compress_then_analyze(self):
        """Chain: compress text with Module A, then analyze with Module B."""
        executor = CompTextExecutor()

        # Step 1: Compress
        r1 = executor.execute("@A:compress The quick brown fox jumps over the lazy dog repeatedly")
        assert r1[0].success
        compressed = r1[0].result

        # Step 2: Analyze
        r2 = executor.execute("@B:analyze This is a positive great message")
        assert r2[0].success
        assert "sentiment" in r2[0].result

    def test_all_registered_modules_loadable(self):
        """Verify all 14 modules (A-N) are loadable through the executor."""
        executor = CompTextExecutor()
        codes = set()
        for cmd in executor.get_available_commands():
            codes.add(cmd.get("module", ""))
        # Should have at least modules A through N
        for letter in "ABCDEFGHIJKLMN":
            assert letter in codes, f"Module {letter} not registered"

    def test_execution_result_metadata(self):
        """Verify ExecutionResult carries module/command metadata."""
        results = execute("@A:compress hello world")
        r = results[0]
        assert r.success
        assert r.metadata.get("module") == "A"
        assert r.metadata.get("command") == "compress"

    def test_failed_parse_returns_error(self):
        """Completely invalid input should return a graceful error."""
        results = execute("not a valid command at all")
        assert len(results) == 1
        assert results[0].success is False
        assert results[0].error is not None


# ---------------------------------------------------------------------------
# Token reduction end-to-end
# ---------------------------------------------------------------------------

class TestTokenReductionWorkflow:
    """End-to-end token reduction benchmark tests."""

    def test_all_default_cases_reduce(self):
        """Every default benchmark case should achieve >50% reduction."""
        for case in DEFAULT_CASES:
            metrics = calculate_reduction(case)
            assert metrics["reduction_pct"] > 50, (
                f"Case '{case.name}' only achieved {metrics['reduction_pct']}% reduction"
            )

    def test_aggregate_reduction_above_90(self):
        """Aggregate reduction across all default cases should exceed 90%."""
        total_nl = sum(token_count(c.original) for c in DEFAULT_CASES)
        total_ct = sum(token_count(c.comptext) for c in DEFAULT_CASES)
        pct = round((1 - total_ct / total_nl) * 100, 1)
        assert pct > 90, f"Aggregate reduction {pct}% is below 90%"

    def test_token_count_caching(self):
        """Repeated calls to token_count should return identical results (cache test)."""
        text = "This is a test sentence for caching verification"
        count1 = token_count(text)
        count2 = token_count(text)
        assert count1 == count2
        assert count1 > 0

    def test_v5_parser_token_reduction(self):
        """Use the V5 parser's built-in token reduction calculator."""
        parser = CompTextParserV5()
        stats = parser.calculate_token_reduction(
            "Write a well-structured Python function that calculates Fibonacci",
            "C;P:FIB"
        )
        assert stats["reduction_percent"] >= 50
        assert stats["tokens_saved"] > 0


# ---------------------------------------------------------------------------
# Deprecation warnings
# ---------------------------------------------------------------------------

class TestDeprecationWarnings:
    """Verify legacy components emit proper deprecation warnings."""

    def test_v4_parser_emits_warning(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            from comptext_codex.parser import CompTextParser
            CompTextParser()
            deprecation_warnings = [
                x for x in w if issubclass(x.category, DeprecationWarning)
            ]
            assert len(deprecation_warnings) >= 1
            assert "deprecated" in str(deprecation_warnings[0].message).lower()


# ---------------------------------------------------------------------------
# Cross-module integration: Module N token analytics with real data
# ---------------------------------------------------------------------------

class TestModuleNIntegration:
    """Test Module N (Token Analytics) with real text inputs."""

    def test_tok_count_matches_global(self):
        """Module N's tok_count should agree with the global token_count."""
        from comptext_codex.modules.module_n import ModuleN

        module = ModuleN()
        text = "The quick brown fox jumps over the lazy dog"
        result = module.execute_tok_count(text)
        assert result["token_count"] == token_count(text)

    def test_tok_reduce_realistic(self):
        """Module N's tok_reduce on a realistic pair."""
        from comptext_codex.modules.module_n import ModuleN

        module = ModuleN()
        result = module.execute_tok_reduce(
            original=(
                "Write comprehensive and production-grade unit tests with full branch "
                "coverage for the authentication and authorization module including "
                "edge cases, error handling, and security vulnerability checks"
            ),
            comptext="T;P;R:AUTH",
        )
        assert result["reduction_pct"] > 50
        assert result["tokens_saved"] > 0

    def test_tok_compare_models(self):
        """Module N's tok_compare should return sorted model costs."""
        from comptext_codex.modules.module_n import ModuleN

        module = ModuleN()
        result = module.execute_tok_compare(
            "Sample text for multi-model comparison",
            models="gpt-4o,gpt-4,claude-sonnet-4",
        )
        assert len(result["models"]) == 3
        costs = [m["cost_usd"] for m in result["models"]]
        assert costs == sorted(costs), "Models should be sorted by cost ascending"
