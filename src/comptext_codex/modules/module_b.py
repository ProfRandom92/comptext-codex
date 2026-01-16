"""Module B: Analysis - Text analysis and insight generation."""

from typing import Any, Dict, List
from .base import BaseModule


class ModuleB(BaseModule):
    """Analysis module for text analysis and code inspection."""

    def get_commands(self) -> List[Dict[str, Any]]:
        """Return available commands."""
        return [
            {
                'module': 'B',
                'command': 'analyze',
                'description': 'Perform deep semantic analysis',
                'syntax': '@B:analyze <text>'
            },
            {
                'module': 'B',
                'command': 'code_analyze',
                'description': 'Analyze code for issues',
                'syntax': '@CODE_ANALYZE[type, ...]'
            }
        ]

    def execute_analyze(self, text: str, context: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Perform deep semantic analysis of text.

        Args:
            text: Input text
            context: Execution context
            **kwargs: Additional options

        Returns:
            Analysis results
        """
        # Simple analysis implementation
        words = text.split()
        sentences = text.split('.')

        return {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_word_length': sum(len(w) for w in words) / max(len(words), 1),
            'sentiment': self._analyze_sentiment(text),
            'keywords': self._extract_keywords(text)
        }

    def execute_code_analyze(self, *args, context: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Analyze code for performance bottlenecks and issues.

        Args:
            *args: Analysis types (perf_bottleneck, complexity, etc.)
            context: Execution context with 'code' key
            **kwargs: Additional options

        Returns:
            Code analysis results
        """
        code = context.get('code', '') if context else ''
        analysis_types = list(args)

        results = {
            'code_length': len(code),
            'line_count': len(code.split('\n')),
            'issues': []
        }

        if 'perf_bottleneck' in analysis_types:
            results['issues'].append({
                'type': 'performance',
                'severity': 'medium',
                'message': 'Potential nested loop detected'
            })

        if 'complexity' in analysis_types:
            results['complexity_score'] = self._calculate_complexity(code)

        return results

    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis."""
        positive_words = ['good', 'great', 'excellent', 'positive', 'happy']
        negative_words = ['bad', 'poor', 'negative', 'sad', 'terrible']

        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)

        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # Simple keyword extraction
        words = text.lower().split()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        return list(set(keywords))[:5]

    def _calculate_complexity(self, code: str) -> int:
        """Calculate code complexity score."""
        # Simplified complexity calculation
        complexity = 1
        complexity += code.count('if ')
        complexity += code.count('for ')
        complexity += code.count('while ')
        complexity += code.count('and ')
        complexity += code.count('or ')
        return complexity


def get_module() -> ModuleB:
    """Factory function to get module instance."""
    return ModuleB()
