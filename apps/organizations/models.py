import secrets
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

# All querysets must be scoped to org via .filter(org=request.org)


def generate_token():
    return secrets.token_urlsafe(32)


class Organization(models.Model):
    PLAN_FREE = "free"
    PLAN_STARTER = "starter"
    PLAN_PRO = "pro"
    PLAN_ENTERPRISE = "enterprise"

    PLAN_CHOICES = [
        (PLAN_FREE, "Free"),
        (PLAN_STARTER, "Starter"),
        (PLAN_PRO, "Pro"),
        (PLAN_ENTERPRISE, "Enterprise"),
    ]

    INDUSTRY_CHOICES = [
        ("technology", "Technology & Software"),
        ("finance", "Finance & Banking"),
        ("healthcare", "Healthcare"),
        ("education", "Education"),
        ("ecommerce", "E-Commerce & Retail"),
        ("media", "Media & Entertainment"),
        ("manufacturing", "Manufacturing"),
        ("real_estate", "Real Estate"),
        ("legal", "Legal & Professional Services"),
        ("government", "Government"),
        ("nonprofit", "Non-Profit"),
        ("consulting", "Consulting & Services"),
        ("other", "Other"),
    ]

    SIZE_CHOICES = [
        ("1", "Just me"),
        ("2_10", "2–10 employees"),
        ("11_50", "11–50 employees"),
        ("51_200", "51–200 employees"),
        ("201_500", "201–500 employees"),
        ("501_plus", "501+ employees"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_orgs",
    )
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default=PLAN_FREE)
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    logo = models.ImageField(upload_to="org_logos/", blank=True, null=True)
    # Company profile
    industry = models.CharField(max_length=50, blank=True, choices=INDUSTRY_CHOICES)
    company_size = models.CharField(max_length=20, blank=True, choices=SIZE_CHOICES)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    # Contact & registration
    phone = models.CharField(max_length=30, blank=True)
    support_email = models.EmailField(blank=True)
    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    registration_number = models.CharField(max_length=100, blank=True)
    # Onboarding
    onboarding_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Organization.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def is_on_trial(self):
        return bool(self.trial_ends_at and self.trial_ends_at > timezone.now())

    @property
    def is_paid(self):
        return self.plan != self.PLAN_FREE

    def member_count(self):
        return self.memberships.count()


class Membership(models.Model):
    ROLE_OWNER = "owner"
    ROLE_ADMIN = "admin"
    ROLE_MEMBER = "member"
    ROLE_BILLING_ADMIN = "billing_admin"

    ROLES = [
        (ROLE_OWNER, "Owner"),
        (ROLE_ADMIN, "Admin"),
        (ROLE_MEMBER, "Member"),
        (ROLE_BILLING_ADMIN, "Billing Admin"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=ROLES, default=ROLE_MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "org")
        ordering = ["joined_at"]

    def __str__(self):
        return f"{self.user.email} in {self.org.name} as {self.role}"

    @property
    def is_owner(self):
        return self.role == self.ROLE_OWNER

    @property
    def is_admin_or_owner(self):
        return self.role in (self.ROLE_OWNER, self.ROLE_ADMIN)


class Invitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="invitations")
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_invitations",
    )
    email = models.EmailField()
    role = models.CharField(max_length=20, choices=Membership.ROLES, default=Membership.ROLE_MEMBER)
    token = models.CharField(max_length=64, unique=True, default=generate_token)
    accepted_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invite {self.email} to {self.org.name}"

    @property
    def is_expired(self):
        return self.expires_at < timezone.now()

    @property
    def is_accepted(self):
        return self.accepted_at is not None
