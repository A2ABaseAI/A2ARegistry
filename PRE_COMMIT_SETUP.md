# Pre-commit Hooks Setup Guide

This guide explains how to set up and use pre-commit hooks for the A2A Registry project to ensure code quality before commits.

## 🎯 Overview

Pre-commit hooks automatically run quality checks before each commit, ensuring that:
- Code follows style guidelines
- No security vulnerabilities are introduced
- Type checking passes
- All tests pass
- Code is properly formatted

## 🚀 Quick Setup

### Option 1: Simple Git Hook (Already Active)

The project already has a simple pre-commit hook installed at `.git/hooks/pre-commit` that runs `make qa` before each commit.

**Status**: ✅ **Already Active**

### Option 2: Advanced Pre-commit Framework

For more comprehensive checks, you can use the `pre-commit` Python framework:

```bash
# Install pre-commit
make install-deps

# Install pre-commit hooks
make pre-commit-install
```

## 🔧 Available Commands

### Makefile Targets

```bash
# Install pre-commit hooks
make pre-commit-install

# Run pre-commit on all files
make pre-commit-run

# Update pre-commit hooks to latest versions
make pre-commit-update
```

### Manual Commands

```bash
# Install pre-commit hooks
pre-commit install

# Run on all files
pre-commit run --all-files

# Run on specific files
pre-commit run --files app/main.py

# Update hooks
pre-commit autoupdate
```

## 📋 What Gets Checked

### Simple Hook (Current)
- ✅ Linting (flake8)
- ✅ Security analysis (bandit)
- ✅ Type checking (mypy)
- ✅ Tests (pytest)

### Advanced Hook (Optional)
- ✅ Trailing whitespace removal
- ✅ End-of-file fixes
- ✅ YAML/JSON/TOML syntax checks
- ✅ Merge conflict detection
- ✅ Large file detection
- ✅ Black code formatting
- ✅ isort import sorting
- ✅ flake8 linting
- ✅ bandit security checks
- ✅ mypy type checking
- ✅ Full quality checks (`make qa`)

## 🎮 Usage Examples

### Basic Workflow

```bash
# Make changes to code
git add .
git commit -m "feat: add new feature"
# Pre-commit hooks run automatically
```

### If Hooks Fail

```bash
# Fix the issues shown in the output
# Then commit again
git add .
git commit -m "feat: add new feature"
```

### Skip Hooks (Not Recommended)

```bash
# Skip pre-commit hooks (use with caution)
git commit --no-verify -m "feat: add new feature"
```

## 🔍 Troubleshooting

### Common Issues

1. **Virtual Environment Not Found**
   ```bash
   # Solution: Run from project root
   cd /path/to/a2a-registry
   ```

2. **Makefile Not Found**
   ```bash
   # Solution: Ensure you're in the project root
   pwd  # Should show .../a2a-registry
   ```

3. **Quality Checks Fail**
   ```bash
   # Run individual checks to see specific issues
   make lint      # Check linting issues
   make security  # Check security issues
   make type      # Check type issues
   make test      # Check test failures
   ```

### Hook Not Running

```bash
# Check if hook is executable
ls -la .git/hooks/pre-commit

# Reinstall if needed
chmod +x .git/hooks/pre-commit
```

## 📁 Configuration Files

### Simple Hook
- **File**: `.git/hooks/pre-commit`
- **Purpose**: Runs `make qa` before commits

### Advanced Hook
- **File**: `.pre-commit-config.yaml`
- **Purpose**: Comprehensive pre-commit framework configuration

## 🎯 Benefits

### For Developers
- ✅ Catch issues before they reach the repository
- ✅ Consistent code style across the team
- ✅ Automatic code formatting
- ✅ Security vulnerability detection

### For the Project
- ✅ Higher code quality
- ✅ Reduced review time
- ✅ Consistent formatting
- ✅ Better security posture

## 🔄 Workflow Integration

### CI/CD Integration
The same quality checks run in CI/CD pipelines, ensuring consistency between local development and production.

### Team Collaboration
All team members benefit from the same quality standards, reducing merge conflicts and improving code consistency.

## 📚 Additional Resources

- [Pre-commit Documentation](https://pre-commit.com/)
- [Git Hooks Documentation](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)
- [A2A Registry Quality Checks](QUALITY_CHECKS.md)

## 🆘 Support

If you encounter issues with pre-commit hooks:

1. Check the troubleshooting section above
2. Run `make qa` manually to see specific issues
3. Check the project documentation
4. Ask for help in the project's communication channels
