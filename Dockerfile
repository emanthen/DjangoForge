# Stage 1: builder
FROM python:3.12-slim AS builder

RUN pip install uv

WORKDIR /app

COPY pyproject.toml .
RUN uv sync --no-dev

# Stage 2: runtime
FROM python:3.12-slim AS runtime

RUN addgroup --system django && adduser --system --group django

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

COPY . .

RUN mkdir -p staticfiles mediafiles && chown -R django:django /app

USER django

EXPOSE 8000

ENTRYPOINT ["sh", "-c", "python manage.py collectstatic --no-input && exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 60 --access-logfile -"]
