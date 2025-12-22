# CompText Codex Definitions

This directory contains YAML definitions for the CompText DSL codex.

## Structure

- `modules.yaml` - Module definitions (A-M codes)
- `commands.yaml` - Command definitions with syntax and examples
- `profiles.yaml` - Profile configurations
- `MODULE_CATALOG.md` - Human-readable summary of modules and guardrails
- `EXAMPLE_CATALOG.md` - Index of the 55+ example categories

## Validation

Validate all codex files:

```bash
python scripts/validate_codex.py --codex-dir codex
```

## Building

Build the codex bundle:

```bash
python scripts/build_bundle.py --codex-dir codex --out dist/codex.bundle.json --version v0.0.0
```
