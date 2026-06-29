# Environment Variables Reference

Quick reference for all environment variables. For full explanations, see [Configuration](../getting-started/configuration.md).

---

## Required in all environments

| Variable | Example |
|----------|---------|
| `SECRET_KEY` | `change-me-to-a-50-char-random-string` |
| `DATABASE_URL` | `postgres://postgres:postgres@db:5432/djangoforge` |
| `REDIS_URL` | `redis://redis:6379/0` |

---

## Required in production

| Variable | Example |
|----------|---------|
| `ALLOWED_HOSTS` | `yourdomain.com,www.yourdomain.com` |
| `ANYMAIL_MAILGUN_API_KEY` | `key-xxxxxxxxxxxxxxxx` |
| `ANYMAIL_MAILGUN_SENDER_DOMAIN` | `mail.yourdomain.com` |
| `STRIPE_PUBLIC_KEY` | `pk_live_xxxxxxxx` |
| `STRIPE_SECRET_KEY` | `sk_live_xxxxxxxx` |
| `STRIPE_WEBHOOK_SECRET` | `whsec_xxxxxxxx` |
| `STRIPE_LIVE_MODE` | `True` |
| `SENTRY_DSN` | `https://xxx@xxx.ingest.sentry.io/xxx` |
| `AWS_ACCESS_KEY_ID` | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `AWS_STORAGE_BUCKET_NAME` | `my-djangoforge-media` |

---

## Optional (have defaults)

| Variable | Default | Options |
|----------|---------|---------|
| `DEBUG` | `False` | `True` / `False` |
| `DJANGO_SETTINGS_MODULE` | `config.settings.development` | `...production` / `...testing` |
| `TIME_ZONE` | `UTC` | Any valid TZ (e.g. `America/New_York`) |
| `DB_CONN_MAX_AGE` | `60` | Integer seconds |
| `CACHE_TIMEOUT` | `300` | Integer seconds |
| `LOG_LEVEL` | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `AXES_FAILURE_LIMIT` | `5` | Integer |
| `AXES_COOLOFF_TIME` | `1` | Hours (float) |
| `DEFAULT_FROM_EMAIL` | `hello@djangoforge.dev` | Email address |
| `AWS_S3_REGION_NAME` | `us-east-1` | AWS region |
| `SENTRY_TRACES_SAMPLE_RATE` | `0.1` | Float 0.0–1.0 |

---

## OAuth (optional — omit to disable social login)

| Variable | Where to get it |
|----------|----------------|
| `GOOGLE_OAUTH_CLIENT_ID` | [console.cloud.google.com](https://console.cloud.google.com/) |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Google Cloud Console |
| `GITHUB_OAUTH_CLIENT_ID` | [github.com/settings/apps](https://github.com/settings/apps) |
| `GITHUB_OAUTH_CLIENT_SECRET` | GitHub Developer Settings |

---

## Security flags (production)

| Variable | Production value |
|----------|-----------------|
| `SECURE_SSL_REDIRECT` | `True` |
| `SESSION_COOKIE_SECURE` | `True` |
| `CSRF_COOKIE_SECURE` | `True` |
| `DB_SSL_REQUIRE` | `True` |

---

## Generating a SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Or with OpenSSL:

```bash
openssl rand -base64 50
```

---

## AWS Secrets Manager (production)

In production, secrets are loaded from AWS Secrets Manager via the ECS task role. The Terraform module creates a secret at `djangoforge/production/app` with all required keys as JSON:

```json
{
  "SECRET_KEY": "...",
  "DATABASE_URL": "postgres://...",
  "REDIS_URL": "redis://...",
  "STRIPE_SECRET_KEY": "sk_live_...",
  "STRIPE_WEBHOOK_SECRET": "whsec_...",
  "ANYMAIL_MAILGUN_API_KEY": "key-...",
  "SENTRY_DSN": "https://..."
}
```

Update the secret:

```bash
aws secretsmanager update-secret \
  --secret-id djangoforge/production/app \
  --secret-string file://secrets.json
```
