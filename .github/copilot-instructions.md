# COMPTEXT V4.0 SYSTEM INSTRUCTIONS

You are operating in "CompText Mode". The user will communicate using a highly compressed DSL (Domain Specific Language) to save tokens and increase precision.

## 1. THE PROTOCOL
- **If you see** `CMD:...;` or `BATCH:...` syntax -> **ACT IMMEDIATELY**.
- **DO NOT** explain the syntax back to the user.
- **DO NOT** allow "chatty" intros (e.g., "Here is the code..."). Just output the result.
- **PRIORITY:** High Efficiency, Zero Fluff, Production-Grade Code.

## 2. THE VOCABULARY (CompText Bible)
[MODULE A: COMMANDS]
- `CMD:` Primary Action (CODE, FIX, MOD, TEST, DOC, EXPL, OPT)
- `LNG:` Language (PY, TS, JS, RS, GO, SQL, HTM)
- `FRM:` Framework (RCT=React, PND=Pandas, DJ=Django, NEXT=NextJS)

[MODULE B: OUTPUT & STYLE]
- `FMT:` Format (CODE=Code Only, MD=Markdown, LST=List, JSON)
- `STY:` Tone (PRO=Professional, CONCISE=Short, ROBUST=Error-safe)
- `PRF:` Prefs (NO_COM=No comments, ES6=Modern JS, TYPED=Strict types)

[MODULE C: CONTEXT & SKILL]
- `SKL:` Skill Target (EXP=Expert, MST=Master/Architect - implies deep abstraction)
- `CTX:` Context (Use project files as reference)

[MODULE G: BATCH PROCESSING]
- Syntax: `BATCH: [Task1] || [Task2] || [Task3]`
- `SEP:` `||` (Separator)
- Execution: Perform all tasks in one single response block, separated by headers.

## 3. EXAMPLE INTERACTION
User: `CMD:FIX; LNG:TS; SKL:MST; PRF:NO_COM; TSK:MEM_LEAK`
You: (Outputs *only* the fixed TypeScript code, solving the memory leak with master-level patterns, no comments).


## Module G Batch

# Module G: Batch Processing

## Overview

Module G introduces batch processing capabilities to CompText, enabling efficient execution of multiple commands in a single operation. This module is designed to maximize token efficiency when executing multiple related tasks.

## Syntax

```
BATCH: [Cmd1] || [Cmd2] || [Cmd3]
```

The `BATCH` command groups multiple CompText commands together, separated by `||` delimiters. Each command is executed according to the specified execution mode.

### Basic Structure

```
BATCH: [@COMMAND1[params]] || [@COMMAND2[params]] || [@COMMAND3[params]]
```

## Parameters

### Execution Modes

The batch processor supports two execution modes:

#### `SEQ` - Sequential Execution

Commands are executed one after another in the order specified. Each command completes before the next one starts.

**Syntax:**
```
BATCH[mode=SEQ]: [Cmd1] || [Cmd2] || [Cmd3]
```

**Use Cases:**
- When commands depend on results from previous commands
- When order matters (e.g., data pipeline: extract → transform → load)
- When resources are limited and parallel execution might cause conflicts

**Example:**
```
BATCH[mode=SEQ]: [@EXTRACT[source=db]] || [@TRANSFORM[clean=true]] || [@LOAD[dest=warehouse]]
```

#### `PAR` - Parallel Execution

Commands are executed simultaneously, independent of each other. This maximizes throughput for independent operations.

**Syntax:**
```
BATCH[mode=PAR]: [Cmd1] || [Cmd2] || [Cmd3]
```

**Use Cases:**
- When commands are independent and don't rely on each other
- When maximizing execution speed is critical
- When processing multiple data sources simultaneously

**Example:**
```
BATCH[mode=PAR]: [@CODE_ANALYZE[file1.py]] || [@CODE_ANALYZE[file2.py]] || [@CODE_ANALYZE[file3.py]]
```

### Default Behavior

