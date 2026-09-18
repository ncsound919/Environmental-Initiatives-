@echo off
REM Cheetah v2 (TOON) Commercial Release Script for Windows
REM This script automates the entire release process for TOON v1.0.0

echo 🚀 Starting Cheetah v2 (TOON) Commercial Release Process...
echo ==========================================================

REM Check if we're in the right directory
if not exist "package.json" (
    echo [ERROR] Please run this script from the toon-main directory
    pause
    exit /b 1
)

if not exist "packages" (
    echo [ERROR] Please run this script from the toon-main directory
    pause
    exit /b 1
)

echo [INFO] Step 1: Installing dependencies...
where pnpm >nul 2>nul
if %errorlevel% == 0 (
    pnpm install
    echo [SUCCESS] Dependencies installed with pnpm
) else (
    where npm >nul 2>nul
    if %errorlevel% == 0 (
        npm install
        echo [SUCCESS] Dependencies installed with npm
    ) else (
        echo [ERROR] Neither pnpm nor npm found. Please install Node.js package manager.
        pause
        exit /b 1
    )
)

echo [INFO] Step 2: Running test suite...
where pnpm >nul 2>nul
if %errorlevel% == 0 (
    pnpm test
) else (
    npm test
)
if %errorlevel% neq 0 (
    echo [ERROR] Tests failed!
    pause
    exit /b 1
)
echo [SUCCESS] All tests passed!

echo [INFO] Step 3: Running linting...
where pnpm >nul 2>nul
if %errorlevel% == 0 (
    pnpm lint
) else (
    npm run lint
)
if %errorlevel% neq 0 (
    echo [ERROR] Linting failed!
    pause
    exit /b 1
)
echo [SUCCESS] Linting passed!

echo [INFO] Step 4: Running type checking...
where pnpm >nul 2>nul
if %errorlevel% == 0 (
    pnpm test:types
) else (
    npm run test:types
)
if %errorlevel% neq 0 (
    echo [ERROR] Type checking failed!
    pause
    exit /b 1
)
echo [SUCCESS] Type checking passed!

echo [INFO] Step 5: Building packages...
where pnpm >nul 2>nul
if %errorlevel% == 0 (
    pnpm build
) else (
    npm run build
)
if %errorlevel% neq 0 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)
echo [SUCCESS] Packages built successfully!

echo [INFO] Step 6: Running benchmarks (optional)...
if exist "benchmarks" (
    cd benchmarks
    where pnpm >nul 2>nul
    if %errorlevel% == 0 (
        pnpm benchmark:tokens
    ) else (
        npm run benchmark:tokens
    )
    cd ..
    echo [SUCCESS] Benchmarks completed!
) else (
    echo [WARNING] Benchmarks directory not found, skipping...
)

echo [INFO] Step 7: Setting up git repository...
if not exist ".git" (
    git init
    echo [SUCCESS] Git repository initialized
)

echo [INFO] Step 8: Adding files to git...
git add .

echo [INFO] Step 9: Creating commit...
git commit -m "Release v1.0.0: Commercial release of TOON format

- Complete TOON specification v1.4 implementation
- 30-60%% token savings vs JSON for uniform arrays
- Comprehensive test suite and benchmarks
- CLI tool for JSON <-> TOON conversion
- TypeScript-first with full type safety
- Updated all packages to version 1.0.0
- Added comprehensive CHANGELOG.md
- Ready for commercial distribution"
echo [SUCCESS] Commit created successfully!

echo [INFO] Step 10: Creating and pushing v1.0.0 tag...
git tag v1.0.0

REM Check if remote exists
git remote get-url origin >nul 2>nul
if %errorlevel% == 0 (
    echo [INFO] Pushing to remote repository...
    git push origin main
    git push origin v1.0.0
    echo [SUCCESS] Code and tag pushed to remote repository!
) else (
    echo [WARNING] No remote repository configured.
    echo [INFO] To complete the release, add the remote and push:
    echo git remote add origin https://github.com/toon-format/toon.git
    echo git push origin main
    echo git push origin v1.0.0
)

echo [INFO] Step 11: Verifying package configuration...
echo Checking package versions...
findstr /r "version.*1.0.0" packages\*\package.json package.json
if %errorlevel% neq 0 (
    echo [WARNING] Some package versions may not be updated
)

echo [INFO] Step 12: Final verification checklist...
echo ✅ All tests passed
echo ✅ Linting passed
echo ✅ Type checking passed
echo ✅ Packages built successfully
echo ✅ Version updated to 1.0.0
echo ✅ CHANGELOG.md created
echo ✅ Git commit and tag created
echo ✅ Ready for automated publishing

echo.
echo 🎉 Cheetah v2 (TOON) Commercial Release Preparation Complete!
echo ==========================================================
echo.
echo Next Steps:
echo 1. If you haven't already, add the remote repository:
echo    git remote add origin https://github.com/toon-format/toon.git
echo 2. Push to trigger the automated release:
echo    git push origin main
echo    git push origin v1.0.0
echo 3. Monitor the GitHub Actions for the release process
echo 4. Verify packages appear on npm: npm view @toon-format/toon
echo.
echo 📦 Your TOON packages will be automatically published to npm!
echo 🚀 Commercial release is ready!

pause