# Adding a New Django App

This guide walks you through adding a new feature as a Django app in DjangoForge, following the project's conventions.

---

## Step 1: Create the app

```bash
python manage.py startapp reports apps/reports
```

This creates the app inside the `apps/` directory where all apps live.

---

## Step 2: Register the app

Add it to `INSTALLED_APPS` in `config/settings/base.py`:

```python
LOCAL_APPS = [
    "apps.accounts",
    "apps.organizations",
    "apps.billing",
    "apps.api",
    "apps.audit",
    "apps.flags",
    "apps.notifications",
    "apps.reports",   # ← add here
]
```

---

## Step 3: Write the model

```python
# apps/reports/models.py
import uuid
from django.db import models
from apps.organizations.managers import OrgScopedManager


class Report(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org        = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE, related_name="reports")
    title      = models.CharField(max_length=200)
    content    = models.TextField(blank=True)
    created_by = models.ForeignKey("accounts.User", null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects    = OrgScopedManager()   # scoped to current org automatically
    unscoped   = models.Manager()     # for admin/Celery (no request context)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
```

**Conventions:**
- UUID primary keys (no auto-incrementing IDs exposed to users)
- `org` FK on every tenant-scoped model
- `OrgScopedManager` as `objects`, `models.Manager()` as `unscoped`
- `created_at` / `updated_at` timestamps

---

## Step 4: Create the migration

```bash
python manage.py makemigrations reports
python manage.py migrate
```

---

## Step 5: Register in admin

```python
# apps/reports/admin.py
from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display  = ["title", "org", "created_by", "created_at"]
    list_filter   = ["org", "created_at"]
    search_fields = ["title", "org__name", "created_by__email"]
    readonly_fields = ["id", "created_at", "updated_at"]
    raw_id_fields = ["org", "created_by"]
```

---

## Step 6: Write views

```python
# apps/reports/views.py
from django.views.generic import ListView, CreateView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from apps.organizations.mixins import OrgRequiredMixin, OrgAdminMixin
from apps.audit.utils import log_event
from .models import Report
from .forms import ReportForm


class ReportListView(OrgRequiredMixin, ListView):
    model = Report
    template_name = "reports/list.html"
    context_object_name = "reports"
    paginate_by = 20


class ReportCreateView(OrgAdminMixin, CreateView):
    model = Report
    form_class = ReportForm
    template_name = "reports/create.html"
    success_url = reverse_lazy("reports:list")

    def form_valid(self, form):
        form.instance.org = self.request.org
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        log_event("report.created", org=self.request.org, actor=self.request.user, request=self.request, metadata={"report_id": str(self.object.id)})
        return response
```

---

## Step 7: Write URLs

```python
# apps/reports/urls.py
from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.ReportListView.as_view(), name="list"),
    path("create/", views.ReportCreateView.as_view(), name="create"),
    path("<uuid:pk>/", views.ReportDetailView.as_view(), name="detail"),
    path("<uuid:pk>/delete/", views.ReportDeleteView.as_view(), name="delete"),
]
```

Include in the root URL conf (`config/urls.py`):

```python
path("reports/", include("apps.reports.urls")),
```

---

## Step 8: Write templates

Create `templates/reports/list.html`:

```html
{% extends "base.html" %}
{% load df_filters %}
{% block title %}Reports — {{ current_org.name }}{% endblock %}

{% block content %}
<div class="max-w-5xl mx-auto px-4 py-8">
  <div class="flex items-center justify-between mb-6">
    <div>
      <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Reports</h1>
      <p class="text-slate-500 dark:text-slate-400 text-sm mt-1">{{ reports.paginator.count }} total</p>
    </div>
    {% if membership.role in "owner,admin" %}
    <a href="{% url 'reports:create' %}" class="btn-primary">+ New Report</a>
    {% endif %}
  </div>

  {% if reports %}
  <div class="card divide-y divide-slate-100 dark:divide-slate-800">
    {% for report in reports %}
    <div class="px-6 py-4 flex items-center justify-between">
      <div>
        <a href="{% url 'reports:detail' report.pk %}" class="font-medium text-slate-900 dark:text-white hover:text-primary-600">
          {{ report.title }}
        </a>
        <p class="text-xs text-slate-400 mt-0.5">{{ report.created_at|date:"M j, Y" }}</p>
      </div>
    </div>
    {% endfor %}
  </div>
  {% else %}
  {% include "components/_empty_state.html" with title="No reports yet" message="Create your first report to get started." action_url=create_url action_label="New Report" %}
  {% endif %}
</div>
{% endblock %}
```

---

## Step 9: Add a sidebar nav item

In `templates/components/_sidebar.html`, add a navigation link:

```html
{% url 'reports:list' as url_reports %}
<a href="{{ url_reports }}"
   class="nav-item {% if request.path|slice:':8' == '/reports' %}active{% endif %}">
  <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
    <path stroke-linecap="round" stroke-linejoin="round" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
  </svg>
  <span>Reports</span>
</a>
```

---

## Step 10: Write tests

```python
# apps/reports/tests/test_views.py
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestReportListView:
    def test_requires_login(self, client):
        resp = client.get(reverse("reports:list"))
        assert resp.status_code == 302  # redirect to login

    def test_shows_org_reports(self, auth_client, org, report_factory):
        report_factory(org=org, title="Q1 Report")
        resp = auth_client.get(reverse("reports:list"))
        assert resp.status_code == 200
        assert "Q1 Report" in resp.content.decode()

    def test_does_not_show_other_org_reports(self, auth_client, other_org, report_factory):
        report_factory(org=other_org, title="Secret Report")
        resp = auth_client.get(reverse("reports:list"))
        assert "Secret Report" not in resp.content.decode()
```

---

## Checklist

- [ ] App created with `startapp` in `apps/` directory
- [ ] Added to `INSTALLED_APPS`
- [ ] Model has `org` FK + `OrgScopedManager` + `unscoped` manager
- [ ] Migration created and applied
- [ ] Admin registered with search/filter
- [ ] Views use `OrgRequiredMixin` (and `OrgAdminMixin` for write views)
- [ ] URLs have `app_name` set, included in `config/urls.py`
- [ ] Templates extend `base.html`, load `df_filters`
- [ ] Sidebar nav item added
- [ ] Tests cover list, create, cross-org isolation
- [ ] Audit events logged for write actions
