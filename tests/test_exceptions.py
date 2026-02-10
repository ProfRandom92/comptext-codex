"""Tests for the unified exception hierarchy."""

import pytest

from comptext_codex.exceptions import (
    CompTextError,
    ParserError,
    InvalidSyntaxError,
    UnknownCommandError,
    ExecutionError,
    ModuleNotFoundError_,
    CommandNotFoundError,
    HandlerError,
    TokenReductionError,
    EncodingError,
    BenchmarkDriftError,
    ConfigurationError,
)


class TestExceptionHierarchy:
    """Verify that every exception is a subclass of CompTextError."""

    @pytest.mark.parametrize("exc_cls", [
        ParserError,
        InvalidSyntaxError,
        UnknownCommandError,
        ExecutionError,
        ModuleNotFoundError_,
        CommandNotFoundError,
        HandlerError,
        TokenReductionError,
        EncodingError,
        BenchmarkDriftError,
        ConfigurationError,
    ])
    def test_is_subclass_of_comptext_error(self, exc_cls):
        assert issubclass(exc_cls, CompTextError)

    def test_parser_subtree(self):
        assert issubclass(InvalidSyntaxError, ParserError)
        assert issubclass(UnknownCommandError, ParserError)

    def test_execution_subtree(self):
        assert issubclass(ModuleNotFoundError_, ExecutionError)
        assert issubclass(CommandNotFoundError, ExecutionError)
        assert issubclass(HandlerError, ExecutionError)

    def test_token_subtree(self):
        assert issubclass(EncodingError, TokenReductionError)
        assert issubclass(BenchmarkDriftError, TokenReductionError)

    def test_catch_all_with_base(self):
        """A single except CompTextError should catch any subclass."""
        with pytest.raises(CompTextError):
            raise HandlerError("test")
        with pytest.raises(CompTextError):
            raise InvalidSyntaxError("test")
        with pytest.raises(CompTextError):
            raise BenchmarkDriftError("test")

    def test_backward_compat_token_reduction(self):
        """token_reduction module still re-exports the same classes."""
        from comptext_codex.token_reduction import (
            TokenReductionError as TR,
            EncodingError as EE,
            BenchmarkDriftError as BD,
        )
        assert TR is TokenReductionError
        assert EE is EncodingError
        assert BD is BenchmarkDriftError


class TestBaseModuleExceptions:
    """Verify BaseModule raises CommandNotFoundError for unknown commands."""

    def test_unknown_command_raises(self):
        from comptext_codex.modules.module_a import ModuleA
        from dataclasses import dataclass

        @dataclass
        class FakeCmd:
            command: str = "nonexistent"
            args: list = None
            kwargs: dict = None

            def __post_init__(self):
                self.args = self.args or []
                self.kwargs = self.kwargs or {}

        module = ModuleA()
        with pytest.raises(CommandNotFoundError):
            module.execute(FakeCmd(), context={})
