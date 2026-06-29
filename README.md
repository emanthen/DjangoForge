<div align="center">

<br>

<img src="https://raw.githubusercontent.com/emanthen/djangoforge/main/docs/assets/logo.svg" width="64" height="64" alt="DjangoForge Logo">

# DjangoForge

### Production-ready Django SaaS boilerplate. Ship in days, not months.

[![License: MIT](https://img.shields.io/badge/License-MIT-violet.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Django 5.2 LTS](https://img.shields.io/badge/Django-5.2%20LTS-0C4B33?logo=django&logoColor=white)](https://djangoproject.com)
[![CI](https://github.com/emanthen/djangoforge/actions/workflows/ci.yml/badge.svg)](https://github.com/emanthen/djangoforge/actions)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](https://hub.docker.com)
[![Terraform](https://img.shields.io/badge/Terraform-AWS%20ECS-7B42BC?logo=terraform&logoColor=white)](infra/terraform/)

<br>

**[Quick Start](#-quick-start)** &nbsp;·&nbsp; **[What's Included](#-whats-included)** &nbsp;·&nbsp; **[Documentation](#-documentation)** &nbsp;·&nbsp; **[Contributing](#-contributing)**

<br>

> Built from a real production codebase. Everything you need — nothing you don't.

</div>

---

## Why DjangoForge?

Every Django SaaS developer rebuilds the same foundation: auth, billing, teams, email, background tasks, deployment. That's **80–200 hours** before you write a single line of product logic.

DjangoForge solves this. It's extracted from [KibaPay](https://github.com/emanthen), a real production payment platform, battle-tested at scale. Clone, configure, ship.

| | **DjangoForge** | cookiecutter-django | apptension/saas-boilerplate | SaaS Pegasus |
|---|:---:|:---:|:---:|:---:|
| **Price** | **Free** | Free | Free | $249–$999 |
| **License** | **MIT** | BSD | MIT | Commercial |
| **Stripe billing** | ✅ | ❌ | ✅ | ✅ |
| **Multi-tenancy** | ✅ | ❌ | ✅ | ✅ |
| **AWS ECS Fargate** | ✅ | ❌ | ❌ | ❌ |
| **Terraform IaC** | ✅ | ❌ | ❌ | ❌ |
| **Pure Django** | ✅ | ✅ | ❌ | ✅ |
| **Setup time** | **~5 min** | ~30 min | 2–4 hrs | ~1 hr |

---

## ⚡ Quick Start

```bash
# 1. Clone
git clone https://github.com/emanthen/djangoforge && cd djangoforge

# 2. Configure
cp .env.example .env          # Edit SECRET_KEY, Stripe keys, etc.

# 3. Start all services
docker compose up -d

# 4. Seed demo data
docker compose exec web python manage.py seed_data

# 5. Open the app
open http://localhost:8000
```

**Demo accounts:**
| Email | Password | Role |
|-------|----------|------|
| `alice@example.com` | `demo123` | Owner · Pro plan |
| `bob@example.com` | `demo123` | Member · Free plan |
| `admin@djangoforge.dev` | `admin123` | Django superuser |

> **No Docker?** See [local development guide](docs/getting-started/quick-start.md#without-docker).

---

## ✅ What's Included

### 🔐 Authentication & Security
- Custom `User` model with email as username (no `username` field)
- Email verification with secure signed tokens
- Password reset via allauth
- Google & GitHub OAuth (django-allauth)
- Brute-force protection (django-axes — 5 failures → 1h lockout)
- CSRF, XSS, HSTS, clickjacking protection in production
- Secure session handling (Redis-backed, 2-week expiry)

### 🏢 Organizations & Multi-tenancy
- Row-level multi-tenancy via `TenantMiddleware`
- `OrgScopedManager` with thread-local for automatic query scoping
- Role-based access: **Owner**, **Admin**, **Member**, **Billing Admin**
- Member invitations via email with 7-day expiry
- Organization switching without re-login
- Ownership transfer with audit trail

### 💳 Billing (Stripe)
- Stripe Checkout (hosted payment page)
- Stripe Customer Portal (self-serve billing management)
- Webhook handler with **signature verification** + **deduplication** (no double-processing)
- Handles: `subscription.created/updated/deleted`, `invoice.payment_succeeded/failed`
- Three-tier pricing: Free · Starter ($29) · Pro ($79)

### ⚡ Background Tasks
- Celery 5 + Redis as broker + result backend
- django-celery-beat for scheduled tasks (DB-backed cron)
- Flower dashboard at `:5555`
- Task retry with exponential backoff

### 🌐 REST API
- Django REST Framework with session authentication
- drf-spectacular → OpenAPI 3.0 schema at `/api/schema/`
- Swagger UI at `/api/docs/`, ReDoc at `/api/redoc/`
- Rate limiting: 100/hr anon, 1000/hr authenticated
- Endpoints: health check, `/api/me/`, organizations, memberships

### 🎛 Feature Flags
- DB-backed feature flags (no external service needed)
- Rollout modes: global · per-org · per-user · percentage (0–100%)
- Template access: `{% if flags.ai_features %}...{% endif %}`
- Django admin management UI

### 📋 Audit Log
- `AuditEvent` model: action, actor, org, resource, IP, user agent, metadata
- `log_event()` utility called throughout codebase
- 90-day automatic retention via Celery beat
- Indexed on `(org, created_at)`, `(actor, created_at)`, `action`

### 🎨 Frontend
- **HTMX** for partial page updates (no full reloads)
- **Alpine.js** for reactive components (dark mode, dropdowns, modals)
- **Tailwind CSS 4** via CDN (zero build step in dev)
- **Inter font** — clean, professional typography
- Dark mode with `localStorage` persistence
- Responsive sidebar layout with mobile overlay
- Professional email templates (6 types)

### 🚀 Deployment
- **Docker Compose** — one command for web + worker + beat + flower + db + redis
- **Multi-stage Dockerfile** — builder + runtime, non-root user, minimal image
- **GitHub Actions CI/CD** → ECR → ECS Fargate rolling deploy
- **Terraform** — 8 modules: VPC, ECR, RDS, ElastiCache, ALB, ECS, S3, SecretsManager, CloudWatch

### 📊 Observability
- Sentry with Django + Celery + Redis integrations
- Structured JSON logging (python-json-logger) for CloudWatch
- `X-Request-ID` header on every response for distributed tracing
- `/api/health/` endpoint (checks DB, Redis, Celery)
- Log retention configurable via `AUDIT_LOG_RETENTION_DAYS`

---

## 🏗 Project Structure

```
djangoforge/
│
├── apps/
│   ├── accounts/           # User model, auth, email verification
│   │   ├── models.py       # Custom User (email auth, last_login_ip)
│   │   ├── views.py        # Signup, login, profile, dashboard
│   │   ├── forms.py        # LoginForm, SignupForm, ProfileForm
│   │   ├── tokens.py       # Email verification token generator
│   │   └── templatetags/   # df_filters (humanize_action, initials)
│   ├── organizations/      # Multi-tenancy, roles, invitations
│   │   ├── models.py       # Organization, Membership, Invitation
│   │   ├── middleware.py   # TenantMiddleware (attaches request.org)
│   │   ├── mixins.py       # OrgRequiredMixin, OrgAdminMixin, OrgOwnerMixin
│   │   └── context_processors.py
│   ├── billing/            # Stripe Checkout + webhooks
│   │   ├── views.py        # PricingView, CheckoutView, WebhookView
│   │   ├── models.py       # WebhookEvent (deduplication)
│   │   ├── handlers.py     # Stripe event handlers
│   │   └── utils.py        # get_or_create_stripe_customer
│   ├── api/                # DRF REST API
│   │   ├── views.py        # HealthCheckView, MeView, ViewSets
│   │   └── serializers.py
│   ├── flags/              # Feature flags
│   │   ├── models.py       # FeatureFlag with is_enabled_for()
│   │   └── context_processors.py  # FlagProxy for templates
│   ├── audit/              # Audit log
│   │   ├── models.py       # AuditEvent
│   │   ├── utils.py        # log_event()
│   │   └── middleware.py   # RequestIDMiddleware
│   └── notifications/      # In-app notifications
│
├── config/
│   ├── settings/
│   │   ├── base.py         # All shared settings
│   │   ├── local.py        # Dev overrides
│   │   ├── production.py   # Sentry, security headers, JSON logging
│   │   └── testing.py      # SQLite, fast hashing, eager Celery
│   ├── celery.py
│   ├── urls.py
│   └── wsgi.py
│
├── templates/
│   ├── base.html           # Dark/light layout with sidebar
│   ├── components/         # _sidebar, _navbar, _flash_messages, etc.
│   ├── accounts/           # login, signup, profile, verify_email
│   ├── billing/            # pricing, success
│   ├── organizations/      # members, settings, create, transfer
│   ├── dashboard/          # index
│   ├── emails/             # 6 HTML email templates
│   └── errors/             # 404, 500, 403
│
├── static/
│   └── js/app.js           # HTMX CSRF + global interactions
│
├── tests/
│   ├── factories.py        # UserFactory, OrgFactory, MembershipFactory
│   ├── test_accounts.py
│   ├── test_organizations.py
│   └── test_billing.py
│
├── infra/terraform/        # AWS ECS Fargate IaC
│   └── modules/            # vpc, ecr, rds, elasticache, alb, ecs, s3, secrets, cloudwatch
│
├── .github/workflows/
│   ├── ci.yml              # Test + lint + SAST on every PR
│   └── deploy.yml          # Build → ECR → ECS on push to main
│
├── docker-compose.yml      # web, worker, beat, flower, db, redis
├── Dockerfile              # Multi-stage builder + runtime
└── pyproject.toml          # uv deps, ruff config, pytest config
```

---

## 🛠 Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Runtime** | Python | 3.12 |
| **Framework** | Django | 5.2 LTS |
| **Database** | PostgreSQL | 16 |
| **Cache / Broker** | Redis | 7 |
| **Task Queue** | Celery + django-celery-beat | 5.x |
| **Auth** | django-allauth | — |
| **Billing** | dj-stripe | — |
| **Email** | django-anymail | Mailgun / SES / SendGrid |
| **API** | Django REST Framework + drf-spectacular | — |
| **Frontend** | HTMX + Alpine.js + Tailwind CSS 4 | — |
| **Package Manager** | uv | — |
| **Linting** | ruff | — |
| **Testing** | pytest + pytest-django + factory-boy | — |
| **Containers** | Docker + Docker Compose | — |
| **IaC** | Terraform | AWS ECS Fargate |
| **CI/CD** | GitHub Actions | — |
| **Monitoring** | Sentry + CloudWatch | — |

---

## 📚 Documentation

| Topic | Link |
|-------|------|
| Quick Start | [docs/getting-started/quick-start.md](docs/getting-started/quick-start.md) |
| Configuration (env vars) | [docs/deployment/environment-variables.md](docs/deployment/environment-variables.md) |
| AWS ECS Fargate Deployment | [docs/deployment/aws-ecs-fargate.md](docs/deployment/aws-ecs-fargate.md) |
| Stripe Setup | [docs/billing/stripe-setup.md](docs/billing/stripe-setup.md) |
| Contributing | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Security Policy | [SECURITY.md](SECURITY.md) |
| Changelog | [CHANGELOG.md](CHANGELOG.md) |

---

## 🤝 Contributing

Contributions are welcome and appreciated!

1. **Fork** this repository
2. **Create** a feature branch: `git checkout -b feat/my-feature`
3. **Write tests** — coverage must stay above 70%
4. **Run checks**: `uv run ruff check . && uv run pytest`
5. **Open a PR** with a clear description

Read [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

### Development Setup (without Docker)

```bash
# Install dependencies
uv sync --all-extras

# Set up environment
cp .env.example .env.local
export DJANGO_SETTINGS_MODULE=config.settings.local

# Run migrations
uv run python manage.py migrate

# Start dev server
uv run python manage.py runserver
```

---

## 🔒 Security

Found a vulnerability? Please report it privately via [SECURITY.md](SECURITY.md).

**Do not** open a public GitHub issue for security vulnerabilities.

---

## 📄 License

DjangoForge is open-source software licensed under the **MIT License**.

See [LICENSE](LICENSE) for the full text.

---

<div align="center">

Built with ❤️ by [Prabhat](https://github.com/emanthen) in Nepal 🇳🇵

If DjangoForge saved you time, please **[⭐ star this repo](https://github.com/emanthen/djangoforge)** — it helps others discover it!

**[GitHub](https://github.com/emanthen/djangoforge)** &nbsp;·&nbsp; **[Issues](https://github.com/emanthen/djangoforge/issues)** &nbsp;·&nbsp; **[Discussions](https://github.com/emanthen/djangoforge/discussions)**

</div>
