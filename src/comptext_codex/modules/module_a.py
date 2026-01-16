"""Module A: Core Commands - Essential CompText DSL commands for text manipulation."""

import re
from typing import Any, Dict, List
from .base import BaseModule


class ModuleA(BaseModule):
    """Core Commands module for text manipulation and basic operations."""

    def get_commands(self) -> List[Dict[str, Any]]:
        """Return available commands."""
        return [
            {
                'module': 'A',
                'command': 'compress',
                'description': 'Compress text by removing redundancy',
                'syntax': '@A:compress <text>'
            },
            {
                'module': 'A',
                'command': 'expand',
                'description': 'Expand compressed text to full form',
                'syntax': '@A:expand <compressed_text>'
            }
        ]

    def execute_compress(self, text: str, context: Dict[str, Any] = None, **kwargs) -> str:
        """Compress text by removing redundancy while preserving meaning.

        Args:
            text: Input text to compress
            context: Execution context
            **kwargs: Additional options

        Returns:
            Compressed text
        """
        if not text:
            return ""

        # Remove redundant words
        words = text.split()
        seen = set()
        compressed = []

        for word in words:
            word_lower = word.lower()
            if word_lower not in seen or word_lower in ['the', 'a', 'an']:
                compressed.append(word)
                seen.add(word_lower)

        # Remove extra whitespace
        result = ' '.join(compressed)

        # Remove repeated phrases
        result = re.sub(r'\b(\w+)\s+\1\b', r'\1', result, flags=re.IGNORECASE)

        return result

    def execute_expand(self, compressed_text: str, context: Dict[str, Any] = None, **kwargs) -> str:
        """Expand compressed text to full verbose form.

        Args:
            compressed_text: Compressed text
            context: Execution context
            **kwargs: Additional options

        Returns:
            Expanded text
        """
        # This is a simplified expansion - in practice would use NLP models
        return f"Expanded form: {compressed_text}"


def get_module() -> ModuleA:
    """Factory function to get module instance."""
    return ModuleA()
