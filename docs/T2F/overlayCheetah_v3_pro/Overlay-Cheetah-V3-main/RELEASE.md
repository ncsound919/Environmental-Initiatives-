# Cheetah v2 (TOON) Commercial Release Script

This directory contains automated release scripts for Cheetah v2 (TOON) commercial release.

## Quick Start

### Windows (Recommended)
```bash
# Navigate to the toon-main directory
cd "C:\Users\tap45\Desktop\project 5\cheetah v2\toon-main"

# Run the Windows release script
release.bat
```

### Linux/macOS
```bash
# Navigate to the toon-main directory
cd /path/to/cheetah-v2/toon-main

# Make the script executable and run it
chmod +x release.sh
./release.sh
```

## What the Script Does

The release script automates the entire commercial release process:

1. **✅ Dependency Installation** - Installs all required packages
2. **✅ Test Suite** - Runs comprehensive tests to verify functionality
3. **✅ Linting** - Checks code quality and style
4. **✅ Type Checking** - Verifies TypeScript types are correct
5. **✅ Build Packages** - Compiles all packages for distribution
6. **✅ Benchmarks** - Runs performance validation (optional)
7. **✅ Git Setup** - Initializes repository if needed
8. **✅ Commit Changes** - Creates release commit with detailed message
9. **✅ Create Tag** - Tags the release as v1.0.0
10. **✅ Push to Remote** - Triggers automated publishing via GitHub Actions

## Prerequisites

- **Node.js** (v18 or higher)
- **pnpm** (recommended) or **npm**
- **Git** configured with user name and email
- **GitHub repository access** (for pushing)

## Manual Steps (if script fails)

If the automated script encounters issues, you can run these steps manually:

```bash
# 1. Install dependencies
pnpm install

# 2. Run tests
pnpm test

# 3. Run linting
pnpm lint

# 4. Type checking
pnpm test:types

# 5. Build packages
pnpm build

# 6. Git operations
git add .
git commit -m "Release v1.0.0: Commercial release of TOON format"
git tag v1.0.0
git push origin main
git push origin v1.0.0
```

## Post-Release Verification

After the script completes and GitHub Actions finish:

1. **Check npm**: `npm view @toon-format/toon`
2. **Test CLI**: `npx @toon-format/cli --help`
3. **Verify GitHub Release**: Check the releases page on GitHub
4. **Monitor CI Badges**: Ensure they show passing status

## Troubleshooting

### Common Issues

**"pnpm command not found"**
- Install pnpm: `npm install -g pnpm`
- Or use npm instead (script auto-detects)

**"Git user not configured"**
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

**"No remote repository configured"**
```bash
git remote add origin https://github.com/toon-format/toon.git
```

**Tests fail**
- Check Node.js version (requires v18+)
- Ensure all dependencies installed correctly
- Run `pnpm install` again

**Build fails**
- Check TypeScript configuration
- Ensure all imports are correct
- Verify tsdown configuration

### Environment-Specific Issues

**Windows Command Prompt**
- Use `release.bat` instead of `.sh`
- Ensure Git is in your PATH
- Run as Administrator if needed

**PowerShell**
- May need to run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Then run: `.\release.bat`

**Linux/macOS**
- Make script executable: `chmod +x release.sh`
- Ensure proper permissions for git operations

## Release Checklist

Before running the script, verify:

- [ ] All code changes are committed
- [ ] Version numbers updated to 1.0.0
- [ ] CHANGELOG.md is complete
- [ ] Documentation is up-to-date
- [ ] Tests pass locally
- [ ] Build succeeds locally
- [ ] Git is properly configured
- [ ] Remote repository is accessible

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all prerequisites are met
3. Run individual commands manually to isolate the problem
4. Check GitHub Actions logs for CI/CD issues
5. Review the TOON documentation for guidance

---

**🚀 Ready for commercial release!** 

The script will handle everything from testing to publishing. Just run it and monitor the process!