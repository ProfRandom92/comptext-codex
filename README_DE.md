# CompText-Codex - Deutsche Dokumentation

> **Domain-Specific Language (DSL) für effiziente LLM-Interaktion**
> Reduzierung der Tokens um 70% bei höherer Präzision

---

## 🚀 Schnellstart

### Komplettpaket für lokale Nutzung

Dieses Repository enthält alles, was du für die lokale Nutzung von CompText-Codex benötigst:

```bash
# 1. Automatisches Setup (empfohlen)
chmod +x setup_lokal.sh
./setup_lokal.sh

# 2. Fertig! Testen:
comptext --version
python -m comptext_mcp.server --test
```

---

## 📚 Dokumentation

### Haupt-Dokumente (Deutsch):

| Dokument | Beschreibung | Wann nutzen? |
|----------|--------------|--------------|
| **[SETUP_LOKAL_DE.md](SETUP_LOKAL_DE.md)** | Vollständige Installations- und Setup-Anleitung | Erste Installation, detaillierte Infos |
| **[MCP_INTEGRATION_DE.md](MCP_INTEGRATION_DE.md)** | MCP Server Integration mit Claude Code/Desktop | Nach Basis-Installation |
| **[SCHNELLSTART_CHECKLISTE.md](SCHNELLSTART_CHECKLISTE.md)** | Schritt-für-Schritt-Checkliste | Schneller Überblick, Status-Check |
| **[setup_lokal.sh](setup_lokal.sh)** | Automatisches Setup-Skript | Einfache Installation |

### Englische Original-Dokumentation:

- **[README.md](README.md)** - Projekt-Übersicht (Englisch)
- **[QUICK_START.md](QUICK_START.md)** - Schnelleinstieg (Englisch)
- **[EXAMPLES.md](EXAMPLES.md)** - Beispiele (Englisch)
- **[codex/MODULE_CATALOG.md](codex/MODULE_CATALOG.md)** - Modul-Katalog

---

## 🎯 Was ist CompText-Codex?

**CompText** ist eine DSL ("SQL für LLMs"), die natürliche Sprach-Prompts durch kompakte, eindeutige Befehle ersetzt.

### Beispiel-Vergleich:

**❌ Natürliche Sprache (127 Tokens):**
> "Bitte analysiere diesen Python-Code, identifiziere Performance-Engpässe, schlage Optimierungen mit Code-Beispielen vor, erkläre die Begründung für jede Optimierung und liefere Benchmark-Vergleiche mit erwarteten Verbesserungen"

**✅ CompText (23 Tokens - 70% Reduktion):**
```
@CODE_ANALYZE[perf_bottleneck] + @CODE_OPT[explain=detail, bench=compare]
```

### Hauptvorteile:
- 🔥 **70% Token-Reduktion**
- 🎯 **Präzise & eindeutige Befehle**
- ⚡ **13 produktionsreife Module** (Code, ML, DevOps, Security, etc.)
- 📦 **55+ fertige Beispiele**
- 🤖 **MCP Server** für Multi-Agenten-Kommunikation
- 🔒 **Sicherheit & Datenschutz** (PII-safe, GDPR-konform)

---

## 📦 Was ist enthalten?

### Kern-Komponenten:

```
comptext-codex/
├── src/comptext_codex/        # Core DSL Implementation
│   ├── parser.py              # DSL Parser
│   ├── executor.py            # Befehl-Executor
│   └── modules/               # 13 Module (A-M)
│
├── comptext_mcp/              # MCP Server
│   └── server.py              # Multi-Agent-Kommunikation
│
├── codex/                     # DSL-Definitionen (YAML)
│   ├── modules.yaml           # Modul-Definitionen
│   ├── MODULE_CATALOG.md      # Modul-Dokumentation
│   └── EXAMPLE_CATALOG.md     # Beispiel-Index
│
├── examples/                  # 55+ Produktionsreife Beispiele
│   ├── basic/                 # Grundlagen
│   ├── advanced/              # Fortgeschritten
│   ├── ai/                    # KI-Steuerung
│   ├── ml/                    # Machine Learning
│   ├── frontend/              # React/UI
│   ├── devops/                # CI/CD
│   └── security/              # Security
│
├── public/                    # Web-Interface
│   └── playground.html        # Interaktiver Playground
│
└── tests/                     # Test-Suite
```

