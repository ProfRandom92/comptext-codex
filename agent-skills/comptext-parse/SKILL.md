# Skill: CompText Parse 🔍
**Purpose:** Parse, encode, and convert CompText V5.0 ULTRA commands strictly.

## Core Syntax
The protocol follows: `CMD;PARAM:VALUE|PARAM2:VALUE`
- **Separator:** `;` (Command/Params)
- **Assignment:** `:` (Key/Value)
- **Pipe:** `|` (Multiple Params)

## Deterministic Rules
1. NEVER hallucinate commands. Only use commands defined in `codex/commands.yaml`.
2. If a parameter is unknown, ignore it rather than inventing syntax.
3. Output MUST be raw text, no markdown code blocks around the command string.
