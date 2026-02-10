"""Unified exception hierarchy for CompText Codex.

All module and subsystem exceptions inherit from ``CompTextError`` so
callers can catch a single base class when needed, while still being able
to distinguish individual failure modes.

Hierarchy::

    CompTextError
    ├── ParserError
    │   ├── InvalidSyntaxError
    │   └── UnknownCommandError
    ├── ExecutionError
    │   ├── ModuleNotFoundError_
    │   ├── CommandNotFoundError
    │   └── HandlerError
    ├── TokenReductionError
    │   ├── EncodingError
    │   └── BenchmarkDriftError
    └── ConfigurationError
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class CompTextError(Exception):
    """Root exception for all CompText Codex errors."""


# ---------------------------------------------------------------------------
# Parser errors
# ---------------------------------------------------------------------------

class ParserError(CompTextError):
    """Raised when command parsing fails."""


class InvalidSyntaxError(ParserError):
    """Raised when the command string does not match any known syntax."""


class UnknownCommandError(ParserError):
    """Raised when a parsed command references an unknown command name."""


# ---------------------------------------------------------------------------
# Execution errors
# ---------------------------------------------------------------------------

class ExecutionError(CompTextError):
    """Raised when command execution fails."""


class ModuleNotFoundError_(ExecutionError):
    """Raised when a requested module code is not registered.

    Named with trailing underscore to avoid shadowing the builtin
    ``ModuleNotFoundError``.
    """


class CommandNotFoundError(ExecutionError):
    """Raised when a module does not implement the requested command."""


class HandlerError(ExecutionError):
    """Raised when a command handler raises an unexpected exception."""


# ---------------------------------------------------------------------------
# Token-reduction errors (re-exported from token_reduction for convenience)
# ---------------------------------------------------------------------------

class TokenReductionError(CompTextError):
    """Base exception for token reduction operations."""


class EncodingError(TokenReductionError):
    """Raised when BPE encoding fails or is unavailable."""


class BenchmarkDriftError(TokenReductionError):
    """Raised when pinned benchmark values drift from expected."""


# ---------------------------------------------------------------------------
# Configuration / setup errors
# ---------------------------------------------------------------------------

class ConfigurationError(CompTextError):
    """Raised for invalid configuration (missing codex dir, bad YAML, etc.)."""
