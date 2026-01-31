# Repository Automation Configuration

This document describes the configuration settings required for automated repository operations.

## GitHub Repository Settings

### 1. Actions Permissions

**Location**: Settings > Actions > General

#### Workflow Permissions
- ✅ **Read and write permissions** - REQUIRED
  - Allows workflows to push code and create branches
  
- ✅ **Allow GitHub Actions to create and approve pull requests** - REQUIRED
  - Enables automated PR creation

#### Actions Permissions
- ✅ **Allow all actions and reusable workflows** - RECOMMENDED
  - Or: Allow actions from specific organizations/repositories

### 2. Branch Protection Rules (Optional but Recommended)

**Location**: Settings > Branches > Add rule

#### For `main` branch:
- ✅ **Require pull request reviews before merging**
  - Minimum: 1 approval
  
- ✅ **Require status checks to pass before merging**
  - Status checks: CI, tests
  
- ✅ **Require branches to be up to date before merging**
  
- ✅ **Require linear history** - RECOMMENDED
  
- ❌ **Do not allow force pushes**
  
- ❌ **Do not allow deletions**

#### Bypass Settings:
- ✅ **Allow administrators to bypass** - OPTIONAL
- ✅ **Allow specific users/teams to bypass** - CONFIGURE AS NEEDED

### 3. Collaborators and Teams

**Location**: Settings > Collaborators and teams

Ensure automation users/bots have appropriate permissions:
- **Write access** - Minimum for commit/push operations
- **Maintain access** - For full automation capabilities
- **Admin access** - If managing repository settings

### 4. GitHub Apps (If using GitHub Apps)

**Location**: Settings > GitHub Apps

If using a GitHub App for automation:
1. Install the app to the repository
2. Grant required permissions:
   - Repository permissions:
     - Contents: Read and write
     - Pull requests: Read and write
     - Issues: Read and write
     - Workflows: Read and write (if triggering workflows)

## Environment Variables

### Required for Automation

```bash
# GitHub Personal Access Token (for external tools)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxx

# Optional: Configure logging
GITHUB_ACTIONS_RUNNER_DEBUG=true  # Enable debug logging
ACTIONS_STEP_DEBUG=true           # Enable step debug logging
```

### Token Scopes Required

When creating a Personal Access Token (classic):
- ✅ `repo` (Full control of private repositories)
- ✅ `workflow` (Update GitHub Action workflows)

When creating a Fine-grained personal access token:
- **Repository permissions**:
  - Contents: Read and write
  - Pull requests: Read and write
  - Issues: Read and write
  - Workflows: Read and write

## Workflow File Configuration

The automation workflow (`.github/workflows/automated-pr.yml`) includes:

```yaml
permissions:
  contents: write        # Required for commits and pushes
  pull-requests: write   # Required for PR creation
  issues: write          # Required for issue references in PRs
```

## Security Considerations

### 1. Token Security
- ✅ Never commit tokens to repository
- ✅ Use GitHub Secrets for sensitive data
- ✅ Rotate tokens regularly (every 90 days recommended)
- ✅ Use minimal required permissions

### 2. Branch Protection
- ✅ Protect production branches (main, release/*)
- ✅ Require code review for sensitive changes
- ✅ Enable required status checks

### 3. Audit Logging
- ✅ Enable audit log review
- ✅ Monitor workflow runs
- ✅ Review automated commits regularly

## Verification Checklist

Use this checklist to verify configuration:

- [ ] GitHub Actions enabled in repository
- [ ] Workflow permissions set to "Read and write"
- [ ] "Allow GitHub Actions to create and approve pull requests" enabled
- [ ] Branch protection rules configured (if applicable)
- [ ] GITHUB_TOKEN has required scopes
- [ ] Workflow file (automated-pr.yml) committed to main branch
- [ ] Test run successful: `gh workflow run automated-pr.yml -f operation=create_branch -f branch_name=test/automation`

## Configuration via GitHub CLI

Automate configuration with these commands:

```bash
# Enable Actions
gh api repos/ProfRandom92/comptext-codex/actions/permissions \
  -X PUT \
  -f enabled=true

# Set workflow permissions
gh api repos/ProfRandom92/comptext-codex/actions/permissions/workflow \
  -X PUT \
  -F default_workflow_permissions=write \
  -F can_approve_pull_request_reviews=true

# Add branch protection (example)
gh api repos/ProfRandom92/comptext-codex/branches/main/protection \
  -X PUT \
  -f required_status_checks[strict]=true \
  -f required_status_checks[contexts][]=CI \
  -f enforce_admins=false \
  -f required_pull_request_reviews[required_approving_review_count]=1 \
  -f restrictions=null

# Add repository secret (for external tokens)
gh secret set CUSTOM_TOKEN -b"token_value"
```

## Configuration via GitHub API

For programmatic configuration:

```python
import requests
import os

def configure_workflow_permissions():
    """Configure workflow permissions via GitHub API"""
    
    url = "https://api.github.com/repos/ProfRandom92/comptext-codex/actions/permissions/workflow"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    payload = {
        "default_workflow_permissions": "write",
        "can_approve_pull_request_reviews": True
    }
    
    response = requests.put(url, json=payload, headers=headers)
    return response.status_code == 204

# Run configuration
if __name__ == "__main__":
    if configure_workflow_permissions():
        print("✅ Workflow permissions configured successfully")
    else:
        print("❌ Failed to configure workflow permissions")
```

## Troubleshooting Configuration Issues

### Issue: "Actions are disabled for this repository"
**Solution**:
```bash
gh api repos/ProfRandom92/comptext-codex/actions/permissions \
  -X PUT \
  -f enabled=true
```

### Issue: "Resource not accessible by integration"
**Solution**: Update workflow permissions:
```bash
gh api repos/ProfRandom92/comptext-codex/actions/permissions/workflow \
  -X PUT \
  -F default_workflow_permissions=write
```

### Issue: "Pull request creation not allowed"
**Solution**: Enable PR creation for workflows:
```bash
gh api repos/ProfRandom92/comptext-codex/actions/permissions/workflow \
  -X PUT \
  -F can_approve_pull_request_reviews=true
```

## References

- [GitHub Actions Permissions](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#permissions-for-the-github_token)
- [Managing Actions Permissions](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)
- [Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)

---

**Last Updated**: 2026-01-31
**Applies to**: GitHub Actions, GitHub API v2022-11-28
