# CompText MCP Server Integration mit Claude Code (Lokal)

> **Vollständige Anleitung zur lokalen Integration des CompText MCP Servers mit Claude Code**
> Version: 4.0.0 | Stand: 2026-01-29

---

## 📋 Inhaltsverzeichnis

1. [Was ist MCP?](#was-ist-mcp)
2. [Voraussetzungen](#voraussetzungen)
3. [MCP Server im CompText Repo](#mcp-server-im-comptext-repo)
4. [Installation & Konfiguration](#installation--konfiguration)
5. [Integration mit Claude Code CLI](#integration-mit-claude-code-cli)
6. [Integration mit Claude Desktop](#integration-mit-claude-desktop)
7. [MCP Server testen](#mcp-server-testen)
8. [Verwendung in Claude](#verwendung-in-claude)
9. [Troubleshooting](#troubleshooting)
10. [Erweiterte Konfiguration](#erweiterte-konfiguration)

---

## 🤔 Was ist MCP?

**Model Context Protocol (MCP)** ist ein offenes Protokoll, das es LLMs ermöglicht, mit externen Tools und Datenquellen zu kommunizieren.

### MCP für CompText:
- **Multi-Agenten-Kommunikation:** Mehrere AI-Agenten können über CompText-Befehle kommunizieren
- **Kontextfreigabe:** Shared Memory und State Management zwischen Agenten
- **Tool-Integration:** CompText-Befehle als Tools für Claude verfügbar machen
- **Workflow-Orchestrierung:** Komplexe Multi-Step-Workflows koordinieren

---

## ✅ Voraussetzungen

### Software:
- ✅ **Python 3.10+** (bereits aus Haupt-Setup)
- ✅ **CompText-Codex** installiert (siehe `SETUP_LOKAL_DE.md`)
- ✅ **pip** Package Manager
- ✅ **Claude Code CLI** oder **Claude Desktop App**

### Python-Packages:
```bash
# Bereits in requirements.txt enthalten:
mcp>=0.9.0
pydantic>=2.0.0
```

---

## 📦 MCP Server im CompText Repo

Der MCP Server ist bereits im CompText-Codex Repository enthalten:

```
comptext-codex/
├── comptext_mcp/              # MCP Server Implementation
│   ├── __init__.py
│   └── server.py              # Haupt-Server-Datei
├── tests/
│   └── test_mcp_server.py     # MCP Server Tests
└── examples/
    └── mcp/                   # MCP Beispiele
        ├── agent_coordination.py
        └── multi_agent_workflow.py
```

### Server-Funktionen:

Der MCP Server (`comptext_mcp/server.py`) bietet:
- **CompText Command Execution:** Führt CompText-Befehle aus
- **State Management:** Verwaltet Kontext zwischen Agenten
- **Tool Registration:** Registriert CompText-Module als MCP-Tools
- **Error Handling:** Robuste Fehlerbehandlung und Logging

---

## 🔧 Installation & Konfiguration

### Schritt 1: MCP Package prüfen

```bash
# Virtuelle Umgebung aktivieren
source venv/bin/activate

# MCP Package prüfen
python -c "import mcp; print(f'MCP Version: {mcp.__version__}')"

# Falls nicht installiert:
pip install mcp>=0.9.0
```

### Schritt 2: MCP Server testen

```bash
# Server im Test-Modus starten
python -m comptext_mcp.server --test

# Erwartete Ausgabe:
# ✅ CompText MCP Server v4.0.0
# ✅ Server running in test mode
# ✅ All modules loaded successfully
```

### Schritt 3: Server-Konfiguration erstellen

```bash
# Server-Konfigurationsdatei erstellen
cat > mcp_server_config.json << 'EOF'
{
  "server": {
    "name": "comptext",
    "version": "4.0.0",
    "log_level": "INFO"
  },
  "modules": {
    "enabled": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M"],
    "auto_load": true
  },
  "security": {
    "enable_audit": true,
    "pii_safe": true,
    "max_tokens_per_request": 10000
  }
}
EOF
```

---

## 🖥️ Integration mit Claude Code CLI

### Schritt 1: Claude Code MCP Konfiguration

Claude Code CLI verwendet MCP-Server über eine Konfigurationsdatei.

**Konfigurationsdatei-Pfad:**
- Linux/macOS: `~/.config/claude-code/mcp_servers.json`
- Windows: `%APPDATA%\claude-code\mcp_servers.json`

### Schritt 2: MCP Server konfigurieren

```bash
# Konfigurations-Verzeichnis erstellen
mkdir -p ~/.config/claude-code

# MCP Server Konfiguration erstellen
cat > ~/.config/claude-code/mcp_servers.json << EOF
{
  "mcpServers": {
    "comptext": {
      "command": "python",
      "args": [
        "-m",
        "comptext_mcp.server"
      ],
      "cwd": "$(pwd)",
      "env": {
        "COMPTEXT_LOG_LEVEL": "INFO",
        "COMPTEXT_CONFIG": "$(pwd)/mcp_server_config.json",
        "PYTHONPATH": "$(pwd)/src"
      }
    }
  }
}
EOF

echo "✅ MCP Server Konfiguration erstellt"
```

### Schritt 3: Claude Code mit MCP Server starten

```bash
# Claude Code mit MCP-Unterstützung starten
claude-code --mcp

# Oder in einem Projekt-Verzeichnis:
cd /dein/projekt
claude-code --mcp
```

### Schritt 4: MCP Server Status prüfen

```bash
# Im Claude Code Terminal:
# Frage Claude:
"Liste alle verfügbaren MCP-Server auf"

# Erwartete Antwort sollte "comptext" enthalten
```

---

## 🖼️ Integration mit Claude Desktop

### Für Claude Desktop App (GUI):

**macOS Konfiguration:**
```bash
# Konfigurations-Datei bearbeiten
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Oder erstellen, falls nicht vorhanden:
cat > ~/Library/Application\ Support/Claude/claude_desktop_config.json << EOF
{
  "mcpServers": {
    "comptext": {
      "command": "python",
      "args": ["-m", "comptext_mcp.server"],
      "cwd": "/absolute/path/to/comptext-codex",
      "env": {
        "COMPTEXT_LOG_LEVEL": "INFO",
        "PYTHONPATH": "/absolute/path/to/comptext-codex/src"
      }
    }
  }
}
EOF
```

**Windows Konfiguration:**
```powershell
# Konfigurations-Datei bearbeiten
notepad %APPDATA%\Claude\claude_desktop_config.json

# Inhalt:
{
  "mcpServers": {
    "comptext": {
      "command": "python",
      "args": ["-m", "comptext_mcp.server"],
      "cwd": "C:\\path\\to\\comptext-codex",
      "env": {
        "COMPTEXT_LOG_LEVEL": "INFO",
        "PYTHONPATH": "C:\\path\\to\\comptext-codex\\src"
      }
    }
  }
}
```

**Linux Konfiguration:**
```bash
# Konfigurations-Datei bearbeiten
nano ~/.config/Claude/claude_desktop_config.json

# Oder erstellen:
mkdir -p ~/.config/Claude
cat > ~/.config/Claude/claude_desktop_config.json << EOF
{
  "mcpServers": {
    "comptext": {
      "command": "python",
      "args": ["-m", "comptext_mcp.server"],
      "cwd": "/absolute/path/to/comptext-codex",
      "env": {
        "COMPTEXT_LOG_LEVEL": "INFO",
        "PYTHONPATH": "/absolute/path/to/comptext-codex/src"
      }
    }
  }
}
EOF
```

### Claude Desktop neu starten

Nach der Konfiguration:
1. Claude Desktop komplett beenden
2. Neu starten
3. MCP Server sollte automatisch geladen werden

---

## 🧪 MCP Server testen

### Test 1: Server-Start im Standalone-Modus

```bash
# Server manuell starten
python -m comptext_mcp.server --test

# Erwartete Ausgabe:
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   CompText MCP Server v4.0.0
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ✅ Parser initialized
# ✅ Registry loaded (13 modules)
# ✅ MCP Server ready
#
# Available Tools:
# - comptext_execute
# - comptext_validate
# - comptext_list_modules
#
# Server running in test mode...
```

### Test 2: Python API testen

```python
# test_mcp_integration.py
from comptext_mcp.server import CompTextMCPServer

# Server initialisieren
server = CompTextMCPServer()

# Command ausführen
result = server.execute_command(
    command="@CODE_ANALYZE[perf_bottleneck]",
    context={"code": "def fibonacci(n):\n    return fibonacci(n-1) + fibonacci(n-2)"}
)

print(result)
```

```bash
python test_mcp_integration.py
```

### Test 3: Mit Claude Desktop testen

1. **Claude Desktop öffnen**
2. **Neue Konversation starten**
3. **CompText-Befehl senden:**

```
Verwende CompText-Codex, um folgenden Code zu analysieren:

@CODE_ANALYZE[perf_bottleneck, complexity]

Code:
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

4. **Erwartete Antwort:**
   - Claude sollte den MCP Server nutzen
   - Analyse sollte durchgeführt werden
   - Ergebnisse sollten zurückgeliefert werden

---

## 💬 Verwendung in Claude

### Grundlegende Befehle:

```
# Liste verfügbare CompText-Module
Liste alle verfügbaren CompText-Module auf

# Code analysieren
Analysiere folgenden Code mit CompText:
@CODE_ANALYZE[perf_bottleneck]
[Code hier]

# Dokumentation generieren
Generiere API-Dokumentation:
@DOC_GEN[api, format=markdown, include_examples=true]
[Source Code hier]

# ML Pipeline
Führe AutoML aus:
@AUTOML[task=classification, metric=f1] + @MODEL_EVAL[cv=5]
[Dataset info hier]
```

### Erweiterte Workflows:

```
# Multi-Step ETL Pipeline
Führe folgende ETL-Pipeline aus:
@EXTRACT[source=database, table=users] +
@TRANSFORM[clean=true, normalize=true] +
@LOAD[dest=warehouse, format=parquet]

# Frontend Component mit Tests
Generiere React-Komponente mit Tests:
@COMPONENT_GEN[type=react, styling=tailwind] +
@TEST_GEN[framework=jest, coverage=80]

# Security Audit
Führe Security-Audit durch:
@VULN_SCAN[depth=comprehensive] +
@COMPLIANCE[standards=GDPR,OWASP]
```

---

## 🐛 Troubleshooting

### Problem 1: MCP Server startet nicht

```bash
# Fehler: "Module 'mcp' not found"

# Lösung:
source venv/bin/activate
pip install mcp>=0.9.0

# Test:
python -c "import mcp; print('OK')"
```

### Problem 2: Server wird in Claude nicht erkannt

```bash
# Prüfe Konfigurationsdatei:
# macOS:
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Linux:
cat ~/.config/Claude/claude_desktop_config.json

# Windows:
type %APPDATA%\Claude\claude_desktop_config.json

# Sicherstellen:
# 1. Absolute Pfade verwenden
# 2. JSON ist valide (keine Syntax-Fehler)
# 3. Python-Command ist korrekt
# 4. Claude Desktop neu gestartet
```

### Problem 3: Server läuft, aber Befehle funktionieren nicht

```bash
# Debug-Modus aktivieren:
export COMPTEXT_LOG_LEVEL=DEBUG
python -m comptext_mcp.server --test

# Log-Datei prüfen:
tail -f ~/.comptext/server.log

# Oder direkt in Python:
python -c "
from comptext_mcp.server import CompTextMCPServer
import logging
logging.basicConfig(level=logging.DEBUG)
server = CompTextMCPServer()
server.test()
"
```

### Problem 4: Permission Denied

```bash
# Fehler: Permission denied beim Server-Start

# Lösung:
chmod +x comptext_mcp/server.py

# Oder Python-Modul verwenden:
python -m comptext_mcp.server
```

### Problem 5: PYTHONPATH-Probleme

```bash
# Fehler: "No module named 'comptext_codex'"

# Lösung 1: PYTHONPATH setzen
export PYTHONPATH="/absolute/path/to/comptext-codex/src:$PYTHONPATH"

# Lösung 2: Package installieren
pip install -e .

# Test:
python -c "from comptext_codex import CompTextParser; print('OK')"
```

---

## ⚙️ Erweiterte Konfiguration

### Umgebungsvariablen:

```bash
# Logging-Level
export COMPTEXT_LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR

# Konfigurationsdatei
export COMPTEXT_CONFIG=/path/to/mcp_server_config.json

# Cache-Verzeichnis
export COMPTEXT_CACHE_DIR=~/.comptext/cache

# Python-Pfad
export PYTHONPATH=/path/to/comptext-codex/src

# MCP Server Port (falls relevant)
export COMPTEXT_MCP_PORT=8765
```

### Server-Konfiguration (`mcp_server_config.json`):

```json
{
  "server": {
    "name": "comptext",
    "version": "4.0.0",
    "log_level": "INFO",
    "max_workers": 4,
    "timeout": 300
  },
  "modules": {
    "enabled": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M"],
    "auto_load": true,
    "lazy_loading": false
  },
  "security": {
    "enable_audit": true,
    "audit_file": "~/.comptext/audit.log",
    "pii_safe": true,
    "max_tokens_per_request": 10000,
    "rate_limit": {
      "requests_per_minute": 60,
      "tokens_per_minute": 50000
    }
  },
  "performance": {
    "cache_enabled": true,
    "cache_ttl": 3600,
    "compression": true
  },
  "features": {
    "multi_agent": true,
    "state_management": true,
    "context_sharing": true
  }
}
```

### Claude Desktop erweiterte Konfiguration:

```json
{
  "mcpServers": {
    "comptext": {
      "command": "python",
      "args": [
        "-m",
        "comptext_mcp.server",
        "--config", "/path/to/mcp_server_config.json",
        "--log-level", "INFO"
      ],
      "cwd": "/absolute/path/to/comptext-codex",
      "env": {
        "COMPTEXT_LOG_LEVEL": "INFO",
        "COMPTEXT_CONFIG": "/path/to/mcp_server_config.json",
        "COMPTEXT_CACHE_DIR": "/path/to/cache",
        "PYTHONPATH": "/absolute/path/to/comptext-codex/src"
      },
      "restart_on_failure": true,
      "max_restarts": 3,
      "health_check_interval": 60
    }
  }
}
```

---

## 📊 Server-Monitoring

### Log-Dateien:

```bash
# Server-Logs
tail -f ~/.comptext/server.log

# Audit-Logs
tail -f ~/.comptext/audit.log

# Error-Logs
grep "ERROR" ~/.comptext/server.log
```

### Performance-Metriken:

```python
# metrics_check.py
from comptext_mcp.server import CompTextMCPServer

server = CompTextMCPServer()
metrics = server.get_metrics()

print(f"Requests handled: {metrics['total_requests']}")
print(f"Average response time: {metrics['avg_response_time']}ms")
print(f"Cache hit rate: {metrics['cache_hit_rate']}%")
print(f"Active modules: {metrics['active_modules']}")
```

---

## 🔄 Multi-Agent-Workflows

### Beispiel: Koordinierte Code-Review:

```python
# multi_agent_review.py
from comptext_mcp.server import CompTextMCPServer

server = CompTextMCPServer()

# Agent 1: Code-Analyse
analysis = server.execute_command(
    "@CODE_ANALYZE[perf_bottleneck, security, complexity]",
    context={"code": code_to_review}
)

# Agent 2: Test-Generierung
tests = server.execute_command(
    "@TEST_GEN[framework=pytest, coverage=90]",
    context={"code": code_to_review, "analysis": analysis}
)

# Agent 3: Dokumentation
docs = server.execute_command(
    "@DOC_GEN[api, format=markdown, include_examples=true]",
    context={"code": code_to_review}
)

# Zusammenführen
final_report = server.execute_command(
    "@A:summarize",
    context={
        "analysis": analysis,
        "tests": tests,
        "docs": docs
    }
)
```

---

## 📚 Weitere Ressourcen

### Dokumentation:
- **CompText Main Repo:** https://github.com/ProfRandom92/comptext-codex
- **MCP Protokoll Spec:** https://modelcontextprotocol.io
- **Claude Desktop Docs:** https://docs.anthropic.com/claude/docs

### Beispiele im Repo:
```bash
ls examples/mcp/
# - agent_coordination.py
# - multi_agent_workflow.py
# - context_sharing.py
# - state_management.py
```

### Tests:
```bash
# MCP Server Tests ausführen
pytest tests/test_mcp_server.py -v

# Integration Tests
pytest tests/test_mcp_integration.py -v
```

---

## ✅ Checkliste: Vollständige Integration

- [ ] CompText-Codex installiert (`pip install -e .`)
- [ ] MCP Package installiert (`pip install mcp>=0.9.0`)
- [ ] MCP Server getestet (`python -m comptext_mcp.server --test`)
- [ ] Konfigurationsdatei erstellt (`mcp_server_config.json`)
- [ ] Claude Code/Desktop konfiguriert
- [ ] Server in Claude sichtbar (Liste MCP-Server)
- [ ] Test-Befehl erfolgreich ausgeführt
- [ ] Logs werden geschrieben
- [ ] Multi-Agenten-Workflow getestet

---

## 🎯 Nächste Schritte

Nach erfolgreicher Integration:

1. **Beispiele durchgehen:**
   ```bash
   cd examples/mcp
   python agent_coordination.py
   ```

2. **Eigene Workflows erstellen:**
   - Multi-Step-Pipelines
   - Koordinierte Code-Reviews
   - Automatisierte Dokumentation

3. **Performance optimieren:**
   - Caching aktivieren
   - Lazy Loading nutzen
   - Rate Limits anpassen

4. **Monitoring einrichten:**
   - Log-Rotation konfigurieren
   - Metriken sammeln
   - Alerts einrichten

---

## 📄 Lizenz

Dieses Projekt ist unter der **MIT-Lizenz** lizenziert.

---

## 👤 Support

Bei Fragen oder Problemen:
- **GitHub Issues:** https://github.com/ProfRandom92/comptext-codex/issues
- **Dokumentation:** `SETUP_LOKAL_DE.md`
- **MCP Tests:** `tests/test_mcp_server.py`

---

**Viel Erfolg mit der CompText MCP Integration! 🚀**

*Erstellt: 2026-01-29 | Version: 4.0.0*
