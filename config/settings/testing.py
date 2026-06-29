from .base import *  # noqa: F401, F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "TEST": {"NAME": ":memory:"},
    }
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

AXES_ENABLED = False

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

ACCOUNT_EMAIL_VERIFICATION = "none"

STRIPE_SECRET_KEY = "sk_test_fake_key_for_testing"
STRIPE_PUBLISHABLE_KEY = "pk_test_fake_key_for_testing"
DJSTRIPE_WEBHOOK_SECRET = "whsec_fake_secret_for_testing"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {"null": {"class": "logging.NullHandler"}},
    "root": {"handlers": ["null"]},
}
