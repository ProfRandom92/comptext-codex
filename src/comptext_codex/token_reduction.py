"""Token reduction measurement utilities for natural language and CompText commands.

Enterprise-grade module with deterministic BPE token counting via tiktoken
(cl100k_base) and pinned benchmark expectations for CI/CD stability.
"""

from __future__ import annotations

import functools
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Iterable, Sequence

try:
    import tiktoken
    TIKTOKEN_AVAILABLE: Final[bool] = True
except ImportError:
    TIKTOKEN_AVAILABLE: Final[bool] = False  # type: ignore[misc]

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enterprise exception hierarchy
# Re-export from central exceptions module for backward compatibility.
# ---------------------------------------------------------------------------

from .exceptions import (  # noqa: E402
    TokenReductionError,
    EncodingError,
    BenchmarkDriftError,
)

# ---------------------------------------------------------------------------
# Encoding singleton – avoids repeated deserialization of the BPE vocabulary
# ---------------------------------------------------------------------------
ENCODING_MODEL: Final[str] = "cl100k_base"


@functools.lru_cache(maxsize=4)
def _get_encoding(model: str = ENCODING_MODEL) -> Any:
    """Return a cached tiktoken encoding instance (thread-safe singleton)."""
    if not TIKTOKEN_AVAILABLE:
        raise EncodingError("tiktoken is not installed")
    return tiktoken.get_encoding(model)


# ---------------------------------------------------------------------------
# Benchmark cases – deterministic sample prompts with pinned BPE token counts
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TokenReductionCase:
    """Represents a single token reduction scenario.

    Attributes:
        name: Human-readable case identifier (unique across DEFAULT_CASES).
        original: Verbose natural-language prompt.
        comptext: Equivalent CompText V5 ULTRA command.
        expected_nl_tokens: Pinned BPE token count for ``original`` (CI guard).
        expected_ct_tokens: Pinned BPE token count for ``comptext`` (CI guard).
    """

    name: str
    original: str
    comptext: str
    expected_nl_tokens: int = 0
    expected_ct_tokens: int = 0


