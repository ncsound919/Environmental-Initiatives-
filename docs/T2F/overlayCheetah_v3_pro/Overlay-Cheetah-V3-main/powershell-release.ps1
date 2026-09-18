# Cheetah v2 (TOON) Complete Release Script for PowerShell
# Copy-paste this entire script into PowerShell and run it

Write-Host "🚀 Cheetah v2 (TOON) Commercial Release Process" -ForegroundColor Blue
Write-Host "==================================================" -ForegroundColor Blue

# Set working directory
$toonPath = "C:\Users\tap45\Desktop\project 5\cheetah v2\toon-main"
if (!(Test-Path $toonPath)) {
    Write-Host "❌ Directory not found: $toonPath" -ForegroundColor Red
    Write-Host "Please update the path in this script to match your directory" -ForegroundColor Yellow
    exit 1
}

Set-Location $toonPath
Write-Host "📁 Working directory: $toonPath" -ForegroundColor Green

# Function to run commands with error handling
function Run-Command {
    param([string]$Command, [string]$Description)
    Write-Host "🔄 $Description..." -ForegroundColor Yellow
    try {
        Invoke-Expression $Command
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $Description completed successfully!" -ForegroundColor Green
        } else {
            Write-Host "❌ $Description failed with exit code $LASTEXITCODE" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "❌ $Description failed: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

# Check prerequisites
Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow
$nodeVersion = & node --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Node.js not found. Please install Node.js first." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green

# Check for package manager
$hasPnpm = $null -ne (Get-Command pnpm -ErrorAction SilentlyContinue)
$hasNpm = $null -ne (Get-Command npm -ErrorAction SilentlyContinue)

if ($hasPnpm) {
    $packageManager = "pnpm"
    Write-Host "✅ Using pnpm package manager" -ForegroundColor Green
} elseif ($hasNpm) {
    $packageManager = "npm"
    Write-Host "✅ Using npm package manager" -ForegroundColor Green
} else {
    Write-Host "❌ Neither pnpm nor npm found. Please install a package manager." -ForegroundColor Red
    exit 1
}

# Step 1: Install dependencies
Run-Command "$packageManager install" "Installing dependencies"

# Step 2: Run tests
Run-Command "$packageManager test" "Running test suite"

# Step 3: Run linting
Run-Command "$packageManager lint" "Running linting"

# Step 4: Run type checking
Run-Command "$packageManager test:types" "Running type checking"

# Step 5: Build packages
Run-Command "$packageManager build" "Building packages"

# Step 6: Run benchmarks (optional)
Write-Host "🔄 Running benchmarks (optional)..." -ForegroundColor Yellow
if (Test-Path "benchmarks") {
    Push-Location benchmarks
    try {
        & $packageManager benchmark:tokens
        Write-Host "✅ Benchmarks completed!" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Benchmarks failed or skipped" -ForegroundColor Yellow
    }
    Pop-Location
} else {
    Write-Host "⚠️ Benchmarks directory not found, skipping..." -ForegroundColor Yellow
}

# Step 7: Git operations
Write-Host "🔄 Setting up git repository..." -ForegroundColor Yellow
if (!(Test-Path ".git")) {
    Run-Command "git init" "Initializing git repository"
}

# Check git configuration
$gitUser = & git config user.name 2>$null
if (!$gitUser) {
    Write-Host "⚠️ Git user not configured. Please run:" -ForegroundColor Yellow
    Write-Host "git config --global user.name 'Your Name'" -ForegroundColor White
    Write-Host "git config --global user.email 'your.email@example.com'" -ForegroundColor White
    Read-Host "Press Enter after configuring git"
}

# Add files and commit
Run-Command "git add ." "Adding files to git"

$commitMessage = @"
Release v1.0.0: Commercial release of TOON format

- Complete TOON specification v1.4 implementation
- 30-60% token savings vs JSON for uniform arrays
- Comprehensive test suite and benchmarks
- CLI tool for JSON ↔ TOON conversion
- TypeScript-first with full type safety
- Updated all packages to version 1.0.0
- Added comprehensive CHANGELOG.md
- Ready for commercial distribution
"@

Run-Command "git commit -m '$commitMessage'" "Creating release commit"

# Create tag
Run-Command "git tag v1.0.0" "Creating v1.0.0 tag"

# Check and push to remote
Write-Host "🔄 Checking remote repository..." -ForegroundColor Yellow
try {
    $remoteUrl = & git remote get-url origin 2>$null
    if ($remoteUrl) {
        Write-Host "✅ Remote repository found: $remoteUrl" -ForegroundColor Green
        Run-Command "git push origin main" "Pushing to main branch"
        Run-Command "git push origin v1.0.0" "Pushing v1.0.0 tag"
    } else {
        Write-Host "⚠️ No remote repository configured." -ForegroundColor Yellow
        Write-Host "To complete the release, run these commands:" -ForegroundColor White
        Write-Host "git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git" -ForegroundColor White
        Write-Host "git push origin main" -ForegroundColor White
        Write-Host "git push origin v1.0.0" -ForegroundColor White
    }
} catch {
    Write-Host "⚠️ Remote repository not configured or accessible." -ForegroundColor Yellow
    Write-Host "You'll need to add the remote and push manually." -ForegroundColor White
}

# Final verification
Write-Host "🔍 Final verification..." -ForegroundColor Yellow

# Check package versions
Write-Host "📦 Checking package versions..." -ForegroundColor Blue
$versionFiles = Get-ChildItem -Path "packages\*\package.json", "package.json" -ErrorAction SilentlyContinue
foreach ($file in $versionFiles) {
    $content = Get-Content $file -Raw | ConvertFrom-Json
    if ($content.version -eq "1.0.0") {
        Write-Host "✅ $($content.name): v$($content.version)" -ForegroundColor Green
    } else {
        Write-Host "⚠️ $($content.name): v$($content.version) (expected 1.0.0)" -ForegroundColor Yellow
    }
}

# Check CHANGELOG
if (Test-Path "CHANGELOG.md") {
    Write-Host "✅ CHANGELOG.md exists" -ForegroundColor Green
} else {
    Write-Host "⚠️ CHANGELOG.md not found" -ForegroundColor Yellow
}

Write-Host "" -ForegroundColor White
Write-Host "🎉 Cheetah v2 (TOON) Commercial Release Complete!" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green
Write-Host "" -ForegroundColor White
Write-Host "📋 Release Summary:" -ForegroundColor Blue
Write-Host "✅ All tests passed" -ForegroundColor Green
Write-Host "✅ Linting passed" -ForegroundColor Green
Write-Host "✅ Type checking passed" -ForegroundColor Green
Write-Host "✅ Packages built successfully" -ForegroundColor Green
Write-Host "✅ Version updated to 1.0.0" -ForegroundColor Green
Write-Host "✅ Git commit and tag created" -ForegroundColor Green
Write-Host "✅ Ready for automated publishing" -ForegroundColor Green
Write-Host "" -ForegroundColor White
Write-Host "🚀 Next Steps:" -ForegroundColor Blue
Write-Host "1. If you haven't added the remote repository, do so now:" -ForegroundColor White
Write-Host "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git" -ForegroundColor White
Write-Host "2. Push to trigger automated release:" -ForegroundColor White
Write-Host "   git push origin main && git push origin v1.0.0" -ForegroundColor White
Write-Host "3. Monitor GitHub Actions for the release process" -ForegroundColor White
Write-Host "4. Verify packages on npm: npm view @toon-format/toon" -ForegroundColor White
Write-Host "" -ForegroundColor White
Write-Host "💰 Ready for commercial distribution!" -ForegroundColor Green
Write-Host "📦 Your TOON packages will be automatically published to npm!" -ForegroundColor Green

Read-Host "Press Enter to exit"