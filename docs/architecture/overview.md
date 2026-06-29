# Architecture Overview

DjangoForge is a multi-tenant SaaS boilerplate. Each tenant is an **Organization**. Users belong to one or more organizations with role-based access. This document describes how the pieces fit together.

---

## High-level structure

```
DjangoForge/
├── apps/                  # All Django applications
│   ├── accounts/          # User model, auth, profile
│   ├── organizations/     # Orgs, memberships, invitations
│   ├── billing/           # Stripe subscriptions & webhooks
│   ├── api/               # DRF REST API
│   ├── audit/             # Immutable event log
│   ├── flags/             # Feature flags
│   └── notifications/     # In-app notifications
├── config/
│   ├── settings/          # base / development / production / testing
│   ├── urls.py            # Root URL conf
│   └── celery_app.py      # Celery application instance
├── templates/             # Django templates (Jinja2-style syntax)
├── static/                # CSS, JS, images
├── infra/                 # Terraform modules
├── docs/                  # You are here
└── docker-compose.yml
```

---

## Request lifecycle

```
Browser / API client
        │
        ▼
    ALB (AWS)
        │
        ▼
  Gunicorn (web container)
        │
        ▼
  Django WSGI
        │
   Middleware stack
   ┌────────────────────────┐
   │ SecurityMiddleware      │  HSTS, SSL redirect
   │ SessionMiddleware       │  Load session from Redis
   │ RequestIDMiddleware     │  Add X-Request-ID header
   │ TenantMiddleware        │  Set request.org + membership
   │ AuditMiddleware         │  Track user agent / IP
   │ CommonMiddleware        │  Trailing slashes
   │ CsrfViewMiddleware      │  CSRF token validation
   │ AuthenticationMiddleware│  Attach request.user
   │ MessageMiddleware       │  Django messages framework
   └────────────────────────┘
        │
   URL routing (config/urls.py)
        │
   View (CBV or DRF ViewSet)
        │
   Response (HTML template or JSON)
```

---

## App responsibilities

### `accounts` — Users & authentication

- Custom `User` model extending `AbstractBaseUser`
  - `email` is the `USERNAME_FIELD` (no `username` column)
  - Fields: `email`, `first_name`, `last_name`, `avatar`, `email_verified_at`, `last_login_ip`
  - `full_name` property returns `first_name + last_name`
- `EmailVerificationToken` — HMAC-based token with 24h expiry
- `LoginView`, `SignupView`, `LogoutView`, `DashboardView`, `ProfileView`
- Custom template filters: `humanize_action`, `initials` (in `templatetags/df_filters.py`)

### `organizations` — Multi-tenancy

- `Organization` model with UUID PK, slug, plan, trial dates
- `Membership` model: `user` + `org` + `role` (owner / admin / member / billing_admin)
- `Invitation` model: email-based invite with 7-day expiry token
- `TenantMiddleware` — attaches `request.org` and `request.membership` from session
- `OrgScopedManager` — thread-local queryset scoping (prevents cross-org data leaks)
- CBV mixins: `OrgRequiredMixin`, `OrgAdminMixin`, `OrgOwnerMixin`

See [Multi-tenancy](./multi-tenancy.md) for details.

### `billing` — Stripe subscriptions

- Stripe Checkout (hosted payment page) + Customer Portal (self-serve)
- `WebhookView` — validates Stripe signature, deduplicates events
- Webhook handlers for: subscription created/updated/deleted, invoice paid/failed
- `WebhookEvent` model for idempotent processing

See [Billing](../features/billing.md) for details.

### `api` — REST API

- Django REST Framework ViewSets
- `HealthCheckView` — unauthenticated, for ALB health checks
- `MeView` — authenticated user profile
- `OrganizationViewSet` — CRUD for orgs the user belongs to
- OpenAPI 3.0 schema via drf-spectacular (`/api/schema/`)
- Swagger UI at `/api/docs/`, ReDoc at `/api/redoc/`
- Rate limiting: 100/hr anonymous, 1000/hr authenticated

### `audit` — Audit log

- `AuditEvent` model: `actor`, `org`, `action` (string), `metadata` (JSON), `ip`, `user_agent`
- `log_event()` utility used throughout the codebase
- 90-day retention via Celery beat task
- Admin view with filtering by org/actor/action

### `flags` — Feature flags

- `Flag` model: name, enabled, percentage rollout, per-org/user targeting
- `FlagProxy` context processor makes flags available in templates: `{{ flags.my_flag }}`
- `@flag_required("my_flag")` decorator for views
- Admin interface to toggle flags without a deploy

### `notifications` — In-app notifications

- `Notification` model: `recipient`, `verb`, `target_url`, `is_read`
- Unread count shown in sidebar nav
- Mark-as-read via HTMX

---

## Data flow: organization context

Every authenticated page request follows this pattern:

1. `TenantMiddleware` reads `current_org_id` from session
2. Fetches the `Organization` and the user's `Membership` from the database
3. Sets `request.org` and `request.membership`
4. The `org_context` context processor injects `current_org`, `membership`, and `user_orgs` into every template
5. Views use `OrgRequiredMixin` to gate access — redirects to org creation if no org
6. `OrgScopedManager` ensures model queries are automatically filtered to `request.org`

---

## Caching strategy

| What | Backend | TTL |
|------|---------|-----|
| Django sessions | Redis | `SESSION_COOKIE_AGE` (default 2 weeks) |
| Django cache | Redis | varies per view |
| Celery results | Redis | 24 hours |
| Feature flags | DB (no cache) | real-time |

---

## Background jobs (Celery)

| Task | Trigger | App |
|------|---------|-----|
| Send verification email | On signup | accounts |
| Send invitation email | On invite create | organizations |
| Sync Stripe subscription | Webhook received | billing |
| Send billing emails | Subscription events | billing |
| Prune audit events (>90 days) | Daily cron (beat) | audit |

See [Background Tasks](./background-tasks.md) for the full task catalog.

---

## Frontend stack

```
Tailwind CSS 4 (CDN)   ← utility classes, design tokens
Alpine.js 3            ← reactive state (dropdowns, dark mode, tabs)
HTMX 1.x               ← partial page updates (forms, lists)
```

The base layout (`templates/base.html`) provides:
- Responsive sidebar layout (collapsible on mobile)
- Dark mode via `localStorage` key `df-dark`
- Flash message component with auto-dismiss
- HTMX CSRF injection via `htmx:configRequest` event

---

## Security layers

| Layer | Technology |
|-------|-----------|
| Brute-force protection | `django-axes` (5 failures → 1h lockout) |
| CSRF | Django built-in (HTMX-aware) |
| XSS | Django auto-escape in templates |
| Clickjacking | `X-Frame-Options: DENY` |
| SQL injection | Django ORM parameterized queries |
| Open redirect | Manual `startswith("/")` check in `LoginView` |
| Stripe webhook forgery | `stripe.Webhook.construct_event()` signature |
| Webhook replay | `WebhookEvent` deduplication table |
| Secret exposure | `detect-secrets` pre-commit hook |
| SAST | Bandit in CI |
| CVE scanning | Safety in CI |
