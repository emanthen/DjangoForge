# Multi-Tenancy

DjangoForge uses **row-level multi-tenancy**: every organization's data lives in the same database tables, filtered by an `org` foreign key. There are no separate schemas or databases per tenant.

---

## Data model

```
User (accounts.User)
  │ one-to-many (via Membership)
  ▼
Organization (organizations.Organization)
  │
  ├── Membership  (user + org + role)
  ├── Invitation  (pending email invites)
  └── ... (every other model has an org FK)
```

### Organization

```python
class Organization(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name         = models.CharField(max_length=100)
    slug         = models.SlugField(unique=True)
    plan         = models.CharField(choices=["free","starter","pro"])
    trial_ends_at = models.DateTimeField(null=True)
    stripe_customer_id = models.CharField(null=True)
    created_at   = models.DateTimeField(auto_now_add=True)
```

### Membership roles

| Role | Permissions |
|------|-------------|
| `owner` | Full access, can delete org, transfer ownership |
| `admin` | Manage members, settings (cannot delete org) |
| `member` | Read/write to org data |
| `billing_admin` | Manage billing only |

---

## How tenancy is enforced

### 1. TenantMiddleware (request scoping)

`apps/organizations/middleware.py` runs on every request:

```python
class TenantMiddleware:
    def __call__(self, request):
        if request.user.is_authenticated:
            org_id = request.session.get("current_org_id")
            if org_id:
                request.org = Organization.objects.get(id=org_id)
                request.membership = Membership.objects.get(
                    org=request.org, user=request.user
                )
            else:
                request.org = None
                request.membership = None
        return self.get_response(request)
```

After middleware runs, every view can access `request.org` and `request.membership` without a database query.

### 2. OrgScopedManager (queryset scoping)

Models that belong to an org use `OrgScopedManager`:

```python
class Widget(models.Model):
    org      = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name     = models.CharField(max_length=100)

    objects  = OrgScopedManager()  # scoped to current org
    unscoped = models.Manager()    # for admin / cross-org queries
```

`OrgScopedManager` reads the current org from a thread-local variable set by middleware:

```python
class OrgScopedManager(models.Manager):
    def get_queryset(self):
        org = _thread_locals.current_org
        if org is None:
            return super().get_queryset()
        return super().get_queryset().filter(org=org)
```

This means `Widget.objects.all()` automatically returns only the current org's widgets. You never accidentally return another org's data.

> **Always use `Widget.unscoped.all()`** in management commands, Celery tasks, and admin views where there is no request context.

### 3. CBV Mixins

Enforce org membership at the view level:

```python
class OrgRequiredMixin:
    """Redirects to org creation if user has no active org."""
    def dispatch(self, request, *args, **kwargs):
        if not getattr(request, "org", None):
            return redirect("organizations:create")
        return super().dispatch(request, *args, **kwargs)

class OrgAdminMixin(OrgRequiredMixin):
    """Raises 403 if the user is not an admin or owner."""
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.membership.role not in ("owner", "admin"):
            raise PermissionDenied
        return response

class OrgOwnerMixin(OrgRequiredMixin):
    """Raises 403 if the user is not the owner."""
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.membership.role != "owner":
            raise PermissionDenied
        return response
```

Usage:

```python
class SettingsView(OrgAdminMixin, TemplateView):
    template_name = "organizations/settings.html"

class TransferOwnershipView(OrgOwnerMixin, FormView):
    ...
```

### 4. Context processor

`apps/organizations/context_processors.py` injects org data into every template:

```python
def org_context(request):
    return {
        "current_org": getattr(request, "org", None),
        "membership": getattr(request, "membership", None),
        "user_orgs": get_user_orgs(request.user),
    }
```

In any template:

```html
<span>{{ current_org.name }}</span>
{% if membership.role == "owner" %}
  <a href="{% url 'organizations:settings' %}">Settings</a>
{% endif %}
```

---

## Switching organizations

Users can belong to multiple organizations. The org switcher in the sidebar calls:

```
POST /organizations/switch/<org_id>/
```

This sets `request.session["current_org_id"] = org_id` and redirects to the dashboard.

---

## Adding a new tenant-scoped model

When you create a model that should be scoped to an org:

```python
from apps.organizations.managers import OrgScopedManager

class Report(models.Model):
    org      = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE)
    title    = models.CharField(max_length=200)

    objects  = OrgScopedManager()
    unscoped = models.Manager()

    class Meta:
        ordering = ["-created_at"]
```

That's it — `Report.objects.all()` is now scoped automatically in any view context.

---

## Invitations

```
Invitation.create(email, org, invited_by, role)
  → sends email with token link
  → link: /organizations/accept-invite/<token>/
  → creates User (if new) + Membership
```

Tokens are HMAC-based with a 7-day expiry. They are single-use (marked `accepted=True` after use).

---

## Trial period

New organizations get a 14-day trial by default. The trial end date is stored in `Organization.trial_ends_at`.

```python
org.is_on_trial   # True if trial hasn't expired
org.trial_expired # True if trial ended with no paid plan
org.is_paid       # True if plan is "starter" or "pro"
```

Templates and views check `org.is_on_trial` to show trial banners and feature gates.
