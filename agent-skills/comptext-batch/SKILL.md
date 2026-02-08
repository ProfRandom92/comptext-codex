# Skill: CompText Batch ⚡
**Purpose:** Execute multi-step workflows in a single transaction.

## Workflow Patterns

### 1. The "Analyze & Fix" Pattern
Use this for code review tasks to save round-trips.
```comptext
ANALYZE;T:CODE|D:DEEP >> FIX;M:AUTO|S:STRICT
```

### 2. The "Architecture Review" Pattern
```comptext
CTX;L:ARCH|F:HIGH >> CRIT;M:SEC|LVL:H >> OUT;F:MD
```

## Batching Rules
* Use `>>` to chain commands (Pipeline Mode).
* Ensure the output of Command A is compatible with Input of Command B.
