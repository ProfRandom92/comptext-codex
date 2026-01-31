# CompText-Codex - Vollständiges Lokales Setup

> **Komplettpaket zur lokalen Nutzung des CompText DSL Repositories**
> Version: 4.0.0 | Stand: 2026-01-29

---

## 📋 Inhaltsverzeichnis

1. [Was ist CompText-Codex?](#was-ist-comptext-codex)
2. [Systemvoraussetzungen](#systemvoraussetzungen)
3. [Schnellstart (5 Minuten)](#schnellstart-5-minuten)
4. [Detaillierte Installation](#detaillierte-installation)
5. [Erste Schritte](#erste-schritte)
6. [Verwendungsmöglichkeiten](#verwendungsmöglichkeiten)
7. [MCP Server Konfiguration](#mcp-server-konfiguration)
8. [Interaktiver Playground](#interaktiver-playground)
9. [Tests ausführen](#tests-ausführen)
10. [Häufige Probleme & Lösungen](#häufige-probleme--lösungen)
11. [Projekt-Struktur](#projekt-struktur)
12. [Weitere Ressourcen](#weitere-ressourcen)

---

## 🎯 Was ist CompText-Codex?

**CompText-Codex** ist eine **Domain-Specific Language (DSL)** für effiziente LLM-Interaktionen - wie "SQL für LLMs".

### Hauptvorteile:
- **🔥 70% Token-Reduktion** gegenüber natürlicher Sprache
- **🎯 Präzise & eindeutige** Befehle
- **⚡ 13 produktionsreife Module** (Code-Analyse, ML-Pipelines, DevOps, Security, etc.)
- **📦 55+ fertige Beispiele**
- **🤖 MCP Server** für Multi-Agenten-Kommunikation

### Beispiel-Vergleich:

**Natürliche Sprache (127 Tokens):**
> "Bitte analysiere diesen Python-Code, identifiziere Performance-Engpässe, schlage Optimierungen mit Code-Beispielen vor, erkläre die Begründung für jede Optimierung und liefere Benchmark-Vergleiche mit erwarteten Verbesserungen"

**CompText (23 Tokens - 70% Reduktion):**
```
@CODE_ANALYZE[perf_bottleneck] + @CODE_OPT[explain=detail, bench=compare]
```

---

## 💻 Systemvoraussetzungen

### Pflicht:
- **Python:** Version 3.10 oder höher
- **pip:** Python Package Manager
- **Git:** Versionskontrolle

### Optional (für Entwicklung):
- **Node.js:** Für Web-Playground (lokale Entwicklung)
- **Docker:** Für containerisierte Nutzung
- **Claude Desktop:** Für MCP Integration

### Betriebssystem:
- ✅ Linux (getestet)
- ✅ macOS (kompatibel)
- ✅ Windows (kompatibel mit WSL2 empfohlen)

---

## ⚡ Schnellstart (5 Minuten)

```bash
# 1. Repository klonen
git clone https://github.com/ProfRandom92/comptext-codex.git
cd comptext-codex

# 2. Dependencies installieren
pip install -r requirements.txt

# 3. Package installieren (development mode)
pip install -e .

# 4. Installation testen
comptext --version

# 5. Codex validieren
python scripts/validate_codex.py --codex-dir codex --schema-dir schemas

# 6. Beispiel ausführen
python -c "from comptext_codex import CompTextParser; parser = CompTextParser(); print('✅ Installation erfolgreich!')"
```

**✅ Fertig!** Du kannst jetzt CompText nutzen.

---

## 🔧 Detaillierte Installation

### Schritt 1: Repository klonen

```bash
# SSH (empfohlen wenn SSH-Key konfiguriert)
git clone git@github.com:ProfRandom92/comptext-codex.git

# HTTPS (einfacher, aber weniger sicher)
git clone https://github.com/ProfRandom92/comptext-codex.git

# In das Verzeichnis wechseln
cd comptext-codex
```

### Schritt 2: Virtuelle Umgebung erstellen (empfohlen)

```bash
# Virtuelle Umgebung erstellen
python -m venv venv

# Aktivieren
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Überprüfen
which python  # sollte auf venv/bin/python zeigen
```

### Schritt 3: Dependencies installieren

```bash
# Basis-Dependencies
pip install -r requirements.txt

# Oder nur Core-Dependencies (ohne Dev-Tools)
pip install pydantic>=2.0.0 typing-extensions>=4.5.0 pyyaml>=6.0 click>=8.0.0 rich>=13.0.0 mcp>=0.9.0

# Entwickler-Dependencies (optional)
pip install pytest>=7.4.0 pytest-cov>=4.1.0 black>=23.0.0 flake8>=6.0.0 mypy>=1.5.0
```

### Schritt 4: Package installieren

```bash
# Development Mode (empfohlen für lokale Entwicklung)
pip install -e .

# Oder reguläre Installation
pip install .

# Installation überprüfen
comptext --version
comptext --help
```

### Schritt 5: Validierung & Tests

```bash
# 1. Codex-Definitionen validieren
python scripts/validate_codex.py --codex-dir codex --schema-dir schemas

# 2. Codex Bundle erstellen
python scripts/build_bundle.py --codex-dir codex --out dist/codex.bundle.json --version v4.0.0

# 3. Token-Reduktions-Tests
python scripts/test_token_reduction.py
# Erstellt: TOKEN_REDUCTION_RESULTS.md

# Oder via CLI:
comptext token-benchmark --output TOKEN_REDUCTION_RESULTS.md

# 4. Token-Report anzeigen
comptext token-report --codex-dir codex --format json
```

---

## 🚀 Erste Schritte

### 1. Python API nutzen

```python
from comptext_codex import CompTextParser

# Parser initialisieren
parser = CompTextParser()

# Beispiel 1: Code-Analyse
command = "@CODE_ANALYZE[perf_bottleneck] + @CODE_OPT[explain=detail]"
result = parser.execute(command, code="""
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
""")

# Beispiel 2: Dokumentation generieren
command = "@DOC_GEN[api, format=markdown, include_examples=true]"
result = parser.execute(command, source_code="your_api_code.py")

# Beispiel 3: ML Pipeline
command = "@AUTOML[task=classification, metric=f1] + @MODEL_EVAL[cv=5]"
result = parser.execute(command, dataset="data.csv")
```

### 2. CLI nutzen

```bash
# Token-Report
comptext token-report --codex-dir codex --format json

# Token-Benchmark
comptext token-benchmark --output results.md

# Hilfe anzeigen
comptext --help
```

### 3. Beispiele durchgehen

```bash
# Verfügbare Beispiele anzeigen
ls examples/

# Kategorien:
# - basic/          - Grundlagen
# - advanced/       - Fortgeschrittene Nutzung
# - ai/             - KI-Steuerung
# - frontend/       - React/UI-Komponenten
# - ml/             - Machine Learning
# - ml_pipelines/   - AutoML
# - database/       - Datenbank-Operationen
# - devops/         - CI/CD, Infrastructure
# - security/       - Sicherheits-Scans
# - testing/        - Test-Generierung
# - etl/            - Daten-Pipelines
# - documentation/  - API-Docs
# - mcp/            - Multi-Agent-Kommunikation

# Beispiel ausführen
python examples/basic/simple_commands.py
```

---

## 📚 Verwendungsmöglichkeiten

### Die 13 Module im Überblick:

| Modul | Kürzel | Beschreibung | Beispiele |
|-------|--------|--------------|-----------|
| **General/Core** | A | Text-Verarbeitung, Workflows | `@A:compress`, `@A:summarize` |
| **Programming** | B | Code-Analyse, Optimierung | `@CODE_ANALYZE`, `@CODE_OPT` |
| **Visualization** | C | Charts, Diagramme | `@CHART_GEN`, `@DIAGRAM` |
| **AI Control** | D | Modell-Konfiguration | `@MODEL_SELECT`, `@PROMPT_TUNE` |
| **ML Pipelines** | E | AutoML, Feature Engineering | `@AUTOML`, `@FEATURE_ENG` |
| **Documentation** | F | API-Docs, Tutorials | `@DOC_GEN`, `@CHANGELOG` |
| **Testing** | G | Test-Generierung | `@TEST_GEN`, `@COVERAGE` |
| **Database** | H | Schema, Query-Optimierung | `@SCHEMA_DESIGN`, `@QUERY_OPT` |
| **Security** | I | Vulnerability Scans | `@VULN_SCAN`, `@COMPLIANCE` |
| **DevOps** | J | CI/CD, Monitoring | `@CICD_SETUP`, `@CONTAINER` |
| **Frontend/UI** | K | Komponenten-Generierung | `@COMPONENT_GEN`, `@RESPONSIVE` |
| **ETL** | L | Daten-Pipelines | `@EXTRACT`, `@TRANSFORM`, `@LOAD` |
| **MCP Integration** | M | Multi-Agenten-Kommunikation | `@AGENT_COORD`, `@TASK_DELEGATE` |

### Erweiterte Syntax:

```bash
# Einfache Befehle
@A:compress <text>

# Parametrisch
@CODE_ANALYZE[perf_bottleneck, complexity]

# Key-Value-Paare
@AUTOML[task=classification, metric=f1, cv=5]

# Chaining (Verkettung)
@EXTRACT[source=db] + @TRANSFORM[clean=true] + @LOAD[dest=warehouse]

# Conditionals (Bedingungen)
@CMD1[...] IF condition THEN @CMD2[...] ELSE @CMD3[...]

# Loops (Schleifen)
FOR item IN dataset: @COMMAND[item]
```

---

## 🔌 MCP Server Konfiguration

### Für Claude Desktop:

1. **MCP Server testen:**
```bash
python -m comptext_mcp.server --test
```

2. **Claude Desktop Konfiguration:**

Datei: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
oder: `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

```json
{
  "mcpServers": {
    "comptext": {
      "command": "python",
      "args": ["-m", "comptext_mcp.server"],
      "env": {
        "COMPTEXT_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

3. **Claude Desktop neu starten**

4. **Testen in Claude:**
```
Verwende CompText-Codex, um diesen Code zu analysieren: [code]
```

---

## 🎮 Interaktiver Playground

### Web-Playground lokal starten:

```bash
# Einfacher HTTP-Server
cd public
python -m http.server 8000

# Oder mit Node.js
npx serve public -l 8000

# Im Browser öffnen
# http://localhost:8000/playground.html
```

### Features des Playgrounds:
- ✨ Live DSL-Editor mit Syntax-Highlighting
- 📊 Echtzeit Token-Einsparungs-Metriken
- 📚 Alle 13 Module mit Beispielen
- 🎯 Befehls-Validierung und Formatierung
- 💾 Teilen & Export-Funktionalität

---

## 🧪 Tests ausführen

### Unit-Tests:

```bash
# Alle Tests
pytest

# Mit Coverage
pytest --cov=comptext_codex --cov-report=html

# Spezifische Tests
pytest tests/test_parser.py
pytest tests/test_executor.py
pytest tests/test_modules.py

# Verbose Output
pytest -v

# Coverage-Report öffnen
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Code-Qualität:

```bash
# Formatierung prüfen
black --check src/

# Formatierung anwenden
black src/

# Linting
flake8 src/

# Type-Checking
mypy src/

# Import-Sortierung
isort src/
```

---

## 🛠️ Häufige Probleme & Lösungen

### Problem 1: Import-Fehler

```bash
# Fehler: ModuleNotFoundError: No module named 'comptext_codex'

# Lösung:
pip install -e .  # Package im development mode installieren
```

### Problem 2: Python-Version

```bash
# Fehler: Python 3.8 oder älter

# Lösung:
python --version  # Muss >= 3.10 sein
# Ggf. Python upgraden oder pyenv nutzen
```

### Problem 3: Dependencies fehlen

```bash
# Fehler: ModuleNotFoundError für pydantic, click, etc.

# Lösung:
pip install -r requirements.txt
```

### Problem 4: MCP Server startet nicht

```bash
# Fehler: mcp not found

# Lösung:
pip install mcp>=0.9.0

# Test:
python -m comptext_mcp.server --test
```

### Problem 5: Codex-Validierung schlägt fehl

```bash
# Fehler: JSON Schema validation failed

# Lösung:
# Sicherstellen, dass alle YAML-Dateien korrekt formatiert sind
python scripts/validate_codex.py --codex-dir codex --schema-dir schemas
```

---

## 📁 Projekt-Struktur

```
comptext-codex/
│
├── src/comptext_codex/           # Core Implementation
│   ├── __init__.py               # Public API
│   ├── parser.py                 # DSL Parser
│   ├── executor.py               # Befehl-Executor
│   ├── registry.py               # Modul-Registry
│   ├── store.py                  # SQLite-Store (10x schneller)
│   ├── repl.py                   # Interaktive REPL
│   ├── cli.py                    # CLI Interface
│   ├── token_reduction.py        # Token-Optimierung
│   ├── token_report.py           # Token-Analyse
│   └── modules/                  # 13 Module (A-M)
│       ├── base.py
│       ├── module_a.py           # General/Core
│       ├── module_b.py           # Programming
│       ├── module_c.py           # Visualization
│       ├── module_d.py           # AI Control
│       ├── module_e.py           # ML Pipelines
│       ├── module_f.py           # Documentation
│       ├── module_g.py           # Testing
│       ├── module_h.py           # Database
│       ├── module_i.py           # Security
│       ├── module_j.py           # DevOps
│       ├── module_k.py           # Frontend/UI
│       ├── module_l.py           # ETL
│       └── module_m.py           # MCP Integration
│
├── comptext_mcp/                 # MCP Server
│   ├── __init__.py
│   └── server.py
│
├── codex/                        # DSL-Definitionen (YAML)
│   ├── modules.yaml              # Modul-Definitionen
│   ├── commands.yaml             # Befehls-Syntax
│   ├── profiles.yaml             # Profile
│   ├── MODULE_CATALOG.md         # Modul-Katalog
│   └── EXAMPLE_CATALOG.md        # Beispiel-Index
│
├── examples/                     # 55+ Beispiele
│   ├── basic/                    # Grundlagen
│   ├── advanced/                 # Fortgeschritten
│   ├── ai/                       # KI-Steuerung
│   ├── frontend/                 # React/UI
│   ├── ml/                       # Machine Learning
│   ├── ml_pipelines/             # AutoML
│   ├── database/                 # Datenbank
│   ├── devops/                   # CI/CD
│   ├── security/                 # Security
│   ├── testing/                  # Testing
│   ├── etl/                      # ETL
│   ├── documentation/            # Dokumentation
│   └── mcp/                      # Multi-Agent
│
├── tests/                        # Test-Suite
│   ├── conftest.py
│   ├── test_parser.py
│   ├── test_executor.py
│   ├── test_modules.py
│   ├── test_cli.py
│   ├── test_mcp_server.py
│   ├── test_token_reduction.py
│   └── test_token_report.py
│
├── public/                       # Web-Interface
│   ├── playground.html           # Interaktiver Playground
│   ├── index.html
│   └── demo.html
│
├── scripts/                      # Utility-Skripte
│   ├── validate_codex.py         # Codex-Validierung
│   ├── build_bundle.py           # Bundle erstellen
│   └── test_token_reduction.py   # Token-Tests
│
├── docs/                         # Dokumentation
│   ├── README.md
│   ├── api/
│   │   ├── parser.md
│   │   └── executor.md
│   └── guides/
│       └── getting-started.md
│
├── .github/                      # GitHub-Workflows
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── build-codex-bundle.yml
│   │   └── codex-pr-check.yml
│   └── agents/
│
├── README.md                     # Haupt-Readme
├── SETUP_LOKAL_DE.md             # Diese Datei
├── requirements.txt              # Python-Dependencies
├── pyproject.toml                # Projekt-Konfiguration
├── setup.py                      # Setup-Skript
└── LICENSE                       # MIT-Lizenz
```

---

## 📚 Weitere Ressourcen

### Dokumentation:
- **[Quick Start Guide](QUICK_START.md)** - Schnelleinstieg in 5 Minuten
- **[Examples](EXAMPLES.md)** - 55+ produktionsreife Beispiele
- **[Module Catalog](codex/MODULE_CATALOG.md)** - Alle 13 Module mit Details
- **[Example Catalog](codex/EXAMPLE_CATALOG.md)** - Kategorisierter Beispiel-Index
- **[Contributing](CONTRIBUTING.md)** - Beitragen zum Projekt

### Online:
- **Homepage:** https://comptext-txsu.vercel.app
- **Dokumentation:** https://profrandom92.github.io/comptext-docs
- **Repository:** https://github.com/ProfRandom92/comptext-codex
- **Issues:** https://github.com/ProfRandom92/comptext-codex/issues

### Community:
- GitHub Issues für Bug-Reports und Feature-Requests
- Diskussionen in GitHub Discussions
- Pull Requests willkommen!

---

## 🎯 Nächste Schritte

Nach der Installation kannst du:

1. **Beispiele durchgehen:**
   ```bash
   cd examples/basic
   python simple_commands.py
   ```

2. **Playground öffnen:**
   ```bash
   cd public
   python -m http.server 8000
   # Browser: http://localhost:8000/playground.html
   ```

3. **Eigene Befehle testen:**
   ```python
   from comptext_codex import CompTextParser
   parser = CompTextParser()
   # Deine Befehle hier...
   ```

4. **MCP Server einrichten:**
   - Siehe [MCP Server Konfiguration](#mcp-server-konfiguration)

5. **Token-Einsparungen messen:**
   ```bash
   comptext token-benchmark --output my_results.md
   ```

---

## 📊 Performance-Benchmarks

| Metrik | Natürliche Sprache | CompText | Verbesserung |
|--------|-------------------|----------|--------------|
| Tokens pro Aufgabe | 250 (Ø) | 75 (Ø) | **70% Reduktion** |
| Mehrdeutigkeits-Fehler | 15% | 2% | **87% Reduktion** |
| Ausführungszeit | 1.2s | 0.8s | **33% schneller** |

---

## 🔒 Sicherheit & Datenschutz

- **PII-sichere Operationen**
- **Differential Privacy Budgets** (ε-Budgets pro Modul)
- **Federated-ready Metriken**
- **Audit-Trails** mit Request-ID-Tracking
- **Threat-Model:** Prompt-Injection-Härtung, Model-Leakage-Guardrails

---

## 📄 Lizenz

Dieses Projekt ist unter der **MIT-Lizenz** lizenziert - siehe [LICENSE](LICENSE) für Details.

---

## 👤 Autor

**[@ProfRandom92](https://github.com/ProfRandom92)**

---

## ❓ Hilfe & Support

Bei Fragen oder Problemen:

1. **Dokumentation prüfen** (dieses Dokument)
2. **[Häufige Probleme](#häufige-probleme--lösungen)** durchgehen
3. **GitHub Issues** durchsuchen
4. **Neues Issue** erstellen: https://github.com/ProfRandom92/comptext-codex/issues

---

**Viel Erfolg mit CompText-Codex! 🚀**

*Erstellt: 2026-01-29 | Version: 4.0.0*
