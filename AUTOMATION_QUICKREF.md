# Quick Reference: Repository Automation

> Fast reference for automated PR, commit, push, and branch operations

## 🚀 Quick Commands

### Create Pull Request
```bash
# Via helper script
./automation_helper.sh create-pr \
  --title "Feature: Add new functionality" \
  --body "Description of changes" \
  --base main

# Via gh CLI directly
gh workflow run automated-pr.yml \
  -f operation=create_pr \
  -f pr_title="Feature: New functionality" \
  -f pr_body="Description" \
  -f base_branch=main
```

### Commit and Push
```bash
# Via helper script
./automation_helper.sh commit-push \
  --message "feat: add new feature"

# Via gh CLI directly
gh workflow run automated-pr.yml \
  -f operation=commit_and_push \
  -f commit_message="feat: add new feature"
```

### Switch Branch
```bash
# Via helper script
./automation_helper.sh switch-branch \
  --branch feat/new-feature

# Via gh CLI directly
gh workflow run automated-pr.yml \
  -f operation=switch_branch \
  -f branch_name=feat/new-feature
```

### Create Branch
```bash
# Via helper script
./automation_helper.sh create-branch \
  --branch feat/automated-feature

# Via gh CLI directly
gh workflow run automated-pr.yml \
  -f operation=create_branch \
  -f branch_name=feat/automated-feature
```

## 🔍 Monitor Workflow

```bash
# List recent workflow runs
gh run list --workflow=automated-pr.yml --limit 5

# View specific run details
gh run view <run-id>

# View run logs
gh run view <run-id> --log

# Watch run in real-time
gh run watch <run-id>
```

## 🔐 Setup (One-time)

1. **Install GitHub CLI**
   ```bash
   # macOS
   brew install gh
   
   # Linux
   sudo apt install gh
   ```

2. **Authenticate**
   ```bash
   gh auth login
   ```

3. **Configure Repository** (if needed)
   ```bash
   # Enable workflow permissions
   gh api repos/ProfRandom92/comptext-codex/actions/permissions/workflow \
     -X PUT \
     -F default_workflow_permissions=write
   ```

## 📚 Full Documentation

- **English**: [AUTOMATION_SETUP.md](AUTOMATION_SETUP.md)
- **Deutsch**: [AUTOMATION_SETUP_DE.md](AUTOMATION_SETUP_DE.md)

## 🐍 Python API Example

```python
import requests
import os

def trigger_pr_creation(title, body, base="main"):
    url = "https://api.github.com/repos/ProfRandom92/comptext-codex/actions/workflows/automated-pr.yml/dispatches"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    payload = {
        "ref": "main",
        "inputs": {
            "operation": "create_pr",
            "pr_title": title,
            "pr_body": body,
            "base_branch": base
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code == 204

# Usage
trigger_pr_creation("New Feature", "Added automated operations")
```

## 💻 JavaScript/Node.js Example

```javascript
const fetch = require('node-fetch');

async function triggerPRCreation(title, body, base = 'main') {
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
                operation: 'create_pr',
                pr_title: title,
                pr_body: body,
                base_branch: base
            }
        })
    });
    
    return response.status === 204;
}

// Usage
triggerPRCreation('New Feature', 'Added automated operations');
```

## ⚠️ Common Issues

| Issue | Solution |
|-------|----------|
| "Resource not accessible" | Check workflow permissions in repo settings |
| "Workflow file not found" | Ensure workflow is committed to default branch |
| "Authentication failed" | Run `gh auth login` or set GITHUB_TOKEN |
| "Branch protection rules" | Use `create_pr` instead of `commit_and_push` |

## 📞 Support

- **Issues**: https://github.com/ProfRandom92/comptext-codex/issues
- **Discussions**: https://github.com/ProfRandom92/comptext-codex/discussions
- **Email**: See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

---

**Last Updated**: 2026-01-31
