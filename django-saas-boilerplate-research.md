# Django SaaS Boilerplate — Full Deep Research Document
> Version 1.0 · June 2026 · Built for: Prabhat (Backend & Cloud Engineer, Nepal)
> Purpose: Build, open-source, and grow GitHub stars via Reddit promotion

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Market Landscape — Every Competitor Mapped](#2-market-landscape--every-competitor-mapped)
3. [What Every Competitor is Missing](#3-what-every-competitor-is-missing)
4. [Current Market Problems Developers Are Facing](#4-current-market-problems-developers-are-facing)
5. [Full Feature Specification](#5-full-feature-specification)
6. [Security — Complete Checklist](#6-security--complete-checklist)
7. [MIT License — Everything You Need to Know](#7-mit-license--everything-you-need-to-know)
8. [Documentation Structure — Every File Required](#8-documentation-structure--every-file-required)
9. [Project Repository Structure](#9-project-repository-structure)
10. [Tech Stack Decision Matrix](#10-tech-stack-decision-matrix)
11. [GitHub Star Growth Strategy](#11-github-star-growth-strategy)
12. [Reddit Promotion Playbook](#12-reddit-promotion-playbook)
13. [Launch Timeline — Week by Week](#13-launch-timeline--week-by-week)
14. [Naming & Positioning](#14-naming--positioning)
15. [Honest Risk Assessment](#15-honest-risk-assessment)

---

## 1. Executive Summary

**The gap is real and nobody owns it yet.**

No open-source Django boilerplate above 3,000 stars ships the complete modern stack:
Stripe billing + multi-tenancy + Celery + AWS ECS Fargate IaC + GitHub Actions CI/CD — all in one working, clone-and-deploy repo.

The closest competitor (apptension/saas-boilerplate) has everything but is React + GraphQL + AWS CDK heavy — not "pure Django," and notoriously hard to set up. The most-starred option (cookiecutter-django at 13,500+) deliberately omits billing and multi-tenancy.

**Your unfair advantage:** You've already built this exact stack for KibaPay. You're not guessing — you're extracting from a real production system and generalizing it. That's the story. That's the Reddit post.

**Star ceiling estimate:** 500–2,000 stars in year 1 is realistic for a well-executed launch. The FastAPI equivalent (full-stack-fastapi-template) hit 43,000+ stars — the ceiling for a polished Django equivalent is high.

---

## 2. Market Landscape — Every Competitor Mapped

### 2.1 Open Source — Active

| Repo | Stars (Jun 2026) | License | Stack | Stripe | Multi-tenant | Celery | AWS ECS | CI/CD | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| cookiecutter/cookiecutter-django | ~13,500 | BSD-3 | Django + Traefik | ❌ | ❌ | ✅ optional | ❌ | ✅ GH Actions | Missing billing, tenancy, cloud-native deploy |
| apptension/saas-boilerplate | ~2,900 | MIT | Django + React + GraphQL + AWS CDK | ✅ | ✅ | ✅ | ✅ CDK | ✅ | Overkill, JS-heavy, complex setup |
| PaulleDemon/Django-SAAS-Boilerplate | ~290 | MIT | Django + Tailwind + Firebase | ✅ (basic) | ❌ | ❌ | ❌ | ❌ | No Celery, no cloud deploy, Firebase dep |
| ernestofgonzalez/djangorocket | ~203 | MIT | Django + Tailwind | ✅ | ❌ | ❌ | ❌ | partial | Solo dev, infrequently updated |
| roperi/YaSaas | ~125 | MIT | Django + DRF + React | ✅ | ❌ | ❌ | ❌ | ❌ | Abandoned look, no tests |
| eriktaveras/django-saas-boilerplate | ~113 | MIT | Django + HTMX | ✅ | ❌ (paid) | ❌ | ❌ | ✅ | Multi-tenancy is paywalled |
| testdrivenio/django-ecs-terraform | ~900 | MIT | Django + ECS + Terraform | ❌ | ❌ | ❌ | ✅ | ❌ | Deploy only, no SaaS features |
| briancaffey/terraform-aws-django | ~400 | MIT | Terraform modules only | ❌ | ❌ | ❌ | ✅ | ❌ | Infra only, no app code |

### 2.2 Paid / Closed Source (your real competition for mindshare)

| Product | Price | Stack | Key features | What's missing |
|---|---|---|---|---|
| SaaS Pegasus | $249–$999 | Django + React or HTMX + Tailwind | Teams, Stripe, feature flags, 2FA, Celery, Wagtail CMS, AI examples | Closed source, no AWS ECS IaC, Heroku/Render focused |
| Advantch | $199+ | Django + HTMX + AI | AI integration, teams, billing | Closed source |
| Hyper SaaS | $149+ | Django + React 18 + Next.js 14 | TypeScript, Zod, Stripe | Heavy JS, closed source |
| SaaS Hammer | $99+ | Django + Hotwire | Minimal JS, Stripe | Small community, limited docs |

### 2.3 Key Insight from Competitor Analysis

- **cookiecutter-django** is a project scaffolder, not a SaaS boilerplate. It gives you structure, not features.
- **apptension/saas-boilerplate** is the closest to complete but requires: AWS CDK, NX monorepo, React, GraphQL, Node.js. Developers report setup taking 2–4 hours even with docs. Issues show "works on my machine" complaints.
- **Every paid product (Pegasus etc.)** is Heroku/Render/Railway-first. AWS ECS Fargate production setup is explicitly documented by none of them.
- **The test:** Go to GitHub, search `django saas boilerplate aws ecs`. You get scattered blog posts and zero starred repos. That search query is your keyword target.

---

## 3. What Every Competitor is Missing

This is the core of your positioning. These are the gaps that developers are actually complaining about in forums, issues, and Reddit threads:

### 3.1 Missing from ALL open-source options

| Gap | Why it matters |
|---|---|
| **Working AWS ECS Fargate IaC** | Every Django deploy guide uses Heroku or a VPS. ECS Fargate is what teams actually use at scale, and zero boilerplates ship working Terraform for it |
| **Stripe webhooks that are production-safe** | Most billing implementations are tutorials — no idempotency, no signature verification, no retry deduplication |
| **Row-level multi-tenancy that works out of the box** | Boilerplates either skip it or push to `django-tenants` schema approach which is operationally complex |
| **One-command local setup** | Most repos need 5–10 manual steps before `docker compose up` works |
| **Database migrations as a pre-deploy ECS task** | Every AWS deployment guide skips this — people run migrations manually or it breaks on first deploy |
| **Per-seat billing** | All boilerplates do flat subscriptions. B2B SaaS needs per-user pricing |
| **Tenant-scoped Celery tasks** | Background tasks that know which tenant they're running for — nobody ships this |
| **Environment-specific settings done right** | Most split `settings/base.py + local.py + production.py` but leak secrets in templates |
| **GitHub Actions that actually test before deploy** | Most CI/CD examples skip test coverage gates |
| **Structured JSON logging for CloudWatch** | Print-based logging in Docker is useless for production debugging |

### 3.2 Missing from cookiecutter-django specifically

- No Stripe/billing
- No multi-tenancy
- No subscription management
- No SaaS-specific models (Organization, Membership, Plan, Subscription)
- ECS support exists in an old blog post only — not in the template itself
- No usage-based billing support
- No teams/orgs concept

### 3.3 Missing from apptension/saas-boilerplate specifically

- Requires React + GraphQL frontend (no pure-Django option)
- Requires AWS CDK + Node.js even for backend setup
- No Terraform alternative (CDK only)
- NX monorepo adds cognitive overhead for solo/small teams
- Setup takes 2–4 hours (confirmed in GitHub issues)
- Documentation gaps on environment variable management
- No per-seat billing example
- No structured logging to CloudWatch

### 3.4 Missing from all paid options

- **All are closed source** — can't audit, fork, or self-host the boilerplate itself
- **None ship AWS ECS Fargate Terraform** — Pegasus docs mention AWS but point to Heroku/Render
- **None are free** — $249 minimum blocks indie developers and students
- **No built-in cost monitoring** — no budget alarms, no cost tags in IaC

---

## 4. Current Market Problems Developers Are Facing

Based on Django Forum posts, Reddit threads, GitHub issues, and Stack Overflow patterns as of 2025–2026:

### 4.1 The "Rebuild the Same Foundation" Problem
Every Django developer building a SaaS rebuilds auth, billing, multi-tenancy, email, and background tasks from scratch. The average time lost: **80–200 hours** before writing a single line of product logic. This is the exact pain point your boilerplate solves.

### 4.2 Stripe Integration is Broken in Most Tutorials
The #1 complaint in r/django about billing: webhook handlers that break on retry, no idempotency, no Stripe signature verification, and tutorials that use deprecated Stripe APIs. Developers end up with billing bugs they can't reproduce.

### 4.3 Deployment is the Unsolved Last Mile
A Django app works locally. Deploying it to AWS with SSL, migrations, env vars, secrets, auto-scaling, and CI/CD takes a senior DevOps engineer a full week the first time. No boilerplate ships this as working code.

### 4.4 Multi-tenancy Documentation is Terrible
`django-tenants` documentation is dense and schema-based tenancy has sharp edges (missing `public` schema migrations, etc.). Row-level tenancy is simpler but no resource shows a complete, production-hardened implementation.

### 4.5 Security is an Afterthought
Most Django boilerplates ship with `DEBUG=True` in examples, hardcoded `SECRET_KEY` in settings files, no `SECURITY.md`, no rate limiting, and no CSP headers. First-time developers copy these patterns into production.

### 4.6 "It Works on My Machine" Setup Friction
The biggest conversion killer for GitHub stars: a boilerplate that requires 30 minutes of troubleshooting before it runs. Every missing `.env.example` value, every platform-specific Docker issue, every undocumented dependency breaks the first experience.

### 4.7 No Real Testing Examples
Boilerplates ship with minimal or zero tests. Developers then build on an untested foundation and wonder why refactoring is painful. A boilerplate with 80%+ test coverage on its own code is a strong signal of quality.

---

## 5. Full Feature Specification

### 5.1 Authentication & User Management

**Must ship:**
- Custom `CustomUser` model (email as username) — do this from day 1, migrating later is painful
- `django-allauth` for: email/password, Google OAuth, GitHub OAuth
- Email verification (mandatory, with resend endpoint)
- Password reset with secure tokens
- Password change (authenticated)
- 2FA/TOTP via `django-otp` or `allauth.mfa`
- Remember me / session expiry controls
- Login rate limiting via `django-axes` (blocks brute force, uses Redis)
- Account deletion (GDPR requirement)
- Admin impersonation (view account as user, for support) via `django-hijack`

**Settings:**
```python
AUTH_USER_MODEL = 'users.CustomUser'
AUTHENTICATION_BACKENDS = ['allauth.account.auth_backends.AuthenticationBackend']
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_USERNAME_REQUIRED = False
PASSWORD_HASHERS = ['django.contrib.auth.hashers.Argon2PasswordHasher', ...]  # Argon2 first
```

### 5.2 Organizations & Multi-Tenancy

**Architecture choice: Row-level isolation (default), schema-based (documented alternative)**

Row-level (recommended for new projects):
```
Organization → has many Members → has many Subscriptions
Each model with org-scoped data has: organization = FK(Organization)
Middleware sets thread-local current_org from subdomain or request header
All querysets scoped via custom Manager: .get_queryset().filter(org=get_current_org())
```

**Core models:**
- `Organization` — name, slug, created_at, owner
- `OrganizationMembership` — user, org, role (OWNER/ADMIN/MEMBER), invited_by, joined_at
- `Invitation` — email, org, token, expires_at, accepted_at
- Subdomain routing middleware (optional)
- Roles & permissions via `django-guardian` or simple FK role field
- Owner transfer flow
- Member invite via email (Celery task)
- Remove member flow

### 5.3 Stripe Billing (Production-Safe)

**Use `dj-stripe` — do not hand-roll Stripe.**

Plans to support:
- Free tier (no payment method required)
- Monthly/annual flat subscription
- Per-seat subscription (charge × team members)
- One-time payments (lifetime deal)
- Trials (7/14/30 day)
- Coupons/discounts

**Webhook safety checklist (most boilerplates fail this):**
```python
# 1. Always verify Stripe signature
@require_POST
@csrf_exempt
def stripe_webhook(request):
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    try:
        event = stripe.Webhook.construct_event(
            request.body, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

# 2. Idempotency — dedupe by event ID
WebhookEvent.objects.get_or_create(stripe_id=event['id'])

# 3. Return 2xx quickly, process async via Celery
process_stripe_event.delay(event)

# 4. Handle all critical events:
# customer.subscription.created/updated/deleted
# invoice.payment_succeeded/failed
# customer.subscription.trial_will_end
# payment_intent.succeeded
```

**Billing models:**
- `Plan` — name, stripe_price_id, amount, interval, features (JSONField)
- `Subscription` — org, plan, stripe_subscription_id, status, trial_end, current_period_end
- `Invoice` — subscription, stripe_invoice_id, amount, paid_at
- `PaymentMethod` — user/org, stripe_pm_id, last4, brand

### 5.4 Background Tasks (Celery + Redis)

```
Celery broker: Redis
Result backend: Redis
Beat scheduler: django-celery-beat (DB-based schedules)
Monitoring: Flower (in Docker Compose)
```

**Pre-built task examples:**
- `send_trial_ending_email` — scheduled 3 days before trial ends
- `sync_stripe_subscriptions` — periodic reconciliation
- `send_invitation_email`
- `process_stripe_event`
- `cleanup_expired_invitations`
- `generate_monthly_report`

**Tenant-scoped tasks:**
```python
@app.task(bind=True)
def tenant_aware_task(self, org_id, *args, **kwargs):
    org = Organization.objects.get(id=org_id)
    with tenant_context(org):
        # task body runs in org scope
        ...
```

### 5.5 REST API (Django REST Framework)

- `drf-spectacular` for OpenAPI 3.0 schema + Swagger UI + ReDoc
- JWT auth via `djangorestframework-simplejwt`
- API key auth (for server-to-server, use `djangorestframework-api-key`)
- Versioning (`/api/v1/`)
- Throttling: anonymous (100/hour), authenticated (1000/hour)
- Standard error response format
- Pagination (cursor-based for large datasets)
- Example CRUD resource (full test coverage)
- Filters via `django-filter`

### 5.6 Email

- `django-anymail` for provider-agnostic email (Mailgun default, AWS SES, SendGrid switchable via one env var)
- Transactional email templates:
  - Welcome / confirm email
  - Password reset
  - Team invitation
  - Trial ending (3 days notice)
  - Payment failed
  - Subscription cancelled
  - Invoice receipt
- HTML templates with base layout (Tailwind-styled or mjml)
- Email preview in dev (`django-mail-panel` in DEBUG)
- Unsubscribe token support for marketing emails

### 5.7 Feature Flags

```python
# Simple DB-backed flags (no extra service needed)
class FeatureFlag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    enabled_globally = models.BooleanField(default=False)
    enabled_for_orgs = models.ManyToManyField(Organization, blank=True)
    enabled_for_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    rollout_percentage = models.IntegerField(default=0)

# Usage
if flag_is_enabled('new_dashboard', request.user, request.org):
    return render_new_dashboard()
```

Alternative: `django-waffle` (battle-tested, more features).

### 5.8 Admin

- Customized Django admin with `unfold` or `django-jazzmin` theme
- Per-org admin scoping (superadmin sees all, org admin sees only their org)
- Impersonation (view app as a specific user) via `django-hijack`
- Admin actions: cancel subscription, extend trial, reset 2FA
- Audit log for admin actions

### 5.9 Frontend (Django Templates + HTMX)

Default: **Django Templates + HTMX + Alpine.js + Tailwind CSS v4**

Components to ship:
- Base layout with sidebar nav
- Dashboard skeleton (metrics cards, table, chart placeholder)
- Auth pages (login, register, forgot password, 2FA setup)
- Settings pages (profile, password, 2FA, notifications)
- Team management (members table, invite modal, roles)
- Billing page (current plan, usage, upgrade/downgrade, cancel)
- Invoice list

Optional documented path: DRF API + React (separate frontend repo).

### 5.10 Monitoring & Observability

- Sentry error tracking (Django + Celery worker integration)
- Structured JSON logging to stdout (CloudWatch picks this up automatically on ECS)
- Request correlation IDs via middleware
- Health check endpoint (`/health/`) with DB + Redis + Celery checks
- Django Debug Toolbar in development
- Prometheus metrics endpoint (optional, via `django-prometheus`)
- CloudWatch Alarms in Terraform (5xx rate, CPU, memory)

---

## 6. Security — Complete Checklist

### 6.1 Django Settings Security (production.py must have all of these)

```python
# Core
DEBUG = False
SECRET_KEY = env('DJANGO_SECRET_KEY')  # min 50 chars, random, from AWS Secrets Manager
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS')

# HTTPS enforcement
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookie security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS')

# Clickjacking
X_FRAME_OPTIONS = 'DENY'

# Content Security Policy (Django 6.0 has native CSP)
CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ["'self'"],
        "script-src": ["'self'"],
        "style-src": ["'self'", "'unsafe-inline'"],  # adjust for Tailwind
        "img-src": ["'self'", "data:", "https:"],
        "font-src": ["'self'"],
        "connect-src": ["'self'"],
        "frame-ancestors": ["'none'"],
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Session security
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'  # Redis-backed
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 1209600  # 2 weeks

# File uploads
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880

# Database
CONN_MAX_AGE = 60  # persistent connections
```

### 6.2 OWASP Top 10 Coverage

| OWASP Risk | Django built-in | Your boilerplate adds |
|---|---|---|
| A01: Broken Access Control | `@login_required`, permissions | Per-org queryset scoping, role checks |
| A02: Cryptographic Failures | Argon2 hashing, HTTPS settings | Encrypt sensitive fields (`django-encrypted-model-fields`) |
| A03: Injection | ORM parameterized queries | Audit all `raw()` and `extra()` usage — add CI check |
| A04: Insecure Design | — | Threat model doc, row-level isolation architecture |
| A05: Security Misconfiguration | `check --deploy` | Settings audit in CI, no hardcoded secrets check |
| A06: Vulnerable Components | — | Dependabot enabled, `pip-audit` in CI |
| A07: Auth Failures | Sessions, CSRF | django-axes brute force protection, 2FA, Argon2 |
| A08: Integrity Failures | — | Stripe webhook signature verification |
| A09: Logging Failures | — | Structured logging, correlation IDs, Sentry |
| A10: SSRF | — | Validate all outbound URL inputs, allowlist |

### 6.3 Rate Limiting

```python
# Via django-ratelimit (OWASP recommended)
@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def login_view(request): ...

@ratelimit(key='user', rate='100/h', method='POST', block=True)
def api_endpoint(request): ...

# Via DRF throttling
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    }
}
```

Additionally use `django-axes` for login attempt tracking (stored in Redis for performance).

### 6.4 Secrets Management

**Never commit secrets. Ever.**

Pattern used in this boilerplate:
```
Local dev:   .env file (gitignored) + django-environ
Staging/Prod: AWS Secrets Manager → injected as env vars at ECS task startup
CI/CD:       GitHub Actions secrets → passed as --build-arg or env vars
```

`.env.example` ships with every required variable documented and with safe placeholder values. A pre-commit hook (`detect-secrets` or `gitleaks`) blocks accidental commits of real secrets.

### 6.5 Dependency Auditing

```yaml
# .github/workflows/security.yml
- name: Audit Python deps
  run: pip-audit --requirement requirements/base.txt

- name: Bandit SAST scan
  run: bandit -r . -ll

- name: Check for hardcoded secrets
  run: gitleaks detect --source . --verbose
```

Plus: **Dependabot enabled** in `.github/dependabot.yml` for both Python and GitHub Actions dependencies.

### 6.6 Docker Security

```dockerfile
# Production Dockerfile best practices
FROM python:3.12-slim AS builder
# ... build stage ...

FROM python:3.12-slim AS production
# Run as non-root user
RUN addgroup --system django && adduser --system --group django
USER django

# No secrets in image — use env vars at runtime
# Minimal image — no dev tools
# Read-only filesystem where possible
```

### 6.7 AWS Security (Terraform)

- ECS tasks run with minimal IAM task role (only what's needed)
- RDS in private subnets, no public endpoint
- ElastiCache in private subnets
- Security groups: ECS can reach RDS, ElastiCache; ALB is public-facing only
- Secrets in AWS Secrets Manager (not environment variables hardcoded in task def)
- S3 bucket: public access block enabled, server-side encryption (AES-256)
- CloudTrail enabled for audit logging
- VPC Flow Logs for network monitoring
- ALB access logs to S3

### 6.8 SECURITY.md Content

Every repository MUST have `SECURITY.md`. Template:

```markdown
## Security Policy

### Supported Versions
| Version | Supported |
|---------|-----------|
| latest  | ✅        |
| < 1.0   | ❌        |

### Reporting a Vulnerability
**Do NOT open a public GitHub issue for security vulnerabilities.**

Email: security@yourproject.com (or use GitHub private vulnerability reporting)
Response time: 48 hours acknowledgement, 7 days for a fix plan.

We follow responsible disclosure — we'll credit you in the changelog if you wish.
```

---

## 7. MIT License — Everything You Need to Know

### 7.1 Why MIT (not Apache 2.0 or GPL)

| License | Allows commercial use | Patent protection | Must open-source forks | Best for |
|---|---|---|---|---|
| **MIT** | ✅ | ❌ | ❌ | Maximum adoption — anyone can use, modify, sell |
| Apache 2.0 | ✅ | ✅ | ❌ | Enterprise projects needing patent safety |
| GPL v3 | ✅ | ✅ | ✅ (required) | Community-first, no proprietary forks |

**Use MIT.** It maximizes adoption, star velocity, and commercial use — which is what you want for a boilerplate. Developers building SaaS products will not use a GPL boilerplate because their product would have to be GPL too.

### 7.2 Complete MIT License Text

Create `LICENSE` in repo root with exactly this:

```
MIT License

Copyright (c) 2026 Prabhat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 7.3 What MIT Means for Users

- ✅ Use in commercial products (they can sell a SaaS built on it)
- ✅ Modify without sharing changes
- ✅ Private forks
- ✅ Include in paid products
- ✅ Sublicense
- ❌ You are NOT liable for anything (important clause)
- ❌ No warranty given

### 7.4 Third-Party License Compliance

Your boilerplate bundles multiple packages. All of these must be compatible with MIT:

| Package | License | Compatible? |
|---|---|---|
| Django | BSD-3-Clause | ✅ |
| djangorestframework | BSD-2-Clause | ✅ |
| django-allauth | MIT | ✅ |
| dj-stripe | BSD-2-Clause | ✅ |
| Celery | BSD-3-Clause | ✅ |
| django-axes | MIT | ✅ |
| django-environ | MIT | ✅ |
| Stripe Python SDK | Apache 2.0 | ✅ |
| psycopg2 | LGPL | ✅ (can use in MIT project) |

**None of your dependencies require you to open-source derivative works.** You're safe with MIT.

Add to README: `This project is MIT licensed. See [LICENSE](LICENSE) for details.`

---

## 8. Documentation Structure — Every File Required

### 8.1 Repository Root Files

```
README.md              ← Main landing page (see spec below)
LICENSE                ← MIT license text
CHANGELOG.md           ← Version history (keep-a-changelog format)
CONTRIBUTING.md        ← How to contribute
CODE_OF_CONDUCT.md     ← Contributor Covenant
SECURITY.md            ← Vulnerability reporting policy
.env.example           ← All required env vars with safe placeholders
.gitignore             ← Standard Django + node_modules + .env
Makefile               ← Developer shortcuts (make run, make test, make migrate)
docker-compose.yml     ← Local development
docker-compose.prod.yml ← Production-like local testing
```

### 8.2 README.md Structure (Every Section)

```markdown
# [Logo/Banner Image]

# Project Name
> One-line description: open-source, AWS-ready Django SaaS boilerplate with Stripe, teams & one-command Fargate deploy

[![License: MIT](badge)] [![Django](badge)] [![Python](badge)] [![Build](badge)] [![Stars](badge)]

## ✨ Demo
[Live demo link] | [Demo video GIF]

## 🚀 Quick Start
git clone ...
cd project
cp .env.example .env
docker compose up
# → App at http://localhost:8000

## 📦 What's Included
[Feature table]

## 🏗️ Architecture
[Diagram]

## 📋 Requirements
- Docker & Docker Compose
- Python 3.12+
- (For AWS deploy) AWS CLI, Terraform 1.5+

## 🛠️ Local Development
[Step by step]

## ☁️ AWS Deployment
[terraform apply walkthrough]

## 🧪 Testing
make test

## 📖 Documentation
[Link to /docs]

## 🗺️ Roadmap
[Milestone table]

## 🤝 Contributing
[Link to CONTRIBUTING.md]

## 📄 License
MIT

## 🌟 Star History
[Star history chart image]
```

### 8.3 CONTRIBUTING.md Structure

```markdown
# Contributing to [Project Name]

## Ways to Contribute
- Report bugs (use issue template)
- Suggest features (use discussion)
- Submit PRs (read this guide first)
- Improve documentation
- Write tests

## Development Setup
[Full local setup steps]

## Code Style
- Python: ruff (formatting + linting)
- Pre-commit hooks: run `pre-commit install`
- Commit messages: Conventional Commits format

## Pull Request Process
1. Fork the repo
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Write tests for new code
4. Ensure all tests pass: `make test`
5. Update CHANGELOG.md
6. Submit PR against `main`

## Commit Message Format
feat: add per-seat billing support
fix: correct stripe webhook signature check
docs: update AWS deployment guide
chore: upgrade Django to 5.2

## Review Process
- PRs need 1 approval
- CI must pass (tests, lint, security scan)
- Coverage must not drop

## Code of Conduct
[Link to CODE_OF_CONDUCT.md]
```

### 8.4 docs/ Directory Structure

```
docs/
├── getting-started/
│   ├── installation.md
│   ├── configuration.md
│   └── quick-start.md
├── features/
│   ├── authentication.md
│   ├── billing.md
│   ├── multi-tenancy.md
│   ├── background-tasks.md
│   ├── api.md
│   └── email.md
├── deployment/
│   ├── aws-ecs-fargate.md     ← THE key doc — step by step
│   ├── environment-variables.md
│   ├── database-migrations.md
│   └── ssl-and-domains.md
├── security/
│   ├── overview.md
│   ├── secrets-management.md
│   └── owasp-compliance.md
├── contributing/
│   ├── development-setup.md
│   └── testing.md
└── reference/
    ├── models.md
    ├── api-endpoints.md
    └── settings.md
```

### 8.5 GitHub Issue Templates (.github/ISSUE_TEMPLATE/)

```yaml
# .github/ISSUE_TEMPLATE/bug_report.yml
name: Bug Report
description: Something isn't working
labels: ["bug"]
body:
  - type: input
    label: Django version
  - type: input
    label: Python version
  - type: textarea
    label: Steps to reproduce
  - type: textarea
    label: Expected behavior
  - type: textarea
    label: Actual behavior
  - type: textarea
    label: Relevant logs
```

```yaml
# .github/ISSUE_TEMPLATE/feature_request.yml
name: Feature Request
labels: ["enhancement"]
body:
  - type: textarea
    label: Problem this solves
  - type: textarea
    label: Proposed solution
  - type: dropdown
    label: Would you submit a PR?
    options: [Yes, No, Maybe]
```

### 8.6 Pull Request Template (.github/PULL_REQUEST_TEMPLATE.md)

```markdown
## Description
[What does this PR do?]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] I wrote tests for this change
- [ ] All existing tests pass (`make test`)
- [ ] Coverage has not dropped

## Checklist
- [ ] Code follows project style (ruff passes)
- [ ] CHANGELOG.md updated
- [ ] Documentation updated
- [ ] No secrets in code
```

---

## 9. Project Repository Structure

```
django-saas-boilerplate/
│
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml
│   │   └── feature_request.yml
│   ├── workflows/
│   │   ├── ci.yml              ← lint, test, coverage on every PR
│   │   ├── deploy.yml          ← build Docker, push ECR, deploy ECS on merge to main
│   │   └── security.yml        ← pip-audit, bandit, gitleaks weekly
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── dependabot.yml
│
├── apps/
│   ├── users/                  ← CustomUser, profile
│   ├── organizations/          ← Org, Membership, Invitation
│   ├── billing/                ← Plan, Subscription, Invoice, webhook handler
│   ├── core/                   ← Base models, middleware, utils
│   ├── api/                    ← DRF views, serializers, URLs
│   └── dashboard/              ← HTMX views, templates
│
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   ├── production.py
│   │   └── test.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── templates/
│   ├── base.html
│   ├── account/               ← allauth overrides
│   ├── dashboard/
│   ├── billing/
│   ├── organizations/
│   └── email/                 ← transactional email templates
│
├── static/
│   ├── css/                   ← Tailwind compiled output
│   ├── js/                    ← HTMX, Alpine.js
│   └── img/
│
├── terraform/
│   ├── modules/
│   │   ├── vpc/
│   │   ├── ecs/
│   │   ├── rds/
│   │   ├── elasticache/
│   │   ├── s3/
│   │   └── alb/
│   ├── environments/
│   │   ├── staging/
│   │   └── production/
│   └── README.md              ← Terraform-specific docs
│
├── tests/
│   ├── conftest.py
│   ├── factories.py           ← factory_boy factories for all models
│   ├── test_users/
│   ├── test_organizations/
│   ├── test_billing/
│   └── test_api/
│
├── docs/                      ← see section 8.4
│
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── docker-compose.yml
├── docker-compose.prod.yml
├── Dockerfile
├── LICENSE
├── Makefile
├── pyproject.toml             ← ruff config, pytest config
├── README.md
├── requirements/
│   ├── base.txt
│   ├── local.txt
│   └── production.txt
└── SECURITY.md
```

---

## 10. Tech Stack Decision Matrix

| Decision | Choice | Why | Alternative |
|---|---|---|---|
| Python version | 3.12 | Fastest CPython, typing improvements | 3.11 also fine |
| Django version | 5.2 LTS (or 6.0) | LTS = supported until 2028 | 6.0 for native CSP, async views |
| Package manager | `uv` | 10–100x faster than pip, becoming standard | pip + pip-tools |
| Frontend | HTMX + Alpine.js + Tailwind v4 | Less JS, faster TTL, 80% of SaaS is CRUD | React (documented as alternative) |
| Database | PostgreSQL 16 | JSONB, full-text search, row-level security | MySQL (not recommended) |
| Cache/Broker | Redis 7 | Celery broker + result + cache + rate limit | Valkey (Redis fork, compatible) |
| Auth | django-allauth | Most complete, maintained, MFA support | custom |
| Billing | dj-stripe | Battle-tested, webhook sync, model layer | hand-rolled |
| ORM | Django ORM | Built-in, safe by default | SQLAlchemy |
| API | DRF + drf-spectacular | De facto standard | Django Ninja (async, alternative) |
| Email | django-anymail | Provider-agnostic | django-ses (AWS only) |
| Testing | pytest + pytest-django | Most Django devs use this | unittest |
| Code quality | ruff | Replaces flake8 + black + isort + pylint | flake8 |
| IaC | Terraform | AWS-native, most common in jobs | AWS CDK (JS heavy) |
| Container | Docker + Docker Compose v2 | Standard | Podman |
| CI/CD | GitHub Actions | Free for public repos | CircleCI |

---

## 11. GitHub Star Growth Strategy

### 11.1 README as Landing Page (Highest Leverage)

The README is your homepage. These elements are non-negotiable:

1. **Above the fold** (visible without scrolling):
   - Logo/banner image
   - One-line positioning statement
   - Quick Start (< 3 commands)
   - Demo GIF (30–60 seconds, shows login → dashboard → billing → deploy)
   - 4–6 badges (license, Django version, Python, stars, build status)

2. **Feature section**: use a table or emoji-bulleted list. Make it scannable in 10 seconds.

3. **Architecture diagram**: a simple block diagram showing Django + Celery + Postgres + Redis + S3 + ALB + ECS. Developers love architecture diagrams.

4. **"Why not just use X"** section addressing cookiecutter-django and SaaS Pegasus directly.

5. **Screenshots**: dashboard page, billing page, admin. Real > mockup.

### 11.2 GitHub SEO

- Repo name: `django-saas-boilerplate` (exact keyword match)
- Description (About): "Open-source Django SaaS boilerplate — Stripe, multi-tenancy, Celery, one-command AWS ECS Fargate deploy"
- Website: link to live demo
- Topics (max 20, use all 20):
  `django`, `saas`, `saas-boilerplate`, `django-saas`, `boilerplate`,
  `stripe`, `celery`, `multi-tenancy`, `aws-ecs`, `fargate`,
  `terraform`, `htmx`, `tailwindcss`, `postgresql`, `redis`,
  `github-actions`, `python`, `starter-kit`, `open-source`, `docker`

### 11.3 Star Conversion Funnel

```
Person finds repo (search/Reddit/HN)
         ↓
Reads above-the-fold README (10 sec)
         ↓
Clicks demo link / watches GIF
         ↓
Stars (if impressed)
         ↓
Clones (if building something)
```

Every friction point in this funnel kills stars. Fix: one-command setup, working demo, clear positioning.

### 11.4 Awesome Lists & Directories

Submit to these — they provide permanent, compounding referral traffic:

- `awesome-django` (GitHub) — PR to add your repo
- `awesome-selfhosted` — if applicable
- `builtwithdjango.com` — submit your project
- `boilerplatelist.com` — they already list competitors
- `pyboilerplate.com`
- `djangopackages.org`

### 11.5 Cross-100 Star Threshold First

Before any public launch, reach 100 stars via direct outreach:
- DM 20–50 developer friends / Twitter followers / LinkedIn connections
- Post in any private Slack/Discord dev communities you're in
- Ask 5–10 previous colleagues to star it

100 stars gives social proof that makes cold visitors more likely to star.

---

## 12. Reddit Promotion Playbook

### 12.1 Target Subreddits (ranked by value)

| Subreddit | Members | Rules | Strategy |
|---|---|---|---|
| r/django | ~200k | Technical, relevant | Best fit — post "how I built it" |
| r/Python | ~700k | Quality posts only | Lead with technical depth |
| r/SideProject | ~131k | Made for sharing | Friendly, just show what you made |
| r/coolgithubprojects | ~50k | Purpose-built | Direct share OK |
| r/selfhosted | ~500k | Open source friendly | Emphasize "self-hostable" |
| r/opensource | ~210k | Genuine OSS | "Free alternative to SaaS Pegasus" |
| r/webdev | ~1.6M | Value-first only | Only post if genuinely educational |
| r/SaaS | ~200k | Weekly megathread only | Use "Share Your Side Project" thread |
| r/startups | ~1.2M | Megathread only | Use "Feedback Friday" thread |

### 12.2 Account Preparation (Do This 4 Weeks Before Launch)

Reddit AutoMod filters accounts with:
- Age < 30 days
- Karma < 100–500 (varies by sub)
- No comment history in the sub

Action: Spend 2–4 weeks commenting helpfully in r/django and r/Python:
- Answer Django questions you know well
- Share useful resources in threads
- Don't mention your project yet
- Goal: 200+ karma, 30+ day account age

### 12.3 Post Formats That Work

**Format A — "I built this, here's what I learned"**
```
Title: I got tired of rebuilding the same Django SaaS foundation — 
so I spent 3 months extracting it from a real production app and 
open-sourcing it

Body:
Every time I started a new Django SaaS I was rebuilding:
- Stripe subscriptions (and getting webhooks wrong)
- Multi-tenant architecture (always under-engineered the first time)
- AWS ECS Fargate deployment (3-day odyssey every single time)
- Celery + Redis setup
- Auth with 2FA

I just finished extracting all of this from a real production 
payment platform I built. It's on GitHub: [link]

Here's the architecture decision I'm most unsure about...
[ask a genuine question to invite discussion]

Lessons learned:
- Stripe webhook idempotency is not optional (story of a bug)
- Row-level multi-tenancy is 10x simpler than schema-based for small teams
- AWS ECS migrations are painful without a task definition pattern

What would you do differently?
```

**Format B — "Show r/django: [Name] — feature list"**
```
Title: Show r/django: [Project Name] — open-source Django SaaS boilerplate 
(Stripe, teams, AWS ECS, one-command setup)

Body: brief, honest, invite feedback
```

### 12.4 Timing

- Best days: Tuesday, Wednesday, Thursday
- Best time: 9 AM–11 AM US Eastern (covers both US morning and EU afternoon)
- Coordinate with Show HN and Dev.to post in same 48-hour window

### 12.5 What Gets You Banned

- ❌ Multiple posts in same day across different subreddits
- ❌ Only posting your own content (no community engagement)
- ❌ Not disclosing you're the author
- ❌ Buying upvotes
- ❌ Asking friends to upvote (vote manipulation)
- ❌ Crossposting too aggressively

### 12.6 Handling the Comment Section

Be in the thread within 15 minutes of posting. Answer every comment personally. This signals the post is active and Reddit's algorithm promotes it more.

Common objections to prepare for:
- "Why not just use cookiecutter-django?" → No billing, no tenancy, no cloud deploy
- "SaaS Pegasus exists" → Paid, closed source, no AWS IaC
- "apptension/saas-boilerplate exists" → React+GraphQL+CDK monorepo, 2-4h setup
- "Isn't this just a tutorial project?" → Show the real production origin

---

## 13. Launch Timeline — Week by Week

### Phase 0: Build (Weeks 1–6)

**Week 1–2: Core models & auth**
- CustomUser, Organization, Membership models
- django-allauth setup + email verification
- Docker Compose working with one command
- `.env.example` with all vars documented

**Week 3–4: Billing & background tasks**
- dj-stripe integration
- Webhook handler (production-safe)
- Celery + Redis working
- Stripe checkout + customer portal

**Week 5–6: AWS deploy + CI/CD**
- Terraform modules: VPC, ECS, RDS, ElastiCache, ALB, S3
- GitHub Actions: test → build → push ECR → deploy ECS
- Migration task pattern
- CloudWatch structured logging

### Phase 1: Polish (Weeks 7–8)

- Demo GIF recorded (must be compelling)
- Live demo deployed (your own AWS account)
- README polished to landing page standard
- All docs written
- Tests passing with >70% coverage
- Security audit: run `manage.py check --deploy`, Bandit, dependency audit

### Phase 2: Pre-launch Seeding (Weeks 9–10)

- Reddit account karma building (daily comments in r/django, r/Python)
- Write Dev.to/Hashnode article: "I extracted a real Django SaaS production setup — here's the architecture"
- DM 20–50 developer friends/contacts to seed first 50 stars
- Submit to awesome-lists + boilerplatelist.com

### Phase 3: Launch (Week 11 — Tuesday or Wednesday)

**Day 0 (Monday):** Publish Dev.to article  
**Day 1 (Tuesday, 9 AM ET):**
- Submit Show HN: "Show HN: [Name] – open-source Django SaaS boilerplate (Stripe, teams, one-command AWS deploy)"
- Post r/SideProject
- Post r/coolgithubprojects

**Day 2 (Wednesday, 9 AM ET):**
- Post r/django ("I built this, here's what I learned" format)
- Post r/Python

**Day 3–7:** Post in weekly megathreads of r/SaaS, r/startups

### Phase 4: Sustain (Week 12+)

- Weekly releases (even small: "v0.2.1 — fix Docker healthcheck")
- Respond to all issues <24 hours
- Monthly "what's new" update post in r/django
- Write follow-up articles as you add features

---

## 14. Naming & Positioning

### 14.1 Candidate Names

| Name | Available? | Pros | Cons |
|---|---|---|---|
| `django-saas-boilerplate` | Check GitHub | Exact keyword match | Generic |
| `launchkit` | Check | Memorable | Not Django-specific |
| `django-launchpad` | Check | Good meaning | May conflict |
| `saasify-django` | Check | Verb = action | Awkward |
| `djangolaunch` | Check | Clean, brandable | New word |
| `shipfast-django` | Check | Trend-following | Could age badly |

**Recommendation:** Use `django-saas-boilerplate` as the **repo name** (for search SEO), but give the project a brandable name (e.g. "LaunchKit for Django") for marketing. This way you get keyword search traffic AND memorable branding.

### 14.2 Positioning Statement Options

**Primary:** "The open-source Django SaaS boilerplate that actually deploys to AWS"

**Secondary hooks:**
- "Free and open-source alternative to SaaS Pegasus"
- "From `git clone` to production on AWS in under an hour"
- "Built from a real production SaaS — not a tutorial project"
- "The Django SaaS foundation I wish existed when I started"

### 14.3 GitHub Topics to Target (Search Terms)

Developers search for:
- `django saas boilerplate` ← primary
- `django saas template`
- `django saas starter`
- `django stripe`
- `django multi tenant`
- `django aws ecs`
- `django htmx saas`
- `python saas boilerplate`
- `open source saas pegasus alternative`

---

## 15. Honest Risk Assessment

### What could go wrong

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Setup breaks on first clone | High (if not tested on fresh machine) | Kills momentum — no stars | Test on a fresh Docker environment before launch |
| Stripe integration becomes outdated | Medium (Stripe changes APIs) | Trust erosion | Pin stripe-python version, add changelog notices |
| apptension or Pegasus closes the gap | Low-Medium | Competition | Double down on your AWS-native differentiator |
| Reddit posts get removed | Medium | Wasted launch day | Read each sub's rules, build karma first |
| Low stars despite effort | Medium | Discouraging | Treat 200+ as a success; assess README and setup friction |
| Maintainer burnout | High (solo project) | Abandoned look | Set expectations in README: community-maintained, not SLA |
| Security vulnerability in boilerplate | Low | Reputation damage | Security audit before launch, clear SECURITY.md, Dependabot |

### What success actually looks like

| Milestone | Timeframe | What it means |
|---|---|---|
| 100 stars | Launch week | Proof of concept — the idea resonates |
| 500 stars | Month 1–2 | Organic discovery is working |
| 1,000 stars | Month 3–6 | Critical mass — shows up in searches |
| 2,000+ stars | Month 6–12 | Potential to monetize (Pro tier, consulting, sponsorship) |

Stars are not money. But at 1,000+ stars you have a portfolio asset, consulting credibility, and the foundation to build a paid tier (hosted version, Pro features, support plans).

### The single most important thing

**The `docker compose up` must work on the first try, on any machine.**

If a developer clones your repo, runs one command, and it just works — they star it, they tell their friends, they come back. If they spend 20 minutes debugging Docker networking or missing env vars, they close the tab and you never see them again.

Test this on a completely fresh machine or VM before launch. It is worth more than any Reddit post.

---

*Research compiled June 2026. Star counts are approximate and change daily. Reddit rules change — verify each subreddit's sidebar before posting. Package versions should be verified at time of implementation.*