If no mode is specified, `SEQ` (sequential) is the default:
```
BATCH: [Cmd1] || [Cmd2] || [Cmd3]  # Executes sequentially
```

## Examples

### Example 1: Sequential Data Processing

**Natural Language (42 tokens):**
> "First extract data from the database, then clean and transform it, and finally load it into the data warehouse"

**CompText with BATCH (12 tokens - 71% reduction):**
```
BATCH[mode=SEQ]: [@EXTRACT[source=db]] || [@TRANSFORM[clean=true]] || [@LOAD[dest=warehouse]]
```

### Example 2: Parallel Code Analysis

**Natural Language (56 tokens):**
> "Analyze file1.py for performance issues, analyze file2.py for security vulnerabilities, and analyze file3.py for code style violations. Run all analyses simultaneously."

**CompText with BATCH (18 tokens - 68% reduction):**
```
BATCH[mode=PAR]: [@CODE_ANALYZE[file1.py, perf_bottleneck]] || [@SEC_SCAN[file2.py, severity=high]] || [@CODE_ANALYZE[file3.py, style]]
```

### Example 3: Documentation Generation Pipeline

**Natural Language (48 tokens):**
> "Generate API documentation for the project, create a tutorial guide, and build a changelog from git history. Do these tasks one after another."

**CompText with BATCH (15 tokens - 69% reduction):**
```
BATCH[mode=SEQ]: [@DOC_GEN[api, format=markdown]] || [@DOC_GEN[tutorial]] || [@CHANGELOG[source=git]]
```

### Example 4: Parallel Test Execution

**Natural Language (35 tokens):**
> "Run unit tests, integration tests, and end-to-end tests simultaneously to save time"

**CompText with BATCH (10 tokens - 71% reduction):**
```
BATCH[mode=PAR]: [@TEST_RUN[unit]] || [@TEST_RUN[integration]] || [@TEST_RUN[e2e]]
```

## Token Efficiency

The BATCH command provides significant token savings:

| Scenario | Natural Language | CompText BATCH | Reduction |
|----------|------------------|----------------|-----------|
| 3-step pipeline | 42 tokens | 12 tokens | 71% |
| Parallel analysis | 56 tokens | 18 tokens | 68% |
| Doc generation | 48 tokens | 15 tokens | 69% |
| Test suite | 35 tokens | 10 tokens | 71% |

**Average savings: 70% token reduction**

## Advanced Features

### Error Handling

In `SEQ` mode, if a command fails, the batch stops and returns the error.

In `PAR` mode, all commands execute independently. Failed commands return errors, but don't stop other commands.

### Result Aggregation

Batch results are returned as an array, with each element corresponding to the result of each command in order.

```
BATCH[mode=SEQ]: [Cmd1] || [Cmd2] || [Cmd3]
# Returns: [Result1, Result2, Result3]
```

## Integration with Other Modules

The BATCH command works seamlessly with all existing CompText modules:

- **Module A-E:** Core commands, analysis, ML pipelines
- **Module F-J:** Documentation, testing, database, security, DevOps
- **Module K-M:** Frontend, ETL, MCP integration

## Security Considerations

- Each command in a batch maintains its own security context
- Parallel execution doesn't share state between commands
- Batch operations are subject to the same PII and differential privacy constraints as individual commands

## Best Practices

1. **Use SEQ when**: Commands have dependencies or need ordered execution
2. **Use PAR when**: Commands are independent and can run concurrently
3. **Keep batches focused**: Group related commands for clarity
4. **Consider resource limits**: Large parallel batches may need throttling
5. **Handle errors gracefully**: Account for partial failures in PAR mode

## Performance Metrics

- **Token efficiency**: 68-71% reduction vs natural language
- **Execution speedup (PAR)**: Up to N× faster for N independent commands
- **Memory overhead**: Minimal - batch structure adds ~2-3 tokens per command

## Future Enhancements

Potential extensions to Module G:
- Conditional branching within batches
- Nested batch operations
- Resource throttling controls
- Dynamic batch composition
- Batch templates for common workflows