DEFAULT_CASES: Final[Sequence[TokenReductionCase]] = (
    TokenReductionCase(
        name="Code Generation",
        original=(
            "Write a well-structured, thoroughly documented, and computationally efficient "
            "Python function that calculates the Fibonacci sequence using recursive logic "
            "with dynamic programming memoization techniques to cache all previously "
            "computed intermediate values and completely avoid redundant recursive "
            "calculations for significantly improved runtime performance and reduced "
            "memory consumption across large input values"
        ),
        comptext="C;P:FIB",
        expected_nl_tokens=55,
        expected_ct_tokens=5,
    ),
    TokenReductionCase(
        name="Code Review",
        original=(
            "Please carefully and methodically analyze this entire Python source code file "
            "from top to bottom, systematically identify every single performance bottleneck "
            "and computational inefficiency throughout the codebase, suggest concrete and "
            "actionable optimizations with detailed before-and-after code examples for each "
            "identified issue, thoroughly explain the underlying reasoning and engineering "
            "tradeoffs behind every single proposed optimization, and provide comprehensive "
            "benchmark comparisons showing the expected improvements in runtime execution "
            "speed and peak memory consumption for the entire application under realistic "
            "production workloads"
        ),
        comptext="A;P:PERF",
        expected_nl_tokens=90,
        expected_ct_tokens=6,
    ),
    TokenReductionCase(
        name="Batch Pipeline",
        original=(
            "First perform a thorough and comprehensive deep-dive analysis of the entire "
            "repository structure including every single source code file across all directories, "
            "all external and internal dependencies listed in configuration manifests, every "
            "build script and deployment configuration, continuous integration pipeline definitions, "
            "and environment-specific settings to fully understand the complete project architecture "
            "and systematically identify any potential structural issues or anti-patterns, "
            "then design and implement comprehensive and well-structured Python unit tests "
            "with full branch coverage for the complete authentication and authorization module "
            "covering all standard flows, edge cases, invalid input handling, error recovery "
            "scenarios, boundary conditions, race conditions, and known security vulnerabilities "
            "including injection attacks and privilege escalation vectors, and finally "
            "generate exhaustive and production-ready API documentation for every single "
            "public-facing REST endpoint in the entire system including complete request and response "
            "JSON schemas with field-level descriptions and validation constraints, authentication "
            "and authorization requirements per endpoint, all possible HTTP status codes with "
            "detailed error response bodies, rate limiting and throttling policies, pagination "
            "strategies, versioning information, and practical usage examples with curl commands "
            "and SDK code snippets for all supported client languages"
        ),
        comptext="B:[A:REPO]|[T;P;R:AUTH]|[D:API]",
        expected_nl_tokens=210,
        expected_ct_tokens=19,
    ),
    TokenReductionCase(
        name="Bug Fix",
        original=(
            "Locate and fix the critical memory leak in the TypeScript WebSocket real-time "
            "bidirectional connection handler module that is causing the production server "
            "to gradually and continuously consume all available system memory and eventually "
            "crash with a fatal out-of-memory error after running continuously for several "
            "hours under sustained heavy concurrent load from thousands of simultaneously "
            "connected clients sending frequent messages"
        ),
        comptext="F;T:MEM",
        expected_nl_tokens=64,
        expected_ct_tokens=5,
    ),
    TokenReductionCase(
        name="Query Optimization",
        original=(
            "Analyze and optimize every single slow-running and computationally inefficient "
            "database query that is causing severe performance degradation and timeout errors "
            "in the user analytics reporting dashboard by carefully examining detailed query "
            "execution plans and cost estimates, systematically identifying all missing or "
            "suboptimal database indexes, restructuring complex multi-table joins and nested "
            "subqueries for better execution efficiency, and implementing appropriate composite "
            "indexes, materialized views, and comprehensive query rewrites to dramatically "
            "improve response times and significantly reduce overall database server load "
            "during peak traffic periods"
        ),
        comptext="O;S:ANALYTICS",
        expected_nl_tokens=96,
        expected_ct_tokens=8,
    ),
    TokenReductionCase(
        name="Documentation",
        original=(
            "Generate thorough, comprehensive, and production-ready API documentation for "
            "every single public-facing REST endpoint in the entire application, including "
            "complete and detailed request and response JSON schemas with individual field "
            "descriptions, data type specifications, and validation rules, detailed authentication "
            "and authorization requirements for each individual endpoint including required "
            "scopes and permission levels, exhaustive listings of all possible HTTP error "
            "codes with fully detailed example error response bodies and troubleshooting "
            "guidance, rate limiting and request throttling policies with burst allowances, "
            "and practical real-world usage examples with curl commands and client SDK snippets"
        ),
        comptext="D:API",
        expected_nl_tokens=103,
        expected_ct_tokens=3,
    ),
    TokenReductionCase(
        name="Explain Code",
        original=(
            "Provide a detailed, comprehensive, and pedagogically structured explanation "
            "of how the recursive descent parser implementation works within the compiler "
            "frontend processing pipeline, covering the complete tokenization and lexical "
            "analysis phase including regular expression pattern matching and token "
            "classification, the abstract syntax tree construction process with all supported "
            "node types and their relationships, operator precedence handling using Pratt "
            "parsing techniques with binding power levels, and every error detection, "
            "recovery, and synchronization mechanism used to provide meaningful and "
            "actionable diagnostic messages to the developer during compilation"
        ),
        comptext="E:PARSER",
        expected_nl_tokens=95,
        expected_ct_tokens=4,
    ),
    TokenReductionCase(
        name="Test Suite",
        original=(
            "Design and implement a complete, thorough, and production-grade test suite "
            "for the payment processing and billing module written in Python, including "
            "granular unit tests for every single public method and class with full branch "
            "coverage, end-to-end integration tests with realistically mocked payment "
            "gateway responses and webhook callbacks, comprehensive edge case coverage "
            "for international multi-currency conversion with proper rounding and decimal "
            "precision handling across all supported currencies, proper error handling "
            "and automatic retry logic scenarios for network failures, timeouts, and "
            "transient gateway errors, and thorough idempotency verification to prevent "
            "duplicate transaction processing under concurrent request conditions"
        ),
        comptext="T;P;R:PAY",
        expected_nl_tokens=113,
        expected_ct_tokens=7,
    ),
)

