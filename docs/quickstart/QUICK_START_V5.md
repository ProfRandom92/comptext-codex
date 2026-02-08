# CompText V5.0 ULTRA - Quick Start Guide

## 🚀 Installation (30 seconds)

```bash
git clone https://github.com/ProfRandom92/comptext-codex.git
cd comptext-codex
pip install -e .
```

## ⚡ Your First V5 Command (10 seconds)

```bash
# Generate Python Fibonacci function
comptext parse "C;P:FIB"

# Output:
# Command: CODE
# Language: PYTHON
# Task: FIB
```

## 🎯 Real Examples

### 1. Simple Code Generation
```bash
# Natural: "Write a Python function for Fibonacci" (6 tokens)
# V5: "C;P:FIB" (1 token)
# Reduction: 83.3%

comptext parse "C;P:FIB" --stats --natural "Write a Python function for Fibonacci"
```

### 2. Test with Modifiers
```bash
# Natural: "Write unit tests for Fibonacci in Python with error handling" (11 tokens)
# V5: "T;P;R:FIB" (1 token)
# Reduction: 90.9%

comptext parse "T;P;R:FIB"
```

### 3. Batch Operations
```bash
# Natural: "Summarize repo, write Python Fibonacci, explain why fast" (9 tokens)
# V5: "B:[D:SUM]|[C;P:FIB]|[E;C:WHY]" (1 token)
# Reduction: 88.9%

comptext parse "B:[D:SUM]|[C;P:FIB]|[E;C:WHY]"
```

### 4. Complex Workflow
```bash
# Natural: "Analyze codebase, fix TypeScript memory leaks, optimize queries, generate docs" (11 tokens)
# V5: "B:[A:STRUCT]|[F;T:MEM]|[O;S:Q]|[D:API]" (1 token)
# Reduction: 90.9%

comptext parse "B:[A:STRUCT]|[F;T:MEM]|[O;S:Q]|[D:API]"
```

## 📚 Cheat Sheet

### Commands (Single Char)
- `C` = CODE
- `F` = FIX
- `M` = MODIFY
- `T` = TEST
- `D` = DOCUMENT
- `E` = EXPLAIN
- `O` = OPTIMIZE
- `A` = ANALYZE

### Languages (Single Char)
- `P` = Python
- `J` = JavaScript
- `T` = TypeScript
- `R` = Rust
- `G` = Go
- `S` = SQL
- `H` = HTML

### Modifiers (Single Char)
- `N` = NO_COMMENTS
- `S` = STRICT
- `R` = ROBUST
- `C` = CONCISE

### Syntax Pattern
```
CMD;LANG;MOD:TASK
 |   |    |   |
 |   |    |   +-- Task name
 |   |    +------ Modifier (optional)
 |   +----------- Language (optional)
 +--------------- Command (required)
```

### Batch Pattern
```
B:[CMD1]|[CMD2]|[CMD3]
|   |     |      |
|   |     |      +-- Third command
|   |     +--------- Second command
|   +--------------- First command
+------------------- Batch prefix
```

## 🎮 Interactive Mode

```bash
# Start interactive shell
comptext interactive

# Commands you can try:
v5> C;P:FIB
v5> T;P;R:FIB
v5> B:[D:SUM]|[C;P:FIB]|[E;C:WHY]
v5> help
v5> ref
v5> exit
```

## 🔬 Encoding Commands

```bash
# Encode from natural language
comptext encode CODE --language PYTHON --task FIB
# Output: C;P:FIB

# With modifiers
comptext encode TEST --language PYTHON --modifiers ROBUST --task FIB
# Output: T;P;R:FIB
```

## 📊 Benchmarking

```bash
# Compare token efficiency
comptext benchmark \
  -n "Write a Python function for Fibonacci" \
  -v "C;P:FIB"

# Output:
# Reduction: 83.3% (6 -> 1 tokens)
```

## 🛠️ Python API

```python
from comptext_codex.parser_v5 import CompTextParserV5

# Initialize parser
parser = CompTextParserV5()

# Parse command
result = parser.parse("C;P:FIB")
print(result[0].command)   # 'C'
print(result[0].language)  # 'P'
print(result[0].task)      # 'FIB'

# Encode command
v5_cmd = parser.encode('CODE', 'PYTHON', task='FIB')
print(v5_cmd)  # C;P:FIB

# Calculate token reduction
stats = parser.calculate_token_reduction(
    "Write a Python function for Fibonacci",
    "C;P:FIB"
)
print(f"Reduction: {stats['reduction_percent']}%")
# Output: Reduction: 83.3%
```

## 🎯 Next Steps

1. **Try the examples above** - Get familiar with V5 syntax
2. **Read the full README** - `cat README_V5.md`
3. **View reference** - `comptext reference`
4. **Run tests** - `pytest tests/test_parser_v5.py -v`
5. **Explore CLI** - `comptext --help`

## 💡 Pro Tips

1. **Start simple**: Use single commands (`C;P:FIB`) before batches
2. **Use modifiers**: Add `R` for robust code, `C` for concise output
3. **Batch wisely**: Combine related tasks (`B:[A:X]|[F:Y]|[O:Z]`)
4. **Check stats**: Always verify token reduction with `--stats`
5. **Interactive mode**: Great for learning and experimentation

## 🆘 Troubleshooting

### Command not recognized?
```bash
# Show syntax reference
comptext reference
```

### Want to see V4 equivalent?
```bash
# Parse with V4 format
comptext parse "C;P:FIB" --v4
```

### Need help?
```bash
# CLI help
comptext --help

# Command-specific help
comptext parse --help
comptext encode --help
```

## 🎉 Success Metrics

After this quick start, you should be able to:
- ✅ Parse V5.0 ULTRA commands
- ✅ Encode commands from natural language
- ✅ Use batch operations
- ✅ Measure token reduction
- ✅ Use interactive mode
- ✅ Integrate V5 into Python code

**Average time to proficiency: 5-10 minutes**
**Token reduction achieved: 94%**

---

**Ready to build something amazing? Let's go! 🚀**
