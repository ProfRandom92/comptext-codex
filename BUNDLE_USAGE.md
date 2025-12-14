# Git Bundle Usage Instructions

## What is this bundle?

`pr-sync-bundle.bundle` is a Git bundle file containing the synchronized versions of:
- `feat/codex-v2` - with main merged in, conflicts resolved
- `codex/alle-comptext-repositorys-funktionsfahig-machen` - with main merged in, conflicts resolved

**Bundle Location**: This bundle file should be in the root of the repository alongside this documentation. If it's missing, you can recreate it using the `sync_pr_branches.sh` script or download it from the PR assets.

## How to use this bundle

### Option 1: Extract and push directly (Recommended)

```bash
# 1. Verify the bundle
git bundle verify pr-sync-bundle.bundle

# 2. List what's in the bundle
git bundle list-heads pr-sync-bundle.bundle

# 3. Fetch the branches from the bundle
git fetch pr-sync-bundle.bundle feat/codex-v2:feat/codex-v2-synced
git fetch pr-sync-bundle.bundle codex/alle-comptext-repositorys-funktionsfahig-machen:codex/alle-comptext-repositorys-funktionsfahig-machen-synced

# 4. Verify the branches look correct
git log feat/codex-v2-synced -5
git log codex/alle-comptext-repositorys-funktionsfahig-machen-synced -5

# 5. Push to overwrite the remote branches
# WARNING: --force will overwrite remote branches. Use --force-with-lease for safer alternative.
# Consider backing up branches first: git branch backup/feat/codex-v2 feat/codex-v2
echo "⚠️  About to force push. Press Ctrl+C to cancel, Enter to continue..."
read -r
git push origin feat/codex-v2-synced:feat/codex-v2 --force
git push origin codex/alle-comptext-repositorys-funktionsfahig-machen-synced:codex/alle-comptext-repositorys-funktionsfahig-machen --force

# 6. Clean up local temporary branches
git branch -D feat/codex-v2-synced codex/alle-comptext-repositorys-funktionsfahig-machen-synced
```

### Option 2: Use as reference to apply manually

If you prefer not to force push, you can:

1. Extract the bundle to a temporary directory
2. Review the merge commits
3. Apply the same merges manually using the provided `sync_pr_branches.sh` script

```bash
# Clone bundle to temporary location
mkdir /tmp/pr-sync-review
cd /tmp/pr-sync-review
git clone /path/to/pr-sync-bundle.bundle .

# Review the changes
git log --oneline --graph --all

# Then apply manually using the sync script in the original repo
```

## What's in the bundle?

### Commit: feat/codex-v2
- Hash: `f68b9dc5a8ae2b0fa66fe5ccbf55695e5d2ad9fe`
- Message: "Merge main into feat/codex-v2 - resolve conflicts by accepting main versions"
- Parents: `d94baa3` (original HEAD), `734937c` (main)

### Commit: codex/alle-comptext-repositorys-funktionsfahig-machen
- Hash: `516e7031c3717cc547d52c4f450b412b87de519d`
- Message: "Merge main into codex/alle-comptext-repositorys-funktionsfahig-machen - resolve conflicts"
- Parents: `41d0210` (original HEAD), `734937c` (main)

## Verification

After applying the bundle, you should verify:

```bash
# Check that branches can merge cleanly into main
git checkout main
git merge --no-commit --no-ff feat/codex-v2
# Should show: Automatic merge went well; stopped before committing
git merge --abort

git merge --no-commit --no-ff codex/alle-comptext-repositorys-funktionsfahig-machen
# Should show: Automatic merge went well; stopped before committing
git merge --abort
```

## Safety Notes

- The bundle contains the full history and should be safe to apply
- Using `--force` to push will overwrite the remote branches
- Ensure no one else is working on these branches before force pushing
- Consider creating backup branches before applying if you want to preserve the original state

## Alternative: Manual sync

If you prefer not to use the bundle, you can run the provided script:
```bash
./sync_pr_branches.sh
```

This will perform the same merges from scratch.
