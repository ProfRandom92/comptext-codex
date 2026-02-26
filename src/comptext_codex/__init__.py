"""CompText Codex - Domain-Specific Language for efficient LLM interaction.

Migration from Notion/YAML to SQLite-based architecture provides:
- ~10x faster startup (no YAML parsing)
- Queryable command/module catalog
- Single-file database (codex.db)
- Type-safe metadata via dataclasses
"""

from .kvtc import KVTCCompressor
from .token_reduction import (
    calculate_reduction,
    token_count,
    BenchmarkDriftError,
    EncodingError,
    TokenReductionError,
)
from .token_report import build_token_report, load_commands, load_modules
from .parser import CompTextParser, CompTextCommand, parse
from .executor import CompTextExecutor, ExecutionResult, execute
from .repl import CompTextREPL
from .store import CodexStore
from .registry import (
    registry,
    codex_module,
    codex_command,
    ensure_modules_loaded,
    ModuleMeta,
    CommandMeta,
)

__all__ = [
    # KVTC Strategy
    "KVTCCompressor",
    # Token utilities
    "token_count",
    "calculate_reduction",
    # Exceptions
    "TokenReductionError",
    "EncodingError",
    "BenchmarkDriftError",
    # Report utilities
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
    # New: SQLite Store & Registry
    "CodexStore",
    "registry",
    "codex_module",
    "codex_command",
    "ensure_modules_loaded",
    "ModuleMeta",
    "CommandMeta",
]

__version__ = "5.0.4"
