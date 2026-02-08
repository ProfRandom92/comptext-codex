# Automated Repository Operations - Setup Guide

> **Complete guide for autonomous repository operations**
> Enables automated agents to: create PRs, commit, push, and switch branches

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Repository Configuration](#repository-configuration)
4. [GitHub Actions Workflow](#github-actions-workflow)
5. [Usage](#usage)
6. [API Integration](#api-integration)
7. [Permissions](#permissions)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This repository is configured to allow automated agents (e.g., GitHub Copilot, CI/CD tools) to independently perform:

- ✅ **Create Pull Requests** - Automated PR creation with title and description
- ✅ **Commit Changes** - Commit changes with meaningful messages
- ✅ **Push Operations** - Push code to remote repository
- ✅ **Branch Switching** - Switch between branches
- ✅ **Branch Creation** - Create new branches and push them

---

## ✅ Prerequisites

### Repository Requirements:
- GitHub Repository with Actions enabled
- Appropriate permissions (see [Permissions](#permissions))
- `GITHUB_TOKEN` with sufficient permissions

### For Local Development:
- Git installed and configured
- GitHub CLI (gh) optional but recommended
- Write access to repository

---

## 🔧 Repository Configuration

### Step 1: Enable GitHub Actions

```bash
# Check if Actions are enabled
gh api repos/ProfRandom92/comptext-codex/actions/permissions

# Enable if not already activated:
gh api repos/ProfRandom92/comptext-codex/actions/permissions \
  -X PUT \
  -f enabled=true
```

### Step 2: Set Workflow Permissions

In Repository Settings under `Settings > Actions > General > Workflow permissions`:

- ✅ Enable **Read and write permissions**
- ✅ Enable **Allow GitHub Actions to create and approve pull requests**

Alternatively via API:
```bash
gh api repos/ProfRandom92/comptext-codex/actions/permissions/workflow \
  -X PUT \
  -F default_workflow_permissions=write \
  -F can_approve_pull_request_reviews=true
```

### Step 3: Branch Protection Rules (Optional but recommended)

For `main` branch:
```bash
# Enable Branch Protection
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

The automated workflow (`.github/workflows/automated-pr.yml`) supports the following operations:

### 1. Create Pull Request

```bash
gh workflow run automated-pr.yml \
  -f operation=create_pr \
  -f pr_title="New Feature Implementation" \
  -f pr_body="Description of changes..." \
  -f base_branch=main
```

### 2. Commit and Push

```bash
gh workflow run automated-pr.yml \
  -f operation=commit_and_push \
  -f commit_message="feat: add new feature"
```

### 3. Switch Branch

```bash
gh workflow run automated-pr.yml \
  -f operation=switch_branch \
  -f branch_name=feat/new-feature
```

### 4. Create New Branch

```bash
gh workflow run automated-pr.yml \
  -f operation=create_branch \
  -f branch_name=feat/automated-feature
```

---

## 💻 Usage

### Via GitHub Web Interface:

1. Go to `Actions` tab in the repository
2. Select `Automated PR Operations` workflow
3. Click on `Run workflow`
4. Choose operation and fill in parameters
5. Click `Run workflow` button

### Via GitHub CLI:

```bash
# Install gh CLI (if not already installed)
# macOS:
brew install gh

# Linux:
sudo apt install gh

# Authenticate
gh auth login

# Run workflow
gh workflow run automated-pr.yml \
  -f operation=create_pr \
  -f pr_title="Automated PR" \
  -f pr_body="This PR was created automatically"
```

### Via REST API:

```bash
# With curl
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

## 🔗 API Integration

### Python Example:

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

# Usage:
if __name__ == "__main__":
    # Create PR
    trigger_workflow(
        "create_pr",
        pr_title="Automated Feature",
        pr_body="This PR was created automatically",
        base_branch="main"
    )
    
    # Commit and Push
    trigger_workflow(
        "commit_and_push",
        commit_message="feat: automated commit"
    )
```

### JavaScript/Node.js Example:

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

// Usage:
triggerWorkflow('create_pr', {
    pr_title: 'Automated PR',
    pr_body: 'Created by automation script',
    base_branch: 'main'
});
```

---

## 🔐 Permissions

### Required GitHub Token Permissions:

The `GITHUB_TOKEN` needs the following permissions:

- ✅ **contents: write** - For commits and push operations
- ✅ **pull-requests: write** - For PR creation and management
- ✅ **issues: write** - For issue references in PRs
- ✅ **workflows: write** - For workflow triggers (optional)

### Create Token (for external tools):

1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Create new token with the following scopes:
   - `repo` (full control)
   - `workflow`
3. Store token securely and set as environment variable:
   ```bash
   export GITHUB_TOKEN=ghp_your_token_here
   ```

### Configure Repository Secrets:

For sensitive data (e.g., API keys):
```bash
gh secret set SECRET_NAME -b"secret_value"
```

---

## 🔍 Monitor Workflow Status

### Check Workflow Run Status:

```bash
# List all workflow runs
gh run list --workflow=automated-pr.yml

# Details for a specific run
gh run view RUN_ID

# View logs for a run
gh run view RUN_ID --log
```

### Via Python:

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

### Issue 1: "Resource not accessible by integration"

**Cause:** Token doesn't have sufficient permissions

**Solution:**
```bash
# Check repository workflow permissions
gh api repos/ProfRandom92/comptext-codex/actions/permissions

# Set permissions
gh api repos/ProfRandom92/comptext-codex/actions/permissions/workflow \
  -X PUT \
  -F default_workflow_permissions=write
```

### Issue 2: "Workflow file not found"

**Cause:** Workflow file doesn't exist on the target branch

**Solution:**
```bash
# Push workflow file to main branch
git checkout main
git add .github/workflows/automated-pr.yml
git commit -m "Add automated PR workflow"
git push origin main
```

### Issue 3: "Branch protection rules prevent push"

**Cause:** Branch protection rules prevent direct pushes

**Solution:**
- Use `create_pr` operation instead of `commit_and_push`
- Or: Adjust branch protection rules to allow GitHub Actions

### Issue 4: "Authentication failed"

**Cause:** GITHUB_TOKEN is not set or invalid

**Solution:**
```bash
# Set token
export GITHUB_TOKEN=your_token_here

# Test token
gh auth status
```

---

## 📚 Advanced Configuration

### Custom Workflow for Specific Requirements:

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
      
      # Your custom steps here
      - name: Custom operation
        run: |
          echo "Custom automation logic"
```

### Automation with Scheduled Workflows:

```yaml
# .github/workflows/scheduled-automation.yml
name: Scheduled Automation

on:
  schedule:
    # Daily at 00:00 UTC
    - cron: '0 0 * * *'

jobs:
  scheduled-task:
    runs-on: ubuntu-latest
    steps:
      # Automated tasks
```

---

## 📊 Best Practices

1. **Commit Messages:** Follow [Conventional Commits](https://www.conventionalcommits.org/)
   ```
   feat: add new feature
   fix: resolve bug
   docs: update documentation
   ```

2. **Branch Naming:** Use consistent prefixes
   ```
   feat/feature-name
   fix/bug-description
   docs/documentation-update
   ```

3. **PR Descriptions:** Use templates for consistent PRs
   ```markdown
   ## Changes
   - List of changes
   
   ## Testing
   - How was it tested
   
   ## Related Issues
   - Closes #123
   ```

4. **Workflow Monitoring:** Regularly monitor workflow runs
   ```bash
   gh run list --workflow=automated-pr.yml --limit 10
   ```

---

## 🔗 Additional Resources

### Documentation:
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub REST API](https://docs.github.com/en/rest)
- [GitHub CLI Manual](https://cli.github.com/manual/)

### Repository Docs:
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution Guidelines
- [BRANCH_STRATEGY.md](BRANCH_STRATEGY.md) - Branch Management
- [MCP_INTEGRATION_DE.md](MCP_INTEGRATION_DE.md) - MCP Integration

---

## ✅ Setup Completion Checklist

- [ ] GitHub Actions enabled
- [ ] Workflow permissions set to "write"
- [ ] Branch protection rules configured (optional)
- [ ] `automated-pr.yml` workflow committed and pushed
- [ ] GITHUB_TOKEN created with correct permissions
- [ ] Workflow tested (at least one successful run)
- [ ] Team informed about new automation
- [ ] Documentation linked in README

---

## 🎯 Next Steps

After successful configuration:

1. **Perform Test Run:**
   ```bash
   gh workflow run automated-pr.yml \
     -f operation=create_branch \
     -f branch_name=test/automation
   ```

2. **Integrate into CI/CD:**
   - Integrate workflow into existing pipelines
   - Adjust trigger conditions

3. **Setup Monitoring:**
   - Enable workflow run notifications
   - Configure error alerts

4. **Team Training:**
   - Inform team about new workflows
   - Document best practices

---

**Good luck with repository automation! 🚀**

*Created: 2026-01-31 | Version: 1.0.0*
