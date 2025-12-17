# CompText Module Catalog (A–M)

This catalog lists the 13 production modules with their roles plus the security/privacy guardrails captured in `modules.yaml`.

| Code | Name | Purpose | Security & Privacy | MCP | Token Priority |
| --- | --- | --- | --- | --- | --- |
| A | Core Commands | Essential CompText DSL commands for text manipulation | PII-safe; DP ε≤1.0 per call; federated-ready; audited via request_id+role | ✅ | high |
| B | Analysis | Text analysis and insight generation | PII-safe; DP ε≤0.5 per call; federated-ready; audited via request_id+trace | ✅ | medium |
| C | Formatting | Document formatting and structure | PII-safe; DP ε≤0.1 per call; federated-ready: no; audit=request_id | ✅ | medium |
| D | AI Control | Model selection, prompt governance, and safety filters | PII-safe; DP ε≤0.5 per call; federated-ready; policy-bound audit | ✅ | high |
| E | ML Pipelines | AutoML, feature engineering, and experiment tracking | PII-sensitive; DP ε≤2.0 per job; federated-ready; audit by dataset_id | ✅ | high |
| F | Documentation | API docs, tutorials, changelogs, design docs | PII-safe; DP ε≤0.2 per call; federated-ready: no; audit=request_id | ✅ | medium |
| G | Testing | Test generation, coverage insights, quality gates | PII-safe; DP ε≤0.3 per suite; federated-ready; audit run_id | ✅ | medium |
| H | Database | Schema design, migrations, query optimization | PII-sensitive; DP ε≤1.0 per call; federated-ready: no; audit db_scope | ✅ | medium |
| I | Security | Vulnerability scans, compliance checks, threat modeling | PII-safe; DP ε≤0.2 per scan; federated-ready; audit severity-bound | ✅ | high |
| J | DevOps | CI/CD workflows, observability, release automation | PII-safe; DP ε≤0.1 per call; federated-ready; audit pipeline_id | ✅ | medium |
| K | Frontend/UI | Component scaffolding, accessibility, responsive design | PII-safe; DP ε≤0.05 per call; federated-ready: no; audit=request_id | ✅ | medium |
| L | ETL | Data extraction, transformation, and loading with validations | PII-sensitive; DP ε≤1.0 per job; federated-ready; audit lineage | ✅ | high |
| M | MCP Integration | Multi-agent messaging, tool routing, contract governance | PII-safe; DP ε≤0.2 per exchange; federated-ready; audit session_id | ✅ | high |

**Notes**
- `DP ε` values are per-request/job budgets; aggregate budgets must be composed upstream.
- `federated-ready` indicates the module exposes metrics compatible with federated aggregation pipelines.
- Guardrails align with the security/privacy metadata stored in `codex/modules.yaml`.
