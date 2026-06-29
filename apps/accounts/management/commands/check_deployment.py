import os
import sys

from django.core.management.base import BaseCommand

REQUIRED_ENV_VARS = [
    "SECRET_KEY",
    "DATABASE_URL",
    "REDIS_URL",
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "DEFAULT_FROM_EMAIL",
    "ALLOWED_HOSTS",
]


class Command(BaseCommand):
    help = "Validate all required environment variables before serving traffic"

    def handle(self, *args, **options):
        missing = []
        for var in REQUIRED_ENV_VARS:
            if not os.environ.get(var):
                missing.append(var)

        if missing:
            self.stderr.write(self.style.ERROR("❌ Missing required environment variables:"))
            for var in missing:
                self.stderr.write(f"   - {var}")
            sys.exit(1)

        self.stdout.write(self.style.SUCCESS("✅ All required environment variables are set."))
