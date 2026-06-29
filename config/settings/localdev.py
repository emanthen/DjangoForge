"""
Local development settings — no Docker, no PostgreSQL, no Redis required.
Uses SQLite + in-memory cache + console email.
"""
from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# SQLite — no PostgreSQL needed
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

# In-memory cache — no Redis needed
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Use database-backed sessions (no Redis)
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# Celery — run tasks synchronously in-process (no worker needed)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Print emails to console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Local file storage (no S3)
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# Skip whitenoise manifest (avoids collectstatic requirement)
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Disable brute-force protection (easier dev logins)
AXES_ENABLED = False

# Skip email verification for faster testing
ACCOUNT_EMAIL_VERIFICATION = "none"

# Fake Stripe keys (billing pages load, no real charges)
STRIPE_SECRET_KEY = "sk_test_fake_key_for_local"
STRIPE_PUBLISHABLE_KEY = "pk_test_fake_key_for_local"
DJSTRIPE_WEBHOOK_SECRET = "whsec_fake_for_local"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "{levelname} {module}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
    },
    "root": {"handlers": ["console"], "level": "DEBUG"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "apps": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
    },
}
