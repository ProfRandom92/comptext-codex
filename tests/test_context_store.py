"""Tests for ContextStore with KVTC compression."""

import numpy as np
import pytest
from pydantic import ValidationError

from comptext_codex.context_store import (
    CompressedState,
    ContextStore,
    _compress_kv_cache_py,
)


@pytest.fixture
def ctx_store():
    """Create a fresh ContextStore instance."""
    return ContextStore()


class TestCompressKvCachePy:
    """Tests for the pure-Python fallback compression."""

    def test_returns_bytes(self):
        result = _compress_kv_cache_py([0.5, 1.0, 0.0], 4)
        assert isinstance(result, bytes)

    def test_compressed_smaller_than_raw(self):
        data = [float(i) / 1000 for i in range(1000)]
        compressed = _compress_kv_cache_py(data, 4)
        # Raw float32 data would be 4000 bytes; compressed should be smaller
        assert len(compressed) < len(data) * 4

    def test_bit_budget_affects_output(self):
        data = [0.5, 1.0, 0.25]
        result_4 = _compress_kv_cache_py(data, 4)
        result_8 = _compress_kv_cache_py(data, 8)
        # Different bit budgets produce different quantized values
        assert result_4 != result_8


class TestCompressedState:
    """Tests for the CompressedState Pydantic model."""

    def test_create_valid(self):
        state = CompressedState(
            state_id="test-1",
            payload=b"\x00\x01",
            bit_budget=4,
            original_shape=(2, 3),
        )
        assert state.state_id == "test-1"
        assert state.payload == b"\x00\x01"
        assert state.bit_budget == 4
        assert state.original_shape == (2, 3)

    def test_default_bit_budget(self):
        state = CompressedState(
            state_id="test-2",
            payload=b"\x00",
            original_shape=(1,),
        )
        assert state.bit_budget == 8

    def test_bit_budget_validation_min(self):
        with pytest.raises(ValidationError):
            CompressedState(
                state_id="test-3",
                payload=b"\x00",
                bit_budget=0,
                original_shape=(1,),
            )

    def test_bit_budget_validation_max(self):
        with pytest.raises(ValidationError):
            CompressedState(
                state_id="test-4",
                payload=b"\x00",
                bit_budget=9,
                original_shape=(1,),
            )


class TestContextStoreInsert:
    """Tests for inserting states into ContextStore."""

    def test_insert_1d_tensor(self, ctx_store):
        tensor = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        ctx_store.insert_state("s1", tensor, bit_budget=4)
        assert "s1" in ctx_store
        assert len(ctx_store) == 1

    def test_insert_2d_tensor(self, ctx_store):
        tensor = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)
        ctx_store.insert_state("s2", tensor, bit_budget=4)
        state = ctx_store.get_state("s2")
        assert state is not None
        assert state.original_shape == (2, 2)

    def test_insert_preserves_shape(self, ctx_store):
        tensor = np.zeros((3, 4, 5), dtype=np.float32)
        ctx_store.insert_state("s3", tensor, bit_budget=4)
        state = ctx_store.get_state("s3")
        assert state.original_shape == (3, 4, 5)

    def test_insert_default_bit_budget(self, ctx_store):
        tensor = np.array([1.0], dtype=np.float32)
        ctx_store.insert_state("s4", tensor)
        state = ctx_store.get_state("s4")
        assert state.bit_budget == 4  # default

    def test_insert_overwrite(self, ctx_store):
        tensor1 = np.array([1.0, 2.0], dtype=np.float32)
        tensor2 = np.array([3.0, 4.0, 5.0], dtype=np.float32)
        ctx_store.insert_state("s5", tensor1, bit_budget=4)
        ctx_store.insert_state("s5", tensor2, bit_budget=4)
        state = ctx_store.get_state("s5")
        assert state.original_shape == (3,)


class TestContextStoreLookup:
    """Tests for O(1) state retrieval."""

    def test_get_existing(self, ctx_store):
        tensor = np.array([1.0], dtype=np.float32)
        ctx_store.insert_state("exists", tensor, bit_budget=4)
        state = ctx_store.get_state("exists")
        assert state is not None
        assert state.state_id == "exists"

    def test_get_missing_returns_none(self, ctx_store):
        assert ctx_store.get_state("nonexistent") is None

    def test_payload_is_bytes(self, ctx_store):
        tensor = np.array([0.5, 1.0], dtype=np.float32)
        ctx_store.insert_state("bytes-check", tensor, bit_budget=4)
        state = ctx_store.get_state("bytes-check")
        assert isinstance(state.payload, bytes)
        assert len(state.payload) > 0


class TestContextStoreOperations:
    """Tests for delete, list, len, contains."""

    def test_delete_existing(self, ctx_store):
        tensor = np.array([1.0], dtype=np.float32)
        ctx_store.insert_state("del-me", tensor, bit_budget=4)
        assert ctx_store.delete_state("del-me") is True
        assert "del-me" not in ctx_store

    def test_delete_missing(self, ctx_store):
        assert ctx_store.delete_state("nope") is False

    def test_list_states(self, ctx_store):
        tensor = np.array([1.0], dtype=np.float32)
        ctx_store.insert_state("a", tensor, bit_budget=4)
        ctx_store.insert_state("b", tensor, bit_budget=4)
        ids = ctx_store.list_states()
        assert sorted(ids) == ["a", "b"]

    def test_len_empty(self, ctx_store):
        assert len(ctx_store) == 0

    def test_len_after_inserts(self, ctx_store):
        tensor = np.array([1.0], dtype=np.float32)
        ctx_store.insert_state("x", tensor, bit_budget=4)
        ctx_store.insert_state("y", tensor, bit_budget=4)
        assert len(ctx_store) == 2

    def test_contains(self, ctx_store):
        tensor = np.array([1.0], dtype=np.float32)
        ctx_store.insert_state("in-store", tensor, bit_budget=4)
        assert "in-store" in ctx_store
        assert "not-in-store" not in ctx_store

    def test_rust_available_property(self, ctx_store):
        # Should be a boolean regardless of whether Rust is compiled
        assert isinstance(ctx_store.rust_available, bool)
