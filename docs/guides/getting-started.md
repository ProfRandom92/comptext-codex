# Getting Started with CompText

This guide will help you get up and running with CompText-Codex in minutes.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install from Source

```bash
# Clone the repository
git clone https://github.com/ProfRandom92/comptext-codex.git
cd comptext-codex

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Verify Installation

```bash
# Check CLI is available
comptext --help

# Run token report
comptext token-report --codex-dir codex
```

## Quick Start

### 1. Basic Text Compression

```python
from comptext_codex.executor import CompTextExecutor

executor = CompTextExecutor()

# Compress text
results = executor.execute("@A:compress The quick brown fox jumps repeatedly")
print(results[0].result)
```

### 2. Code Analysis

```python
code = """
def slow_function(items):
    for i in items:
        for j in items:
            if i == j:
                print(i)
"""

results = executor.execute(
    "@CODE_ANALYZE[perf_bottleneck, complexity]",
    context={'code': code}
)
print(results[0].result)
```

### 3. Chained Commands

```python
# Chain multiple operations
command = "@EXTRACT[source=db] + @TRANSFORM[clean=true] + @LOAD[dest=warehouse]"
results = executor.execute(command)

for result in results:
    print(result.result)
```

## Key Concepts

### Commands

CompText commands follow patterns:
- **Simple**: `@A:compress text`
- **Parametric**: `@CODE_ANALYZE[type1, type2]`
- **Key-Value**: `@AUTOML[task=classification, metric=f1]`

### Modules

13 production modules (A-M):
- **A**: Core commands
- **B**: Analysis
- **C**: Formatting
- **D**: AI Control
- **E**: ML Pipelines
- **F**: Documentation
- **G**: Testing
- **H**: Database
- **I**: Security
- **J**: DevOps
- **K**: Frontend/UI
- **L**: ETL
- **M**: MCP Integration

### Context

Pass data to commands via context:
```python
executor.execute(
    "@AUTOML[task=classification]",
    context={'dataset': 'data.csv', 'target': 'label'}
)
```

## Next Steps

- Explore [Examples](../../examples/)
- Read [DSL Syntax Guide](syntax.md)
- Learn [Advanced Patterns](../tutorials/advanced-patterns.md)

## Troubleshooting

### Module Import Errors

```bash
# Reinstall package
pip install -e .
```

### Command Not Found

Ensure the codex directory is accessible:
```python
executor = CompTextExecutor(codex_dir="./codex")
```

## Support

- GitHub Issues: https://github.com/ProfRandom92/comptext-codex/issues
- Documentation: https://github.com/ProfRandom92/comptext-codex/docs
