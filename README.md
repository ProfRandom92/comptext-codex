# CompText-Codex

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

> A Domain-Specific Language (DSL) for efficient LLM interaction - reducing prompts by 70% with structured, composable commands.

## 🚀 What is CompText-Codex?

CompText is a DSL designed to replace verbose natural language prompts with compact, unambiguous commands. Think of it as **"SQL for LLMs"** or **"shorthand for AI control"**.

### Before vs After

❌ **Natural Language (26 tokens via whitespace heuristic):**
> "Please analyze this Python code, identify performance bottlenecks, suggest optimizations with code examples, explain the reasoning behind each optimization, and provide benchmark comparisons showing expected improvements"

✅ **CompText (4 tokens via whitespace heuristic):**
```
@CODE_ANALYZE[perf_bottleneck] + @CODE_OPT[explain=detail, bench=compare]
```

**Result: ~85% token reduction** while being MORE precise.

---

## 📦 What's Included?

### **Core Modules (Built-In)**

- **General**: Summarization, translation, pattern extraction
- **Programming**: Code analysis, optimization, debugging, docs, security scan
- **Visualization**: Chart/diagram/dashboard blueprints
- **AI Control**: Model config, prompt optimization, chain planning

### **Starter Examples**
- Quick-start snippets in `README.md` and `QUICK_START.md`
- Parser/executor demo script in the tests to validate token savings

---

## 🎯 Why Use CompText?

| Benefit | Description |
|---------|-------------|
| **🔥 Token Efficiency** | Save 50-80% tokens vs natural language |
| **🎯 Precision** | Eliminate ambiguity in complex instructions |
| **♻️ Reusability** | Save common workflows as compact commands |
| **🤖 Automation** | Perfect for API usage and batch processing |
| **📝 Version Control** | DSL commands easier to version than prose |

---

## ⚡ Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ProfRandom92/comptext-codex.git
cd comptext-codex

# Install dependencies (optional: all core features use the standard library)
pip install -r requirements.txt

# Install package
pip install -e .
```

### Basic Usage

```python
from comptext import CompTextParser

# Initialize parser
parser = CompTextParser()

# Example 1: Code Analysis
command = "@CODE_ANALYZE[perf_bottleneck] + @CODE_OPT[explain=detail]"
result = parser.execute(command, code="your_code_here")

# Example 2: Documentation Generation
command = "@DOC_GEN[api, format=markdown, include_examples=true]"
result = parser.execute(command, source_code="...")

# Example 3: Chained AI task
command = "@CHAIN[steps=analyze;optimize;report]"
result = parser.execute(command)
```

### Checking Token Savings Programmatically

```python
from comptext import estimate_tokens, token_reduction

natural = "Please analyze this Python code, identify performance bottlenecks, ..."
dsl = "@CODE_ANALYZE[perf_bottleneck] + @CODE_OPT[explain=detail, bench=compare]"

natural_tokens, dsl_tokens, reduction = token_reduction(natural, dsl)
print(natural_tokens, dsl_tokens, reduction)  # 26, 4, ~0.85
```

Or directly from the CLI:

```bash
comptext "@CODE_ANALYZE[perf_bottleneck] + @CODE_OPT[explain=detail, bench=compare]" \
  --natural "Please analyze this Python code, identify performance bottlenecks, ..." \
  --show-tokens
```

---

## 📚 Documentation

- **[Quick Start Guide](QUICK_START.md)** - Get up and running in 5 minutes
- **[Examples](EXAMPLES.md)** - 55+ production-ready examples
- **[Contributing](CONTRIBUTING.md)** - How to contribute

---

## 💡 Real-World Use Cases

### 1. API Cost Optimization
Reduce token usage by 70% in production LLM applications.

### 2. Code Generation Pipelines
Consistent, reproducible code generation.

### 3. Data Analysis Workflows
Complex multi-step analysis in compact form.

### 4. Multi-Agent Systems
Clear role definitions and task assignments.

---

## 🏗️ Project Structure

```
comptext-codex/
├── comptext/                 # Core DSL implementation
│   ├── __init__.py
│   ├── parser.py             # Command parser
│   ├── executor.py           # Command executor
│   ├── cli.py                # Command-line interface
│   ├── data/                 # Packaged CSV helpers
│   └── modules/              # Command implementations
├── comptext_mcp/             # MCP Server implementation (optional)
├── examples/                 # 55+ usage examples
├── tests/                    # pytest test suite
├── docs/                     # Documentation
├── README.md
├── QUICK_START.md
├── EXAMPLES.md
├── CONTRIBUTING.md
├── requirements.txt
├── setup.py
└── LICENSE
```

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📊 Performance Benchmarks

| Metric | Natural Language | CompText | Improvement |
|--------|------------------|----------|-------------|
| Tokens per task (sample above) | 26 | 4 | **~85% reduction** |
| Ambiguity errors (qualitative) | Higher | Lower | **Fewer retries** |
| Execution time (prompted runs) | Longer prompts | Short prompts | **Less latency** |

---

## 🛠️ Tech Stack

- **Language:** Python 3.8+
- **Protocol:** MCP (Model Context Protocol)
- **Testing:** pytest, coverage
- **CI/CD:** GitHub Actions
- **License:** MIT

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ by [@ProfRandom92](https://github.com/ProfRandom92)**
