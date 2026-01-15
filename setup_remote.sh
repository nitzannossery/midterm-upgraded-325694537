#!/bin/bash
# Script to set up remote Git repository for midterm project

echo "=========================================="
echo "Git Remote Repository Setup"
echo "=========================================="
echo ""

# Check if remote already exists
if git remote get-url origin >/dev/null 2>&1; then
    echo "✅ Remote repository already configured:"
    git remote -v
    echo ""
    read -p "Do you want to change it? (y/n): " change_remote
    if [ "$change_remote" != "y" ]; then
        echo "Keeping existing remote."
        exit 0
    fi
    git remote remove origin
fi

echo "Please choose your Git hosting service:"
echo "1. GitHub"
echo "2. GitLab"
echo "3. Bitbucket"
echo "4. Custom URL"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "📝 Steps to create GitHub repository:"
        echo "1. Go to: https://github.com/new"
        echo "2. Repository name: midterm-upgraded-325694537"
        echo "3. Description: Financial Analysis Multi-Agent System with Comprehensive Evaluation Framework"
        echo "4. Choose Public or Private"
        echo "5. DO NOT initialize with README (we already have one)"
        echo "6. Click 'Create repository'"
        echo ""
        read -p "Enter your GitHub username: " github_username
        read -p "Enter repository name (default: midterm-upgraded-325694537): " repo_name
        repo_name=${repo_name:-midterm-upgraded-325694537}
        repo_url="https://github.com/$github_username/$repo_name.git"
        ;;
    2)
        echo ""
        echo "📝 Steps to create GitLab repository:"
        echo "1. Go to: https://gitlab.com/projects/new"
        echo "2. Project name: midterm-upgraded-325694537"
        echo "3. Choose Public or Private"
        echo "4. Click 'Create project'"
        echo ""
        read -p "Enter your GitLab username: " gitlab_username
        read -p "Enter repository name (default: midterm-upgraded-325694537): " repo_name
        repo_name=${repo_name:-midterm-upgraded-325694537}
        repo_url="https://gitlab.com/$gitlab_username/$repo_name.git"
        ;;
    3)
        echo ""
        echo "📝 Steps to create Bitbucket repository:"
        echo "1. Go to: https://bitbucket.org/repo/create"
        echo "2. Repository name: midterm-upgraded-325694537"
        echo "3. Choose Private or Public"
        echo "4. Click 'Create repository'"
        echo ""
        read -p "Enter your Bitbucket username: " bitbucket_username
        read -p "Enter repository name (default: midterm-upgraded-325694537): " repo_name
        repo_name=${repo_name:-midterm-upgraded-325694537}
        repo_url="https://bitbucket.org/$bitbucket_username/$repo_name.git"
        ;;
    4)
        echo ""
        read -p "Enter the full repository URL: " repo_url
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "Repository URL: $repo_url"
echo ""
read -p "Have you created the repository? (y/n): " created

if [ "$created" != "y" ]; then
    echo ""
    echo "⚠️  Please create the repository first, then run this script again."
    echo "Or you can manually run:"
    echo "  git remote add origin $repo_url"
    echo "  git push -u origin main"
    exit 1
fi

echo ""
echo "Adding remote repository..."
git remote add origin "$repo_url"

echo ""
echo "Checking remote..."
git remote -v

echo ""
read -p "Push to remote repository? (y/n): " push_now

if [ "$push_now" = "y" ]; then
    echo ""
    echo "Pushing to remote..."
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ SUCCESS! Repository pushed to remote."
        echo ""
        echo "Your repository URL:"
        echo "$repo_url"
        echo ""
        echo "You can view it in your browser!"
    else
        echo ""
        echo "❌ Push failed. Please check:"
        echo "1. Repository exists and is accessible"
        echo "2. You have write permissions"
        echo "3. Authentication is set up (SSH keys or credentials)"
    fi
else
    echo ""
    echo "Remote added. To push later, run:"
    echo "  git push -u origin main"
fi

echo ""
echo "Done!"
