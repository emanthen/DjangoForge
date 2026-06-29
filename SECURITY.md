# Security Policy

## Supported Versions

| Version | Supported |
|---------|:---------:|
| latest (`main`) | ✅ |
| < 1.0.0 | ❌ |

We only provide security fixes for the latest release. We encourage all users to stay up-to-date.

---

## Reporting a Vulnerability

**⚠️ Do NOT open a public GitHub Issue for security vulnerabilities.**

Please use one of the following responsible disclosure channels:

1. **GitHub Private Vulnerability Reporting** (preferred) — [Report here](https://github.com/emanthen/djangoforge/security/advisories/new)
2. **Email** — `security@djangoforge.dev` (PGP key available on request)

### What to Include

Please provide as much detail as possible:

- **Description**: What is the vulnerability? What component is affected?
- **Impact**: What could an attacker do? (e.g., RCE, data leak, privilege escalation)
- **Reproduction steps**: Minimal steps to reproduce the issue
- **Environment**: DjangoForge version, Python version, Django version
- **Suggested fix**: If you have one (optional, but appreciated)

### Response SLA

| Stage | Timeframe |
|-------|-----------|
| Acknowledgement | ≤ 48 hours |
| Initial assessment | ≤ 5 business days |
| Fix / mitigation plan | ≤ 7 days |
| Patch release (critical) | ≤ 14 days |
| Patch release (high) | ≤ 30 days |

We follow **responsible disclosure**. If you report a valid vulnerability, we will:
- Credit you in the release notes (with your permission)
- Coordinate a public disclosure after the fix is released

---

## Security Architecture

DjangoForge is designed with security as a first-class concern:

### Authentication & Authorization
- ✅ Custom `User` model with email as the unique identifier (no `username`)
- ✅ Email verification required before first login
- ✅ Brute-force protection via `django-axes` (5 failures → 1h cooldown)
- ✅ `AUTHENTICATION_BACKENDS` explicitly ordered (axes → allauth → modelbackend)
- ✅ Row-level multi-tenancy — `OrgScopedManager` prevents cross-org data access
- ✅ `OrgRequiredMixin`, `OrgAdminMixin`, `OrgOwnerMixin` enforce role-based access

### Session & Cookie Security
- ✅ Sessions backed by Redis (not database or client-side)
- ✅ `SESSION_COOKIE_SECURE = True` in production
- ✅ `SESSION_COOKIE_HTTPONLY = True` (no JavaScript access)
- ✅ `SESSION_COOKIE_SAMESITE = "Lax"` (CSRF protection)
- ✅ `CSRF_COOKIE_SECURE = True` in production

### Transport Security
- ✅ `SECURE_SSL_REDIRECT = True` in production
- ✅ `SECURE_HSTS_SECONDS = 31536000` (1 year)
- ✅ `SECURE_HSTS_INCLUDE_SUBDOMAINS = True`
- ✅ `SECURE_HSTS_PRELOAD = True`
- ✅ `X_FRAME_OPTIONS = "DENY"` (clickjacking protection)
- ✅ `SECURE_CONTENT_TYPE_NOSNIFF = True`
- ✅ `SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"`

### Billing & Webhooks
- ✅ Stripe webhook **signature verification** (`stripe.Webhook.construct_event`)
- ✅ Webhook **deduplication** via `WebhookEvent.get_or_create(stripe_id=...)` — prevents double-processing
- ✅ Stripe keys loaded exclusively from environment variables
- ✅ `STRIPE_LIVE_MODE` flag prevents accidental live key usage

### CSRF Protection
- ✅ Django's built-in CSRF middleware on all forms
- ✅ HTMX requests inject CSRF token via `htmx:configRequest` event listener
- ✅ `@csrf_exempt` used only on the Stripe webhook endpoint (protected by signature verification instead)

### Secrets Management
- ✅ All secrets via environment variables (never hardcoded)
- ✅ `.env` is in `.gitignore` — never committed
- ✅ `detect-secrets` pre-commit hook catches accidental secret commits
- ✅ AWS Secrets Manager integration via Terraform (production)
- ✅ `Bandit` SAST scanning in CI catches common Python security mistakes
- ✅ `Safety` CVE scanning for known vulnerabilities in dependencies

### Data Protection
- ✅ Passwords hashed with Argon2 (configured in production settings)
- ✅ Account deletion anonymizes email to `deleted+{id}@djangoforge.dev` (GDPR-friendly)
- ✅ Audit log records all sensitive actions with actor, org, IP, and user agent

---

## Pre-Deployment Security Checklist

Before going live, verify the following:

```bash
# Django's built-in security check
python manage.py check --deploy
```

- [ ] `DEBUG = False`
- [ ] `SECRET_KEY` is at least 50 chars, random, loaded from env
- [ ] `ALLOWED_HOSTS` is restricted to your domain(s)
- [ ] `STRIPE_WEBHOOK_SECRET` is set (the `whsec_...` value from Stripe dashboard)
- [ ] `STRIPE_LIVE_MODE = True` with production keys (not test keys)
- [ ] Database is NOT publicly accessible (private subnet in production)
- [ ] Redis is NOT publicly accessible
- [ ] `ANYMAIL_*` keys are set for transactional email
- [ ] `SENTRY_DSN` is set for error tracking
- [ ] HTTPS is enforced (ALB → redirect HTTP → HTTPS)
- [ ] Security group rules limit inbound to ALB only (no direct access to containers)
