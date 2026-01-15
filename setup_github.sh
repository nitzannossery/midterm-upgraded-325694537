#!/bin/bash
# Quick setup script for GitHub user: nitzannossery

GITHUB_USER="nitzannossery"
REPO_NAME="midterm-upgraded-325694537"
REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"
WEB_URL="https://github.com/$GITHUB_USER/$REPO_NAME"

echo "=========================================="
echo "GitHub Remote Setup"
echo "=========================================="
echo ""
echo "GitHub User: $GITHUB_USER"
echo "Repository: $REPO_NAME"
echo "URL: $REPO_URL"
echo "Web: $WEB_URL"
echo ""

# Check if remote already exists
if git remote get-url origin >/dev/null 2>&1; then
    current_url=$(git remote get-url origin)
    echo "⚠️  Remote already exists: $current_url"
    echo ""
    read -p "Do you want to replace it? (y/n): " replace
    if [ "$replace" = "y" ]; then
        git remote remove origin
        echo "✅ Removed existing remote"
    else
        echo "Keeping existing remote."
        exit 0
    fi
fi

echo ""
echo "📝 IMPORTANT: Make sure you've created the repository on GitHub!"
echo ""
echo "Steps:"
echo "1. Go to: https://github.com/new"
echo "2. Repository name: $REPO_NAME"
echo "3. Description: Financial Analysis Multi-Agent System with Comprehensive Evaluation Framework"
echo "4. Choose: Public or Private"
echo "5. ⚠️  DO NOT initialize with README (we already have one)"
echo "6. Click: 'Create repository'"
echo ""
read -p "Have you created the repository? (y/n): " created

if [ "$created" != "y" ]; then
    echo ""
    echo "Please create the repository first, then run this script again."
    echo ""
    echo "Or create it now at: https://github.com/new"
    exit 1
fi

echo ""
echo "Adding remote repository..."
git remote add origin "$REPO_URL"

if [ $? -ne 0 ]; then
    echo "❌ Failed to add remote. It might already exist."
    exit 1
fi

echo "✅ Remote added successfully!"
echo ""
echo "Remote configuration:"
git remote -v
echo ""

read -p "Push to GitHub now? (y/n): " push_now

if [ "$push_now" = "y" ]; then
    echo ""
    echo "Pushing to GitHub..."
    echo "This may take a moment..."
    echo ""
    
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
        echo "You can:"
        echo "  - View it in your browser"
        echo "  - Share the link with others"
        echo "  - Continue working: git add, git commit, git push"
        echo ""
    else
        echo ""
        echo "❌ Push failed. Possible reasons:"
        echo "  1. Repository doesn't exist yet"
        echo "  2. Authentication issue (need SSH keys or token)"
        echo "  3. Network problem"
        echo ""
        echo "To fix authentication:"
        echo "  - Set up SSH keys: https://github.com/settings/keys"
        echo "  - Or use Personal Access Token with HTTPS"
        echo ""
        echo "Remote is configured. You can push later with:"
        echo "  git push -u origin main"
    fi
else
    echo ""
    echo "Remote configured. To push later, run:"
    echo "  git push -u origin main"
    echo ""
    echo "Your repository URL: $WEB_URL"
fi

echo ""
echo "Done!"
