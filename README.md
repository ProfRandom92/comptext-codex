# CompText-Codex

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Version](https://img.shields.io/badge/version-4.0.0-green.svg)](https://github.com/ProfRandom92/comptext-codex/releases)
[![Commands](https://img.shields.io/badge/commands-415+-purple.svg)](#-commands-catalog)

> A Domain-Specific Language (DSL) for efficient LLM interaction - reducing prompts by 70% with structured, composable commands.

## What is CompText-Codex?

CompText is a DSL designed to replace verbose natural language prompts with compact, unambiguous commands. Think of it as **"SQL for LLMs"** or **"shorthand for AI control"**.

### Before vs After

**Natural Language (62 tokens):**
> "Please analyze this Python code, identify performance bottlenecks, suggest optimizations with code examples, explain the reasoning behind each optimization, and provide benchmark comparisons showing expected improvements"

**CompText (18 tokens):**
```
@CODE_ANALYZE[perf_bottleneck] + @CODE_OPT[explain=detail, bench=compare]
```

**Result: 71% token reduction** while being MORE precise. See [TOKEN_REDUCTION_RESULTS.md](TOKEN_REDUCTION_RESULTS.md) for comprehensive benchmarks.

---

## What's Included?

### **18 Production Modules (415+ Commands)**

| Module | Name | Purpose |
|--------|------|---------|
| **A** | Core Commands | Essential DSL commands for text manipulation |
| **B** | Analysis | Text analysis and insight generation |
| **C** | Formatting | Document formatting and structure |
| **D** | AI Control | Model selection, prompt governance, safety filters |
| **E** | ML Pipelines | AutoML, feature engineering, experiment tracking |
| **F** | Documentation | API docs, tutorials, changelogs, design docs |
| **G** | Testing | Test generation, coverage insights, quality gates |
| **H** | Database | Schema design, migrations, query optimization |
| **I** | Security | Vulnerability scans, compliance, threat modeling |
| **J** | DevOps | CI/CD workflows, observability, release automation |
| **K** | Frontend/UI | Component scaffolding, accessibility, responsive design |
| **L** | ETL | Data extraction, transformation, loading |
| **M** | MCP Integration | Multi-agent messaging, tool routing |
| **N** | Agent Orchestration | Multi-agent coordination, workflow management |
| **O** | Observability | Metrics collection, distributed tracing |
| **P** | Performance | Caching strategies, optimization hints |
| **Q** | Quality Assurance | Code quality gates, linting, standards |
| **R** | Release Management | Version control, changelog generation |

### **55+ Ready-to-Use Examples**
- React dashboards with Tailwind CSS
- Kubernetes CI/CD pipelines
- ML workflows with AutoML
- GDPR compliance implementations
- Complete API documentation generation

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

## 🎮 Try it Now - Interactive Playground

**[Launch Playground →](public/playground.html)**

Experience CompText in your browser with our interactive playground:
- ✨ Live DSL editor with syntax highlighting
- 📊 Real-time token savings metrics
- 📚 13 module categories with examples
- 🎯 Command validation and formatting
- 💾 Share & export functionality

Perfect for learning the syntax, testing commands, and seeing token reduction in action!

---

## ⚡ Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ProfRandom92/comptext-codex.git
cd comptext-codex

# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .
```

### Validate codex definitions

```bash
python scripts/validate_codex.py --codex-dir codex --schema-dir schemas
```

### Build the codex bundle locally

```bash
python scripts/build_bundle.py --codex-dir codex --out dist/codex.bundle.json --version v0.0.0
```

### Token reduction test suite

```bash
python scripts/test_token_reduction.py
```

This generates `TOKEN_REDUCTION_RESULTS.md` with reproducible sample cases.
You can also invoke the CLI directly:

```bash
comptext token-benchmark --output TOKEN_REDUCTION_RESULTS.md
```

### CLI token report

After installing the project, inspect token cost hints directly from the codex:

```bash
comptext token-report --codex-dir codex --format json
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

# Example 3: ML Pipeline
command = "@AUTOML[task=classification, metric=f1] + @MODEL_EVAL[cv=5]"
result = parser.execute(command, dataset="data.csv")
```

---

## 📚 Documentation

- **[Quick Start Guide](QUICK_START.md)** - Get up and running in 5 minutes
- **[Examples](EXAMPLES.md)** - 55+ production-ready examples
- **[Module Catalog](codex/MODULE_CATALOG.md)** - 13 modules with security/privacy guardrails
- **[Example Catalog](codex/EXAMPLE_CATALOG.md)** - Category index pointing to all snippets
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

## Project Structure

```
comptext-codex/
├── src/comptext_codex/       # Core DSL implementation
│   ├── parser.py             # Command parser
│   ├── executor.py           # Command executor
│   ├── store.py              # SQLite data layer
│   ├── cli.py                # Command-line interface
│   ├── repl.py               # Interactive REPL
│   └── modules/              # 18 module implementations
├── comptext_mcp/             # MCP Server implementation
├── codex/                    # DSL definitions
│   ├── modules.yaml          # 18 module definitions
│   ├── commands/             # 415+ individual command YAMLs
│   └── profiles.yaml         # Usage profiles
├── examples/                 # 55+ usage examples
├── public/                   # Web interface
│   ├── playground.html       # Interactive DSL editor
│   ├── demo.html             # Token reduction demo
│   └── index.html            # Landing page
├── tests/                    # pytest test suite
├── scripts/                  # Utility scripts
├── codex.db                  # SQLite database
├── TOKEN_REDUCTION_RESULTS.md # Benchmark results
├── README.md
├── QUICK_START.md
├── EXAMPLES.md
├── CONTRIBUTING.md
└── LICENSE
```

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## Performance Benchmarks

Based on 16 test cases ([full results](TOKEN_REDUCTION_RESULTS.md)):

| Metric | Natural Language | CompText | Improvement |
|--------|------------------|----------|-------------|
| Total tokens (16 tasks) | 462 | 172 | **62.8% reduction** |
| Best case (SQL Query Opt) | 36 tokens | 9 tokens | **75% reduction** |
| Average reduction | - | - | **59.8%** |
| Estimated API cost savings | - | - | **$8.70 per 1000 calls** |

---

## Tech Stack

- **Language:** Python 3.10+
- **Database:** SQLite (embedded, zero-config)
- **Protocol:** MCP (Model Context Protocol)
- **Web Interface:** HTML5, JavaScript (vanilla)
- **Testing:** pytest, coverage
- **CI/CD:** GitHub Actions
- **License:** MIT

---

## 🚢 Release Process

- Push a tag (e.g., `v1.2.3`) to trigger the release workflow.
- The workflow validates the codex, builds `dist/codex.bundle.json` with the tag as the version, and generates SHA-256 checksums.
- Release assets include:
  - `codex.bundle.json`
  - `codex.bundle.json.sha256`
  - `codex.bundle.latest-stable.json`
  - `codex.bundle.latest-stable.json.sha256`

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ by [@ProfRandom92](https://github.com/ProfRandom92)**
