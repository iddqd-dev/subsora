# CI/CD Quality Gates Setup Guide

## Overview

This guide explains how to set up linting, testing, and security scanning for each component.

## Backend (Python)

### 1. Add Linting Dependencies

Update `backend/requirements.txt`:

```
# Existing dependencies...

# Testing & Quality
pytest==8.4.1           # Already present
pytest-cov==4.1.0       # Coverage reporting
flake8==7.0.0          # Code style linting
black==24.1.0          # Code formatter
isort==5.13.0          # Import sorting
```

### 2. Configure Tools

#### Create `backend/.flake8`

```ini
[flake8]
max-line-length = 120
extend-ignore = E203, W503
exclude = .git,.venv,__pycache__,.pytest_cache,alembic
```

#### Create `backend/pyproject.toml` (for black and isort)

```toml
[tool.black]
line-length = 120
target-version = ['py311']
exclude = '.venv|alembic'

[tool.isort]
profile = "black"
line_length = 120
skip = [".venv", "alembic"]
```

### 3. Run Linting & Tests Locally

```bash
cd backend

# Format code
black .
isort .

# Check without formatting
black --check .
isort --check-only .

# Lint
flake8 .

# Run tests with coverage
pytest tests/ -v --cov=app --cov-report=html
```

### 4. Pre-commit Hook (Optional)

Create `backend/.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/PyCQA/isort
    rev: 5.13.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/PyCQA/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ["--max-line-length=120", "--extend-ignore=E203,W503"]
```

Then install:
```bash
pip install pre-commit
pre-commit install
```

## Frontend (TypeScript/React)

### 1. Configure ESLint

Already exists in `frontend/eslint.config.js`. Verify it has:

```javascript
export default [
  js.configs.recommended,
  {
    rules: {
      "no-unused-vars": "warn",
      "no-explicit-any": "warn",
    }
  }
]
```

### 2. Update package.json

Ensure these scripts exist in `frontend/package.json`:

```json
{
  "scripts": {
    "lint": "eslint . --ext .ts,.tsx",
    "lint:fix": "eslint . --ext .ts,.tsx --fix",
    "type-check": "tsc --noEmit",
    "build": "vite build"
  }
}
```

### 3. Run Linting Locally

```bash
cd frontend

# Check linting
npm run lint

# Fix issues
npm run lint:fix

# Type checking
npm run type-check
```

## Bot (Python)

### 1. Add Linting Dependencies

Update `bot/requirements.txt`:

```
# Existing dependencies...

# Quality & Testing
flake8==7.0.0
black==24.1.0
isort==5.13.0
pytest==8.4.1
```

### 2. Configure Tools

Same as backend - create `.flake8` and `pyproject.toml` in bot directory.

### 3. Run Linting Locally

```bash
cd bot

black --check .
isort --check-only .
flake8 .
```

## Security Scanning with Trivy

### 1. Local Installation

```bash
# On your development machine
wget https://github.com/aquasecurity/trivy/releases/download/v0.46.0/trivy_0.46.0_Linux-64bit.tar.gz
tar zxvf trivy_0.46.0_Linux-64bit.tar.gz
sudo mv trivy /usr/local/bin/
```

### 2. Scan Docker Images Locally

```bash
# Build image
docker build -t subsora/backend:test ./backend

# Scan for vulnerabilities
trivy image --severity HIGH,CRITICAL subsora/backend:test

# Get detailed report
trivy image --format json --output report.json subsora/backend:test
```

### 3. Scan Repository Code

```bash
# Scan entire repository for misconfigurations
trivy config .

# Scan with custom severity
trivy config --severity HIGH,CRITICAL .
```

## Drone CI Integration

The pipeline automatically runs:

1. **check-changes** - Skip if no relevant changes
2. **lint** - Code style validation
3. **unit-tests** - Pytest with coverage (Python only)
4. **build-push** - Docker image build & push
5. **scan-vulnerabilities** - Trivy scanning
6. **deploy-webhook** - Trigger production deployment

### Failure Conditions

Pipeline fails (blocks deployment) if:
- ❌ Linting fails (black, isort, flake8)
- ❌ Tests fail or don't meet coverage
- ❌ Trivy finds HIGH or CRITICAL vulnerabilities
- ❌ Docker build fails

## CI/CD Best Practices

### 1. Coverage Requirements

For backend component, require minimum coverage:

```bash
# Run with coverage threshold
pytest tests/ --cov=app --cov-report=term-missing --cov-fail-under=80
```

### 2. Type Checking (Optional but Recommended)

Add mypy to Python components:

```bash
pip install mypy
mypy app/ --strict --ignore-missing-imports
```

### 3. Security Scanning

Beyond Trivy, consider:
- **bandit**: Python security issues
- **safety**: Known vulnerabilities in dependencies

```bash
pip install bandit safety
bandit -r app/
safety check
```

### 4. Dependency Scanning

```bash
# Check for outdated packages
pip list --outdated

# In Docker, use:
trivy image --severity HIGH trivy/trivy
```

## Local Development Workflow

### Daily Workflow

```bash
# Before committing
cd backend
black .
isort .
flake8 .
pytest tests/ -v

# Or use pre-commit hook (one-liner for all)
pre-commit run --all-files
```

### After Pull (Before Work)

```bash
# Frontend
cd frontend
npm install
npm run lint

# Backend
cd backend
pip install -r requirements.txt
pytest tests/
```

### Before Pushing

```bash
# Run full quality check
git push origin feature-branch
# Drone will run full pipeline automatically
```

## Troubleshooting

### "pytest: command not found"

```bash
# Install test dependencies
cd backend
pip install pytest pytest-cov
```

### "black: No such file or directory"

```bash
# Install dev dependencies
pip install black isort flake8
```

### Trivy image scanning timeout

```bash
# Skip cache
trivy image --skip-db-update subsora/backend:test

# Use minimal database
trivy image --severity CRITICAL subsora/backend:test
```

### Pipeline passes locally but fails in CI

Common causes:
- Python version mismatch (check Drone image version)
- Missing environment variables
- Transient network issues (re-run pipeline)
- Cache issues (clear Docker layer cache)

## Next Steps

1. ✅ Add linting configuration to each component
2. ✅ Test locally: `npm run lint` / `pytest` / `black --check`
3. ✅ Update Drone pipeline (already done in `.drone.yml`)
4. ✅ Test pipeline with a feature branch
5. ✅ Monitor first deployments in dev environment
6. ✅ Roll out to production after successful dev testing
