# Contributing to DjangoForge

Thank you for taking the time to contribute! DjangoForge is built in the open, and every contribution matters — whether it's a bug report, a new feature, a doc fix, or a test.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Ways to Contribute](#ways-to-contribute)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Commit Messages](#commit-messages)

---

## Code of Conduct

This project follows our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold these standards. Please report unacceptable behavior to the maintainers.

---

## Ways to Contribute

| Type | How |
|------|-----|
| 🐛 Bug report | Open a [GitHub Issue](https://github.com/emanthen/djangoforge/issues) using the bug template |
| 💡 Feature request | Start a [GitHub Discussion](https://github.com/emanthen/djangoforge/discussions) first |
| 📝 Documentation | Edit Markdown files and submit a PR |
| ✅ Tests | Add/improve test coverage for any app |
| 🔧 Code | Fork → branch → PR (see below) |
| 🌍 Translation | Not yet scoped — open a discussion |

---

## Development Setup

### With Docker (recommended)

```bash
# 1. Fork and clone
git clone https://github.com/<your-username>/djangoforge
cd djangoforge

# 2. Set up environment
cp .env.example .env        # Fill in required values

# 3. Start all services
docker compose up -d

# 4. Run migrations + seed data
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_data

# 5. Visit http://localhost:8000
# Login: alice@example.com / demo123
```

### Without Docker

```bash
# Requires: Python 3.12+, PostgreSQL 16, Redis 7

# Install uv package manager
pip install uv

# Install dependencies
uv sync --all-extras

# Configure
cp .env.example .env
export DJANGO_SETTINGS_MODULE=config.settings.local

# Set up database
createdb djangoforge
uv run python manage.py migrate

# Start dev server
uv run python manage.py runserver

# Start Celery worker (separate terminal)
uv run celery -A config.celery worker --loglevel=info
```

### Pre-commit hooks

```bash
uv run pre-commit install
```

This installs `ruff` (format + lint) and `detect-secrets` checks that run on every commit.

---

## Code Style

- **Formatter & linter**: [`ruff`](https://docs.astral.sh/ruff/) — zero config, enforced in CI
- **Python version**: 3.12+, no `from __future__ import annotations` needed
- **Line length**: 100 characters (configured in `pyproject.toml`)
- **Imports**: isort-compatible, enforced by ruff
- **Django**: follow the [Django coding style](https://docs.djangoproject.com/en/5.2/internals/contributing/writing-code/coding-style/)

```bash
# Format and lint
uv run ruff format .
uv run ruff check . --fix

# Or use make (if available)
make lint
```

---

## Testing

Tests live in `tests/` and use `pytest` + `pytest-django` + `factory-boy`.

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=apps --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_accounts.py -v

# Run specific test
uv run pytest tests/test_accounts.py::TestSignup::test_signup_creates_user -v
```

**Rules:**
- Coverage must stay ≥ **70%** — PRs that drop coverage below this threshold will not be merged
- New features require corresponding tests
- Use `factories.py` for test fixtures — do not create raw model instances in tests
- Tests must pass with `DJANGO_SETTINGS_MODULE=config.settings.testing`

---

## Pull Request Process

1. **Fork** the repository and create a branch from `main`:
   ```bash
   git checkout -b feat/my-awesome-feature
   # or
   git checkout -b fix/broken-login-redirect
   ```

2. **Write your code** — keep changes focused. One PR = one concern.

3. **Write tests** for any new behavior.

4. **Run checks locally**:
   ```bash
   uv run ruff check .
   uv run ruff format --check .
   uv run pytest
   ```

5. **Update `CHANGELOG.md`** under `[Unreleased]` with a brief description.

6. **Submit a PR** against the `main` branch with:
   - A clear title (see commit messages below)
   - Description of what changed and why
   - Screenshots for UI changes
   - Reference to the related issue (if any): `Fixes #123`

7. **Address review feedback** — we aim to review within 48–72 hours.

**Merge criteria:**
- ✅ CI passes (tests, lint, Bandit SAST, Safety CVE check)
- ✅ Coverage ≥ 70%
- ✅ At least 1 maintainer approval
- ✅ `CHANGELOG.md` updated

---

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<optional scope>): <short description>

[optional body]

[optional footer: Fixes #123]
```

| Type | When to use |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting (no logic change) |
| `refactor` | Code restructure (no behavior change) |
| `test` | Adding or updating tests |
| `chore` | Build, deps, tooling |
| `ci` | CI/CD pipeline changes |

**Examples:**
```bash
feat(billing): add annual pricing toggle with 20% discount
fix(accounts): correct redirect namespace dashboard:index → accounts:dashboard
docs(readme): add comparison table vs alternatives
chore: upgrade Django to 5.2.1
test(organizations): add invitation expiry edge case tests
```

---

## Questions?

Open a [GitHub Discussion](https://github.com/emanthen/djangoforge/discussions) — we're happy to help!
