"""Advanced token compression strategies for CompText-Codex.

Implements multiple compression levels and strategies to maximize token savings
while maintaining command clarity and executability.
"""

from typing import Dict, List, Tuple, Optional
from enum import Enum
import re


class CompressionLevel(Enum):
    """Compression level for commands."""
    NONE = 0          # No compression
    BASIC = 1         # Basic abbreviations
    MODERATE = 2      # Moderate compression with aliases
    AGGRESSIVE = 3    # Aggressive compression
    ULTRA = 4         # Ultra-compact, maximum savings


class CommandCompressor:
    """Compresses CompText commands for maximum token efficiency."""

    # Common word abbreviations
    ABBREVIATIONS = {
        'analyze': 'anlz',
        'generate': 'gen',
        'create': 'crt',
        'optimize': 'opt',
        'transform': 'xfrm',
        'extract': 'xtr',
        'configure': 'cfg',
        'documentation': 'doc',
        'performance': 'perf',
        'security': 'sec',
        'vulnerability': 'vuln',
        'classification': 'clf',
        'regression': 'reg',
        'deployment': 'dep',
        'infrastructure': 'infra',
        'component': 'comp',
        'interface': 'iface',
        'implementation': 'impl',
        'specification': 'spec',
        'benchmark': 'bench',
        'comparison': 'cmp',
        'explanation': 'expl',
        'recommendation': 'rec',
        'validation': 'val',
        'authentication': 'auth',
        'authorization': 'authz',
        'configuration': 'cfg',
        'development': 'dev',
        'production': 'prod',
        'environment': 'env',
        'application': 'app',
        'database': 'db',
        'repository': 'repo',
    }

    # Parameter name shortcuts
    PARAM_SHORTCUTS = {
        'framework': 'fw',
        'language': 'lang',
        'version': 'ver',
        'include': 'inc',
        'exclude': 'exc',
        'format': 'fmt',
        'output': 'out',
        'input': 'in',
        'source': 'src',
        'destination': 'dest',
        'target': 'tgt',
        'algorithm': 'algo',
        'method': 'mth',
        'strategy': 'strat',
        'threshold': 'thresh',
        'maximum': 'max',
        'minimum': 'min',
        'average': 'avg',
        'enable': 'en',
        'disable': 'dis',
    }

    # Module shortcuts (single char to preserve structure)
    MODULE_SHORTCUTS = {
        'ANALYZE': 'A',
        'CODE': 'C',
        'FORMAT': 'F',
        'AUTOML': 'M',
        'GENERATE': 'G',
        'TEST': 'T',
        'DEPLOY': 'D',
        'EXTRACT': 'E',
        'TRANSFORM': 'X',
        'LOAD': 'L',
    }

    def __init__(self, level: CompressionLevel = CompressionLevel.MODERATE):
        """Initialize compressor.

        Args:
            level: Compression level to use
        """
        self.level = level

    def compress_command(self, command: str) -> str:
        """Compress a CompText command.

        Args:
            command: Original CompText command

        Returns:
            Compressed command string
        """
        if self.level == CompressionLevel.NONE:
            return command

        # Apply compression based on level
        if self.level.value >= CompressionLevel.BASIC.value:
            command = self._apply_basic_compression(command)

        if self.level.value >= CompressionLevel.MODERATE.value:
            command = self._apply_moderate_compression(command)

        if self.level.value >= CompressionLevel.AGGRESSIVE.value:
            command = self._apply_aggressive_compression(command)

        if self.level.value >= CompressionLevel.ULTRA.value:
            command = self._apply_ultra_compression(command)

        return command

    def decompress_command(self, command: str) -> str:
        """Decompress a compressed command (best effort).

        Args:
            command: Compressed command

        Returns:
            Decompressed command
        """
        # Reverse abbreviations
        for full, abbr in self.ABBREVIATIONS.items():
            command = command.replace(abbr, full)

        return command

    def estimate_savings(self, original: str, compressed: str) -> Dict[str, float]:
        """Estimate token savings from compression.

        Args:
            original: Original command
            compressed: Compressed command

        Returns:
            Dictionary with savings metrics
        """
        orig_tokens = len(original.split())
        comp_tokens = len(compressed.split())
        saved_tokens = orig_tokens - comp_tokens
        savings_pct = (saved_tokens / orig_tokens * 100) if orig_tokens > 0 else 0

        orig_chars = len(original)
        comp_chars = len(compressed)
        char_savings_pct = ((orig_chars - comp_chars) / orig_chars * 100) if orig_chars > 0 else 0

        return {
            'original_tokens': orig_tokens,
            'compressed_tokens': comp_tokens,
            'saved_tokens': saved_tokens,
            'savings_percent': round(savings_pct, 1),
            'original_chars': orig_chars,
            'compressed_chars': comp_chars,
            'char_savings_percent': round(char_savings_pct, 1)
        }

    def _apply_basic_compression(self, command: str) -> str:
        """Apply basic compression (abbreviations).

        Args:
            command: Command to compress

        Returns:
            Compressed command
        """
        # Apply word abbreviations
        for full, abbr in self.ABBREVIATIONS.items():
            # Case-insensitive replacement
            pattern = re.compile(re.escape(full), re.IGNORECASE)
            command = pattern.sub(abbr, command)

        return command

    def _apply_moderate_compression(self, command: str) -> str:
        """Apply moderate compression (parameter shortcuts).

        Args:
            command: Command to compress

        Returns:
            Compressed command
        """
        # Apply parameter shortcuts within brackets
        for full, short in self.PARAM_SHORTCUTS.items():
            # Only replace in parameter context (key=value)
            pattern = rf'\b{full}='
            command = re.sub(pattern, f'{short}=', command, flags=re.IGNORECASE)

        return command

    def _apply_aggressive_compression(self, command: str) -> str:
        """Apply aggressive compression (remove spaces, compact syntax).

        Args:
            command: Command to compress

        Returns:
            Compressed command
        """
        # Remove spaces around operators
        command = re.sub(r'\s*=\s*', '=', command)
        command = re.sub(r'\s*,\s*', ',', command)

        # Remove redundant words
        command = command.replace('with ', '')
        command = command.replace('using ', '')
        command = command.replace('for ', '')

        return command

    def _apply_ultra_compression(self, command: str) -> str:
        """Apply ultra compression (maximum density).

        Args:
            command: Command to compress

        Returns:
            Ultra-compressed command
        """
        # Use shortest possible notation
        command = command.replace('true', '1')
        command = command.replace('false', '0')

        # Remove 'include=' prefix if obvious
        command = re.sub(r'include=', '', command)

        # Compact module names
        for full, short in self.MODULE_SHORTCUTS.items():
            command = command.replace(full, short)

        return command


