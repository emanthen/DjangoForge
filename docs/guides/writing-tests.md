# Writing Tests

DjangoForge uses **pytest** with **pytest-django** and **factory-boy** for fixtures. Tests live in `tests/` directories inside each app.

---

## Running tests

```bash
# All tests
pytest

# With coverage
pytest --cov=apps --cov-report=term-missing

# Specific app
pytest apps/accounts/

# Specific test
pytest apps/accounts/tests/test_signup.py::TestSignup::test_creates_user

# Fast — stop on first failure
pytest -x

# Show output (print statements)
pytest -s

# Re-run only failed tests from last run
pytest --lf
```

---

## Test configuration

Settings are in `config/settings/testing.py`. Key differences from development:

```python
CELERY_TASK_ALWAYS_EAGER = True     # tasks run synchronously
CELERY_TASK_EAGER_PROPAGATES = True # task exceptions are raised
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]  # fast hashing
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"        # in-memory email
```

The test database is created automatically by pytest-django. Use `--reuse-db` to skip re-creation between runs (default via `pyproject.toml`).

---

## Fixtures

Fixtures are defined in `conftest.py` files at the root and inside each app. Global fixtures (used across apps) are in the root `conftest.py`.

### Built-in fixtures

```python
# conftest.py provides these globally:
@pytest.fixture
def user(db):
    """A basic active user with verified email."""

@pytest.fixture
def org(db, user):
    """An organization owned by the test user."""

@pytest.fixture
def membership(db, user, org):
    """The owner membership linking user to org."""

@pytest.fixture
def client(db):
    """Django test client (unauthenticated)."""

@pytest.fixture
def auth_client(db, user, org):
    """Authenticated test client with org session set."""
    client = Client()
    client.force_login(user)
    session = client.session
    session["current_org_id"] = str(org.id)
    session.save()
    return client
```

### Factory Boy factories

```python
# apps/accounts/tests/factories.py
import factory
from factory.django import DjangoModelFactory
from django.utils.timezone import now
from apps.accounts.models import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email       = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name  = factory.Faker("first_name")
    last_name   = factory.Faker("last_name")
    password    = factory.PostGenerationMethodCall("set_password", "testpass123!")
    is_active   = True
    email_verified_at = factory.LazyFunction(now)
```

```python
# apps/organizations/tests/factories.py
class OrganizationFactory(DjangoModelFactory):
    class Meta:
        model = Organization

    name = factory.Sequence(lambda n: f"Org {n}")
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
    plan = "free"
```

---

## Writing a view test

```python
# apps/reports/tests/test_views.py
import pytest
from django.urls import reverse
from .factories import ReportFactory


@pytest.mark.django_db
class TestReportListView:
    url = reverse("reports:list")

    def test_requires_login(self, client):
        resp = client.get(self.url)
        assert resp.status_code == 302
        assert "/login/" in resp["Location"]

    def test_returns_200_for_member(self, auth_client):
        resp = auth_client.get(self.url)
        assert resp.status_code == 200

    def test_shows_org_reports(self, auth_client, org):
        report = ReportFactory(org=org, title="Q1 Revenue")
        resp = auth_client.get(self.url)
        assert "Q1 Revenue" in resp.content.decode()

    def test_cross_org_isolation(self, auth_client, other_org):
        ReportFactory(org=other_org, title="Confidential")
        resp = auth_client.get(self.url)
        assert "Confidential" not in resp.content.decode()
```

---

## Writing a model test

```python
@pytest.mark.django_db
class TestReport:
    def test_str(self, org):
        report = ReportFactory(org=org, title="Q1")
        assert str(report) == "Q1"

    def test_org_scoped_manager(self, org, other_org):
        ReportFactory(org=org)
        ReportFactory(org=other_org)

        # Simulate a request with org context
        from apps.organizations.middleware import set_current_org
        set_current_org(org)

        assert Report.objects.count() == 1   # only sees current org
        assert Report.unscoped.count() == 2  # sees all
```

---

## Writing an API test

```python
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
class TestReportAPI:
    def test_list_requires_auth(self, client):
        resp = client.get("/api/reports/")
        assert resp.status_code == 401

    def test_create_report(self, api_client, org):
        resp = api_client.post("/api/reports/", {"title": "My Report"})
        assert resp.status_code == 201
        assert resp.json()["title"] == "My Report"
```

---

## Testing emails

pytest-django provides `mailoutbox` to capture sent emails:

```python
def test_verification_email_sent(self, auth_client, user, mailoutbox):
    auth_client.post(reverse("accounts:signup"), {
        "email": "new@example.com",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
    })
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == ["new@example.com"]
    assert "verify" in mailoutbox[0].subject.lower()
```

---

## Testing Celery tasks

With `CELERY_TASK_ALWAYS_EAGER = True`, tasks run synchronously in tests:

```python
def test_send_invite_email(self, org, user, mailoutbox):
    from apps.organizations.tasks import send_invitation_email
    send_invitation_email.delay(
        email="invitee@example.com",
        org_id=str(org.id),
        invited_by_id=user.id,
    )
    assert len(mailoutbox) == 1
    assert "invitee@example.com" in mailoutbox[0].to
```

---

## Coverage requirements

CI enforces ≥70% coverage across the `apps/` directory:

```bash
pytest --cov=apps --cov-fail-under=70
```

Excluded from coverage (configured in `pyproject.toml`):
- `*/migrations/*`
- `*/tests/*`
- `*/management/*`

---

## Test organization rules

1. One `tests/` directory per app
2. One test file per view module or feature area
3. Factories in `tests/factories.py` per app
4. Use `@pytest.mark.django_db` on every class or function that hits the DB
5. Prefer `auth_client` fixture over manually calling `force_login`
6. Always test cross-org isolation for any queryset
7. Don't use `mock.patch` on database queries — use the real DB
