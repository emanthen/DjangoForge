# Local Development Guide

This guide covers daily development workflows, debugging tools, and productivity tips for working on DjangoForge.

---

## Starting services

```bash
# Start everything
docker compose up

# Start only what you need (faster startup)
docker compose up db redis

# Run Django outside of Docker for faster hot-reload
python manage.py runserver
```

## Rebuilding after dependency changes

When you add a package to `pyproject.toml`, rebuild the image:

```bash
docker compose build web
docker compose up
```

---

## Database

### Create a migration

```bash
# After changing a model
python manage.py makemigrations
python manage.py migrate
```

### Reset the database

```bash
docker compose down -v          # destroys the postgres volume
docker compose up db -d         # start fresh db
python manage.py migrate
python manage.py seed_data
```

### Connect to PostgreSQL directly

```bash
docker compose exec db psql -U postgres djangoforge
```

### Django shell

```bash
python manage.py shell_plus     # auto-imports all models (if django-extensions installed)
python manage.py shell          # standard Django shell
```

---

## Running tests

```bash
# All tests
pytest

# Specific app
pytest apps/accounts/

# Specific file
pytest apps/accounts/tests/test_signup.py

# With coverage
pytest --cov=apps --cov-report=html
open htmlcov/index.html

# Stop on first failure
pytest -x

# Show print statements
pytest -s
```

### Testing with a real database

Tests use a dedicated test database (`djangoforge_test` by default, configured in `config/settings/testing.py`). The `--reuse-db` flag keeps the schema between runs for speed — drop it when migrations change:

```bash
pytest --create-db
```

---

## Celery workers

```bash
# Worker (processes tasks)
celery -A config.celery_app worker -l info

# Beat (sends scheduled tasks)
celery -A config.celery_app beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

# Both in one process (dev only — don't do this in production)
celery -A config.celery_app worker -B -l info

# Flower dashboard (http://localhost:5555)
celery -A config.celery_app flower
```

### Run a task manually in the shell

```python
from apps.billing.tasks import sync_stripe_subscriptions
sync_stripe_subscriptions.delay()
```

---

## Code quality

### Linting and formatting

```bash
# Format code
ruff format .

# Lint (auto-fix)
ruff check . --fix

# Lint only (CI-style — no fix)
ruff check .

# Security scan
bandit -r apps/ -ll

# CVE check on dependencies
safety check
```

### Pre-commit hooks

Install hooks to run checks automatically before every commit:

```bash
pip install pre-commit
pre-commit install
```

Run manually on all files:

```bash
pre-commit run --all-files
```

---

## Django Admin

Access at `http://localhost:8000/admin/` with a superuser account.

Create a superuser:

```bash
python manage.py createsuperuser
```

All models are registered in their app's `admin.py` with search, filtering, and list display configured.

---

## Django Debug Toolbar

Installed in development automatically. Appears as a panel on the right side of all HTML pages.

Shows:
- SQL queries (count + time)
- Cache operations
- Template rendering
- Request/response headers

To disable temporarily:

```bash
DEBUG_TOOLBAR=False python manage.py runserver
```

---

## Stripe webhooks in development

Stripe can't reach `localhost` directly. Use the Stripe CLI to forward events:

```bash
# Install Stripe CLI: https://stripe.com/docs/stripe-cli
stripe login
stripe listen --forward-to localhost:8000/billing/webhook/
```

The CLI prints a webhook signing secret — set it in `.env`:

```dotenv
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
```

Then trigger test events:

```bash
stripe trigger payment_intent.succeeded
stripe trigger invoice.payment_failed
stripe trigger customer.subscription.deleted
```

---

## Email in development

By default, emails are printed to the console where `runserver` is running. Look for the `--- EMAIL ---` separator.

To use a real email inbox in development, use [Mailpit](https://mailpit.axllent.org/):

```bash
# Add to docker-compose.override.yml
services:
  mailpit:
    image: axllent/mailpit
    ports:
      - "8025:8025"
      - "1025:1025"
```

```dotenv
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=localhost
EMAIL_PORT=1025
```

Open `http://localhost:8025` to see all sent emails.

---

## Environment-specific settings

Create a `docker-compose.override.yml` for personal overrides that don't get committed:

```yaml
services:
  web:
    environment:
      - LOG_LEVEL=DEBUG
      - DJANGO_SETTINGS_MODULE=config.settings.development
    volumes:
      - .:/app  # live code reload
```

---

## Useful management commands

| Command | Description |
|---------|-------------|
| `python manage.py seed_data` | Create demo data |
| `python manage.py check_deployment` | Pre-flight production checks |
| `python manage.py migrate` | Apply migrations |
| `python manage.py makemigrations` | Create migrations after model changes |
| `python manage.py createsuperuser` | Create admin user |
| `python manage.py collectstatic` | Gather static files |
| `python manage.py shell` | Interactive Django shell |
| `python manage.py dbshell` | PostgreSQL shell |
| `python manage.py showmigrations` | List migration status |
| `python manage.py diffsettings` | Show settings that differ from defaults |
