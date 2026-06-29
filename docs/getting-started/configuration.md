# Configuration Reference

All configuration is done via environment variables. Copy `.env.example` to `.env` and fill in the values.

DjangoForge uses three settings modules:

| Module | When used |
|--------|-----------|
| `config.settings.base` | Shared settings (all environments) |
| `config.settings.development` | Local development (`DEBUG=True`) |
| `config.settings.production` | Production (`DEBUG=False`, full security headers) |
| `config.settings.testing` | pytest runs |

Set `DJANGO_SETTINGS_MODULE` in your environment to select a module. Docker Compose sets this automatically.

---

## Core Django

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | **Yes** | — | Django secret key. Must be ≥50 chars, random. |
| `DEBUG` | No | `False` | Set to `True` for development only. |
| `ALLOWED_HOSTS` | **Prod** | `localhost` | Comma-separated list of allowed hostnames. |
| `DJANGO_SETTINGS_MODULE` | No | `config.settings.development` | Settings module to load. |
| `TIME_ZONE` | No | `UTC` | Django timezone (e.g. `America/New_York`). |

---

## Database

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | **Yes** | — | PostgreSQL connection string. Format: `postgres://user:pass@host:5432/dbname` |
| `DB_CONN_MAX_AGE` | No | `60` | Connection pool lifetime in seconds. |
| `DB_SSL_REQUIRE` | No | `False` | Set to `True` on RDS to enforce SSL. |

---

## Redis / Cache / Celery

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REDIS_URL` | **Yes** | — | Redis connection string. Format: `redis://host:6379/0` |
| `CELERY_BROKER_URL` | No | Same as `REDIS_URL` | Override broker if different from cache. |
| `CELERY_RESULT_BACKEND` | No | Same as `REDIS_URL` | Override result backend if different. |
| `CACHE_TIMEOUT` | No | `300` | Default cache timeout in seconds. |

---

## Email

DjangoForge uses [django-anymail](https://anymail.dev/) with Mailgun by default.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EMAIL_BACKEND` | No | `anymail.backends.mailgun.EmailBackend` | Override to use a different backend. |
| `ANYMAIL_MAILGUN_API_KEY` | **Prod** | — | Mailgun private API key. |
| `ANYMAIL_MAILGUN_SENDER_DOMAIN` | **Prod** | — | Your Mailgun sending domain. |
| `DEFAULT_FROM_EMAIL` | No | `hello@djangoforge.dev` | Default sender address. |
| `SERVER_EMAIL` | No | `errors@djangoforge.dev` | Address for admin error emails. |

> In development, emails are printed to the console by default (`EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`).

**Switching to SendGrid:**
```dotenv
EMAIL_BACKEND=anymail.backends.sendgrid.EmailBackend
ANYMAIL_SENDGRID_API_KEY=SG.xxxxxx
```

**Switching to SES:**
```dotenv
EMAIL_BACKEND=anymail.backends.amazon_ses.EmailBackend
```
(Uses IAM role — no key needed if running on EC2/ECS with the right role.)

---

## Stripe Billing

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `STRIPE_PUBLIC_KEY` | **Billing** | — | Publishable key (`pk_live_...` or `pk_test_...`) |
| `STRIPE_SECRET_KEY` | **Billing** | — | Secret key (`sk_live_...` or `sk_test_...`) |
| `STRIPE_WEBHOOK_SECRET` | **Billing** | — | Webhook signing secret (`whsec_...`) from Stripe dashboard |
| `STRIPE_LIVE_MODE` | No | `False` | Set to `True` in production. Guards against using test keys in prod. |

> Billing features are disabled if `STRIPE_SECRET_KEY` is empty. You can run DjangoForge without Stripe for non-SaaS use cases.

---

## Authentication & OAuth

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_OAUTH_CLIENT_ID` | OAuth | — | Google Cloud Console OAuth 2.0 client ID |
| `GOOGLE_OAUTH_CLIENT_SECRET` | OAuth | — | Google OAuth client secret |
| `GITHUB_OAUTH_CLIENT_ID` | OAuth | — | GitHub OAuth App client ID |
| `GITHUB_OAUTH_CLIENT_SECRET` | OAuth | — | GitHub OAuth App client secret |

> OAuth providers are disabled if their keys are not set. Social login buttons are hidden automatically.

---

## Error Tracking

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SENTRY_DSN` | **Prod** | — | Sentry DSN. Error tracking is disabled if empty. |
| `SENTRY_ENVIRONMENT` | No | `production` | Environment tag (e.g. `staging`, `production`). |
| `SENTRY_TRACES_SAMPLE_RATE` | No | `0.1` | Transaction sample rate (0.0–1.0). |

---

## File Storage

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AWS_ACCESS_KEY_ID` | **Prod** | — | AWS IAM key with S3 access. |
| `AWS_SECRET_ACCESS_KEY` | **Prod** | — | AWS IAM secret. |
| `AWS_STORAGE_BUCKET_NAME` | **Prod** | — | S3 bucket for user-uploaded files. |
| `AWS_S3_REGION_NAME` | No | `us-east-1` | S3 bucket region. |
| `AWS_S3_CUSTOM_DOMAIN` | No | — | CloudFront distribution domain for serving files. |

> In development, files are served from `MEDIA_ROOT` (local disk).

---

## Security

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECURE_SSL_REDIRECT` | **Prod** | `True` | Redirect HTTP → HTTPS. Set `False` behind a terminating load balancer if the LB handles redirects. |
| `SESSION_COOKIE_SECURE` | **Prod** | `True` | HTTPS-only session cookies. |
| `CSRF_COOKIE_SECURE` | **Prod** | `True` | HTTPS-only CSRF cookies. |
| `AXES_FAILURE_LIMIT` | No | `5` | Login attempts before lockout. |
| `AXES_COOLOFF_TIME` | No | `1` | Lockout duration in hours. |

---

## Logging

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LOG_LEVEL` | No | `INFO` | Root log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `LOG_FORMAT` | No | `json` | Set to `plain` for human-readable local logs. |

---

## Full `.env.example`

```dotenv
# Django
SECRET_KEY=change-me-to-a-50-char-random-string
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=config.settings.development
TIME_ZONE=UTC

# Database
DATABASE_URL=postgres://postgres:postgres@db:5432/djangoforge

# Redis
REDIS_URL=redis://redis:6379/0

# Email (console in dev)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=hello@djangoforge.dev

# Stripe (leave blank to disable billing)
STRIPE_PUBLIC_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_LIVE_MODE=False

# OAuth (leave blank to disable social login)
GOOGLE_OAUTH_CLIENT_ID=
GOOGLE_OAUTH_CLIENT_SECRET=
GITHUB_OAUTH_CLIENT_ID=
GITHUB_OAUTH_CLIENT_SECRET=

# Sentry (leave blank to disable)
SENTRY_DSN=

# AWS S3 (leave blank for local storage)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=us-east-1

# Security (False in dev, True in prod)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```
