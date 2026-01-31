# ✅ CompText-Codex - Schnellstart-Checkliste

> **Komplette Checkliste für lokales Setup und MCP-Integration**
> Version: 4.0.0 | Stand: 2026-01-29

---

## 📦 Phase 1: Basis-Installation (5 Minuten)

### 1.1 Systemvoraussetzungen prüfen
```bash
□ Python 3.10+ installiert?
  python3 --version

□ pip installiert?
  pip3 --version

□ Git installiert?
  git --version
```

### 1.2 Repository klonen
```bash
□ Repository klonen
  git clone https://github.com/ProfRandom92/comptext-codex.git
  cd comptext-codex
```

### 1.3 Automatisches Setup ausführen
```bash
□ Setup-Skript ausführen (empfohlen)
  chmod +x setup_lokal.sh
  ./setup_lokal.sh

  ODER manuell:

□ Virtuelle Umgebung erstellen
  python3 -m venv venv
  source venv/bin/activate  # Linux/macOS
  # venv\Scripts\activate   # Windows

□ Dependencies installieren
  pip install -r requirements.txt

□ Package installieren
  pip install -e .

□ Installation testen
  comptext --version
```

---

## 🔍 Phase 2: Validierung (2 Minuten)

### 2.1 Codex validieren
```bash
□ Codex-Definitionen validieren
  python scripts/validate_codex.py --codex-dir codex --schema-dir schemas

□ Bundle erstellen
  python scripts/build_bundle.py --codex-dir codex --out dist/codex.bundle.json --version v4.0.0
```

### 2.2 Funktionstests
```bash
□ Python API testen
  python -c "from comptext_codex import CompTextParser; parser = CompTextParser(); print('✅ OK')"

□ CLI testen
  comptext --help
  comptext token-report --codex-dir codex --format json
```

---

## 🎮 Phase 3: Erste Schritte (5 Minuten)

### 3.1 Playground starten
```bash
□ Web-Playground öffnen
  cd public
  python -m http.server 8000
  # Browser: http://localhost:8000/playground.html
```

### 3.2 Beispiele durchgehen
```bash
□ Beispiele erkunden
  ls examples/
  cd examples/basic
  # Beispiele anschauen und ausführen
```

### 3.3 Erste CompText-Befehle
```python
□ Python API nutzen
  from comptext_codex import CompTextParser

  parser = CompTextParser()

  # Code analysieren
  result = parser.execute(
      "@CODE_ANALYZE[perf_bottleneck]",
      code="def fib(n): return fib(n-1) + fib(n-2)"
  )
  print(result)
```

---

## 🔌 Phase 4: MCP-Integration (10 Minuten)

### 4.1 MCP Server testen
```bash
□ MCP Package prüfen
  python -c "import mcp; print(f'MCP: {mcp.__version__}')"

□ Server im Test-Modus starten
  python -m comptext_mcp.server --test

  Erwartete Ausgabe:
  ✅ CompText MCP Server v4.0.0
  ✅ Server running in test mode
```

### 4.2 Server-Konfiguration
```bash
□ Server-Config erstellen
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
      "pii_safe": true
    }
  }
  EOF
```

---

## 🖥️ Phase 5: Claude Code Integration

### 5.1 Für Claude Code CLI:

```bash
□ MCP-Konfiguration erstellen
  mkdir -p ~/.config/claude-code

  cat > ~/.config/claude-code/mcp_servers.json << EOF
  {
    "mcpServers": {
      "comptext": {
        "command": "python",
        "args": ["-m", "comptext_mcp.server"],
        "cwd": "$(pwd)",
        "env": {
          "COMPTEXT_LOG_LEVEL": "INFO",
          "PYTHONPATH": "$(pwd)/src"
        }
      }
    }
  }
  EOF

□ Claude Code mit MCP starten
  claude-code --mcp
```

### 5.2 Für Claude Desktop App:

#### macOS:
```bash
□ Desktop-Konfiguration erstellen/bearbeiten
  nano ~/Library/Application\ Support/Claude/claude_desktop_config.json

□ Inhalt einfügen:
  {
    "mcpServers": {
      "comptext": {
        "command": "python",
        "args": ["-m", "comptext_mcp.server"],
        "cwd": "/ABSOLUTER/PFAD/ZU/comptext-codex",
        "env": {
          "COMPTEXT_LOG_LEVEL": "INFO",
          "PYTHONPATH": "/ABSOLUTER/PFAD/ZU/comptext-codex/src"
        }
      }
    }
  }

□ Claude Desktop neu starten
```

#### Linux:
```bash
□ Desktop-Konfiguration erstellen/bearbeiten
  mkdir -p ~/.config/Claude
  nano ~/.config/Claude/claude_desktop_config.json

□ Inhalt wie bei macOS (mit angepassten Pfaden)

□ Claude Desktop neu starten
```

#### Windows:
```powershell
□ Desktop-Konfiguration erstellen/bearbeiten
  notepad %APPDATA%\Claude\claude_desktop_config.json

□ Inhalt:
  {
    "mcpServers": {
      "comptext": {
        "command": "python",
        "args": ["-m", "comptext_mcp.server"],
        "cwd": "C:\\Pfad\\zu\\comptext-codex",
        "env": {
          "COMPTEXT_LOG_LEVEL": "INFO",
          "PYTHONPATH": "C:\\Pfad\\zu\\comptext-codex\\src"
        }
      }
    }
  }

□ Claude Desktop neu starten
```