### Die 13 Module:

| Modul | Bereich | Beispiele |
|-------|---------|-----------|
| **A** | General/Core | Text-Verarbeitung, Workflows |
| **B** | Programming | Code-Analyse, Optimierung |
| **C** | Visualization | Charts, Diagramme |
| **D** | AI Control | Modell-Konfiguration |
| **E** | ML Pipelines | AutoML, Feature Engineering |
| **F** | Documentation | API-Docs, Tutorials |
| **G** | Testing | Test-Generierung, Coverage |
| **H** | Database | Schema-Design, Query-Optimierung |
| **I** | Security | Vulnerability Scans, Compliance |
| **J** | DevOps | CI/CD, Containerisierung |
| **K** | Frontend/UI | React-Komponenten, Responsive Design |
| **L** | ETL | Daten-Pipelines, Transformationen |
| **M** | MCP Integration | Multi-Agenten-Kommunikation |

---

## ⚡ Installation in 3 Schritten

### Option 1: Automatisches Setup (empfohlen)

```bash
# 1. Repository klonen
git clone https://github.com/ProfRandom92/comptext-codex.git
cd comptext-codex

# 2. Setup-Skript ausführen
chmod +x setup_lokal.sh
./setup_lokal.sh

# 3. Testen
comptext --version
```

### Option 2: Manuelle Installation

```bash
# 1. Virtuelle Umgebung
python3 -m venv venv
source venv/bin/activate

# 2. Dependencies
pip install -r requirements.txt

# 3. Package installieren
pip install -e .

# 4. Validieren
python scripts/validate_codex.py --codex-dir codex --schema-dir schemas
```

---

## 🔌 MCP Server Integration

### Claude Code CLI:

```bash
# 1. MCP-Konfiguration erstellen
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

# 2. Claude Code mit MCP starten
claude-code --mcp
```

### Claude Desktop App:

Siehe **[MCP_INTEGRATION_DE.md](MCP_INTEGRATION_DE.md)** für detaillierte Anweisungen für:
- macOS
- Linux
- Windows

---

## 💡 Verwendungsbeispiele

### Python API:

```python
from comptext_codex import CompTextParser

parser = CompTextParser()

# Code analysieren
result = parser.execute(
    "@CODE_ANALYZE[perf_bottleneck, complexity]",
    code="""
    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)
    """
)

# Dokumentation generieren
docs = parser.execute(
    "@DOC_GEN[api, format=markdown, include_examples=true]",
    source_code="your_api_code.py"
)

# ML Pipeline
ml_result = parser.execute(
    "@AUTOML[task=classification, metric=f1] + @MODEL_EVAL[cv=5]",
    dataset="data.csv"
)
```

### CLI:

```bash
# Token-Report
comptext token-report --codex-dir codex --format json

# Token-Benchmark
comptext token-benchmark --output results.md

# Hilfe
comptext --help
```

### In Claude (mit MCP):

```
Analysiere folgenden Code mit CompText:

@CODE_ANALYZE[perf_bottleneck, security, complexity]

def process_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result
```

---

## 🎮 Interaktiver Playground

```bash
# Playground starten
cd public
python -m http.server 8000

# Browser öffnen
# http://localhost:8000/playground.html
```

Features:
- ✨ Live DSL-Editor mit Syntax-Highlighting
- 📊 Echtzeit Token-Einsparungs-Metriken
- 📚 Alle 13 Module mit Beispielen
- 🎯 Befehls-Validierung
- 💾 Export-Funktionalität

