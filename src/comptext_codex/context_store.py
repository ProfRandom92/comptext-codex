"""ContextStore - O(1) Context Lookup Store with Rust-powered KVTC.

Provides an in-memory store for compressed KV cache tensor states
using adaptive quantization and DEFLATE entropy coding via the
Rust core backend.
"""

import zlib
from typing import Any, Dict, Optional, Tuple

import numpy as np
from pydantic import BaseModel, Field

# Import compiled Rust core with fallback to pure-Python implementation
try:
    from comptext_codex.comptext_rust_core import compress_kv_cache

    _RUST_AVAILABLE = True
except ImportError:
    _RUST_AVAILABLE = False


def _compress_kv_cache_py(tensor_data: list, bit_budget: int) -> bytes:
    """Pure-Python fallback for compress_kv_cache when Rust core is unavailable."""
    quant_scale = 255.0 / bit_budget
    quantized = bytes(
        int(max(0.0, min(255.0, val * quant_scale))) for val in tensor_data
    )
    return zlib.compress(quantized, level=1)


class CompressedState(BaseModel):
    """Represents a compressed KV cache tensor state."""

    state_id: str
    payload: bytes = Field(
        ..., description="DEFLATE compressed KV cache byte array"
    )
    bit_budget: int = Field(default=8, ge=1, le=8)
    original_shape: Tuple[int, ...]

    model_config = {"arbitrary_types_allowed": True}


class ContextStore:
    """O(1) Context Lookup Store with Rust-powered KVTC."""

    def __init__(self) -> None:
        self._store: Dict[str, CompressedState] = {}

    @property
    def rust_available(self) -> bool:
        """Whether the Rust core backend is available."""
        return _RUST_AVAILABLE

    def insert_state(
        self, state_id: str, kv_tensor: Any, bit_budget: int = 4
    ) -> None:
        """Compress and store an agent's KV cache tensor state.

        Args:
            state_id: Unique identifier for this state.
            kv_tensor: NumPy ndarray of the KV cache tensor.
            bit_budget: Quantization bit budget (1-8).
        """
        arr = np.asarray(kv_tensor, dtype=np.float32)
        flattened = arr.flatten().tolist()

        if _RUST_AVAILABLE:
            compressed_bytes = compress_kv_cache(flattened, bit_budget)
        else:
            compressed_bytes = _compress_kv_cache_py(flattened, bit_budget)

        self._store[state_id] = CompressedState(
            state_id=state_id,
            payload=compressed_bytes,
            bit_budget=bit_budget,
            original_shape=arr.shape,
        )

    def get_state(self, state_id: str) -> Optional[CompressedState]:
        """O(1) retrieval of the compressed state."""
        return self._store.get(state_id)

    def delete_state(self, state_id: str) -> bool:
        """Remove a compressed state. Returns True if found and removed."""
        return self._store.pop(state_id, None) is not None

    def list_states(self) -> list:
        """List all stored state IDs."""
        return list(self._store.keys())

    def __len__(self) -> int:
        return len(self._store)

    def __contains__(self, state_id: str) -> bool:
        return state_id in self._store
