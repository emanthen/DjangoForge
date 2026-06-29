# Background Tasks

DjangoForge uses **Celery 5** with **Redis** as the message broker. All task definitions live in `tasks.py` files within each app.

---

## Setup

The Celery application is defined in `config/celery_app.py`:

```python
from celery import Celery

app = Celery("djangoforge")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
```

`autodiscover_tasks()` automatically finds `tasks.py` in every installed app.

### Celery settings (in `config/settings/base.py`)

```python
CELERY_BROKER_URL = env("REDIS_URL")
CELERY_RESULT_BACKEND = env("REDIS_URL")
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_TIME_LIMIT = 300          # hard kill after 5 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 270     # SoftTimeLimitExceeded after 4.5 min
CELERY_WORKER_CONCURRENCY = 4
CELERY_TASK_ALWAYS_EAGER = False      # True in testing settings
```

---

## Task catalog

### accounts

| Task | Trigger | Description |
|------|---------|-------------|
| `send_verification_email` | User signup | Sends the email verification link |
| `send_password_reset_email` | Password reset request | Sends the reset link |

### organizations

| Task | Trigger | Description |
|------|---------|-------------|
| `send_invitation_email` | Invitation created | Sends invite with accept link |
| `expire_old_invitations` | Daily cron | Marks invitations older than 7 days as expired |

### billing

| Task | Trigger | Description |
|------|---------|-------------|
| `sync_stripe_subscription` | Webhook received | Updates org plan from Stripe subscription |
| `send_payment_receipt_email` | `invoice.paid` webhook | Sends receipt to billing admin |
| `send_payment_failed_email` | `invoice.payment_failed` webhook | Sends failure notice to billing admin |
| `send_trial_ending_email` | Daily cron | Sends 3-day warning before trial expires |
| `send_subscription_cancelled_email` | `customer.subscription.deleted` webhook | Sends cancellation confirmation |

### audit

| Task | Trigger | Description |
|------|---------|-------------|
| `prune_old_audit_events` | Daily cron | Deletes `AuditEvent` records older than 90 days |

---

## Writing a new task

```python
# apps/myapp/tasks.py
from config.celery_app import app
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@app.task(bind=True, max_retries=3)
def send_welcome_email(self, user_id: int):
    from apps.accounts.models import User
    try:
        user = User.objects.get(id=user_id)
        # ... send email
        logger.info("Sent welcome email to %s", user.email)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
```

**Key conventions:**
- Accept IDs, not model instances (objects can't be serialized to Redis)
- Use `bind=True` + `self.retry()` for retryable failures
- Use `get_task_logger(__name__)` for structured logging
- Import models inside the task body to avoid circular imports

### Trigger a task

```python
# Fire and forget (returns immediately)
send_welcome_email.delay(user_id=user.id)

# With delay (retry countdown)
send_welcome_email.apply_async(args=[user.id], countdown=10)

# Scheduled for a specific time
from datetime import datetime, timezone
send_welcome_email.apply_async(args=[user.id], eta=datetime(2026, 1, 1, tzinfo=timezone.utc))
```

---

## Periodic tasks (cron)

Periodic tasks are managed by `django-celery-beat` and stored in the database. Configure them in the admin or via `CELERY_BEAT_SCHEDULE` in settings:

```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "prune-audit-events": {
        "task": "apps.audit.tasks.prune_old_audit_events",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2am UTC
    },
    "expire-invitations": {
        "task": "apps.organizations.tasks.expire_old_invitations",
        "schedule": crontab(hour=3, minute=0),
    },
    "trial-ending-emails": {
        "task": "apps.billing.tasks.send_trial_ending_email",
        "schedule": crontab(hour=9, minute=0),  # Daily at 9am UTC
    },
}
```

---

## Monitoring with Flower

Flower is a real-time web UI for Celery. In development:

```
http://localhost:5555
```

It shows:
- Active workers
- Task history (success / failure / retry)
- Task execution times
- Queues and their lengths

In production, Flower runs as a separate ECS service. It's protected behind the ALB with IAM authentication.

---

## Testing tasks

In `config/settings/testing.py`:

```python
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
```

With `ALWAYS_EAGER=True`, `.delay()` and `.apply_async()` execute **synchronously** in the same process during tests — no broker needed.

```python
def test_welcome_email_sent(user, mailoutbox):
    send_welcome_email.delay(user_id=user.id)
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [user.email]
```

---

## Error handling

Tasks that fail after all retries log to Sentry automatically via the Sentry Celery integration configured in `config/settings/production.py`.

For critical tasks, add custom error callbacks:

```python
@app.task(bind=True, max_retries=5, on_failure=notify_on_failure)
def critical_task(self):
    ...
```