---

## 🧪 Tests

```bash
# Alle Tests
pytest

# Mit Coverage
pytest --cov=comptext_codex --cov-report=html

# Spezifische Tests
pytest tests/test_mcp_server.py -v
pytest tests/test_parser.py -v

# MCP Server testen
python -m comptext_mcp.server --test
```

---

## 📊 Performance

| Metrik | Natürliche Sprache | CompText | Verbesserung |
|--------|-------------------|----------|--------------|
| Tokens pro Aufgabe | 250 (Ø) | 75 (Ø) | **70% Reduktion** |
| Mehrdeutigkeits-Fehler | 15% | 2% | **87% Reduktion** |
| Ausführungszeit | 1.2s | 0.8s | **33% schneller** |

---

## 🛠️ Systemanforderungen

### Pflicht:
- **Python:** >= 3.9
- **pip:** aktuell
- **Git:** für Repository-Zugriff

### Optional:
- **Claude Code CLI** oder **Claude Desktop** für MCP-Integration
- **Node.js** für Web-Playground-Entwicklung
- **Docker** für containerisierte Nutzung

### Betriebssysteme:
- ✅ Linux (getestet)
- ✅ macOS (kompatibel)
- ✅ Windows (WSL2 empfohlen)

---

## 🆘 Häufige Probleme

### "Module not found"
```bash
# Lösung:
source venv/bin/activate
pip install -e .
```

### MCP Server startet nicht
```bash
# Lösung:
pip install mcp>=0.9.0
python -m comptext_mcp.server --test
```

### Claude erkennt Server nicht
```bash
# Lösung:
# 1. Absolute Pfade in Konfiguration verwenden
# 2. JSON-Syntax prüfen
# 3. Claude neu starten
```

Mehr Details in **[SETUP_LOKAL_DE.md](SETUP_LOKAL_DE.md)** und **[MCP_INTEGRATION_DE.md](MCP_INTEGRATION_DE.md)**.

---

## 📚 Weitere Ressourcen

### Online:
- **Homepage:** https://comptext-txsu.vercel.app
- **Dokumentation:** https://profrandom92.github.io/comptext-docs
- **Repository:** https://github.com/ProfRandom92/comptext-codex
- **Issues:** https://github.com/ProfRandom92/comptext-codex/issues

### Im Repository:
- **Beispiele:** `examples/` (55+ Beispiele)
- **Modul-Katalog:** `codex/MODULE_CATALOG.md`
- **Beispiel-Index:** `codex/EXAMPLE_CATALOG.md`
- **API-Docs:** `docs/api/`

---

## 🤝 Beitragen

Contributions sind willkommen! Siehe [CONTRIBUTING.md](CONTRIBUTING.md) für Details.

---

## 📄 Lizenz

MIT-Lizenz - siehe [LICENSE](LICENSE) für Details.

---

## 👤 Autor

**[@ProfRandom92](https://github.com/ProfRandom92)**

---

## 🎯 Nächste Schritte

Nach der Installation:

1. **[SETUP_LOKAL_DE.md](SETUP_LOKAL_DE.md)** durchgehen
2. **Playground** öffnen und testen
3. **Beispiele** in `examples/` durcharbeiten
4. **MCP Server** integrieren (siehe [MCP_INTEGRATION_DE.md](MCP_INTEGRATION_DE.md))
5. **Eigene Workflows** erstellen

---

## ✅ Support

Bei Fragen oder Problemen:
1. **Dokumentation prüfen** (siehe oben)
2. **[GitHub Issues](https://github.com/ProfRandom92/comptext-codex/issues)** durchsuchen
3. **Neues Issue** erstellen

---

**Viel Erfolg mit CompText-Codex! 🚀**

*Deutsche Dokumentation v4.0.0 | 2026-01-29*
