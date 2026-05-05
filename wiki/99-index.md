# Wiki Full-Text Index (FTS5)

**Last Updated:** 2026-05-05  
**Total Articles:** 12  
**Indexed Sections:** 40+  

## Search This Wiki

For semantic search across all articles, run:

```bash
pnpm wiki:search "your query"
```

## Keyword Index

### Protocol & Design
- **System Overview** → architecture, parser, codex, MCP
- **V5.0 Protocol** → single-char commands, batch, syntax, tasks
- **Compression Engine** → parsing, benchmarks, optimization

### Usage & Integration
- **Python API** → CompTextParserV5, executor, examples
- **CLI Reference** → commands, interactive mode
- **OpenClaw Integration** → skills, automation
- **Agent Teams** → workflows, multi-agent

### Performance
- **Benchmarks** → token savings, speed tests
- **Cost Analysis** → ROI, monthly savings
- **Optimization** → best practices, tuning

### Development
- **Testing** → test suite, coverage
- **Contributing** → dev setup, PR process
- **Troubleshooting** → common issues, debug
- **Codex Structure** → modules, YAML format
- **Command Vocabulary** → all commands, codes

---

## Quick Links

| Topic | Article | Section |
|-------|---------|----------|
| Get started | [System Overview](./00-system-overview.md) | Architecture |
| Learn protocol | [V5.0 Protocol](./01-protocol-v5.md) | Syntax, Examples |
| Use Python API | [Python API](./10-python-api.md) | Parser, Executor |
| CLI commands | [CLI Reference](./11-cli-reference.md) | Commands, Options |
| Deploy as agent | [Agent Teams](./13-agent-teams.md) | Setup, Workflows |
| View stats | [Benchmarks](./20-benchmarks.md) | Token, Speed, Real-World |
| Calculate ROI | [Cost Analysis](./21-cost-analysis.md) | Savings Calculator |
| Debug issues | [Troubleshooting](./40-troubleshooting.md) | Common Issues |

---

## Search Examples

### Find articles by keyword:
```bash
comptext wiki:search "protocol"
# Returns: V5.0 Protocol, System Overview

comptext wiki:search "benchmarks"
# Returns: Benchmarks, Cost Analysis, Compression Engine

comptext wiki:search "agent"
# Returns: Agent Teams, MCP Integration
```

### Filter by category:
```bash
comptext wiki:search "token" --category performance
comptext wiki:search "python" --category integration
comptext wiki:search "command" --category protocol
```

---

## Full Article Index

1. **00-system-overview.md** — Architecture, components, metrics
2. **01-protocol-v5.md** — Command syntax, language codes, batch operations
3. **02-compression-engine.md** — Parser internals, optimization
4. **03-mcp-server.md** — Tool definitions, server setup
5. **10-python-api.md** — CompTextParserV5, executor API
6. **11-cli-reference.md** — CLI commands, flags, examples
7. **12-openclaw-integration.md** — Skill setup, deployment
8. **13-agent-teams.md** — Multi-agent workflows
9. **20-benchmarks.md** — Token savings, speed tests
10. **21-cost-analysis.md** — ROI, monthly/annual savings
11. **30-testing.md** — Test suite, CI/CD
12. **40-troubleshooting.md** — Common issues, debug guide

---

## Metadata

```json
{
  "wiki": {
    "name": "CompText Codex Wiki",
    "created": "2026-05-05",
    "articles": 12,
    "sections": 40,
    "indexed_keywords": 120,
    "fts5_enabled": true,
    "search_latency_ms": 20,
    "token_savings": "94%",
    "last_reindex": "2026-05-05T00:00:00Z"
  }
}
```

## Contributing

To add new articles:

1. Create file in `wiki/` with pattern `NN-title.md`
2. Use consistent heading hierarchy (# → ## → ###)
3. Add article reference to **README.md** navigation
4. Update this index with keyword mappings
5. Push changes (auto-triggers FTS5 reindex)

See [Contributing Guide](../CONTRIBUTING.md) for details.
