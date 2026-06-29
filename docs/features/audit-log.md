# Audit Log

DjangoForge records an immutable audit trail of all sensitive actions. Every event captures who did what, when, from where, and in which organization.

---

## What gets logged

Out of the box, the following actions are logged:

| Action | When |
|--------|------|
| `user.signup` | New user registers |
| `user.login` | Successful login |
| `user.logout` | User logs out |
| `user.email_verified` | Email verification completed |
| `user.password_changed` | Password changed via profile |
| `user.account_deleted` | Account deletion confirmed |
| `org.created` | New organization created |
| `org.settings_updated` | Org name or settings changed |
| `org.deleted` | Organization deleted |
| `org.member_invited` | Invitation sent |
| `org.member_removed` | Member removed |
| `org.member_role_changed` | Member role updated |
| `org.ownership_transferred` | Ownership transferred |
| `billing.subscription_started` | Stripe subscription activated |
| `billing.subscription_cancelled` | Subscription cancelled |
| `billing.plan_changed` | Plan upgraded or downgraded |
| `billing.payment_failed` | Invoice payment failed |

---

## Logging a custom event

Use the `log_event()` utility anywhere in your code:

```python
from apps.audit.utils import log_event

log_event(
    action="report.generated",
    org=request.org,
    actor=request.user,
    request=request,         # extracts IP + user agent automatically
    metadata={
        "report_id": str(report.id),
        "format": "pdf",
    },
)
```

All parameters except `action` are optional. If `request` is provided, `ip` and `user_agent` are extracted automatically.

### Signature

```python
def log_event(
    action: str,
    org: Organization | None = None,
    actor: User | None = None,
    request: HttpRequest | None = None,
    ip: str | None = None,
    user_agent: str | None = None,
    metadata: dict | None = None,
) -> AuditEvent:
```

---

## AuditEvent model

```python
class AuditEvent(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4)
    org        = models.ForeignKey(Organization, null=True, on_delete=models.SET_NULL)
    actor      = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    action     = models.CharField(max_length=100)    # e.g. "user.email_verified"
    ip         = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(blank=True)
    metadata   = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["org", "-created_at"]),
            models.Index(fields=["actor", "-created_at"]),
        ]
```

Events are **never updated** — only created. There is no `updated_at`.

---

## Viewing audit events

### In the app

The dashboard shows the 10 most recent audit events for the current org. Events are formatted with the `humanize_action` template filter:

```
user.email_verified  →  "User Email Verified"
billing.plan_changed →  "Billing Plan Changed"
```

### In Django admin

Go to Admin → Audit → Audit Events. The admin supports:
- Filter by org, actor, action
- Search by IP, user agent, metadata
- Date range filtering

---

## Retention policy

Audit events older than **90 days** are automatically deleted by a Celery beat task:

```python
# apps/audit/tasks.py
@app.task
def prune_old_audit_events():
    cutoff = now() - timedelta(days=90)
    deleted, _ = AuditEvent.objects.filter(created_at__lt=cutoff).delete()
    logger.info("Pruned %d audit events", deleted)
```

This runs daily at 2am UTC (configured in `CELERY_BEAT_SCHEDULE`).

To change the retention period, update `timedelta(days=90)` in the task.

To disable pruning, remove the beat schedule entry.

---

## Querying audit events

```python
from apps.audit.models import AuditEvent

# All events for an org, newest first
events = AuditEvent.objects.filter(org=org).select_related("actor")

# Events by a specific user
events = AuditEvent.objects.filter(actor=user)

# Events of a specific type
events = AuditEvent.objects.filter(action="billing.payment_failed")

# Events in the last 7 days
from django.utils.timezone import now
from datetime import timedelta
events = AuditEvent.objects.filter(
    org=org,
    created_at__gte=now() - timedelta(days=7),
)
```

---

## Security notes

- Audit events are never modified after creation
- The `actor` FK uses `SET_NULL` on user deletion (preserves events when an account is deleted)
- The `org` FK uses `SET_NULL` on org deletion (preserves events when an org is deleted)
- IP addresses are stored unmasked — review your privacy policy if operating in the EU
- Events include `user_agent` for forensics but it can be spoofed — treat as informational only
