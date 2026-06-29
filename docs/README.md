# DjangoForge Documentation

Welcome to the DjangoForge documentation. DjangoForge is a production-ready, open-source Django SaaS boilerplate.

---

## Getting Started

| Guide | Description |
|-------|-------------|
| [Quick Start](./getting-started/quick-start.md) | Get running in 5 minutes with Docker Compose |
| [Configuration](./getting-started/configuration.md) | All environment variables explained |
| [Local Development](./getting-started/local-development.md) | Daily dev workflows, debugging, hot reload |

---

## Architecture

| Guide | Description |
|-------|-------------|
| [Overview](./architecture/overview.md) | System design, request lifecycle, app responsibilities |
| [Multi-Tenancy](./architecture/multi-tenancy.md) | How orgs, memberships, and data scoping work |
| [Background Tasks](./architecture/background-tasks.md) | Celery task catalog and patterns |

---

## Features

| Guide | Description |
|-------|-------------|
| [Authentication](./features/authentication.md) | Signup, login, OAuth, email verification, brute-force protection |
| [Organizations](./features/organizations.md) | Orgs, roles, invitations, plan management |
| [Billing](./features/billing.md) | Stripe Checkout, Customer Portal, webhooks, billing emails |
| [REST API](./features/api.md) | DRF API, authentication, rate limiting, OpenAPI docs |
| [Feature Flags](./features/feature-flags.md) | DB-backed flags, percentage rollout, template/view usage |
| [Audit Log](./features/audit-log.md) | Event logging, retention, querying |

---

## Guides

| Guide | Description |
|-------|-------------|
| [Adding a New App](./guides/adding-a-new-app.md) | Step-by-step guide to extending DjangoForge |
| [Customizing Templates](./guides/customizing-templates.md) | Design system, dark mode, components |
| [Writing Tests](./guides/writing-tests.md) | pytest, factory-boy, fixtures, coverage rules |
| [Environment Variables](./guides/environment-variables.md) | Quick reference for all env vars |

---

## Deployment

| Guide | Description |
|-------|-------------|
| [Docker](./deployment/docker.md) | Dockerfile, Docker Compose, production vs development |
| [AWS ECS Fargate](./deployment/aws-ecs-fargate.md) | Full production deployment on AWS with Terraform |

---

## Stack

| Technology | Version | Role |
|------------|---------|------|
| Python | 3.12 | Runtime |
| Django | 5.2 LTS | Web framework |
| PostgreSQL | 16 | Primary database |
| Redis | 7 | Cache, Celery broker, sessions |
| Celery | 5 | Background tasks |
| DRF | 3.15 | REST API |
| drf-spectacular | 0.27 | OpenAPI schema |
| django-allauth | 65 | OAuth (Google, GitHub) |
| dj-stripe | 2.8 | Stripe billing |
| django-anymail | 10 | Transactional email |
| django-axes | 6.5 | Brute-force protection |
| HTMX | 1.x | Partial page updates |
| Alpine.js | 3.x | Reactive UI components |
| Tailwind CSS | 4 | Utility CSS |
| Terraform | 1.7+ | AWS infrastructure |
| uv | latest | Python package manager |
| ruff | latest | Linting and formatting |
| pytest | 8 | Testing |
