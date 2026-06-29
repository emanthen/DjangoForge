# Authentication

DjangoForge ships a complete authentication system: email/password, email verification, OAuth (Google + GitHub), password reset, and brute-force protection.

---

## User model

Located at `apps/accounts/models.py`. It extends Django's `AbstractBaseUser`:

```python
class User(AbstractBaseUser, PermissionsMixin):
    email            = models.EmailField(unique=True)
    first_name       = models.CharField(max_length=50, blank=True)
    last_name        = models.CharField(max_length=50, blank=True)
    avatar           = models.ImageField(upload_to="avatars/", blank=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    last_login_ip    = models.GenericIPAddressField(null=True, blank=True)
    is_active        = models.BooleanField(default=True)
    is_staff         = models.BooleanField(default=False)
    date_joined      = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # email is already required

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_email_verified(self):
        return self.email_verified_at is not None
```

The model is registered as `AUTH_USER_MODEL = "accounts.User"` in settings.

---

## Signup flow

1. User fills in the signup form (`SignupView`) — email, first name, last name, password
2. `User` is created with `is_active=True`, `email_verified_at=None`
3. Verification email is sent via Celery task
4. User is logged in immediately (can browse but some features require verification)
5. User clicks the link in the email → `VerifyEmailView`
6. Token is validated, `email_verified_at` is set to `now()`

### Verification token

Tokens are generated using Django's `PasswordResetTokenGenerator` subclass (`apps/accounts/tokens.py`):

```python
class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.email_verified_at}"
```

Tokens encode:
- User PK
- Timestamp (used for 24h expiry check)
- `email_verified_at` (token is invalidated once verification succeeds)

---

## Login flow

1. User submits email + password to `LoginView`
2. `django-axes` checks failure history — blocks if limit reached
3. `authenticate()` checks credentials
4. If `is_active=False`: error shown
5. If credentials wrong: axes records failure
6. On success: `login(request, user)`, then:
   - Check for `?next=` parameter (safe redirect — must start with `/`)
   - Otherwise redirect to `accounts:dashboard`

```python
# Safe open-redirect in LoginView.form_valid()
next_url = self.request.GET.get("next", "")
if next_url and next_url.startswith("/"):
    return redirect(next_url)
return redirect("accounts:dashboard")
```

---

## Password reset

Handled by `django-allauth`. Flow:

1. `GET /accounts/password/reset/` — enter email
2. Email sent with reset link (token valid 72h)
3. `GET /accounts/password/reset/key/<token>/` — enter new password
4. Password updated, user logged in

Customize the email template at `templates/account/email/password_reset_key_message.txt` (allauth format).

---

## Brute-force protection (`django-axes`)

Configured in settings:

```python
AXES_FAILURE_LIMIT = 5           # attempts before lockout
AXES_COOLOFF_TIME = timedelta(hours=1)
AXES_LOCKOUT_CALLABLE = None     # raises PermissionDenied by default
AXES_RESET_ON_SUCCESS = True     # clears failure count after successful login
```

Lockouts can be cleared from the Django admin (Axes → Access Attempts → Delete).

---

## OAuth (Google + GitHub)

Powered by `django-allauth[socialaccount]`.

### Setup

1. **Google**: Create credentials at [console.cloud.google.com](https://console.cloud.google.com/) → APIs & Services → Credentials → OAuth 2.0 Client. Set redirect URI to `https://yourdomain.com/accounts/google/login/callback/`

2. **GitHub**: Register at [github.com/settings/apps](https://github.com/settings/apps). Set callback URL to `https://yourdomain.com/accounts/github/login/callback/`

3. Add keys to `.env`:
   ```dotenv
   GOOGLE_OAUTH_CLIENT_ID=xxx.apps.googleusercontent.com
   GOOGLE_OAUTH_CLIENT_SECRET=xxx
   GITHUB_OAUTH_CLIENT_ID=xxx
   GITHUB_OAUTH_CLIENT_SECRET=xxx
   ```

4. Configure in Django admin: Social Applications → Add.

### What happens on OAuth login

- New user: allauth creates a `User` (email auto-verified) + `SocialAccount` record
- Existing user with same email: allauth links the social account to the existing user
- User returns to `accounts:dashboard`

---

## Session security

Sessions are stored in Redis (not the database or client-side cookies):

```python
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"  # Redis
SESSION_COOKIE_SECURE = True          # HTTPS only
SESSION_COOKIE_HTTPONLY = True        # no JS access
SESSION_COOKIE_SAMESITE = "Lax"      # CSRF protection
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14  # 2 weeks
```

---

## Account deletion

Users can delete their own account from the profile page → Danger Zone tab. Deletion:
- Anonymizes email to `deleted+{id}@djangoforge.dev`
- Sets `is_active = False`
- Removes memberships (orphaned orgs without an owner are flagged)
- Logs the deletion in `AuditEvent`

This approach satisfies GDPR "right to erasure" while preserving referential integrity in audit logs.

---

## Extending the User model

Do **not** add fields directly to `AbstractBaseUser` — Django doesn't support swappable models well after migrations exist.

Instead, create a `UserProfile` model with a `OneToOneField`:

```python
class UserProfile(models.Model):
    user         = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    bio          = models.TextField(blank=True)
    website      = models.URLField(blank=True)
    timezone     = models.CharField(max_length=50, default="UTC")
```

Access in templates: `{{ request.user.profile.timezone }}`

---

## URL reference

| URL name | Path | Description |
|----------|------|-------------|
| `accounts:signup` | `/signup/` | Registration form |
| `accounts:login` | `/login/` | Login form |
| `accounts:logout` | `/logout/` | POST to log out |
| `accounts:dashboard` | `/dashboard/` | Main app dashboard |
| `accounts:profile` | `/profile/` | Edit profile |
| `accounts:verify_email_sent` | `/verify-email/sent/` | "Check your email" page |
| `accounts:verify_email` | `/verify-email/<uidb64>/<token>/` | Verify email link |
| `accounts:delete_account` | `/delete-account/` | Account deletion |
