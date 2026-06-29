# Organizations

Organizations are the core multi-tenant unit in DjangoForge. Every user belongs to one or more organizations. All data (billing, audit events, feature flags, etc.) belongs to an organization.

---

## Creating an organization

New users who have no organization are redirected to `/organizations/create/`. The form collects:
- Organization name (auto-generates a slug)
- Plan selection (defaults to "free")

On creation:
1. `Organization` is created
2. Creator is added as a `Membership` with role `owner`
3. Session is updated with `current_org_id`
4. Redirected to dashboard

---

## Membership roles

| Role | Abbr | Who it's for |
|------|------|-------------|
| `owner` | Owner | The founding user. Full access, can delete or transfer ownership. Only one owner per org. |
| `admin` | Admin | Can manage members, settings, billing (but cannot delete org). |
| `member` | Member | Standard access to org resources. |
| `billing_admin` | Billing | Can access billing only. Cannot change org settings or members. |

### Role checks in views

```python
# Require any membership
class MyView(OrgRequiredMixin, View): ...

# Require admin or owner
class SettingsView(OrgAdminMixin, View): ...

# Require owner only
class TransferOwnershipView(OrgOwnerMixin, View): ...
```

### Role checks in templates

```html
{% if membership.role == "owner" %}
  <a href="{% url 'organizations:settings' %}">Org Settings</a>
{% endif %}

{% if membership.role in "owner,admin" %}
  <button>Invite Member</button>
{% endif %}
```

---

## Inviting members

### Via the UI

1. Open the Members page → Click "Invite Member"
2. Enter the invitee's email and select a role
3. An invitation email is sent (via Celery task)

### Via the API

```http
POST /api/organizations/{org_id}/invitations/
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "newuser@example.com",
  "role": "member"
}
```

### Invitation flow

```
Admin sends invite
  → Invitation(email, org, role, token, expires_at=now()+7days) created
  → Email sent with link: /organizations/accept-invite/<token>/
  → Invitee clicks link
  → If new user: SignupView pre-filled with email, Membership created after signup
  → If existing user: Membership created immediately, redirect to dashboard
```

Tokens are HMAC-signed. They expire after 7 days and are single-use.

---

## Removing members

Admins and owners can remove members from the Members page. Removing a member:
- Deletes the `Membership` record
- Does not delete the user's account
- If removed user was the active org, their session `current_org_id` is cleared on next request

Only owners can remove admins. Admins cannot remove other admins.

---

## Changing roles

Owners and admins can change member roles via the role dropdown on the Members page. Restrictions:
- Only the owner can change another owner's role
- Only one owner per org (changing owner role requires a transfer)

---

## Transferring ownership

Only the current owner can transfer ownership:

1. Go to Org Settings → Transfer Ownership
2. Select a current member to become the new owner
3. Confirm with your password
4. The previous owner becomes an `admin`
5. The selected member becomes `owner`

This is recorded in `AuditEvent`.

---

## Organization settings

Accessible via the Settings tab (admin/owner only):

- **Organization name** — updates slug if changed (redirects are handled)
- **Plan info** — shows current plan, trial status, upgrade CTA
- **Danger zone** — delete organization (owner only)

---

## Switching organizations

If a user belongs to multiple organizations, they can switch using the org switcher in the sidebar:

```http
POST /organizations/switch/<org_id>/
```

This:
1. Validates the user has a membership in the target org
2. Sets `request.session["current_org_id"] = org_id`
3. Redirects to dashboard

---

## Organization plan

Plans are stored in `Organization.plan`:

| Value | Display | Features |
|-------|---------|---------|
| `free` | Free | Limited resources, community support |
| `starter` | Starter ($29/mo) | Full features, email support, 5 members |
| `pro` | Pro ($79/mo) | Everything + priority support, unlimited members |

The plan is updated automatically by the Stripe webhook handler when a subscription changes.

Check plan in views:

```python
if request.org.plan == "free":
    raise PermissionDenied("Upgrade to access this feature")
```

Check plan in templates:

```html
{% if current_org.plan == "free" %}
  <div class="upgrade-banner">Upgrade to Pro</div>
{% endif %}
```

---

## Model reference

### Organization

```python
Organization:
  id            UUID (PK)
  name          str (100)
  slug          str (unique)
  plan          str ["free","starter","pro"]
  trial_ends_at datetime (null)
  stripe_customer_id str (null)
  created_at    datetime
  updated_at    datetime
```

### Membership

```python
Membership:
  id     UUID (PK)
  user   FK → User
  org    FK → Organization
  role   str ["owner","admin","member","billing_admin"]
  joined_at datetime
```

### Invitation

```python
Invitation:
  id         UUID (PK)
  org        FK → Organization
  email      str
  role       str
  token      str (unique, HMAC)
  invited_by FK → User
  accepted   bool
  expires_at datetime
  created_at datetime
```