class BatchOptimizer:
    """Optimizes batches of commands for efficiency."""

    def __init__(self):
        """Initialize batch optimizer."""
        self.compressor = CommandCompressor(CompressionLevel.MODERATE)

    def optimize_batch(self, commands: List[str]) -> Tuple[List[str], Dict[str, float]]:
        """Optimize a batch of commands.

        Args:
            commands: List of commands to optimize

        Returns:
            Tuple of (optimized commands, metrics)
        """
        optimized = []
        total_original_tokens = 0
        total_optimized_tokens = 0

        for cmd in commands:
            # Compress command
            compressed = self.compressor.compress_command(cmd)
            optimized.append(compressed)

            # Track metrics
            total_original_tokens += len(cmd.split())
            total_optimized_tokens += len(compressed.split())

        # Calculate batch metrics
        saved_tokens = total_original_tokens - total_optimized_tokens
        savings_pct = (saved_tokens / total_original_tokens * 100) if total_original_tokens > 0 else 0

        metrics = {
            'batch_size': len(commands),
            'original_tokens': total_original_tokens,
            'optimized_tokens': total_optimized_tokens,
            'saved_tokens': saved_tokens,
            'savings_percent': round(savings_pct, 1),
            'avg_savings_per_cmd': round(saved_tokens / len(commands), 1) if commands else 0
        }

        return optimized, metrics

    def merge_similar_commands(self, commands: List[str]) -> List[str]:
        """Merge similar commands for efficiency.

        Args:
            commands: List of commands

        Returns:
            Merged command list
        """
        # Group by module
        grouped: Dict[str, List[str]] = {}

        for cmd in commands:
            # Extract module
            match = re.match(r'@(\w+):', cmd)
            if match:
                module = match.group(1)
                if module not in grouped:
                    grouped[module] = []
                grouped[module].append(cmd)

        # Merge commands in same module
        merged = []
        for module, module_cmds in grouped.items():
            if len(module_cmds) > 1:
                # Try to chain if possible
                chained = ' + '.join(module_cmds)
                merged.append(chained)
            else:
                merged.extend(module_cmds)

        return merged


def demonstrate_compression_levels(command: str) -> Dict[str, Dict]:
    """Demonstrate all compression levels on a command.

    Args:
        command: Command to compress

    Returns:
        Dictionary mapping level names to results
    """
    results = {}

    for level in CompressionLevel:
        compressor = CommandCompressor(level)
        compressed = compressor.compress_command(command)
        metrics = compressor.estimate_savings(command, compressed)

        results[level.name] = {
            'compressed': compressed,
            'metrics': metrics
        }

    return results
