# V5.0 Protocol

## Overview

CompText V5.0 is a **deterministic protocol** for compressing verbose context into compact command structures. It achieves **94% token reduction** through single-character mapping.

## Protocol Syntax

### Basic Format

```
[COMMAND];[LANGUAGE]:[TASK]
```

**Components:**
- `COMMAND` — Single letter (C, F, M, T, D, E, O, A)
- `LANGUAGE` — Single letter (P, J, T, R, G, S, H, ...)
- `TASK` — Task identifier or custom code

### Examples

```
C;P:FIB              → CODE | PYTHON | Fibonacci
F;J:RACE             → FIX | JavaScript | Race condition
T;T:TYPES            → TEST | TypeScript | Type coverage
D;P:API              → DOCUMENT | Python | API reference
E;R:MEMORY           → EXPLAIN | Rust | Memory safety
O;S:PERF             → OPTIMIZE | SQL | Performance
A;H:XSS              → ANALYZE | HTML | XSS vulnerabilities
```

## Command Vocabulary

| Code | Command | Description | Example |
|------|---------|-------------|----------|
| **C** | CODE | Generate new code | `C;P:FIB` |
| **F** | FIX | Debug and fix issues | `F;J:RACE` |
| **M** | MODIFY | Refactor/update code | `M;T:TYPES` |
| **T** | TEST | Write test cases | `T;P:UNIT` |
| **D** | DOCUMENT | Generate documentation | `D;P:API` |
| **E** | EXPLAIN | Explain code/concept | `E;R:MEMORY` |
| **O** | OPTIMIZE | Improve performance | `O;S:PERF` |
| **A** | ANALYZE | Analyze for issues | `A;H:XSS` |

## Language Codes

| Code | Language | Usage | Variants |
|------|----------|-------|----------|
| **P** | Python | AI/ML, backend | py, python |
| **J** | JavaScript | Frontend, Node.js | js, node |
| **T** | TypeScript | Typed JS | ts, tsx |
| **R** | Rust | Systems, embedded | rs, rust |
| **G** | Go | Microservices | go, golang |
| **S** | SQL | Databases | sql, query |
| **H** | HTML | Markup, templates | html, html5 |
| **C** | C/C++ | Low-level | c, cpp |
| **K** | Kotlin | Android | kt, kotlin |
| **W** | WebAssembly | Wasm | wasm, wat |

## Task Codes (Common)

| Code | Task | Description |
|------|------|-------------|
| **FIB** | Fibonacci | Classic algorithm |
| **SORT** | Sorting | Array/list sorting |
| **SEARCH** | Search | Binary/linear search |
| **TREE** | Tree | Tree traversal |
| **GRAPH** | Graph | Graph algorithms |
| **DP** | Dynamic Programming | DP optimization |
| **UNIT** | Unit Tests | Basic test cases |
| **INT** | Integration | Integration tests |
| **E2E** | End-to-End | Full workflow tests |
| **PERF** | Performance | Speed optimization |
| **MEM** | Memory | Memory optimization |
| **API** | API | REST/GraphQL API |
| **DB** | Database | DB schema/query |
| **AUTH** | Authentication | Login/auth system |
| **XSS** | Security | XSS/injection fixes |

## Batch Operations

### Syntax

```
B:[COMMAND1]|[COMMAND2]|[COMMAND3]
```

### Examples

**Generate → Test → Document:**
```
B:[C;P:FIB]|[T;P:FIB]|[D:FIB]
```

Executes:
1. `C;P:FIB` — Generate Python Fibonacci
2. `T;P:FIB` — Create tests for Fibonacci
3. `D:FIB` — Generate documentation

**Multi-language workflow:**
```
B:[C;P:API]|[C;J:API]|[C;T:API]
```

Generates API clients in Python, JavaScript, and TypeScript.

## Token Savings Breakdown

### Natural Language vs. CompText

**Natural:**
```
"Write a Python function that calculates the Fibonacci sequence up to n terms"
```
Tokens: **20**

**CompText V5.0:**
```
C;P:FIB
```
Tokens: **1**

**Reduction:** 95%

### Real-World Examples

| Scenario | Natural | CompText | Reduction |
|----------|---------|----------|----------|
| Simple function | 12 tokens | 1 token | **91.7%** |
| Test suite | 18 tokens | 1 token | **94.4%** |
| Documentation | 15 tokens | 1 token | **93.3%** |
| Batch (3 ops) | 35 tokens | 3 tokens | **91.4%** |
| API workflow | 25 tokens | 1 token | **96.0%** |

## Extension Mechanism

### Custom Task Codes

You can define custom tasks in `codex/commands.yaml`:

```yaml
tasks:
  FIB: "Generate Fibonacci sequence"
  CUSTOM: "Your custom task"
  ML_TRAIN: "Machine learning training"
```

### Custom Profiles

Profiles in `codex/profiles.yaml` extend the base protocol:

```yaml
profiles:
  ml:
    commands: [CODE, FIX, OPTIMIZE, ANALYZE]
    languages: [PYTHON, JUPYTER]
    tasks: [ML_TRAIN, ML_EVAL, ML_TUNE]
```

## Backward Compatibility

- ✅ V4.0 commands still supported
- ✅ Gradual migration possible
- ✅ No breaking changes
- ✅ Feature flags for new syntax

## Parsing Examples

### Using Python API

```python
from comptext_codex.parser_v5 import CompTextParserV5

parser = CompTextParserV5()

# Single command
result = parser.parse("C;P:FIB")
print(result[0].command)   # CODE
print(result[0].language)  # PYTHON
print(result[0].task)      # FIB

# Batch command
result = parser.parse("B:[C;P:API]|[T;P:API]")
for cmd in result:
    print(f"{cmd.command} in {cmd.language}")
```

### Using CLI

```bash
# Parse single command
comptext parse "C;P:FIB"

# Encode from natural language
comptext encode --command CODE --language PYTHON --task FIB

# Batch parsing
comptext parse "B:[C;P:FIB]|[T;P:FIB]"
```

## Best Practices

✅ **DO:**
- Use standard task codes for consistency
- Keep commands under 20 characters
- Use batch operations for workflows
- Store original intent in comments

❌ **DON'T:**
- Create arbitrary task codes
- Mix protocols in same message
- Use undefined language codes
- Assume implicit context

## Error Handling

Invalid syntax returns detailed errors:

```python
try:
    result = parser.parse("INVALID")
except ValueError as e:
    print(e)  # "Invalid command: INVALID"
```
