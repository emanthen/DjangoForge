# REST API

DjangoForge ships a REST API built on **Django REST Framework (DRF)** with automatic OpenAPI documentation.

---

## Base URL

```
https://yourdomain.com/api/
```

All API endpoints are under `/api/` and are versioned via URL path.

---

## Interactive documentation

| URL | Description |
|-----|-------------|
| `/api/schema/` | OpenAPI 3.0 JSON schema (machine-readable) |
| `/api/docs/` | Swagger UI (browser-based testing) |
| `/api/redoc/` | ReDoc (clean reference) |

---

## Authentication

The API supports two authentication methods:

### 1. Session authentication (browser)

Automatically used when the client has a valid Django session cookie. Useful for HTMX requests and browser-based SPA usage.

### 2. Token authentication

```http
Authorization: Bearer <token>
```

Generate a token:

```http
POST /api/auth/token/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

Response:

```json
{
  "token": "abc123...",
  "user_id": 1,
  "email": "user@example.com"
}
```

Tokens do not expire by default. To invalidate, delete the token from the admin.

---

## Rate limiting

| Client type | Limit |
|-------------|-------|
| Anonymous | 100 requests/hour |
| Authenticated | 1000 requests/hour |

Rate limits are per IP for anonymous clients, per user for authenticated clients.

When rate limited, the response is:

```http
HTTP 429 Too Many Requests
Retry-After: 3600
```

---

## Endpoints

### Health check

```http
GET /api/health/
```

Returns `200 OK` when the app is up. Does not require authentication. Used by the ALB health check.

```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

### Current user

```http
GET /api/me/
Authorization: Bearer <token>
```

```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "Ada",
  "last_name": "Lovelace",
  "full_name": "Ada Lovelace",
  "is_email_verified": true,
  "date_joined": "2026-01-01T00:00:00Z"
}
```

### Organizations

```http
GET    /api/organizations/           # List orgs the user belongs to
POST   /api/organizations/           # Create a new org
GET    /api/organizations/{id}/      # Retrieve org details
PATCH  /api/organizations/{id}/      # Update org name
DELETE /api/organizations/{id}/      # Delete org (owner only)
```

**List response:**

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Acme Corp",
    "slug": "acme-corp",
    "plan": "starter",
    "created_at": "2026-01-01T00:00:00Z",
    "membership": {
      "role": "owner",
      "joined_at": "2026-01-01T00:00:00Z"
    }
  }
]
```

---

## Permissions

API views use DRF permission classes:

```python
class OrganizationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOrgMember]
    serializer_class = OrganizationSerializer
```

Custom permission classes (`apps/api/permissions.py`):

| Class | Description |
|-------|-------------|
| `IsOrgMember` | User must be a member of the target org |
| `IsOrgAdmin` | User must be admin or owner |
| `IsOrgOwner` | User must be the org owner |

---

## Serializers

Serializers are in `apps/api/serializers.py`:

```python
class OrganizationSerializer(serializers.ModelSerializer):
    membership = MembershipSerializer(source="get_current_membership", read_only=True)

    class Meta:
        model = Organization
        fields = ["id", "name", "slug", "plan", "created_at", "membership"]
        read_only_fields = ["id", "slug", "plan", "created_at"]
```

---

## Error responses

All errors follow a consistent format:

```json
{
  "detail": "Authentication credentials were not provided."
}
```

For validation errors:

```json
{
  "email": ["Enter a valid email address."],
  "name": ["This field is required."]
}
```

---

## Adding a new endpoint

1. Create a serializer in `apps/api/serializers.py`
2. Create a view/viewset in `apps/api/views.py`
3. Add URL to `apps/api/urls.py`
4. Run the app and visit `/api/docs/` — the endpoint appears automatically (drf-spectacular auto-discovers views)

Example:

```python
# apps/api/serializers.py
class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ["id", "title", "created_at"]

# apps/api/views.py
class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated, IsOrgMember]

    def get_queryset(self):
        return Report.objects.filter(org=self.request.org)

# apps/api/urls.py
router.register("reports", ReportViewSet, basename="report")
```

---

## OpenAPI schema customization

Use drf-spectacular decorators to enrich the auto-generated docs:

```python
from drf_spectacular.utils import extend_schema, OpenApiExample

@extend_schema(
    summary="List reports for the current organization",
    responses={200: ReportSerializer(many=True)},
    examples=[
        OpenApiExample("Example", value={"id": 1, "title": "Q1 Report"})
    ]
)
def list(self, request, *args, **kwargs):
    ...
```

---

## Testing API endpoints

```python
# apps/api/tests/test_reports.py
import pytest
from rest_framework.test import APIClient

@pytest.fixture
def api_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client

def test_list_reports(api_client, org, report_factory):
    report_factory(org=org, title="Q1 Report")
    resp = api_client.get("/api/reports/")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["title"] == "Q1 Report"
```
