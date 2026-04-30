# SKILL: hermes-orchestrator
**Version:** 1.0.0  
**Author:** Hermes / ProfRandom92  
**Last verified:** 2026-04-30  
**Tags:** orchestration, comptext, repo-maintenance, mcp, review

---

## Purpose
Operate as the CompText Codex engineering copilot. Analyze repos, triage issues, validate spec consistency, run tests, and produce PR drafts or review reports.

---

## Trigger Conditions
Use this skill when asked to:
- Analyze one or more CompText repos
- Check spec/example/test consistency
- Triage open GitHub issues
- Create a review report
- Draft a PR with a fix or improvement
- Run nightly maintenance on CompText Codex

---

## Procedure

### Step 1 — Load Context
```
1. Read SOUL.md
2. Read .hermes.md (current repo)
3. Read README.md
4. Read spec/comptext-spec.md (or equivalent in /spec)
5. List /agent-skills/ to check available skills
```

### Step 2 — Scope the Task
```
Determine task type:
  A. Repo review (read-only analysis)
  B. Issue triage (classify open issues)
  C. Spec consistency check (spec vs examples vs tests)
  D. Patch/fix (requires branch + tests)
  E. Nightly sweep (A + B + C combined)
```

### Step 3A — Repo Review
```
1. List all directories
2. For each key area (spec, grammar, examples, tests, docs):
   - Count files
   - Check last-modified dates
   - Flag obvious staleness or gaps
3. Summarize: what is solid, what is at risk, what is missing
4. Output: review-report-YYYY-MM-DD.md in /reports/ (create if missing)
```

### Step 3B — Issue Triage
```
1. Fetch all open GitHub issues via MCP (github tool)
2. Classify each issue:
   - docs: documentation gap or error
   - test: missing or failing test
   - spec: spec ambiguity or contradiction
   - dx: developer experience improvement
   - bug: behavioral defect
   - feat: feature request
3. Output: triage table in report
```

### Step 3C — Spec Consistency Check
```
1. For each file in /examples:
   a. Identify which spec section it demonstrates
   b. Run: python -c "from comptext_codex import ...; ..." (or equivalent)
   c. Compare actual output to expected output in example
   d. Flag mismatches
2. Cross-check: every spec construct should have ≥1 example
3. Output: consistency matrix in report
```

### Step 3D — Patch / Fix
```
PRECONDITIONS:
  - Test suite is passing on main
  - Change scope ≤ 3 files
  - You have read the relevant spec section

1. Create branch: hermes/fix-<short-description>
2. Apply minimal change
3. Run: pytest tests/ -v
4. If all pass: open PR draft
5. If any fail: revert + write failure report
6. PR title: "hermes: <description>"
7. PR body: What | Why | Tested how
```

### Step 4 — Finalize
```
1. Write summary (max 12 bullet points)
2. Prioritize: P1 (blocking), P2 (important), P3 (nice-to-have)
3. If nightly sweep: send summary to configured output (Telegram/file/issue comment)
4. Update this SKILL.md with any new pitfalls discovered
```

---

## Pitfalls
- **Grammar files are fragile.** Never edit `/grammar/` without running `python scripts/validate_grammar.py` immediately after.
- **MCP server needs warm-up.** If `/health` returns 503 on first call, wait 3s and retry once.
- **Example outputs may be cached.** If an example has a `.expected` file, always compare against it — not against your own generated output.
- **Spec may have multiple versions.** Check `/spec/` for versioned files; always use the highest version.
- **`pyproject.toml` vs `setup.py` conflict.** This repo has both — use `pyproject.toml` as the authoritative build config.

---

## Verification
After completing any task:
- [ ] No changes on `main` or `dev` directly
- [ ] All PRs are in draft state
- [ ] `pytest tests/` passes on branch
- [ ] Report written with ≤12 priority items
- [ ] SKILL.md updated if new pitfalls found

---

## Related Skills
- `agent-skills/comptext-parse/SKILL.md`
- `agent-skills/comptext-optimize/SKILL.md`
- `agent-skills/comptext-batch/SKILL.md`
