#!/bin/bash
# Script to synchronize PR branches with main
# This script should be run by someone with push access to the repository

set -e  # Exit on error

echo "=== PR Branch Synchronization Script ==="
echo ""
echo "This script will synchronize the following branches with main:"
echo "  1. feat/codex-v2 (PR #5)"
echo "  2. codex/alle-comptext-repositorys-funktionsfahig-machen (PR #1)"
echo ""
echo "And document that the following branch should be closed:"
echo "  - codex/alle-comptext-repositorys-funktionsfahig-machen-urfjay (PR #2)"
echo ""

# Fetch latest changes
echo "Fetching latest changes from origin..."
git fetch origin

# Synchronize feat/codex-v2
echo ""
echo "=== Synchronizing feat/codex-v2 with main ==="
git checkout feat/codex-v2
if git merge main --allow-unrelated-histories --no-edit; then
    echo "✅ Merged without conflicts"
else
    echo "Merge conflicts detected. Resolving by accepting main branch versions..."
    # List of expected conflict files - check if they exist and have conflicts
    for file in .gitignore README.md .github/workflows/build-codex-bundle.yml scripts/build_bundle.py scripts/validate_codex.py mcp_loader/loader.py; do
        if [ -f "$file" ] && git status --porcelain | grep -q "^UU $file\|^AA $file"; then
            git checkout --theirs "$file"
        fi
    done
    git add .
    git commit -m "Merge main into feat/codex-v2 - resolve conflicts by accepting main versions"
fi
echo "✅ feat/codex-v2 synchronized"

# Synchronize codex/alle-comptext-repositorys-funktionsfahig-machen
echo ""
echo "=== Synchronizing codex/alle-comptext-repositorys-funktionsfahig-machen with main ==="
git checkout codex/alle-comptext-repositorys-funktionsfahig-machen
if git merge main --allow-unrelated-histories --no-edit; then
    echo "✅ Merged without conflicts"
else
    echo "Merge conflicts detected. Resolving by accepting main branch versions..."
    # List of expected conflict files - check if they exist and have conflicts
    for file in README.md SECURITY.md requirements.txt setup.py tests/test_token_reduction.py; do
        if [ -f "$file" ] && git status --porcelain | grep -q "^UU $file\|^AA $file"; then
            git checkout --theirs "$file"
        fi
    done
    git add .
    git commit -m "Merge main into codex/alle-comptext-repositorys-funktionsfahig-machen - resolve conflicts"
fi
echo "✅ codex/alle-comptext-repositorys-funktionsfahig-machen synchronized"

# Push both branches
echo ""
echo "=== Pushing synchronized branches ==="
git push origin feat/codex-v2
git push origin codex/alle-comptext-repositorys-funktionsfahig-machen

echo ""
echo "=== Summary ==="
echo "✅ feat/codex-v2 - synchronized and pushed"
echo "✅ codex/alle-comptext-repositorys-funktionsfahig-machen - synchronized and pushed"
echo "⚠️  codex/alle-comptext-repositorys-funktionsfahig-machen-urfjay - SHOULD BE CLOSED (redundant)"
echo ""
echo "Next steps:"
echo "1. Close PR for codex/alle-comptext-repositorys-funktionsfahig-machen-urfjay"
echo "2. Verify CI/CD passes on synchronized branches"
echo "3. Merge remaining PRs"
