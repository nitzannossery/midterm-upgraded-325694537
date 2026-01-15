#!/bin/bash
# Complete script to create GitHub repo and push code

GITHUB_USER="nitzannossery"
REPO_NAME="midterm-upgraded-325694537"
REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"
WEB_URL="https://github.com/$GITHUB_USER/$REPO_NAME"

echo "=========================================="
echo "GitHub Repository Setup & Push"
echo "=========================================="
echo ""
echo "GitHub User: $GITHUB_USER"
echo "Repository: $REPO_NAME"
echo ""

# Check if we're in a git repo
if [ ! -d .git ]; then
    echo "❌ Not a git repository. Initializing..."
    git init
    git add -A
    git commit -m "Initial commit - midterm upgraded 325694537"
fi

# Check current status
echo "=== Current Git Status ==="
git status --short
echo ""

# Ensure everything is committed
if [ -n "$(git status --porcelain)" ]; then
    echo "Committing uncommitted changes..."
    git add -A
    git commit -m "Update project files before GitHub push"
fi

echo "✅ All files committed"
echo ""

# Check if remote exists
if git remote get-url origin >/dev/null 2>&1; then
    current_url=$(git remote get-url origin)
    echo "⚠️  Remote already exists: $current_url"
    if [ "$current_url" != "$REPO_URL" ]; then
        echo "Updating remote URL..."
        git remote set-url origin "$REPO_URL"
    fi
else
    echo "Adding remote repository..."
    git remote add origin "$REPO_URL"
fi

echo ""
echo "Remote configuration:"
git remote -v
echo ""

echo "=========================================="
echo "📝 IMPORTANT: Create Repository on GitHub"
echo "=========================================="
echo ""
echo "Before pushing, you MUST create the repository on GitHub:"
echo ""
echo "1. Go to: https://github.com/new"
echo "2. Repository name: $REPO_NAME"
echo "3. Description: Financial Analysis Multi-Agent System with Comprehensive Evaluation Framework"
echo "4. Choose: Public or Private"
echo "5. ⚠️  DO NOT initialize with README, .gitignore, or license"
echo "6. Click: 'Create repository'"
echo ""
read -p "Have you created the repository on GitHub? (y/n): " created

if [ "$created" != "y" ]; then
    echo ""
    echo "Please create the repository first at: https://github.com/new"
    echo ""
    echo "After creating, run this script again or manually:"
    echo "  git push -u origin main"
    exit 1
fi

echo ""
echo "Pushing to GitHub..."
echo "This may take a moment..."
echo ""

# Ensure we're on main branch
git branch -M main 2>/dev/null

# Push to GitHub
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ SUCCESS! Repository pushed to GitHub!"
    echo "=========================================="
    echo ""
    echo "Your repository is now available at:"
    echo "🌐 $WEB_URL"
    echo ""
    echo "Repository details:"
    echo "  - Files: $(git ls-files | wc -l | tr -d ' ') files"
    echo "  - Commits: $(git rev-list --count HEAD) commits"
    echo "  - Branch: $(git branch --show-current)"
    echo ""
    echo "You can now:"
    echo "  - View it in your browser: $WEB_URL"
    echo "  - Share the link with others"
    echo "  - Continue working: git add, git commit, git push"
    echo ""
else
    echo ""
    echo "❌ Push failed. Possible reasons:"
    echo "  1. Repository doesn't exist yet (create it at https://github.com/new)"
    echo "  2. Authentication issue"
    echo "  3. Network problem"
    echo ""
    echo "To fix authentication:"
    echo "  - GitHub: Settings → Developer settings → Personal access tokens"
    echo "  - Or set up SSH keys: https://github.com/settings/keys"
    echo ""
    echo "Remote is configured. You can try pushing again with:"
    echo "  git push -u origin main"
fi

echo ""
echo "Done!"
