# Hermes Agent — Setup Guide for CompText Codex

This guide covers local Hermes setup, MCP configuration and nightly automation for the `comptext-codex` repository.

---

## Prerequisites

```bash
# Node 18+
node --version

# Install Hermes
npm install -g @nousresearch/hermes-agent

# Verify
hermes --version
```

---

## Directory Layout

```
~/ai-lab/
  hermes-home/
    SOUL.md            ← copy from comptext-codex/SOUL.md
    .hermes.md         ← copy from comptext-codex/.hermes.md (or symlink)
  repos/
    comptext-codex/    ← git clone https://github.com/ProfRandom92/comptext-codex
    comptext-dsl/      ← git clone https://github.com/ProfRandom92/comptext-dsl (if exists)
    comptext-mcp-server/ ← git clone https://github.com/ProfRandom92/comptext-mcp-server
  mcp/
    hermes-mcp.json    ← see MCP config section below
```

---

## MCP Configuration

Save as `~/ai-lab/mcp/hermes-mcp.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/home/YOUR_USER/ai-lab/repos"
      ],
      "description": "Read/write access to CompText repos only"
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_PAT_HERE"
      },
      "description": "GitHub: issues, PRs, branches for ProfRandom92 repos"
    },
    "comptext": {
      "command": "python3",
      "args": ["-m", "comptext_mcp.server"],
      "cwd": "/home/YOUR_USER/ai-lab/repos/comptext-mcp-server",
      "env": {
        "COMPTEXT_MODE": "local",
        "COMPTEXT_DB": "/home/YOUR_USER/ai-lab/repos/comptext-mcp-server/data/index.db"
      },
      "description": "CompText MCP Server — module search, DSL queries, health check"
    }
  }
}
```

> ⚠️ Replace `YOUR_USER` and `YOUR_PAT_HERE` before use. Never commit this file with real secrets.

---

## GitHub PAT Scopes

Create a dedicated PAT at https://github.com/settings/tokens with **only**:
- `repo` (read + write for ProfRandom92 repos)
- `workflow` (if you want Hermes to trigger Actions)

Do **not** use your main account PAT.

---

## Starting Hermes

```bash
# From your hermes-home directory
cd ~/ai-lab/hermes-home

# Start with MCP config
hermes --mcp-config ../mcp/hermes-mcp.json

# First prompt: introduce the project
# > Read SOUL.md and .hermes.md, then summarize your operating parameters for this session.
```

---

## Nightly Jobs

Hermes supports scheduled tasks in natural language. Configure these in the Hermes UI or via the `--schedule` flag:

### Job 1 — Nightly Repo Review
```
Schedule: every day at 06:15
Task: "Read SOUL.md and .hermes.md for context. Then:
1. List all open GitHub issues in ProfRandom92/comptext-codex and classify them (docs/test/spec/bug/feat).
2. Check if /examples files are consistent with /spec.
3. Run pytest tests/ -v and capture output.
4. Write a review report to /reports/nightly-YYYY-MM-DD.md with max 12 priority items.
5. If pytest fails: include failure output in the report. Do not open any PR.
6. If pytest passes and you find a trivial fix (single file, <10 lines): create a hermes/* branch and open a draft PR."
```

### Job 2 — MCP Health Check
```
Schedule: every day at 08:00
Task: "Call the comptext MCP server /health endpoint. If it returns non-200, write a one-line alert to /reports/mcp-health.log and create a GitHub issue titled 'hermes: MCP server health check failed YYYY-MM-DD'."
```

### Job 3 — Weekly Spec Drift Check
```
Schedule: every Monday at 07:00
Task: "Compare all files in /spec with their corresponding /examples and /tests. For each spec construct, verify: (a) there is at least one example, (b) there is at least one test. Report gaps as a markdown table in /reports/spec-drift-YYYY-WW.md."
```

---

## Branch Protection (Recommended)

In GitHub → Settings → Branches → `main`:
- ✅ Require pull request before merging
- ✅ Require status checks (pytest CI if configured)
- ✅ Require branches to be up to date
- ✅ Do not allow force pushes

Hermes will only ever create branches matching `hermes/*` and open draft PRs.

---

## Phase Rollout

| Phase | What Hermes can do | Trigger |
|---|---|---|
| **1 — Read-only** | Read files, run pytest locally, write reports | Manual |
| **2 — MCP** | Query comptext MCP server for modules/search | Manual |
| **3 — Write (branch)** | Create `hermes/*` branches, open draft PRs | Manual + Nightly |
| **4 — Full automation** | All nightly jobs active, MCP health alerts | Nightly |

Start with Phase 1. Move to the next phase only after verifying the previous one is stable for ≥3 days.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Hermes creates commits on `main` | Check `.hermes.md` Forbidden Actions section; re-read SOUL.md |
| MCP server 503 on start | Wait 5s, retry. Check `python server.py --dry-run` manually |
| pytest import errors | Ensure `pip install -e .` was run in comptext-codex |
| GitHub PAT permission denied | Verify PAT has `repo` scope and is for ProfRandom92 account |
| Hermes ignores `.hermes.md` | Ensure file is in repo root and Hermes session was started from that directory |
