# CompText Codex 6 — Core-10 planner with AGY Rust structural gate

**Research scope:** offline synthetic fixture, draft-only, no automatic execution, no implicit authorization. This work extends the existing unmerged Draft PR #58. No changes to `main`, Wave Memory, Cloudflare Witness, historic SQLite data or the AGY source repository.

## Verified components

- Source: immutable 415-command catalog (`f51e00d712c9466e32071872bb2e220194d06d2af080915806e482ad5df41ebc`), derived from historical `aa59150:codex.db`. Original import remains read-only.
- Draft core: ten explicitly selected historical definitions with exact source identity, syntax, description, typed argument constraints and preserved legacy IDs. Schema `comptext.codex.core10.v1`. **All entries** have `review_state=draft_requires_human_review`, `effect=plan_only`, `can_execute=false`. No command is authorized simply because it appears here.
- Compiler: `experiments/vnext/core_compiler.py`. Exact command-ID binding; no implicit fallback from ambiguous aliases; strict step/parameter fields; ordered steps and deterministic canonical plan SHA-256; fail-closed missing, duplicate, unknown and potentially privileged commands.
- CLI: `python -m experiments.vnext.core_cli`. Publishes a new private, non-overwriting plan file. It performs no plan action.
- AGY bridge: invokes the actual existing independent Rust binary `agy7rust schema-check` on a fixed **redacted metadata-only** summary. The AGY schema is a small SPARK-V7-SCHEMA-compatible **research fixture**, not official SPARK validation. Only fixed scalar field existence is checked by AGY. Python checks command semantics and internal integrity; **neither** independently verifies a human signature or revocation.
- No AGY agent was asked to generate code: the inspected `agy-ct run` coordinates its own offline SPARK doctor/context/demo/handoff stages and explicitly does **not** run subagents, launch code-writing LLMs or control separate Git worktrees.

## Ten draft commands

| ID | Original mnemonic | Proposed typed arguments | Semantics in this version |
|---:|---|---|---|
| 1 | A:@sum | text:string | Summarization proposal |
| 2 | A:@exp | text:string | Expansion proposal |
| 5 | B:analyze | text:string | Analysis proposal |
| 6 | C:format | text:string, format?:string | Formatting proposal |
| 14 | C:json | text:string, indent?:integer | JSON formatting proposal |
| 15 | C:list | text:string, ordered?:boolean | List formatting proposal |
| 16 | C:markdown | text:string, style?:string | Markdown proposal |
| 18 | C:table | text:string, format?:string | Table proposal |
| 129 | F:DOC | target:string | Documentation plan only |
| 360 | G:TEST | target:string | Test generation plan only |

`text` and `target` are carried as literal data, not executable scripts or automatic file targets. Parameter meanings and real agent-side effects require later editorial tests and independent approval.

## P0 gate

Twenty-one records in the pre-existing quarantine dossier are P0 review priorities, including `A:EXEC`, `A:ROLLBACK`, `A:RISKY` and colliding `J:DEPLOY`. They cannot enter Core-10 or compile into a plan through this interface. The complete P0/P1/P2 dossier remains at `experiments/vnext/review/legacy-aa59150-quarantine-81.md`. This phase does not pretend that 81 source definitions were all semantically corrected; they remain quarantined.

## Reproduce offline with AGY installed

```bash
python -m experiments.vnext.core_cli \
  --request experiments/vnext/examples/core10-synthetic-request.json \
  --catalog experiments/vnext/catalog_snapshots/legacy-aa59150-catalog-f51e00d712c9.json \
  --core experiments/vnext/core10.manifest.json \
  --agy-bin /path/to/agy7rust \
  --agy-schema experiments/vnext/agy-plan-meta.schema.json \
  --output /tmp/codex-core10-plan.json
```

If AGY binary/schema is explicitly requested but absent or fails its check, **no output is published**. Plan creation without AGY is supported for development but labelled `AGY_GATE=NOT_RUN`. Never interpret the output as execution permission.

## Actual isolated test evidence

- TDD RED/GREEN: 9 core compiler tests (including forged plan ID and explicit blocking of all 21 P0 records), 4 AGY/CLI tests.
- Real AGY Rust binary invoked both on valid and invalid redacted metadata: accepts complete fields, fails on missing `plan_sha256`, no original text exposed.
- Full suite on isolated Sprite with `COMPTEXT_AGY7RUST_PATH`: **405 Python tests passed, 0 failed**, with one non-blocking `pytest-asyncio` configuration warning.
- Reproducible synthetic test plan: `plan-a7b120f7800ba57b0ea9e586`, compiled 3 stages `A:sum`, `C:json`, `G:test`, approval `not_requested`, `execution_allowed=false`, AGY_GATE=PASS.
- Human approval, independent signer identity, semantic LLM correctness, production workflow automation and remote rollback protection were **not** demonstrated by Core-10.

## Next technical gate

1. Review the 21 P0 definitions and add explicit negative/positive examples. Do not silently promote any of them.
2. Review and release the ten drafted parameter schemas only after independent checks. Then map to read-only agent tooling, never direct shell execution.
3. Compare optional AGY validator provenance with a pinned binary release/signing identity if an actual production trust claim is intended.
4. Introduce actual executor only behind Wave Memory's signed, revocation-aware policy and independently governed witness; keep Codex vocabulary non-authoritative.
