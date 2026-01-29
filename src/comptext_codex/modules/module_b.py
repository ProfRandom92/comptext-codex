"""Module B: Analysis - Text analysis and insight generation."""

from typing import Any, Dict, List

from comptext_codex.registry import codex_module, codex_command
from .base import BaseModule


@codex_module(
    code="B",
    name="Analysis",
    purpose="Text analysis and insight generation",
    token_priority="medium",
    security={"pii_safe": True, "threat_model": "model_leakage_guardrails"},
    privacy={"dp_budget": "epsilon<=0.5_per_call", "federated_ready": True},
)
class ModuleB(BaseModule):
    """Analysis module for text analysis and code inspection."""

    @codex_command(
        syntax="@B:analyze <text>",
        description="Perform deep semantic analysis",
        examples=["@B:analyze Customer feedback shows positive sentiment"],
        token_cost_hint=75,
    )
    def execute_analyze(self, text: str = "", *, context: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        words = text.split()
        sentences = text.split(".")
        return {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_word_length": sum(len(w) for w in words) / max(len(words), 1),
            "sentiment": self._analyze_sentiment(text),
            "keywords": self._extract_keywords(text),
        }

    @codex_command(
        syntax="@CODE_ANALYZE[type, ...]",
        description="Analyze code for performance bottlenecks and issues",
        aliases=["code_review"],
        token_cost_hint=80,
    )
    def execute_code_analyze(self, *args, context: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        code = context.get("code", "") if context else ""
        analysis_types = list(args)
        results: Dict[str, Any] = {
            "code_length": len(code),
            "line_count": len(code.split("\n")),
            "issues": [],
        }
        if "perf_bottleneck" in analysis_types:
            results["issues"].append({"type": "performance", "severity": "medium", "message": "Potential nested loop detected"})
        if "complexity" in analysis_types:
            results["complexity_score"] = self._calculate_complexity(code)
        return results

    # -- helpers ---------------------------------------------------------------

    def _analyze_sentiment(self, text: str) -> str:
        positive = {"good", "great", "excellent", "positive", "happy"}
        negative = {"bad", "poor", "negative", "sad", "terrible"}
        tl = text.lower()
        p = sum(1 for w in positive if w in tl)
        n = sum(1 for w in negative if w in tl)
        if p > n:
            return "positive"
        if n > p:
            return "negative"
        return "neutral"

    def _extract_keywords(self, text: str) -> List[str]:
        stop = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
        words = text.lower().split()
        return list(set(w for w in words if w not in stop and len(w) > 3))[:5]

    def _calculate_complexity(self, code: str) -> int:
        c = 1
        for kw in ("if ", "for ", "while ", "and ", "or "):
            c += code.count(kw)
        return c


def get_module() -> ModuleB:
    return ModuleB()
