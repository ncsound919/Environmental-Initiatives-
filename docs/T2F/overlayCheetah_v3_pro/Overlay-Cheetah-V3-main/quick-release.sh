#!/bin/bash

# Quick Release Script - Minimal version for fast execution
# Just copy-paste and run this in your terminal

echo "🚀 Quick TOON v1.0.0 Release..."
cd "C:\Users\tap45\Desktop\project 5\cheetah v2\toon-main" 2>/dev/null || cd "$(dirname "$0")"

# Install dependencies
echo "📦 Installing dependencies..."
pnpm install 2>/dev/null || npm install

# Run tests
echo "🧪 Running tests..."
pnpm test 2>/dev/null || npm test

# Build packages
echo "🔨 Building packages..."
pnpm build 2>/dev/null || npm run build

# Git operations
echo "📝 Committing release..."
git add .
git commit -m "Release v1.0.0: Commercial release of TOON format" || echo "No changes to commit"
git tag v1.0.0

# Push if remote exists
if git remote get-url origin &>/dev/null; then
    echo "🚀 Pushing to trigger release..."
    git push origin main
    git push origin v1.0.0
else
    echo "⚠️  No remote configured. Add it and push manually:"
    echo "git remote add origin https://github.com/toon-format/toon.git"
    echo "git push origin main && git push origin v1.0.0"
fi

echo "✅ Release preparation complete!"
echo "📦 Packages will be published automatically via GitHub Actions"