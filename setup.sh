#!/bin/bash

# US Financial Moves - Quick Setup Script
# This script helps set up the project for deployment

echo "🚀 US Financial Moves - Setup Script"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "✅ Project directory confirmed"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: US Financial Moves platform"
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
    echo "✅ Node.js dependencies installed"
else
    echo "✅ Node.js dependencies already installed"
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "⚠️  Warning: .env.local not found"
    echo "   Please create .env.local with your Supabase credentials"
    echo "   See DEPLOYMENT.md for details"
else
    echo "✅ Environment file found"
fi

# Check if ingestor directory exists
if [ ! -d "ingestor" ]; then
    echo "❌ Error: Ingestor directory not found"
    exit 1
else
    echo "✅ Ingestor system found"
fi

# Check if GitHub Actions workflows exist
if [ ! -d ".github/workflows" ]; then
    echo "❌ Error: GitHub Actions workflows not found"
    exit 1
else
    echo "✅ GitHub Actions workflows found"
fi

echo ""
echo "🎯 Next Steps:"
echo "1. Create a GitHub repository"
echo "2. Add your repository as remote: git remote add origin <your-repo-url>"
echo "3. Push your code: git push -u origin main"
echo "4. Set up GitHub Secrets (see DEPLOYMENT.md)"
echo "5. Deploy to Vercel"
echo "6. Enable GitHub Actions"
echo ""
echo "📖 For detailed instructions, see DEPLOYMENT.md"
echo ""
echo "🧪 To test the ingestor locally:"
echo "   cd ingestor && python test_reliable_feeds.py"
echo ""
echo "✅ Setup complete! Ready for deployment."
