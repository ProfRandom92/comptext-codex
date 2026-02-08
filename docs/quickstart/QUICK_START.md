# 🚀 Quick Start Guide

Get up and running with CompText-Codex in 5 minutes!

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/ProfRandom92/comptext-codex.git
cd comptext-codex
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Install CompText

```bash
pip install -e .
```

---

## Your First CompText Command

### Example 1: Simple Code Analysis

```python
from comptext import CompTextParser

# Initialize parser
parser = CompTextParser()

# Analyze code for performance issues
code = """
def slow_function(data):
    result = []
    for i in range(len(data)):
        for j in range(len(data)):
            result.append(data[i] * data[j])
    return result
"""

command = "@CODE_ANALYZE[perf_bottleneck]"
result = parser.execute(command, code=code)
print(result)
```

**Output:**
```
Performance Issues Found:
- Nested loops: O(n²) complexity
- List append in loop: inefficient
Suggested: Use list comprehension or numpy
```

### Example 2: Generate Documentation

```python
command = "@DOC_GEN[api, format=markdown, include_examples=true]"

source_code = """
def calculate_total(items, tax_rate=0.1):
    subtotal = sum(item['price'] for item in items)
    tax = subtotal * tax_rate
    return subtotal + tax
"""

result = parser.execute(command, source_code=source_code)
print(result)
```

### Example 3: Create a Dashboard

```python
command = "@DASHBOARD[layout=grid, theme=professional, responsive=true]"

data = {
    "sales": [100, 150, 200, 180, 220],
    "months": ["Jan", "Feb", "Mar", "Apr", "May"]
}

result = parser.execute(command, data=data)
# Generates React dashboard code with Tailwind CSS
```

---

## Command Syntax Basics

### Basic Structure
```
@COMMAND[parameter1, parameter2=value, ...]
```

### Chaining Commands
```
@COMMAND1[...] + @COMMAND2[...] + @COMMAND3[...]
```

### Conditional Execution
```
@COMMAND1[...] IF condition THEN @COMMAND2[...] ELSE @COMMAND3[...]
```

### Loops
```
FOR item IN dataset: @COMMAND[item]
```

---

## Common Commands Cheat Sheet

### Module A - General
```
@SUMMARIZE[length=short, format=bullets]
@TRANSLATE[target_lang=german, style=formal]
@EXTRACT[pattern=emails, output=list]
```

### Module B - Programming
```
@CODE_ANALYZE[perf_bottleneck, security, style]
@CODE_OPT[explain=detail, bench=compare]
@DEBUG[trace=true, breakpoints=auto]
@REFACTOR[pattern=mvc, tests=preserve]
```

### Module C - Visualization
```
@CHART[type=bar, style=professional, export=png]
@DIAGRAM[type=flowchart, notation=uml]
@DASHBOARD[layout=grid, responsive=true]
```

### Module D - AI Control
```
@MODEL_CONFIG[temperature=0.7, max_tokens=500]
@CHAIN[steps=[analyze, summarize, format]]
@PROMPT_OPT[goal=concise, preserve_meaning=true]
```

---

## MCP Server Setup

### For Claude Desktop

1. Edit config file:
   - **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

2. Add CompText server:

```json
{
  "mcpServers": {
    "comptext": {
      "command": "python",
      "args": ["-m", "comptext_mcp.server"],
      "env": {
        "COMPTEXT_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

3. Restart Claude Desktop

4. Test connection:
```
In Claude: "Use CompText to analyze this code..."
```

### For Ollama WebUI

1. Navigate to Settings > Integrations
2. Add MCP Server:
   - **Name:** CompText-Codex
   - **Command:** `python -m comptext_mcp.server`
3. Enable and restart

---

## Next Steps

1. **Explore Examples:** Check out [EXAMPLES.md](EXAMPLES.md) for 55+ real-world use cases
2. **Read API Docs:** See [docs/API.md](docs/API.md) for complete command reference
3. **Join Community:** Star the repo and join discussions
4. **Contribute:** Read [CONTRIBUTING.md](CONTRIBUTING.md) to help improve CompText

---

## Troubleshooting

### Import Error
```bash
# If you see "ModuleNotFoundError: No module named 'comptext'"
pip install -e .
```

### MCP Server Not Connecting
```bash
# Check if server is accessible
python -m comptext_mcp.server --test

# View logs
export COMPTEXT_LOG_LEVEL=DEBUG
python -m comptext_mcp.server
```

### Command Not Recognized
```python
# List available commands
from comptext import CompTextParser
parser = CompTextParser()
print(parser.list_commands())
```

---

**Ready to dive deeper? Check out [EXAMPLES.md](EXAMPLES.md) for advanced usage!**
