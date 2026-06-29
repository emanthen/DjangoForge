from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Seed the database with development data"

    def handle(self, *args, **options):
        from django.contrib.auth import get_user_model
        from apps.organizations.models import Organization, Membership, Invitation
        from apps.flags.models import Flag
        from apps.audit.utils import log_event

        User = get_user_model()

        self.stdout.write("Creating users...")

        admin, _ = User.objects.get_or_create(
            email="admin@djangoforge.dev",
            defaults={
                "first_name": "Admin",
                "last_name": "User",
                "is_staff": True,
                "is_superuser": True,
                "email_verified_at": timezone.now(),
            },
        )
        admin.set_password("admin123")
        admin.save()

        alice, _ = User.objects.get_or_create(
            email="alice@example.com",
            defaults={
                "first_name": "Alice",
                "last_name": "Smith",
                "email_verified_at": timezone.now(),
            },
        )
        alice.set_password("demo123")
        alice.save()

        bob, _ = User.objects.get_or_create(
            email="bob@example.com",
            defaults={
                "first_name": "Bob",
                "last_name": "Jones",
                "email_verified_at": timezone.now(),
            },
        )
        bob.set_password("demo123")
        bob.save()

        self.stdout.write("Creating organizations...")

        acme, _ = Organization.objects.get_or_create(
            slug="acme-corp",
            defaults={
                "name": "Acme Corp",
                "owner": alice,
                "plan": "pro",
            },
        )

        Membership.objects.get_or_create(
            user=alice, org=acme, defaults={"role": "owner"}
        )
        Membership.objects.get_or_create(
            user=bob, org=acme, defaults={"role": "admin"}
        )

        startup, _ = Organization.objects.get_or_create(
            slug="startup-inc",
            defaults={
                "name": "Startup Inc",
                "owner": bob,
                "plan": "free",
                "trial_ends_at": timezone.now() + timezone.timedelta(days=14),
            },
        )
        Membership.objects.get_or_create(
            user=bob, org=startup, defaults={"role": "owner"}
        )
        Membership.objects.get_or_create(
            user=alice, org=startup, defaults={"role": "member"}
        )

        self.stdout.write("Creating invitation...")
        Invitation.objects.get_or_create(
            org=acme,
            email="charlie@example.com",
            defaults={
                "invited_by": alice,
                "role": "member",
                "expires_at": timezone.now() + timezone.timedelta(days=7),
            },
        )

        self.stdout.write("Creating feature flags...")
        ai_flag, _ = Flag.objects.get_or_create(
            name="ai_features",
            defaults={"description": "AI-powered features", "enabled_globally": False},
        )
        ai_flag.enabled_for_orgs.add(acme)

        Flag.objects.get_or_create(
            name="new_dashboard",
            defaults={"description": "Revamped dashboard UI", "enabled_globally": True},
        )

        self.stdout.write("Creating audit events...")
        for action in [
            "user.signup", "user.login", "org.created", "member.invited",
            "billing.subscription_created", "user.profile_updated",
            "org.settings_updated", "member.role_changed", "user.login", "user.logout",
        ]:
            log_event(action, org=acme, actor=alice)

        self.stdout.write(self.style.SUCCESS("\n✅ Seed data created!"))
        self.stdout.write("   Admin:  admin@djangoforge.dev / admin123")
        self.stdout.write("   Alice:  alice@example.com / demo123")
        self.stdout.write("   Bob:    bob@example.com / demo123")
        self.stdout.write("\n   Open http://localhost:8000/login/")
