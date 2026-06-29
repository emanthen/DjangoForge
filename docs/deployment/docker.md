# Docker & Docker Compose

DjangoForge ships a production-grade `Dockerfile` and a `docker-compose.yml` for local development. This document explains both.

---

## Dockerfile

Located at the repo root. Multi-stage build:

```dockerfile
# Stage 1: Builder — installs dependencies
FROM python:3.12-slim AS builder
WORKDIR /app
RUN pip install uv
COPY pyproject.toml .
RUN uv pip install --system -r pyproject.toml

# Stage 2: Runtime — lean final image
FROM python:3.12-slim AS runtime
# Create non-root user
RUN groupadd -r django && useradd -r -g django django
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY . .
RUN chown -R django:django /app
USER django
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4"]
```

**Key design decisions:**
- Multi-stage: builder stage installs packages, runtime stage copies only what's needed (smaller image)
- Non-root `django` user (security best practice — containers should not run as root)
- `uv` for fast dependency installation
- `gunicorn` with 2 workers × 4 threads per worker for Fargate's 0.5 vCPU tasks

### Building the image

```bash
docker build -t djangoforge:latest .

# With build args (e.g. for CI)
docker build --build-arg BUILDKIT_INLINE_CACHE=1 -t djangoforge:latest .
```

---

## Docker Compose (development)

`docker-compose.yml` defines all services for local development:

```yaml
services:
  web:        # Django (Gunicorn)
  worker:     # Celery worker
  beat:       # Celery beat (cron)
  flower:     # Celery monitoring UI
  db:         # PostgreSQL 16
  redis:      # Redis 7
```

### Service details

#### `web` (Django)

```yaml
web:
  build: .
  command: python manage.py runserver 0.0.0.0:8000
  ports:
    - "8000:8000"
  volumes:
    - .:/app           # live code reload
  env_file:
    - .env
  depends_on:
    db:
      condition: service_healthy
    redis:
      condition: service_healthy
```

In development, `runserver` is used instead of gunicorn for hot-reload.

#### `worker` (Celery)

```yaml
worker:
  build: .
  command: celery -A config.celery_app worker -l info --concurrency 2
  env_file:
    - .env
  depends_on:
    - redis
    - db
```

#### `beat` (Celery scheduler)

```yaml
beat:
  build: .
  command: celery -A config.celery_app beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
  env_file:
    - .env
  depends_on:
    - redis
    - db
```

#### `db` (PostgreSQL)

```yaml
db:
  image: postgres:16-alpine
  volumes:
    - postgres_data:/var/lib/postgresql/data
  environment:
    POSTGRES_DB: djangoforge
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: postgres
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U postgres"]
    interval: 5s
    timeout: 5s
    retries: 5
```

#### `redis` (Redis)

```yaml
redis:
  image: redis:7-alpine
  volumes:
    - redis_data:/data
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 5s
    timeout: 5s
    retries: 5
```

#### `flower` (Celery monitoring)

```yaml
flower:
  build: .
  command: celery -A config.celery_app flower --port=5555
  ports:
    - "5555:5555"
  env_file:
    - .env
  depends_on:
    - redis
```

---

## Common commands

```bash
# Start all services
docker compose up

# Start in background
docker compose up -d

# Start only specific services
docker compose up db redis

# Rebuild images after dependency changes
docker compose build
docker compose up --build

# View logs
docker compose logs -f web
docker compose logs -f worker

# Run a command in a running container
docker compose exec web python manage.py migrate
docker compose exec web python manage.py shell
docker compose exec db psql -U postgres djangoforge

# Stop all services
docker compose down

# Stop and destroy volumes (reset database)
docker compose down -v

# Scale the web service
docker compose up --scale web=3
```

---

## docker-compose.override.yml

Create this file for local overrides that don't get committed. It merges with `docker-compose.yml` automatically:

```yaml
# docker-compose.override.yml (gitignored)
services:
  web:
    environment:
      - LOG_LEVEL=DEBUG
      - DEBUG_TOOLBAR=True
  worker:
    command: celery -A config.celery_app worker -l debug --concurrency 1

  # Add Mailpit for email testing
  mailpit:
    image: axllent/mailpit
    ports:
      - "8025:8025"   # UI
      - "1025:1025"   # SMTP
```

---

## Health checks

Both `db` and `redis` services have health checks. The `web` service uses `depends_on` with `condition: service_healthy` to wait for them before starting.

The API endpoint `/api/health/` is the ALB health check target in production. It returns:
```json
{"status": "ok", "version": "1.0.0"}
```

---

## Production vs development image

The `Dockerfile` serves both environments. The difference is in the `CMD`:

| Environment | CMD |
|------------|-----|
| Development | `python manage.py runserver 0.0.0.0:8000` |
| Production | `gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --threads 4` |

In production (ECS), the task definition overrides `CMD` with the gunicorn command.

---

## Static files

In production, static files are collected and served from S3 + CloudFront:

```bash
python manage.py collectstatic --no-input
```

This is run as part of the CI/CD deploy pipeline before the new task starts.

In development, `whitenoise` serves static files directly from Django (no S3 needed).

---

## Image size optimization

The multi-stage build keeps the final image small. Check size:

```bash
docker images djangoforge
# REPOSITORY    TAG      SIZE
# djangoforge   latest   ~350MB
```

To reduce further:
- Remove test dependencies from the main `dependencies` list (put in `dev` optional group)
- Add a `.dockerignore` file (already included) to exclude docs, tests, etc. from the build context
