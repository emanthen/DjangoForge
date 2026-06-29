# Changelog

All notable changes to DjangoForge are documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

---

## [Unreleased]

### Added
- Redesigned frontend with Violet/Inter design system (dark mode, responsive sidebar)
- Custom `df_filters` template tags: `humanize_action`, `initials`
- Professional HTML email templates: verify_email, invitation, payment_receipt, payment_failed, subscription_cancelled, trial_ending
- `DashboardView.get_context_data()` now passes server-computed `greeting` and `member_count`
- `<dialog>` native HTML modal for member invitation (replaces Alpine.js show/hide)

### Fixed
- **Bug**: `{{ event.action|replace:"_":" " }}` in `dashboard/index.html` — `replace` is not a valid Django template filter. Replaced with `{{ event.action|humanize_action }}` custom filter
- **Bug**: `{% now "G" as h %}` in dashboard produced a string, not an integer — greeting comparison `h < 12` was always false. Fixed by computing greeting in `DashboardView`
- **Bug**: `{% with hour=request.user.date_joined.hour %}` in dashboard — `hour` variable was never used (dead code). Removed
- **Bug**: `redirect("dashboard:index")` in `SignupView`, `LoginView`, `VerifyEmailView` — no URL named `dashboard:index` exists. Fixed to `redirect("accounts:dashboard")`
- **Bug**: `redirect(self.request.GET.get("next", "dashboard:index"))` in `LoginView.form_valid()` — passing `"dashboard:index"` string as URL path. Fixed with safe open-redirect check (`next_url.startswith("/")`)
- **Bug**: `get_success_url()` in `LoginView` used `reverse_lazy("dashboard:index")`. Fixed to `reverse_lazy("accounts:dashboard")`
- **Improvement**: Login form no longer uses HTMX (`hx-post`) — HTMX + full-page redirect is incompatible without `HX-Redirect` headers

---

## [1.0.0] — 2026-06-29

### Added
- Custom `User` model with email as `USERNAME_FIELD` (no `username` field)
- Email verification via `PasswordResetTokenGenerator` subclass with 24-hour expiry
- Password reset via django-allauth
- Google & GitHub OAuth via `allauth.socialaccount`
- Brute-force login protection via `django-axes` (5 failures, 1-hour cooldown)
- Organizations model with UUID primary key, slug auto-generation, trial support
- `Membership` model: roles owner / admin / member / billing_admin
- `Invitation` model: email-based invitations with 7-day expiry token
- `TenantMiddleware`: attaches `request.org` and `request.membership` from session
- `OrgScopedManager` with thread-local for automatic queryset scoping
- `OrgRequiredMixin`, `OrgAdminMixin`, `OrgOwnerMixin` CBV mixins
- Stripe billing: `CheckoutView` (hosted page), `CustomerPortalView` (self-serve)
- `WebhookView` with Stripe signature verification and `WebhookEvent` deduplication
- Webhook handlers: subscription created/updated/deleted, invoice paid/failed
- DRF REST API with `HealthCheckView`, `MeView`, `OrganizationViewSet`
- OpenAPI 3.0 schema via `drf-spectacular` → `/api/schema/`
- Swagger UI at `/api/docs/`, ReDoc at `/api/redoc/`
- Feature flags: DB-backed, per-org/user/percentage rollout
- `FlagProxy` context processor for template access (`{{ flags.my_flag }}`)
- `AuditEvent` model with `log_event()` utility throughout codebase
- 90-day audit log retention via Celery beat task
- `RequestIDMiddleware` adds `X-Request-ID` header to all responses
- Celery + Redis background tasks with `django-celery-beat`
- Flower monitoring dashboard
- Django REST Framework with rate limiting (100/hr anon, 1000/hr user)
- HTMX + Alpine.js + Tailwind CSS 4 frontend
- Dark mode with `localStorage` persistence
- Responsive sidebar layout with mobile drawer
- `manage.py seed_data` management command
- Multi-stage Dockerfile (builder + runtime, non-root `django` user)
- Docker Compose: web, worker, beat, flower, db, redis with health checks
- GitHub Actions CI: pytest (≥70% coverage), ruff lint, Bandit SAST, Safety CVE
- GitHub Actions deploy: build → ECR → ECS Fargate rolling deploy
- Terraform modules: VPC, ECR, RDS, ElastiCache, ALB, ECS, S3, SecretsManager, CloudWatch
- Sentry SDK with Django + Celery + Redis + Logging integrations
- Structured JSON logging (python-json-logger) for CloudWatch
- Production security: HSTS, XSS, clickjacking, SSL redirect, referrer policy
- `uv` package manager with `pyproject.toml`
- `ruff` linting + formatting
- `pytest` + `pytest-django` + `factory-boy` test suite
- Pre-commit hooks: ruff, detect-secrets

---

[Unreleased]: https://github.com/emanthen/djangoforge/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/emanthen/djangoforge/releases/tag/v1.0.0
