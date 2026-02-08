"""Enterprise-grade tests for token reduction module.

Tests are organized into categories:
- Determinism: Pinned BPE values that MUST NOT drift across environments.
- Quality gates: Aggregate and per-case reduction thresholds for CI/CD.
- Structural invariants: Case diversity, uniqueness, and coverage guarantees.
- Edge cases: Boundary conditions and error handling.
- Report generation: Output format and content verification.
"""

from pathlib import Path

import pytest

from comptext_codex.token_reduction import (
    DEFAULT_CASES,
    ENCODING_MODEL,
    EXPECTED_AGGREGATE_CT,
    EXPECTED_AGGREGATE_NL,
    EXPECTED_AGGREGATE_PCT,
    TIKTOKEN_AVAILABLE,
    BenchmarkDriftError,
    EncodingError,
    TokenReductionCase,
    TokenReductionError,
    _get_encoding,
    calculate_reduction,
    generate_markdown_report,
    main,
    token_count,
    write_report,
)


# ===================================================================
# 1. DETERMINISM GUARDS – pinned BPE values must be exact
# ===================================================================

class TestDeterminism:
    """Pinned token counts that must be identical across all environments."""

    def test_tiktoken_is_available(self):
        """CI/CD MUST have tiktoken installed – regex fallback is not acceptable."""
        assert TIKTOKEN_AVAILABLE, (
            "tiktoken is not installed. Enterprise builds require BPE precision."
        )

    def test_encoding_model_is_cl100k(self):
        """Encoding model must be cl100k_base (GPT-4/ChatGPT standard)."""
        assert ENCODING_MODEL == "cl100k_base"

    def test_encoding_singleton_caches(self):
        """_get_encoding must return the same object on repeated calls."""
        enc1 = _get_encoding("cl100k_base")
        enc2 = _get_encoding("cl100k_base")
        assert enc1 is enc2, "Encoding not cached – performance regression"

    @pytest.mark.parametrize("case", DEFAULT_CASES, ids=lambda c: c.name)
    def test_pinned_nl_tokens(self, case: TokenReductionCase):
        """NL token count must match pinned expected value exactly."""
        if case.expected_nl_tokens == 0:
            pytest.skip("No pinned expectation set")
        actual = token_count(case.original)
        assert actual == case.expected_nl_tokens, (
            f"[{case.name}] NL tokens drifted: expected={case.expected_nl_tokens}, "
            f"actual={actual}. Update expected_nl_tokens if prompt changed."
        )

    @pytest.mark.parametrize("case", DEFAULT_CASES, ids=lambda c: c.name)
    def test_pinned_ct_tokens(self, case: TokenReductionCase):
        """CompText token count must match pinned expected value exactly."""
        if case.expected_ct_tokens == 0:
            pytest.skip("No pinned expectation set")
        actual = token_count(case.comptext)
        assert actual == case.expected_ct_tokens, (
            f"[{case.name}] CT tokens drifted: expected={case.expected_ct_tokens}, "
            f"actual={actual}. Update expected_ct_tokens if command changed."
        )

    def test_pinned_aggregate_nl_total(self):
        """Aggregate NL token total must match pinned constant."""
        total = sum(token_count(c.original) for c in DEFAULT_CASES)
        assert total == EXPECTED_AGGREGATE_NL, (
            f"Aggregate NL drifted: expected={EXPECTED_AGGREGATE_NL}, actual={total}"
        )

    def test_pinned_aggregate_ct_total(self):
        """Aggregate CT token total must match pinned constant."""
        total = sum(token_count(c.comptext) for c in DEFAULT_CASES)
        assert total == EXPECTED_AGGREGATE_CT, (
            f"Aggregate CT drifted: expected={EXPECTED_AGGREGATE_CT}, actual={total}"
        )

    def test_pinned_aggregate_percentage(self):
        """Aggregate reduction percentage must match pinned constant."""
        total_nl = sum(token_count(c.original) for c in DEFAULT_CASES)
        total_ct = sum(token_count(c.comptext) for c in DEFAULT_CASES)
        pct = round((1 - total_ct / total_nl) * 100, 1)
        assert pct == EXPECTED_AGGREGATE_PCT, (
            f"Aggregate pct drifted: expected={EXPECTED_AGGREGATE_PCT}%, actual={pct}%"
        )


