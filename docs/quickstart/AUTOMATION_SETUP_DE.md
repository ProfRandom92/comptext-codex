# Automated Repository Operations - Setup Guide

> **Vollständige Anleitung für autonome Repository-Operationen**
> Ermöglicht automatisierten Agenten: PR-Erstellung, Commits, Pushes und Branch-Switching

---

## 📋 Inhaltsverzeichnis

1. [Überblick](#überblick)
2. [Voraussetzungen](#voraussetzungen)
3. [Repository-Konfiguration](#repository-konfiguration)
4. [GitHub Actions Workflow](#github-actions-workflow)
5. [Verwendung](#verwendung)
6. [API-Integration](#api-integration)
7. [Berechtigungen](#berechtigungen)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Überblick

Dieses Repository ist so konfiguriert, dass automatisierte Agenten (z.B. GitHub Copilot, CI/CD-Tools) selbstständig folgende Operationen durchführen können:

- ✅ **Pull Requests erstellen** - Automatische PR-Erstellung mit Titel und Beschreibung
- ✅ **Commits durchführen** - Änderungen committen mit aussagekräftigen Messages
- ✅ **Push-Operationen** - Code in Remote-Repository pushen
- ✅ **Branch-Switching** - Zwischen Branches wechseln
- ✅ **Branch-Erstellung** - Neue Branches anlegen und pushen

---

## ✅ Voraussetzungen

### Repository-Anforderungen:
- GitHub Repository mit Actions aktiviert
- Entsprechende Berechtigungen (siehe [Berechtigungen](#berechtigungen))
- `GITHUB_TOKEN` mit ausreichenden Permissions

### Für lokale Entwicklung:
- Git installiert und konfiguriert
- GitHub CLI (gh) optional, aber empfohlen
- Zugriff auf Repository (write access)

---

## 🔧 Repository-Konfiguration

### Schritt 1: GitHub Actions aktivieren

```bash
# Überprüfen, ob Actions aktiviert sind
gh api repos/ProfRandom92/comptext-codex/actions/permissions

# Falls nicht aktiviert, aktivieren:
gh api repos/ProfRandom92/comptext-codex/actions/permissions \
  -X PUT \
  -f enabled=true
```

### Schritt 2: Workflow-Permissions setzen

In den Repository-Settings unter `Settings > Actions > General > Workflow permissions`:

- ✅ **Read and write permissions** aktivieren
- ✅ **Allow GitHub Actions to create and approve pull requests** aktivieren

Alternativ via API:
```bash
gh api repos/ProfRandom92/comptext-codex/actions/permissions/workflow \
  -X PUT \
  -F default_workflow_permissions=write \
  -F can_approve_pull_request_reviews=true
```

### Schritt 3: Branch Protection Rules (Optional aber empfohlen)

Für `main` Branch:
```bash
# Branch Protection aktivieren
gh api repos/ProfRandom92/comptext-codex/branches/main/protection \
  -X PUT \
  -f required_status_checks[strict]=true \
  -f required_status_checks[contexts][]=CI \
  -f enforce_admins=false \
  -f required_pull_request_reviews[required_approving_review_count]=1 \
  -f restrictions=null
```

---

## 🤖 GitHub Actions Workflow

Der automatisierte Workflow (`.github/workflows/automated-pr.yml`) unterstützt folgende Operationen:

### 1. Pull Request erstellen

```bash
gh workflow run automated-pr.yml \
  -f operation=create_pr \
  -f pr_title="Neue Feature-Implementation" \
  -f pr_body="Beschreibung der Änderungen..." \
  -f base_branch=main
```

### 2. Commit und Push

```bash
gh workflow run automated-pr.yml \
  -f operation=commit_and_push \
  -f commit_message="feat: add new feature"
```

### 3. Branch wechseln

```bash
gh workflow run automated-pr.yml \
  -f operation=switch_branch \
  -f branch_name=feat/new-feature
```

### 4. Neuen Branch erstellen

```bash
gh workflow run automated-pr.yml \
  -f operation=create_branch \
  -f branch_name=feat/automated-feature
```

---

## 💻 Verwendung

### Über GitHub Web-Interface:

1. Gehe zu `Actions` Tab im Repository
2. Wähle `Automated PR Operations` Workflow
3. Klicke auf `Run workflow`
4. Wähle Operation und fülle Parameter aus
5. Klicke auf `Run workflow` Button

### Über GitHub CLI:

```bash
# Installation von gh CLI (falls noch nicht installiert)
# macOS:
brew install gh

# Linux:
sudo apt install gh

# Authentifizierung
gh auth login

# Workflow ausführen
gh workflow run automated-pr.yml \
  -f operation=create_pr \
  -f pr_title="Automated PR" \
  -f pr_body="This PR was created automatically"
```

### Über REST API:

```bash
# Mit curl
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/ProfRandom92/comptext-codex/actions/workflows/automated-pr.yml/dispatches \
  -d '{
    "ref": "main",
    "inputs": {
      "operation": "create_pr",
      "pr_title": "Automated PR",
      "pr_body": "Created by automation"
    }
  }'
```

---

## 🔗 API-Integration

### Python-Beispiel:

```python
import requests
import os

def trigger_workflow(operation, **kwargs):
    """Trigger GitHub Actions workflow for automated operations"""
    
    url = "https://api.github.com/repos/ProfRandom92/comptext-codex/actions/workflows/automated-pr.yml/dispatches"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    payload = {
        "ref": "main",
        "inputs": {
            "operation": operation,
            **kwargs
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code == 204

# Verwendung:
if __name__ == "__main__":
    # PR erstellen
    trigger_workflow(
        "create_pr",
        pr_title="Automated Feature",
        pr_body="This PR was created automatically",
        base_branch="main"
    )
    
    # Commit und Push
    trigger_workflow(
        "commit_and_push",
        commit_message="feat: automated commit"
    )
```

### JavaScript/Node.js-Beispiel:

```javascript
const fetch = require('node-fetch');

async function triggerWorkflow(operation, inputs = {}) {
    const url = 'https://api.github.com/repos/ProfRandom92/comptext-codex/actions/workflows/automated-pr.yml/dispatches';
    
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Accept': 'application/vnd.github+json',
            'Authorization': `Bearer ${process.env.GITHUB_TOKEN}`,
            'X-GitHub-Api-Version': '2022-11-28',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            ref: 'main',
            inputs: {
                operation,
                ...inputs
            }
        })
    });
    
    return response.status === 204;
}

// Verwendung:
triggerWorkflow('create_pr', {
    pr_title: 'Automated PR',
    pr_body: 'Created by automation script',
    base_branch: 'main'
});
```

---

## 🔐 Berechtigungen

### Erforderliche GitHub Token-Berechtigungen:

Der `GITHUB_TOKEN` benötigt folgende Permissions:

- ✅ **contents: write** - Für Commits und Push-Operationen
- ✅ **pull-requests: write** - Für PR-Erstellung und -Verwaltung
- ✅ **issues: write** - Für Issue-Referenzen in PRs
- ✅ **workflows: write** - Für Workflow-Trigger (optional)

### Token erstellen (für externe Tools):

1. Gehe zu GitHub Settings > Developer settings > Personal access tokens
2. Erstelle neuen Token mit folgenden Scopes:
   - `repo` (full control)
   - `workflow`
3. Token sicher speichern und als Umgebungsvariable setzen:
   ```bash
   export GITHUB_TOKEN=ghp_your_token_here
   ```

### Repository-Secrets konfigurieren:

Für sensible Daten (z.B. API-Keys):
```bash
gh secret set SECRET_NAME -b"secret_value"
```

---

## 🔍 Workflow-Status überwachen

### Status eines Workflow-Runs prüfen:

```bash
# Alle Workflow-Runs anzeigen
gh run list --workflow=automated-pr.yml

# Details zu einem spezifischen Run
gh run view RUN_ID

# Logs eines Runs anzeigen
gh run view RUN_ID --log
```

### Über Python:

```python
import requests

def get_workflow_status(run_id):
    url = f"https://api.github.com/repos/ProfRandom92/comptext-codex/actions/runs/{run_id}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"
    }
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    return {
        "status": data["status"],
        "conclusion": data.get("conclusion"),
        "html_url": data["html_url"]
    }
```

---

## 🐛 Troubleshooting

### Problem 1: "Resource not accessible by integration"

**Ursache:** Token hat nicht ausreichende Permissions

**Lösung:**
```bash
# Repository Workflow Permissions prüfen
gh api repos/ProfRandom92/comptext-codex/actions/permissions

# Permissions setzen
gh api repos/ProfRandom92/comptext-codex/actions/permissions/workflow \
  -X PUT \
  -F default_workflow_permissions=write
```

### Problem 2: "Workflow file not found"

**Ursache:** Workflow-Datei existiert nicht auf dem Ziel-Branch

**Lösung:**
```bash
# Workflow-Datei auf main Branch pushen
git checkout main
git add .github/workflows/automated-pr.yml
git commit -m "Add automated PR workflow"
git push origin main
```

### Problem 3: "Branch protection rules prevent push"

**Ursache:** Branch Protection Rules verhindern direkte Pushes

**Lösung:**
- Verwende `create_pr` Operation statt `commit_and_push`
- Oder: Passe Branch Protection Rules an, um GitHub Actions zu erlauben

### Problem 4: "Authentication failed"

**Ursache:** GITHUB_TOKEN ist nicht gesetzt oder ungültig

**Lösung:**
```bash
# Token setzen
export GITHUB_TOKEN=your_token_here

# Token testen
gh auth status
```

---

## 📚 Erweiterte Konfiguration

### Custom Workflow für spezielle Anforderungen:

```yaml
# .github/workflows/custom-automation.yml
name: Custom Automation

on:
  workflow_dispatch:
    inputs:
      custom_param:
        description: 'Custom parameter'
        required: true

jobs:
  custom-job:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    
    steps:
      - uses: actions/checkout@v4
      
      # Deine custom Steps hier
      - name: Custom operation
        run: |
          echo "Custom automation logic"
```

### Automatisierung mit Scheduled Workflows:

```yaml
# .github/workflows/scheduled-automation.yml
name: Scheduled Automation

on:
  schedule:
    # Täglich um 00:00 UTC
    - cron: '0 0 * * *'

jobs:
  scheduled-task:
    runs-on: ubuntu-latest
    steps:
      # Automatisierte Tasks
```

---

## 📊 Best Practices

1. **Commit Messages:** Folge [Conventional Commits](https://www.conventionalcommits.org/)
   ```
   feat: add new feature
   fix: resolve bug
   docs: update documentation
   ```

2. **Branch Naming:** Verwende konsistente Prefixes
   ```
   feat/feature-name
   fix/bug-description
   docs/documentation-update
   ```

3. **PR Beschreibungen:** Nutze Templates für konsistente PRs
   ```markdown
   ## Changes
   - List of changes
   
   ## Testing
   - How was it tested
   
   ## Related Issues
   - Closes #123
   ```

4. **Workflow-Monitoring:** Überwache regelmäßig Workflow-Runs
   ```bash
   gh run list --workflow=automated-pr.yml --limit 10
   ```

---

## 🔗 Weitere Ressourcen

### Dokumentation:
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub REST API](https://docs.github.com/en/rest)
- [GitHub CLI Manual](https://cli.github.com/manual/)

### Repository-Docs:
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution Guidelines
- [BRANCH_STRATEGY.md](BRANCH_STRATEGY.md) - Branch Management
- [MCP_INTEGRATION_DE.md](MCP_INTEGRATION_DE.md) - MCP Integration

---

## ✅ Checkliste: Setup-Abschluss

- [ ] GitHub Actions aktiviert
- [ ] Workflow-Permissions auf "write" gesetzt
- [ ] Branch Protection Rules konfiguriert (optional)
- [ ] `automated-pr.yml` Workflow committed und gepusht
- [ ] GITHUB_TOKEN mit korrekten Permissions erstellt
- [ ] Workflow getestet (mindestens eine erfolgreiche Ausführung)
- [ ] Team über neue Automatisierung informiert
- [ ] Dokumentation in README verlinkt

---

## 🎯 Nächste Schritte

Nach erfolgreicher Konfiguration:

1. **Test-Run durchführen:**
   ```bash
   gh workflow run automated-pr.yml \
     -f operation=create_branch \
     -f branch_name=test/automation
   ```

2. **Integration in CI/CD:**
   - Workflow in bestehende Pipelines integrieren
   - Trigger-Bedingungen anpassen

3. **Monitoring einrichten:**
   - Workflow-Run-Benachrichtigungen aktivieren
   - Fehler-Alerts konfigurieren

4. **Team-Training:**
   - Team über neue Workflows informieren
   - Best Practices dokumentieren

---

**Viel Erfolg mit der Repository-Automation! 🚀**

*Erstellt: 2026-01-31 | Version: 1.0.0*
