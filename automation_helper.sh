#!/bin/bash
# Helper script for triggering automated repository operations
# Usage: ./automation_helper.sh <operation> [parameters...]

set -e

REPO_OWNER="ProfRandom92"
REPO_NAME="comptext-codex"
WORKFLOW_FILE="automated-pr.yml"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is not installed${NC}"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}You need to authenticate with GitHub CLI${NC}"
    echo "Run: gh auth login"
    exit 1
fi

# Function to print usage
usage() {
    cat << EOF
${GREEN}Repository Automation Helper${NC}

Usage: $0 <operation> [options]

Operations:
  create-pr      Create a pull request
  commit-push    Commit and push changes
  switch-branch  Switch to a branch
  create-branch  Create a new branch

Examples:
  # Create a PR
  $0 create-pr --title "New feature" --body "Description" --base main

  # Commit and push
  $0 commit-push --message "feat: add new functionality"

  # Switch branch
  $0 switch-branch --branch feat/new-feature

  # Create branch
  $0 create-branch --branch feat/automated-feature

Options:
  --title        PR title (for create-pr)
  --body         PR body/description (for create-pr)
  --base         Base branch for PR (default: main)
  --message      Commit message (for commit-push)
  --branch       Branch name (for switch-branch, create-branch)
  --help         Show this help message

EOF
}

# Parse command line arguments
OPERATION=""
PR_TITLE=""
PR_BODY=""
BASE_BRANCH="main"
COMMIT_MESSAGE=""
BRANCH_NAME=""

if [ $# -eq 0 ]; then
    usage
    exit 0
fi

OPERATION=$1
shift

while [[ $# -gt 0 ]]; do
    case $1 in
        --title)
            PR_TITLE="$2"
            shift 2
            ;;
        --body)
            PR_BODY="$2"
            shift 2
            ;;
        --base)
            BASE_BRANCH="$2"
            shift 2
            ;;
        --message)
            COMMIT_MESSAGE="$2"
            shift 2
            ;;
        --branch)
            BRANCH_NAME="$2"
            shift 2
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            exit 1
            ;;
    esac
done

# Execute the operation
case $OPERATION in
    create-pr)
        if [ -z "$PR_TITLE" ]; then
            echo -e "${RED}Error: --title is required for create-pr${NC}"
            exit 1
        fi
        echo -e "${GREEN}Creating pull request...${NC}"
        gh workflow run $WORKFLOW_FILE \
            -f operation=create_pr \
            -f pr_title="$PR_TITLE" \
            -f pr_body="${PR_BODY:-Automated PR}" \
            -f base_branch="$BASE_BRANCH"
        echo -e "${GREEN}✅ Pull request workflow triggered${NC}"
        ;;
    
    commit-push)
        if [ -z "$COMMIT_MESSAGE" ]; then
            echo -e "${RED}Error: --message is required for commit-push${NC}"
            exit 1
        fi
        echo -e "${GREEN}Committing and pushing changes...${NC}"
        gh workflow run $WORKFLOW_FILE \
            -f operation=commit_and_push \
            -f commit_message="$COMMIT_MESSAGE"
        echo -e "${GREEN}✅ Commit and push workflow triggered${NC}"
        ;;
    
    switch-branch)
        if [ -z "$BRANCH_NAME" ]; then
            echo -e "${RED}Error: --branch is required for switch-branch${NC}"
            exit 1
        fi
        echo -e "${GREEN}Switching to branch: $BRANCH_NAME${NC}"
        gh workflow run $WORKFLOW_FILE \
            -f operation=switch_branch \
            -f branch_name="$BRANCH_NAME"
        echo -e "${GREEN}✅ Branch switch workflow triggered${NC}"
        ;;
    
    create-branch)
        if [ -z "$BRANCH_NAME" ]; then
            echo -e "${RED}Error: --branch is required for create-branch${NC}"
            exit 1
        fi
        echo -e "${GREEN}Creating branch: $BRANCH_NAME${NC}"
        gh workflow run $WORKFLOW_FILE \
            -f operation=create_branch \
            -f branch_name="$BRANCH_NAME"
        echo -e "${GREEN}✅ Branch creation workflow triggered${NC}"
        ;;
    
    *)
        echo -e "${RED}Unknown operation: $OPERATION${NC}"
        usage
        exit 1
        ;;
esac

echo ""
echo -e "${YELLOW}Note: The workflow is running asynchronously.${NC}"
echo "Check status with: gh run list --workflow=$WORKFLOW_FILE"
echo "View logs with: gh run view <run-id> --log"
