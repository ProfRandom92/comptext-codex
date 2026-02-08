# Skill: CompText Optimize 📊
**Purpose:** Decision logic for cost reduction and activation heuristics.

## 🚨 Activation Heuristic (WHEN to use CompText)
Activate CompText V5 compression ONLY if one of these conditions is met:
1. **Context Load:** Input context exceeds 500 tokens.
2. **Handoff:** Data is being passed between >2 Agents (e.g., in n8n or LangGraph).
3. **Explicit Request:** User asks for "efficiency", "low cost", or "speed".

## Cost Impact
| Operation | Raw Token Cost | CompText Cost | Savings |
|-----------|----------------|---------------|---------|
| Analysis  | ~$0.04         | ~$0.002       | **94%** |
| Handoff   | High           | Low (O(1))    | **92%** |
