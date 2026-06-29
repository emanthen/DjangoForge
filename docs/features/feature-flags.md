# Feature Flags

DjangoForge includes a database-backed feature flag system. Flags can be toggled without a code deploy, making it safe to ship incomplete features and gradually roll them out.

---

## How it works

Flags are stored in the `flags.Flag` model. Each flag has:
- A name (snake_case string key)
- An enabled state (global on/off)
- Optional percentage rollout (e.g. 10% of users)
- Optional per-org targeting
- Optional per-user targeting

---

## Managing flags

Flags are managed from the Django admin at `/admin/flags/flag/`.

### Creating a flag

1. Go to Admin → Flags → Flags → Add Flag
2. Set the name (e.g. `new_dashboard`)
3. Check "Enabled" to turn it on globally
4. Optionally set percentage rollout or target specific orgs/users
5. Save — the flag is live immediately

---

## Using flags in templates

The `FlagProxy` context processor injects all flags into every template automatically:

```html
{% if flags.new_dashboard %}
  {# Show the new dashboard UI #}
  {% include "dashboard/new/index.html" %}
{% else %}
  {# Show the old dashboard UI #}
  {% include "dashboard/index.html" %}
{% endif %}
```

The `flags` object supports attribute access by flag name. Unknown flags return `False` (safe default — missing flag = disabled).

---

## Using flags in views

```python
from apps.flags.models import Flag

class MyView(OrgRequiredMixin, View):
    def get(self, request):
        if not Flag.is_enabled("new_feature", request.user, request.org):
            raise PermissionDenied("Feature not available")
        ...
```

### `Flag.is_enabled(name, user=None, org=None)`

Returns `True` if the flag is enabled for the given user/org context. Logic:

1. Flag doesn't exist → `False`
2. Flag exists but `enabled=False` → `False`
3. Flag has per-org targeting → checks if this org is in the list
4. Flag has per-user targeting → checks if this user is in the list
5. Flag has `percentage` set → uses consistent hashing (`hash(user.id + flag.name) % 100 < percentage`)
6. Otherwise → returns `enabled` value (global on/off)

---

## Using flags in views (decorator)

```python
from apps.flags.decorators import flag_required

@flag_required("new_feature")
def new_feature_view(request):
    ...
```

The decorator redirects to a 404 page if the flag is disabled.

For class-based views:

```python
from django.utils.decorators import method_decorator
from apps.flags.decorators import flag_required

@method_decorator(flag_required("new_feature"), name="dispatch")
class NewFeatureView(OrgRequiredMixin, TemplateView):
    template_name = "new_feature.html"
```

---

## Using flags in Celery tasks

```python
from apps.flags.models import Flag

@app.task
def run_new_pipeline(org_id):
    org = Organization.unscoped.get(id=org_id)
    if not Flag.is_enabled("new_pipeline", org=org):
        return  # skip if flag disabled for this org
    ...
```

---

## Flag model reference

```python
class Flag(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    enabled     = models.BooleanField(default=False)
    percentage  = models.IntegerField(null=True, blank=True)  # 0-100 rollout %
    orgs        = models.ManyToManyField("organizations.Organization", blank=True)
    users       = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    description = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
```

---

## Best practices

**Name flags clearly:** Use snake_case, prefix with feature area: `billing_annual_toggle`, `dashboard_v2`, `api_rate_limit_v2`.

**Clean up old flags:** Once a feature is fully rolled out, remove the flag from the database and the conditional code. Flags are technical debt when left indefinitely.

**Keep the fallback safe:** The code path executed when `flags.my_flag` is `False` should always be the old/safe behavior.

**Don't gate critical paths:** Feature flags are for UI features, not security checks. Don't put authentication or authorization behind a flag.

---

## Example: gradual rollout

Scenario: rolling out a redesigned dashboard to 10% of users, expanding to 100% over 2 weeks.

1. Create flag `dashboard_v2` with `enabled=True, percentage=10`
2. Wrap the new dashboard template:
   ```html
   {% if flags.dashboard_v2 %}
     {% include "dashboard/v2/index.html" %}
   {% else %}
     {% include "dashboard/index.html" %}
   {% endif %}
   ```
3. Monitor metrics (error rate, engagement)
4. Gradually increase `percentage` via admin: 10 → 25 → 50 → 100
5. Once at 100%, remove the flag and the old template
