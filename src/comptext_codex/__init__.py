"""CompText Codex - Domain-Specific Language for efficient LLM interaction."""

from .token_reduction import calculate_reduction, token_count
from .token_report import build_token_report, load_commands, load_modules
from .parser import CompTextParser, CompTextCommand, parse
from .executor import CompTextExecutor, ExecutionResult, execute
from .repl import CompTextREPL

__all__ = [
    # Token utilities
    "token_count",
    "calculate_reduction",
    "build_token_report",
    "load_commands",
    "load_modules",
    # Core DSL
    "CompTextParser",
    "CompTextCommand",
    "CompTextExecutor",
    "ExecutionResult",
    "CompTextREPL",
    "parse",
    "execute",
]

__version__ = "3.5.0"
