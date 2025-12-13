# CompText Codex BuildKit

This folder contains:

1) JSON Schemas (Draft 2020-12)
- schemas/module.schema.json
- schemas/command.schema.json
- schemas/profile.schema.json
- schemas/bundle.schema.json

2) CI / Build scripts
- scripts/validate_codex.py
- scripts/build_bundle.py

3) GitHub Actions workflow
- .github/workflows/build-codex-bundle.yml

4) MCP Loader reference (Python)
- mcp_loader/loader.py

Assumptions:
- Your repo has a `codex/` folder with:
  - codex/modules/*.yaml
  - codex/commands/*.yaml
  - codex/profiles/*.yaml

The build produces:
- dist/codex.bundle.json
- dist/codex.bundle.json.sha256


## Recommended distribution (GitHub Release Assets)
- Latest stable: `https://github.com/ProfRandom92/comptext-codex/releases/latest/download/codex.bundle.latest-stable.json`
- Version-pinned example: `https://github.com/ProfRandom92/comptext-codex/releases/download/v3.5.1/codex.bundle.json`

## MCP Server config (recommended)
Set these environment variables:
```bash
CODEX_BUNDLE_URL="https://github.com/ProfRandom92/comptext-codex/releases/latest/download/codex.bundle.latest-stable.json"
CODEX_CACHE_DIR="/var/cache/comptext"
```