# ===================================================================
# 2. QUALITY GATES – minimum thresholds that block releases
# ===================================================================

class TestQualityGates:
    """Reduction thresholds that must pass for any release to proceed."""

    def test_aggregate_above_90_percent(self):
        """Aggregate reduction must exceed 90%."""
        total_nl = sum(token_count(c.original) for c in DEFAULT_CASES)
        total_ct = sum(token_count(c.comptext) for c in DEFAULT_CASES)
        pct = (1 - total_ct / total_nl) * 100
        assert pct > 90, f"Aggregate {pct:.1f}% is below 90% release gate"

    @pytest.mark.parametrize("case", DEFAULT_CASES, ids=lambda c: c.name)
    def test_every_case_above_90_percent(self, case: TokenReductionCase):
        """Every individual case must exceed 90% reduction."""
        m = calculate_reduction(case)
        assert m["reduction_pct"] >= 90.0, (
            f"[{case.name}] only {m['reduction_pct']}% "
            f"(NL={m['original_tokens']}, CT={m['comptext_tokens']})"
        )

    @pytest.mark.parametrize("case", DEFAULT_CASES, ids=lambda c: c.name)
    def test_positive_reduction(self, case: TokenReductionCase):
        """Every case must have strictly positive token savings."""
        m = calculate_reduction(case)
        assert m["token_reduction"] > 0, (
            f"[{case.name}] has zero reduction"
        )


# ===================================================================
# 3. STRUCTURAL INVARIANTS – benchmark diversity guarantees
# ===================================================================

class TestStructuralInvariants:
    """Invariants on the benchmark suite structure."""

    def test_minimum_eight_cases(self):
        assert len(DEFAULT_CASES) >= 8, f"Only {len(DEFAULT_CASES)} cases, need >= 8"

    def test_case_names_unique(self):
        names = [c.name for c in DEFAULT_CASES]
        assert len(names) == len(set(names)), f"Duplicate case names found"

    def test_all_v5_command_types_represented(self):
        """All 7 primary V5 command types must appear in benchmark."""
        all_ct = " ".join(c.comptext for c in DEFAULT_CASES)
        for cmd in ("C", "F", "T", "D", "E", "O", "A"):
            assert cmd in all_ct, f"Command '{cmd}' missing from benchmark"

    def test_batch_syntax_represented(self):
        batch = [c for c in DEFAULT_CASES if c.comptext.startswith("B:")]
        assert len(batch) >= 1, "No batch command (B:) in benchmark"

    def test_nl_prompts_realistic_length(self):
        """NL prompts must be >= 30 BPE tokens (realistic enterprise prompts)."""
        for case in DEFAULT_CASES:
            nl = token_count(case.original)
            assert nl >= 30, f"[{case.name}] NL too short: {nl} tokens"

    def test_comptext_commands_compact(self):
        """CompText commands must be <= 20 BPE tokens (compact by design)."""
        for case in DEFAULT_CASES:
            ct = token_count(case.comptext)
            assert ct <= 20, f"[{case.name}] CT too long: {ct} tokens"

    def test_all_cases_have_pinned_expectations(self):
        """Every case must have non-zero pinned token expectations."""
        for case in DEFAULT_CASES:
            assert case.expected_nl_tokens > 0, (
                f"[{case.name}] missing expected_nl_tokens"
            )
            assert case.expected_ct_tokens > 0, (
                f"[{case.name}] missing expected_ct_tokens"
            )


# ===================================================================
# 4. CORE TOKEN COUNTING – unit tests
# ===================================================================

