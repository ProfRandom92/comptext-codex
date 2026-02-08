# 📦 CompText v5.0.1 - PyPI Upload Guide

## ✅ Vorbereitung (Bereits erledigt!)

Die folgenden Schritte sind bereits abgeschlossen:

1. ✅ Version auf 5.0.1 aktualisiert (setup.py & pyproject.toml)
2. ✅ Packages gebaut:
   - `dist/comptext_codex-5.0.1.tar.gz` (Source Distribution)
   - `dist/comptext_codex-5.0.1-py3-none-any.whl` (Wheel)
3. ✅ Git Tag v5.0.1 erstellt und gepusht

---

## 🚀 Upload zu PyPI

### Option 1: Mit gespeichertem API Token (Empfohlen)

**Schritt 1: Erstelle `.pypirc` Datei**

Erstelle die Datei: `C:\Users\contr\.pypirc`

```ini
[pypi]
username = __token__
password = pypi-DEIN_API_TOKEN_HIER
```

**Wichtig:** Ersetze `pypi-DEIN_API_TOKEN_HIER` mit deinem echten PyPI API Token!

**API Token erstellen:**
1. Gehe zu: https://pypi.org/manage/account/token/
2. Klicke auf "Add API token"
3. Name: "comptext-codex-upload"
4. Scope: "Entire account" oder "Project: comptext-codex"
5. Kopiere den Token (beginnt mit `pypi-...`)

**Schritt 2: Upload durchführen**

```bash
cd C:\comptext-codex
twine upload dist/comptext_codex-5.0.1*
```

Das war's! Twine nutzt automatisch die Credentials aus `.pypirc`.

---

### Option 2: Manuell mit Token (Einmalig)

```bash
cd C:\comptext-codex
twine upload dist/comptext_codex-5.0.1* --username __token__ --password pypi-DEIN_TOKEN
```

---

### Option 3: Mit Username/Password (Alt, nicht empfohlen)

```bash
cd C:\comptext-codex
twine upload dist/comptext_codex-5.0.1*
```

Twine wird nach Username und Password fragen.

---

## ✅ Verification (Nach Upload)

### 1. PyPI Page prüfen
https://pypi.org/project/comptext-codex/

Version 5.0.1 sollte jetzt dort sichtbar sein!

### 2. Installation testen

```bash
# In neuem Virtual Environment
pip install comptext-codex --upgrade

# Version prüfen
pip show comptext-codex
```

Sollte zeigen: `Version: 5.0.1`

### 3. Tools testen

```bash
comptext parse "C;P:FIB"
```

---

## 🐛 Troubleshooting

### Problem: "Invalid credentials"

**Lösung:** Prüfe API Token
- Token beginnt mit `pypi-`
- Username muss `__token__` sein (mit doppeltem Underscore!)
- Keine Leerzeichen im Token

### Problem: "File already exists"

**Lösung:** Version wurde bereits hochgeladen
- PyPI erlaubt kein Überschreiben
- Bump auf v5.0.2 wenn nötig
- Oder nutze TestPyPI für Tests

### Problem: Twine nicht gefunden

**Lösung:** Twine installieren
```bash
pip install twine
```

---

## 📊 Nach dem Upload

### Update Badge in README

Der PyPI Badge sollte automatisch auf v5.0.1 aktualisieren:
```markdown
[![PyPI](https://img.shields.io/pypi/v/comptext-codex?color=blue&style=for-the-badge)](https://pypi.org/project/comptext-codex/)
```

### GitHub Release erstellen

1. Gehe zu: https://github.com/ProfRandom92/comptext-codex/releases
2. Klicke "Create a new release"
3. Tag: v5.0.1 (bereits vorhanden)
4. Title: "v5.0.1 - Agent Teams Ready"
5. Description: (Kopiere aus CHANGELOG_5.0.1.md)
6. Attach: `dist/comptext_codex-5.0.1.tar.gz` & `.whl` Dateien

---

## 🎉 Fertig!

Nach dem Upload ist CompText v5.0.1 weltweit installierbar:

```bash
pip install comptext-codex
```

**Users können dann:**
- Den MCP Server nutzen
- Den Sub-Agent spawnen
- 94% Token Reduction genießen
- Mit Agent Teams arbeiten

---

**Let's ship it! 🚀**