# Pinned aggregate expectations (updated whenever DEFAULT_CASES change)
EXPECTED_AGGREGATE_NL: Final[int] = 826
EXPECTED_AGGREGATE_CT: Final[int] = 57
EXPECTED_AGGREGATE_PCT: Final[float] = 93.1


# ---------------------------------------------------------------------------
# Core token counting (with LRU cache for repeated inputs)
# ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=1024)
def _cached_token_count(text: str, model: str) -> int:
    """Cached inner implementation of token counting."""
    if TIKTOKEN_AVAILABLE:
        try:
            enc = _get_encoding(model)
            return len(enc.encode(text))
        except (KeyError, ValueError) as exc:
            logger.warning("Tiktoken encoding error for model=%s: %s", model, exc)

    # Regex fallback: split on word boundaries AND punctuation
    tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)
    return len(tokens)


def token_count(text: str, model: str = ENCODING_MODEL) -> int:
    """Return a precise token count using tiktoken BPE (cl100k_base).

    Results are cached (LRU, up to 1024 entries) to avoid redundant
    encoding of the same text.  Falls back to a regex-based heuristic
    if tiktoken is unavailable.  The fallback is intentionally
    conservative and will produce different values than BPE – CI tests
    guard against accidental fallback usage.
    """
    if not text:
        return 0
    return _cached_token_count(text, model)


# ---------------------------------------------------------------------------
# Reduction calculation
# ---------------------------------------------------------------------------

def calculate_reduction(case: TokenReductionCase) -> dict[str, Any]:
    """Calculate token reduction metrics for a single case."""
    original_tokens = token_count(case.original)
    comptext_tokens = token_count(case.comptext)
    reduction = max(original_tokens - comptext_tokens, 0)
    reduction_pct = 0.0
    if original_tokens:
        reduction_pct = round((reduction / original_tokens) * 100, 1)

    return {
        "name": case.name,
        "original_tokens": original_tokens,
        "comptext_tokens": comptext_tokens,
        "token_reduction": reduction,
        "reduction_pct": reduction_pct,
    }


# ---------------------------------------------------------------------------
# Markdown report generation
# ---------------------------------------------------------------------------

def generate_markdown_report(cases: Iterable[TokenReductionCase]) -> str:
    """Generate a markdown table summarizing token reductions."""
    metrics: list[dict[str, Any]] = [calculate_reduction(case) for case in cases]
    method = "tiktoken (cl100k_base)" if TIKTOKEN_AVAILABLE else "regex-heuristic"
    lines = [
        "# Token Reduction Results",
        f"**Measurement Method:** {method}",
        "",
        "| Case | Original Tokens | CompText Tokens | Reduction | Reduction % |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]

    for metric in metrics:
        lines.append(
            f"| {metric['name']} | {metric['original_tokens']} | "
            f"{metric['comptext_tokens']} | {metric['token_reduction']} | "
            f"{metric['reduction_pct']} |"
        )

    if metrics:
        total_orig = sum(m["original_tokens"] for m in metrics)
        total_ct = sum(m["comptext_tokens"] for m in metrics)
        total_saved = total_orig - total_ct
        total_pct = round((total_saved / total_orig) * 100, 1) if total_orig else 0
        lines.append(
            f"| **AGGREGATE** | **{total_orig}** | **{total_ct}** "
            f"| **{total_saved}** | **{total_pct}** |"
        )

    lines.append("")
    lines.append(
        "Generated by CompText Codex v5.0.3 token reduction benchmark "
        "using deterministic sample prompts and tiktoken BPE encoding."
    )
    return "\n".join(lines)


def write_report(report_path: Path, content: str) -> None:
    """Write the report content to the given path."""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(content, encoding="utf-8")


def main(output_path: Path | None = None) -> None:
    """Entry point for running the token reduction suite."""
    report_content = generate_markdown_report(DEFAULT_CASES)
    target = output_path or Path.cwd() / "TOKEN_REDUCTION_RESULTS.md"
    write_report(target, report_content)
    print(f"[OK] Token reduction report written to {target}")


if __name__ == "__main__":
    main()