class TestTokenCount:
    """Unit tests for the token_count function."""

    def test_empty_string(self):
        assert token_count("") == 0

    def test_whitespace_only(self):
        assert token_count("   ") == 1  # BPE encodes whitespace

    def test_single_word(self):
        assert token_count("hello") == 1

    def test_multi_word(self):
        assert token_count("hello world") == 2

    def test_bpe_subword_split(self):
        """BPE splits contractions into subword tokens."""
        assert token_count("don't") == 2

    def test_whitespace_heavy(self):
        """BPE tokens include leading whitespace."""
        assert token_count("  a   b c ") == 6

    def test_special_characters(self):
        """Semicolons and colons in CompText syntax generate BPE tokens."""
        count = token_count("C;P:FIB")
        assert count == 5  # C ; P : FIB

    def test_method_is_tiktoken(self):
        """Verify we're using tiktoken, not regex fallback."""
        assert TIKTOKEN_AVAILABLE


# ===================================================================
# 5. EDGE CASES – boundary conditions
# ===================================================================

class TestEdgeCases:
    """Boundary conditions for calculate_reduction."""

    def test_equal_token_counts(self):
        case = TokenReductionCase(name="Equal", original="hello world", comptext="test case")
        m = calculate_reduction(case)
        assert m["token_reduction"] == 0
        assert m["reduction_pct"] == 0.0

    def test_comptext_longer_than_original(self):
        case = TokenReductionCase(name="Negative", original="one", comptext="two three four")
        m = calculate_reduction(case)
        assert m["token_reduction"] == 0
        assert m["reduction_pct"] == 0.0

    def test_empty_original(self):
        case = TokenReductionCase(name="Empty", original="", comptext="test")
        m = calculate_reduction(case)
        assert m["original_tokens"] == 0
        assert m["reduction_pct"] == 0.0


# ===================================================================
# 6. REPORT GENERATION – output format verification
# ===================================================================

class TestReportGeneration:
    """Tests for markdown report output."""

    def test_report_contains_all_cases(self):
        content = generate_markdown_report(DEFAULT_CASES)
        for case in DEFAULT_CASES:
            assert case.name in content

    def test_report_has_aggregate_row(self):
        content = generate_markdown_report(DEFAULT_CASES)
        assert "AGGREGATE" in content

    def test_report_shows_method(self):
        content = generate_markdown_report(DEFAULT_CASES)
        assert "tiktoken" in content or "regex" in content

    def test_report_has_header(self):
        content = generate_markdown_report(DEFAULT_CASES)
        assert content.startswith("# Token Reduction Results")

    def test_empty_cases_no_aggregate(self):
        content = generate_markdown_report([])
        assert "AGGREGATE" not in content

    def test_write_report_creates_parents(self, tmp_path: Path):
        nested = tmp_path / "a" / "b" / "report.md"
        write_report(nested, "test")
        assert nested.exists()
        assert nested.read_text(encoding="utf-8") == "test"

    def test_main_function(self, tmp_path: Path):
        out = tmp_path / "output.md"
        main(output_path=out)
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert "AGGREGATE" in content
        assert "Token Reduction Results" in content


# ===================================================================
# 7. EXCEPTION HIERARCHY – enterprise error types
# ===================================================================

class TestExceptionHierarchy:
    """Exception classes must form a proper inheritance tree."""

    def test_encoding_error_is_token_reduction_error(self):
        assert issubclass(EncodingError, TokenReductionError)

    def test_benchmark_drift_error_is_token_reduction_error(self):
        assert issubclass(BenchmarkDriftError, TokenReductionError)

    def test_token_reduction_error_is_exception(self):
        assert issubclass(TokenReductionError, Exception)

    def test_encoding_error_catchable_as_base(self):
        with pytest.raises(TokenReductionError):
            raise EncodingError("test")

    def test_benchmark_drift_error_catchable_as_base(self):
        with pytest.raises(TokenReductionError):
            raise BenchmarkDriftError("test")
