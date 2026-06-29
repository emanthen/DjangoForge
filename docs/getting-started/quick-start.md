# Quick Start

Get DjangoForge running locally in under 5 minutes using Docker Compose.

## Prerequisites

| Tool | Minimum Version | Install |
|------|----------------|---------|
| Docker | 24.x | [docs.docker.com](https://docs.docker.com/get-docker/) |
| Docker Compose | 2.x | Bundled with Docker Desktop |
| Git | any | [git-scm.com](https://git-scm.com/) |

> **No Python required locally.** Everything runs inside containers.

---

## 1. Clone the repo

```bash
git clone https://github.com/emanthen/djangoforge.git
cd djangoforge
```

## 2. Create your `.env` file

```bash
cp .env.example .env
```

Open `.env` and set at minimum:

```dotenv
SECRET_KEY=change-me-to-a-50-char-random-string
DATABASE_URL=postgres://postgres:postgres@db:5432/djangoforge
REDIS_URL=redis://redis:6379/0

# Leave Stripe keys blank for now — billing is disabled without them
STRIPE_PUBLIC_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
```

> Generate a secret key: `python -c "import secrets; print(secrets.token_urlsafe(50))"`

## 3. Start all services

```bash
docker compose up --build
```

First run takes ~90 seconds while images are built. You'll see logs from:
- `web` — Django / Gunicorn
- `worker` — Celery worker
- `beat` — Celery beat (cron scheduler)
- `flower` — Celery monitoring
- `db` — PostgreSQL 16
- `redis` — Redis 7

## 4. Run migrations & seed data

Open a second terminal:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_data
```

`seed_data` creates demo users, an organization, and sample data.

## 5. Open the app

| URL | What it is |
|-----|-----------|
| `http://localhost:8000` | Main app |
| `http://localhost:8000/admin/` | Django admin |
| `http://localhost:5555` | Flower (Celery monitor) |
| `http://localhost:8000/api/docs/` | Swagger UI |

## 6. Demo credentials

| Email | Password | Role |
|-------|----------|------|
| `admin@example.com` | `admin123!` | Superuser + org owner |
| `member@example.com` | `member123!` | Org member |
| `billing@example.com` | `billing123!` | Billing admin |

---

## Without Docker (uv + local services)

If you prefer a native setup with PostgreSQL and Redis installed locally:

```bash
# Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtualenv + install deps
uv venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Point .env to local services
DATABASE_URL=postgres://postgres:postgres@localhost:5432/djangoforge
REDIS_URL=redis://localhost:6379/0

# Create database
createdb djangoforge

# Run
python manage.py migrate
python manage.py seed_data
python manage.py runserver

# In separate terminals:
celery -A config.celery_app worker -l info
celery -A config.celery_app beat -l info
```

---

## Next steps

- [Configuration reference](./configuration.md) — all `.env` variables explained
- [Local development guide](./local-development.md) — hot reload, debugging, tips
- [Architecture overview](../architecture/overview.md) — understand the codebase
