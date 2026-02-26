"""KVTC Strategy – Key-Value Transform Coding for context compression.

Inspired by the KV Cache Transform Coding paper, this module preserves
"Attention Sinks" (the beginning of a text, e.g. system instructions) and a
"Sliding Window" (the end of a text, e.g. recent context) while compressing
the middle section using existing CompText logic.  This keeps critical context
intact and reduces overall token count.
"""

from __future__ import annotations

from .modules.module_a import ModuleA


class KVTCCompressor:
    """Compress text while preserving head (sink) and tail (window) regions.

    The KVTC strategy keeps the first ``sink_chars`` characters and the last
    ``window_chars`` characters verbatim, compressing only the middle portion
    via :class:`ModuleA.execute_compress`.

    Args:
        sink_chars: Number of leading characters to keep raw (default 500).
        window_chars: Number of trailing characters to keep raw (default 1000).
    """

    def __init__(
        self,
        sink_chars: int = 500,
        window_chars: int = 1000,
    ) -> None:
        self.sink_chars = sink_chars
        self.window_chars = window_chars
        self._compressor = ModuleA()

    def compress(self, text: str) -> str:
        """Compress *text* using the KVTC sink/window strategy.

        If the text is shorter than ``sink_chars + window_chars`` it is
        returned unchanged (no compression needed).

        Returns:
            The compressed string with sink and window regions preserved.
        """
        if len(text) <= self.sink_chars + self.window_chars:
            return text

        sink = text[: self.sink_chars]
        window = text[-self.window_chars :]
        middle = text[self.sink_chars : len(text) - self.window_chars]

        compressed_middle = self._compressor.execute_compress(middle)

        return sink + compressed_middle + window