---

## 🧪 Phase 6: Integration testen

### 6.1 In Claude testen:
```
□ Neue Konversation in Claude starten

□ MCP-Server prüfen:
  "Liste alle verfügbaren MCP-Server auf"

  → Sollte "comptext" enthalten

□ CompText-Befehl testen:
  "Analysiere folgenden Code mit CompText:

  @CODE_ANALYZE[perf_bottleneck, complexity]

  def fibonacci(n):
      if n <= 1:
          return n
      return fibonacci(n-1) + fibonacci(n-2)"

  → Sollte Analyse zurückliefern
```

### 6.2 Weitere Tests:
```
□ Dokumentation generieren:
  "Generiere API-Dokumentation mit CompText:
  @DOC_GEN[api, format=markdown, include_examples=true]"

□ Multi-Step-Pipeline:
  "Führe ETL-Pipeline aus:
  @EXTRACT[source=db] + @TRANSFORM[clean=true] + @LOAD[dest=warehouse]"

□ Security-Audit:
  "Führe Security-Scan durch:
  @VULN_SCAN[depth=comprehensive] + @COMPLIANCE[standards=GDPR]"
```

---

## 📊 Phase 7: Erweiterte Features

### 7.1 Tests ausführen
```bash
□ Unit-Tests
  pytest

□ Mit Coverage
  pytest --cov=comptext_codex --cov-report=html
  open htmlcov/index.html

□ Spezifische Tests
  pytest tests/test_mcp_server.py -v
```

### 7.2 Token-Analyse
```bash
□ Token-Report generieren
  comptext token-report --codex-dir codex --format json > token_report.json

□ Token-Benchmark
  comptext token-benchmark --output TOKEN_REDUCTION_RESULTS.md
  cat TOKEN_REDUCTION_RESULTS.md
```

### 7.3 Monitoring
```bash
□ Server-Logs prüfen
  mkdir -p ~/.comptext
  tail -f ~/.comptext/server.log

□ Audit-Logs prüfen
  tail -f ~/.comptext/audit.log
```

---

## 🚀 Finale Checkliste

### Gesamt-Status:
```
□ CompText-Codex lokal installiert
□ Alle Dependencies verfügbar
□ Package im venv installiert
□ CLI funktioniert (comptext --version)
□ Codex validiert
□ Bundle erstellt
□ Playground läuft lokal
□ Beispiele getestet
□ MCP Server funktioniert standalone
□ MCP Server in Claude/Claude Code integriert
□ Test-Befehle in Claude erfolgreich
□ Dokumentation gelesen
□ Tests laufen durch
□ Monitoring funktioniert
```

---

## 📚 Dokumentation (Schnellzugriff)

### Haupt-Dokumente:
- **[SETUP_LOKAL_DE.md](SETUP_LOKAL_DE.md)** - Vollständiges lokales Setup
- **[MCP_INTEGRATION_DE.md](MCP_INTEGRATION_DE.md)** - Detaillierte MCP-Integration
- **[README.md](README.md)** - Projekt-Übersicht
- **Diese Datei** - Schnellstart-Checkliste

### Weitere Ressourcen:
- **Examples:** `examples/` - 55+ Beispiele
- **Module-Katalog:** `codex/MODULE_CATALOG.md`
- **Beispiel-Index:** `codex/EXAMPLE_CATALOG.md`

---

## 🆘 Häufige Probleme

### Problem: "Module not found"
```bash
Lösung:
□ Virtuelle Umgebung aktivieren
  source venv/bin/activate

□ Package installieren
  pip install -e .
```

### Problem: MCP Server startet nicht
```bash
Lösung:
□ MCP Package prüfen
  pip install mcp>=0.9.0

□ Test-Modus nutzen
  python -m comptext_mcp.server --test
```

### Problem: Claude erkennt Server nicht
```bash
Lösung:
□ Absolute Pfade in Config verwenden
□ JSON-Syntax prüfen
□ Claude Desktop/Code neu starten
□ Logs prüfen: tail -f ~/.comptext/server.log
```

---

## 📈 Nächste Schritte

Nach vollständigem Setup:

1. **Beispiele durcharbeiten:**
   ```bash
   cd examples/
   # Starte mit basic/, dann advanced/
   ```

2. **Eigene Workflows erstellen:**
   - Code-Analyse-Pipelines
   - Automatische Dokumentation
   - ML-Pipelines

3. **Performance optimieren:**
   - Caching aktivieren
   - Lazy Loading nutzen
   - Rate Limits anpassen

4. **Community beitreten:**
   - GitHub Issues verfolgen
   - PRs einreichen
   - Feedback geben

---

## 🎯 Erfolgs-Kriterien

Setup ist erfolgreich, wenn:

✅ `comptext --version` funktioniert
✅ `python -m comptext_mcp.server --test` zeigt "Server ready"
✅ Claude zeigt "comptext" in MCP-Server-Liste
✅ Test-Befehl in Claude wird korrekt ausgeführt
✅ Playground läuft unter http://localhost:8000
✅ Tests laufen durch (`pytest`)

---

## 📞 Support

Bei Fragen:
- **GitHub Issues:** https://github.com/ProfRandom92/comptext-codex/issues
- **Dokumentation:** Siehe oben
- **Tests:** `pytest tests/ -v`

---

**Viel Erfolg! 🚀**

*Checkliste v4.0.0 | 2026-01-29*
