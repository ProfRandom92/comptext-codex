"""Module N: Token Analytics - Live token counting, cost estimation, reduction stats.

Enterprise-grade module with immutable pricing data and deterministic BPE counting.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Any, Dict, Final, List, Mapping, Optional

from comptext_codex.registry import codex_module, codex_command
from comptext_codex.token_reduction import token_count, TIKTOKEN_AVAILABLE
from .base import BaseModule

# Frozen pricing per 1M tokens (input) for common models as of 2025
# MappingProxyType prevents accidental mutation at runtime.
MODEL_PRICING: Final[Mapping[str, float]] = MappingProxyType({
    "gpt-4o": 2.50,
    "gpt-4-turbo": 10.00,
    "gpt-4": 30.00,
    "gpt-3.5-turbo": 0.50,
    "claude-opus-4": 15.00,
    "claude-sonnet-4": 3.00,
    "claude-haiku-3.5": 0.80,
})


@codex_module(
    code="N",
    name="Token Analytics",
    purpose="Live token counting, cost estimation, and reduction statistics",
    token_priority="high",
    mcp_exposed=True,
    security={"pii_safe": True, "threat_model": "standard"},
    privacy={"dp_budget": "none", "audit_logging": False},
)
class ModuleN(BaseModule):
    """Token analytics module for precise LLM cost and reduction metrics."""

    @codex_command(
        syntax="@TOK_COUNT[text]",
        description="Count BPE tokens in text using tiktoken cl100k_base",
        token_cost_hint=5,
    )
    def execute_tok_count(
        self, *args: Any, context: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        text = kwargs.get("text", "") or (args[0] if args else "")
        tokens = token_count(text)
        return {
            "text_length": len(text),
            "token_count": tokens,
            "method": "tiktoken_cl100k_base" if TIKTOKEN_AVAILABLE else "regex_fallback",
            "ratio": round(tokens / len(text), 3) if text else 0,
        }

    @codex_command(
        syntax="@TOK_COST[text, model=gpt-4o]",
        description="Estimate API cost for text based on token count and model pricing",
        token_cost_hint=8,
    )
    def execute_tok_cost(
        self, *args: Any, context: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        text = kwargs.get("text", "") or (args[0] if args else "")
        model = kwargs.get("model", "gpt-4o")
        tokens = token_count(text)
        price_per_1m = MODEL_PRICING.get(model, MODEL_PRICING["gpt-4o"])
        cost = (tokens / 1_000_000) * price_per_1m

        return {
            "token_count": tokens,
            "model": model,
            "price_per_1m_tokens": price_per_1m,
            "estimated_cost_usd": round(cost, 6),
        }

    @codex_command(
        syntax="@TOK_REDUCE[original, comptext]",
        description="Calculate token reduction between natural language and CompText",
        token_cost_hint=10,
    )
    def execute_tok_reduce(
        self, *args: Any, context: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        original = kwargs.get("original", "")
        comptext = kwargs.get("comptext", "")
        orig_tokens = token_count(original)
        ct_tokens = token_count(comptext)
        saved = max(orig_tokens - ct_tokens, 0)
        pct = round((saved / orig_tokens) * 100, 1) if orig_tokens > 0 else 0.0

        return {
            "original_tokens": orig_tokens,
            "comptext_tokens": ct_tokens,
            "tokens_saved": saved,
            "reduction_pct": pct,
            "method": "tiktoken_cl100k_base" if TIKTOKEN_AVAILABLE else "regex_fallback",
        }

    @codex_command(
        syntax="@TOK_BUDGET[budget, model=gpt-4o]",
        description="Calculate how many tokens fit in a USD budget for a given model",
        token_cost_hint=5,
    )
    def execute_tok_budget(
        self, *args: Any, context: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        budget = float(kwargs.get("budget", 1.0))
        model = kwargs.get("model", "gpt-4o")
        price_per_1m = MODEL_PRICING.get(model, MODEL_PRICING["gpt-4o"])
        max_tokens = int((budget / price_per_1m) * 1_000_000)

        return {
            "budget_usd": budget,
            "model": model,
            "price_per_1m_tokens": price_per_1m,
            "max_tokens": max_tokens,
            "approx_words": max_tokens * 3 // 4,
        }

    @codex_command(
        syntax="@TOK_COMPARE[text, models=gpt-4o,claude-sonnet-4]",
        description="Compare token costs across multiple LLM models",
        token_cost_hint=15,
    )
    def execute_tok_compare(
        self, *args: Any, context: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        text = kwargs.get("text", "") or (args[0] if args else "")
        models_str = kwargs.get("models", "gpt-4o,claude-sonnet-4,claude-haiku-3.5")
        models: List[str] = [m.strip() for m in models_str.split(",")]
        tokens = token_count(text)
        breakdown: List[Dict[str, Any]] = []

        for model in models:
            price = MODEL_PRICING.get(model)
            if price is None:
                continue
            cost = (tokens / 1_000_000) * price
            breakdown.append({
                "model": model,
                "price_per_1m": price,
                "cost_usd": round(cost, 6),
            })

        breakdown.sort(key=lambda x: x["cost_usd"])
        cheapest = breakdown[0]["model"] if breakdown else "unknown"

        return {
            "token_count": tokens,
            "models": breakdown,
            "cheapest": cheapest,
        }


def get_module() -> ModuleN:
    return ModuleN()
