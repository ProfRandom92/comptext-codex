# CompText Codex YAML Definitions

This directory contains YAML definitions for CompText modules, commands, and profiles.

## Structure

- `modules/` - Module definitions
- `commands/` - Command definitions  
- `profiles/` - Profile definitions

## Example Module

```yaml
module:
  code: "A"
  name: "Analysis"
  purpose: "Text analysis and processing"
  stability: "Stable"
  mcp_exposed: true
  token_priority: "High"
```

## Example Command

```yaml
commands:
  - name: "Summarize"
    command: "@sum"
    syntax: "@sum <text>"
    description: "Summarize the provided text"
    module: "A"
    example: "@sum This is a long text..."
    stability: "Stable"
    mcp_exposed: true
```
