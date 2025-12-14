"""Utility helpers for working with CompText prompts."""
from __future__ import annotations

from typing import Tuple


def estimate_tokens(text: str) -> int:
    """Roughly estimate token usage using whitespace tokenization.

    The heuristic intentionally stays simple (standard-library only) while
    still providing a stable way to compare natural prompts with their
    CompText equivalents. Punctuation remains attached to the preceding
    word which aligns well with many LLM tokenizers for short prompts.
    """

    if not text:
        return 0
    return len(text.split())


def token_reduction(natural_prompt: str, dsl_prompt: str) -> Tuple[int, int, float]:
    """Calculate the relative token savings when using CompText.

    Returns a tuple of ``(natural_tokens, dsl_tokens, reduction_ratio)``
    where ``reduction_ratio`` is a float in the range ``[0, 1]``. A value
    of ``0.7`` corresponds to a 70% reduction compared to the natural
    language baseline.
    """

    natural_tokens = estimate_tokens(natural_prompt)
    dsl_tokens = estimate_tokens(dsl_prompt)
    if natural_tokens == 0:
        return 0, dsl_tokens, 0.0

    reduction = 1 - (dsl_tokens / natural_tokens)
    return natural_tokens, dsl_tokens, max(0.0, min(1.0, reduction))


__all__ = ["estimate_tokens", "token_reduction"]
