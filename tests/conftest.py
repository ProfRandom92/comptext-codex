"""Enterprise conftest: shared fixtures and session-level determinism guards."""

import sys
from pathlib import Path

import pytest


def _ensure_src_on_path() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


_ensure_src_on_path()


# ---------------------------------------------------------------------------
# Session-scoped determinism guard: fail fast if tiktoken is missing
# ---------------------------------------------------------------------------

def pytest_sessionstart(session: pytest.Session) -> None:
    """Verify tiktoken is available at session start (enterprise requirement)."""
    try:
        from comptext_codex.token_reduction import TIKTOKEN_AVAILABLE
        if not TIKTOKEN_AVAILABLE:
            pytest.exit(
                "FATAL: tiktoken is not installed. "
                "Enterprise builds require deterministic BPE token counting.",
                returncode=1,
            )
    except ImportError:
        pass  # Module not installed yet (e.g. during initial setup)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def all_benchmark_cases():
    """Provide the full DEFAULT_CASES benchmark suite."""
    from comptext_codex.token_reduction import DEFAULT_CASES
    return DEFAULT_CASES


@pytest.fixture
def token_counter():
    """Provide the token_count function for tests."""
    from comptext_codex.token_reduction import token_count
    return token_count


@pytest.fixture
def module_n_instance():
    """Provide a fresh ModuleN instance."""
    from comptext_codex.modules.module_n import ModuleN
    return ModuleN()
