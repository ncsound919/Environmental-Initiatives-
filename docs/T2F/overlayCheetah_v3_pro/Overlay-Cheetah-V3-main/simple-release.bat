@echo off
REM TOON v1.0.0 Release - Simple Windows Batch Script
REM Copy-paste this entire script into a .bat file and run it

echo 🚀 TOON v1.0.0 Release Script
echo ================================

cd /d "C:\Users\tap45\Desktop\project 5\cheetah v2\toon-main"
echo 📁 Working in: %CD%

REM Function to run commands with error checking
goto :main

:run_cmd
set "cmd=%~1"
set "desc=%~2"
echo 🔄 %desc%...
%cmd%
if %errorlevel% neq 0 (
    echo ❌ %desc% failed!
    pause
    exit /b 1
)
echo ✅ %desc% done!
goto :eof

:main
REM Check for package manager
where pnpm >nul 2>nul
if %errorlevel% == 0 (
    set "pm=pnpm"
) else (
    where npm >nul 2>nul
    if %errorlevel% == 0 (
        set "pm=npm"
    ) else (
        echo ❌ No package manager found!
        pause
        exit /b 1
    )
)

call :run_cmd "%pm% install" "Installing dependencies"
call :run_cmd "%pm% test" "Running tests"
call :run_cmd "%pm% lint" "Running linting"
call :run_cmd "%pm% test:types" "Running type checking"
call :run_cmd "%pm% build" "Building packages"

REM Git operations
if not exist ".git" (
    call :run_cmd "git init" "Initializing git"
)

call :run_cmd "git add ." "Adding files"

REM Create commit with multi-line message
echo 📝 Creating commit...
(
echo Release v1.0.0: Commercial release of TOON format
echo.
echo - Complete TOON specification v1.4 implementation
echo - 30-60%% token savings vs JSON for uniform arrays
echo - Comprehensive test suite and benchmarks
echo - CLI tool for JSON ↔ TOON conversion
echo - TypeScript-first with full type safety
echo - Updated all packages to version 1.0.0
echo - Added comprehensive CHANGELOG.md
echo - Ready for commercial distribution
) > commit_msg.txt

git commit -F commit_msg.txt
if %errorlevel% neq 0 (
    echo ❌ Commit failed!
    pause
    exit /b 1
)
echo ✅ Commit created!
del commit_msg.txt

call :run_cmd "git tag v1.0.0" "Creating tag"

REM Check remote
git remote get-url origin >nul 2>nul
if %errorlevel% == 0 (
    call :run_cmd "git push origin main" "Pushing main"
    call :run_cmd "git push origin v1.0.0" "Pushing tag"
) else (
    echo ⚠️ No remote configured. Run these commands:
    echo git remote add origin https://github.com/YOUR_REPO.git
    echo git push origin main ^&^& git push origin v1.0.0
)

echo.
echo 🎉 Release complete!
echo 📦 Check npm: npm view @toon-format/toon
echo 💰 Ready for commercial distribution!

pause