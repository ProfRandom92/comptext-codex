# AGENTS.md — CompText Codex

General guidance for all AI agents (Claude Code, Hermes, Codex CLI, etc.) working on this repository.

## What This Repo Is
`comptext-codex` is the canonical specification and implementation reference for the **CompText DSL** — a semantic compression framework for LLM context optimization. It achieves up to 94–95% token reduction through structured encoding, self-healing specs, and an MCP server interface.

## Key Directories
| Path | Purpose |
|---|---|
| `/spec` | Source of truth — CompText specification documents |
| `/grammar` | Formal grammar definitions (do not edit without validation) |
| `/agent-skills` | Hermes-compatible SKILL.md skills for agent reuse |
| `/examples` | Worked examples (must be spec-consistent) |
| `/comptext_mcp` | MCP server module |
| `/src` | Core Python implementation |
| `/tests` | pytest test suite |
| `/docs` | Human-readable documentation |
| `/integrations` | Third-party integration configs (Hermes, Claude, etc.) |

## Development Contract
1. `/spec` is the source of truth. Code follows spec, not the other way around.
2. All changes must pass `pytest tests/` before committing.
3. Grammar changes require `python scripts/validate_grammar.py` to pass.
4. Examples must be runnable and match current spec behavior.
5. No secrets, tokens or API keys in any committed file.

## Agent-Specific Notes

### Hermes Agent
- Read `.hermes.md` for full Hermes-specific config
- Use `agent-skills/hermes-orchestrator/SKILL.md` as primary operating procedure
- Only operate on `hermes/*` branches

### Claude Code
- Read `SOUL.md` for role and personality
- Use `/spec` + `/examples` as primary context
- Follow the same branch and PR rules as Hermes

### General
- When unsure: write a report, not a commit
- Prefer minimal diffs
- Preserve semantic intent over stylistic improvement
