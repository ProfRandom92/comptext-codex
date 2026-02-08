# 🚀 CompText V5.0.1 - Agent Teams Quick Start

## ✅ Was ist neu?

CompText V5.0.1 ist jetzt **Agent Teams Ready** und bringt einen spezialisierten Sub-Agent mit, der große Dateien analysieren kann, ohne das Haupt-Context-Window zu verschmutzen.

---

## 📦 Installation

### 1. MCP Server zu Claude Desktop hinzufügen

Öffne deine Claude Desktop Config:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`

Füge hinzu:
```json
{
  "mcpServers": {
    "comptext": {
      "command": "python",
      "args": ["C:\\comptext-codex\\server.py"],
      "description": "CompText Speed Server"
    }
  }
}
```

### 2. Server starten (Optional - Auto-Start)

Der Server startet automatisch, wenn Claude Desktop die Config lädt.

**Manueller Start (zum Testen):**
```bash
cd C:\comptext-codex
python server.py
```

---

## 🤖 Sub-Agent nutzen

Der **CompText Specialist Agent** ist bereits definiert in:
```
.claude/agents/comptext-specialist.md
```

### Verwendung:

**In Claude Desktop:**
```
Use the comptext specialist agent to find 'secretKillSwitch' 
in C:\comptext-codex\LegacyMonolith.java
```

**Was passiert:**
1. Claude spawnt einen Sub-Agent (Haiku für Speed)
2. Sub-Agent nutzt `comptext_analyze` Tool
3. Gibt NUR Treffer zurück: `[LegacyMonolith.java:4501] public void secretKillSwitch() {`
4. Kein 20.000-Zeilen-Dump ins Main-Window!

---

## 🔧 Verfügbare Tools

### 1. `comptext_analyze(file_path, query)`

**Funktion:**
- Durchsucht eine Datei nach einem Query-String
- Gibt NUR matching Zeilen mit Zeilennummern zurück
- Verhindert Context-Window-Pollution

**Beispiel:**
```python
comptext_analyze("C:/project/auth.py", "def authenticate")
```

**Output:**
```
✅ Found 3 match(es) in auth.py:

[auth.py:23] def authenticate_user(username, password):
[auth.py:78] # JWT authentication middleware  
[auth.py:142] class AuthenticationError(Exception):
```

### 2. `comptext_parse(command)`

**Funktion:**
- Parst CompText-Protocol-Commands
- Gibt lesbare Struktur zurück

**Beispiel:**
```python
comptext_parse("C;P:FIB")
```

**Output:**
```
✅ Parsed CompText Command: C;P:FIB
   Command: CODE
   Parameters:
     Language: PYTHON
     Task: FIB
```

---

## 📊 Performance-Vergleich

| Methode | Token Overhead | Context Pollution |
|---------|----------------|-------------------|
| **Ganzer File Read** | ~20,000 tokens | ✅ Vollständig verschmutzt |
| **CompText Analyze** | ~50 tokens | ❌ Nur Treffer |

**Einsparung:** 99.75% Token-Reduction für große File-Searches!

---

## 🎯 Use Cases

### 1. Code-Suche in großen Codebases
```
Use comptext to find all 'TODO' comments in C:\project\src
```

### 2. Bug-Hunting in Legacy Code
```
Search for 'deprecated' methods in the LegacyMonolith.java file
```

### 3. Configuration-Check
```
Find all database connection strings in config files
```

---

## 🔍 Sub-Agent Behavior

Der CompText Specialist Agent ist optimiert für:

✅ **Surgical Precision** - Nur relevante Zeilen  
✅ **Token Efficiency** - 94% weniger Overhead  
✅ **Concise Reporting** - Format: `[file:line] content`  
✅ **Zero Context Waste** - Kein File-Dumping  

**Model:** `claude-3-5-haiku-latest` (für maximale Speed)  
**Tools:** `comptext_analyze`, `bash`, `grep`

---

## 📝 Nächste Schritte

1. ✅ Claude Desktop neu starten (Config laden)
2. ✅ Test: "Use comptext to find 'main' in server.py"
3. ✅ Stress-Test mit deinem größten File!

---

## 💡 Pro-Tipp

Kombiniere den Sub-Agent mit dem Main-Agent:

**Main Agent:** "Explain the authentication flow"  
**Sub-Agent:** "Find all auth-related functions using comptext"  
**Main Agent:** "Combine findings and generate documentation"

→ **Result:** Zero context waste, maximale Effizienz!

---

## 🐛 Troubleshooting

**Server startet nicht?**
```bash
pip install fastmcp
python server.py
```

**Sub-Agent wird nicht gefunden?**
- Prüfe: `.claude/agents/comptext-specialist.md` existiert
- Claude Desktop neu starten

**Tool nicht verfügbar?**
- Prüfe: `claude_desktop_config.json` korrekt
- Server läuft? Check mit: `curl http://localhost:8000` (falls Port konfiguriert)

---

**🚀 Happy Analyzing with Agent Teams!**
