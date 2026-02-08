"""Tests for Module N: Token Analytics."""

import pytest

from comptext_codex.modules.module_n import ModuleN, ModuleN as get_module_class, MODEL_PRICING
from comptext_codex.registry import registry
from comptext_codex.token_reduction import TIKTOKEN_AVAILABLE


class TestModuleNPricingIntegrity:
    """Enterprise guard: MODEL_PRICING must be immutable at runtime."""

    def test_pricing_is_frozen(self):
        """MappingProxyType must prevent mutation."""
        with pytest.raises(TypeError):
            MODEL_PRICING["gpt-4o"] = 0.01  # type: ignore[index]

    def test_pricing_cannot_add_key(self):
        with pytest.raises(TypeError):
            MODEL_PRICING["new-model"] = 5.0  # type: ignore[index]

    def test_pricing_cannot_delete_key(self):
        with pytest.raises(TypeError):
            del MODEL_PRICING["gpt-4o"]  # type: ignore[arg-type]

    def test_pricing_has_minimum_models(self):
        assert len(MODEL_PRICING) >= 7

    def test_all_prices_positive(self):
        for model, price in MODEL_PRICING.items():
            assert price > 0, f"{model} has non-positive price {price}"


class TestModuleNRegistration:
    """Test module registration in the codex registry."""

    def test_module_registered(self):
        meta = getattr(ModuleN, "_module_meta", None)
        assert meta is not None
        assert meta.code == "N"
        assert meta.name == "Token Analytics"

    def test_module_has_commands(self):
        commands = registry.get_commands_for_module("N")
        command_ids = {c.command for c in commands}
        assert "tok_count" in command_ids
        assert "tok_cost" in command_ids
        assert "tok_reduce" in command_ids
        assert "tok_budget" in command_ids
        assert "tok_compare" in command_ids

    def test_module_mcp_exposed(self):
        meta = getattr(ModuleN, "_module_meta", None)
        assert meta.mcp_exposed is True


class TestTokCount:
    """Test the token counting command."""

    def setup_method(self):
        self.mod = ModuleN()

    def test_count_simple_text(self):
        r = self.mod.execute_tok_count(text="hello world")
        assert r["token_count"] == 2
        assert r["text_length"] == 11

    def test_count_empty(self):
        r = self.mod.execute_tok_count(text="")
        assert r["token_count"] == 0
        assert r["ratio"] == 0

    def test_count_uses_tiktoken(self):
        r = self.mod.execute_tok_count(text="test")
        assert r["method"] == "tiktoken_cl100k_base"

    def test_count_positional_arg(self):
        r = self.mod.execute_tok_count("hello world")
        assert r["token_count"] == 2


class TestTokCost:
    """Test the cost estimation command."""

    def setup_method(self):
        self.mod = ModuleN()

    def test_cost_default_model(self):
        r = self.mod.execute_tok_cost(text="hello world")
        assert r["model"] == "gpt-4o"
        assert r["estimated_cost_usd"] > 0

    def test_cost_specific_model(self):
        r = self.mod.execute_tok_cost(text="hello world", model="claude-sonnet-4")
        assert r["model"] == "claude-sonnet-4"
        assert r["price_per_1m_tokens"] == 3.0

    def test_cost_empty_text(self):
        r = self.mod.execute_tok_cost(text="")
        assert r["token_count"] == 0
        assert r["estimated_cost_usd"] == 0

    def test_cost_unknown_model_falls_back(self):
        r = self.mod.execute_tok_cost(text="hello", model="unknown-model-xyz")
        # Falls back to gpt-4o pricing
        assert r["price_per_1m_tokens"] == MODEL_PRICING["gpt-4o"]


class TestTokReduce:
    """Test the reduction calculation command."""

    def setup_method(self):
        self.mod = ModuleN()

    def test_reduction_positive(self):
        r = self.mod.execute_tok_reduce(
            original="Write a Python function for Fibonacci",
            comptext="C;P:FIB",
        )
        assert r["tokens_saved"] > 0
        assert r["reduction_pct"] > 0

    def test_reduction_zero_when_equal(self):
        r = self.mod.execute_tok_reduce(original="hello", comptext="world")
        assert r["tokens_saved"] == 0
        assert r["reduction_pct"] == 0.0

    def test_reduction_clamped_at_zero(self):
        r = self.mod.execute_tok_reduce(original="a", comptext="a long comptext string")
        assert r["tokens_saved"] == 0

    def test_reduction_empty_original(self):
        r = self.mod.execute_tok_reduce(original="", comptext="test")
        assert r["original_tokens"] == 0
        assert r["reduction_pct"] == 0.0


class TestTokBudget:
    """Test the budget calculation command."""

    def setup_method(self):
        self.mod = ModuleN()

    def test_budget_default(self):
        r = self.mod.execute_tok_budget(budget=1.0)
        assert r["max_tokens"] > 0
        assert r["approx_words"] > 0

    def test_budget_scaling(self):
        r1 = self.mod.execute_tok_budget(budget=1.0, model="gpt-4o")
        r10 = self.mod.execute_tok_budget(budget=10.0, model="gpt-4o")
        assert r10["max_tokens"] == r1["max_tokens"] * 10

    def test_budget_expensive_model_fewer_tokens(self):
        r_cheap = self.mod.execute_tok_budget(budget=1.0, model="gpt-3.5-turbo")
        r_expensive = self.mod.execute_tok_budget(budget=1.0, model="gpt-4")
        assert r_cheap["max_tokens"] > r_expensive["max_tokens"]


class TestTokCompare:
    """Test the multi-model comparison command."""

    def setup_method(self):
        self.mod = ModuleN()

    def test_compare_returns_sorted(self):
        r = self.mod.execute_tok_compare(
            text="test prompt",
            models="gpt-4o,gpt-4,claude-haiku-3.5",
        )
        costs = [m["cost_usd"] for m in r["models"]]
        assert costs == sorted(costs), "Models should be sorted by cost ascending"

    def test_compare_cheapest_identified(self):
        r = self.mod.execute_tok_compare(
            text="test",
            models="gpt-4,claude-haiku-3.5",
        )
        assert r["cheapest"] == "claude-haiku-3.5"

    def test_compare_skips_unknown_models(self):
        r = self.mod.execute_tok_compare(
            text="test",
            models="gpt-4o,nonexistent-model",
        )
        model_names = [m["model"] for m in r["models"]]
        assert "nonexistent-model" not in model_names
        assert "gpt-4o" in model_names

    def test_compare_default_models(self):
        r = self.mod.execute_tok_compare(text="test")
        assert len(r["models"]) >= 2
