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

## Install CompText Codex (required before starting MCP)

The `comptext-mcp` CLI script is only available after installing the package:

```bash
cd ~/ai-lab/repos/comptext-codex

# Install with MCP extras
pip install -e ".[mcp]"

# Verify the MCP entrypoint is available
comptext-mcp --help

# Verify the MCP server can be imported (stdio server — no HTTP, no --dry-run)
python -c "from comptext_codex.mcp_server_v5 import create_server; print('MCP import OK')"
```

> ⚠️ `comptext-mcp` starts a **stdio MCP server**. It does not expose HTTP endpoints and has no `--dry-run` flag.
> The import test above is the correct way to verify the server is functional.

---

## Verify Installation Path (important for MCP config)

Run this after `pip install -e ".[mcp]"` to understand how the package is installed:

```bash
python -c "import comptext_codex; print(comptext_codex.__file__)"
```

**Interpret the output:**

| Output path contains | Meaning | Action |
|---|---|---|
| `.../site-packages/comptext_codex/__init__.py` | Clean install in site-packages | Remove `PYTHONPATH` from `hermes-mcp.json` |
| `.../comptext-codex/src/comptext_codex/__init__.py` | Editable install via `.pth` file | `PYTHONPATH` is redundant but harmless — can remove |
| `ModuleNotFoundError` | Package not installed in active environment | Re-run `pip install -e ".[mcp]"` in the **correct** venv |

> **If the import fails**, the problem is the Python environment — not `PYTHONPATH`.
> The MCP server process must run in the **same environment** where `pip install` was executed.
> If Hermes spawns the server in a subprocess, verify it inherits your venv or uses the full Python path.

`PYTHONPATH` in the MCP config is kept as a fallback for edge cases (e.g., the MCP host spawns processes without inheriting the shell environment). Once verified that the import works without it, you can remove it.

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
  mcp/
    hermes-mcp.json    ← see MCP config section below
```

---

## MCP Configuration

Save as `~/ai-lab/mcp/hermes-mcp.json`.
The example template is at `integrations/hermes/mcp-config.example.json`.

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
      "command": "comptext-mcp",
      "args": [],
      "env": {
        "PYTHONPATH": "/home/YOUR_USER/ai-lab/repos/comptext-codex/src"
      },
      "description": "CompText V5 MCP Server (stdio) — parse, encode, benchmark, token reduction"
    }
  }
}
```

> ⚠️ Replace `YOUR_USER` and `YOUR_PAT_HERE` before use.
> `comptext-mcp` must be on your PATH (run `pip install -e ".[mcp]"` in comptext-codex first).
> **Never commit this file with real credentials.**
>
> Run the installation path verification above before deciding whether to keep or remove `PYTHONPATH`.

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

### Job 2 — MCP Server Verification
```
Schedule: every day at 08:00
Task: "Run: python -c 'from comptext_codex.mcp_server_v5 import create_server; print(\"MCP OK\")'
If the import fails, append a one-line error to /reports/mcp-health.log
and create a GitHub issue titled 'hermes: MCP server import failed YYYY-MM-DD'."
```

> Note: `comptext-mcp` is a stdio server — there is no HTTP /health endpoint to poll.
> The import test above is the correct health check mechanism.

### Job 3 — Weekly Spec Drift Check
```
Schedule: every Monday at 07:00
Task: "Compare all files in /spec with their corresponding /examples and /tests.
For each spec construct, verify: (a) there is at least one example, (b) there is at least one test.
Report gaps as a markdown table in /reports/spec-drift-YYYY-WW.md."
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
| **2 — MCP** | Use comptext-mcp (stdio) for parse/encode/benchmark | Manual |
| **3 — Write (branch)** | Create `hermes/*` branches, open draft PRs | Manual + Nightly |
| **4 — Full automation** | All nightly jobs active, MCP health alerts | Nightly |

Start with Phase 1. Move to the next phase only after verifying the previous one is stable for ≥3 days.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `comptext-mcp: command not found` | Run `pip install -e ".[mcp]"` in comptext-codex root |
| `ImportError: MCP package not installed` | Run `pip install mcp` or `pip install -e ".[mcp]"` |
| `from comptext_codex import ...` fails | Run `pip install -e .` first; package uses src-layout |
| Import works in shell but fails via Hermes MCP | Hermes spawns a subprocess — set full Python path as `command` or keep `PYTHONPATH` in env |
| Hermes creates commits on `main` | Re-read SOUL.md; check `.hermes.md` Forbidden Actions |
| pytest import errors | Ensure `pip install -e .` was run in comptext-codex |
| GitHub PAT permission denied | Verify PAT has `repo` scope and is for ProfRandom92 account |
| Hermes ignores `.hermes.md` | Ensure file is in repo root and Hermes session started from that directory |
