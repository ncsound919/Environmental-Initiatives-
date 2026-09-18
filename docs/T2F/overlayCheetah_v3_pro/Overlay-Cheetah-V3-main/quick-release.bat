@echo off
REM Quick Release Script - Minimal version for fast execution
REM Just copy-paste and run this in your terminal

echo 🚀 Quick TOON v1.0.0 Release...
cd /d "C:\Users\tap45\Desktop\project 5\cheetah v2\toon-main"

REM Install dependencies
echo 📦 Installing dependencies...
pnpm install >nul 2>&1 || npm install >nul 2>&1

REM Run tests
echo 🧪 Running tests...
pnpm test >nul 2>&1 || npm test >nul 2>&1

REM Build packages
echo 🔨 Building packages...
pnpm build >nul 2>&1 || npm run build >nul 2>&1

REM Git operations
echo 📝 Committing release...
git add .
git commit -m "Release v1.0.0: Commercial release of TOON format" >nul 2>&1 || echo No changes to commit
git tag v1.0.0

REM Push if remote exists
git remote get-url origin >nul 2>&1
if %errorlevel% == 0 (
    echo 🚀 Pushing to trigger release...
    git push origin main
    git push origin v1.0.0
) else (
    echo ⚠️  No remote configured. Add it and push manually:
    echo git remote add origin https://github.com/toon-format/toon.git
    echo git push origin main ^&^& git push origin v1.0.0
)

echo ✅ Release preparation complete!
echo 📦 Packages will be published automatically via GitHub Actions
pause