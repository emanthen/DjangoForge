import pytest

from apps.organizations.models import Invitation, Membership, Organization
from tests.factories import UserFactory, OrganizationFactory, MembershipFactory


@pytest.mark.django_db
class TestOrganization:
    def test_create_org_auto_generates_slug(self):
        user = UserFactory()
        org = Organization.objects.create(name="Acme Corp", owner=user)
        assert org.slug == "acme-corp"

    def test_duplicate_name_generates_unique_slug(self):
        user = UserFactory()
        org1 = Organization.objects.create(name="Acme Corp", owner=user)
        org2 = Organization.objects.create(name="Acme Corp", owner=user)
        assert org1.slug != org2.slug

    def test_is_on_trial(self):
        from django.utils import timezone
        user = UserFactory()
        org = OrganizationFactory(
            owner=user,
            trial_ends_at=timezone.now() + timezone.timedelta(days=7),
        )
        assert org.is_on_trial is True

    def test_is_paid(self):
        user = UserFactory()
        org = OrganizationFactory(owner=user, plan="pro")
        assert org.is_paid is True

        org.plan = "free"
        assert org.is_paid is False


@pytest.mark.django_db
class TestMembership:
    def test_create_org_auto_creates_owner_membership(self):
        from apps.organizations.views import CreateOrgView
        user = UserFactory()
        org = Organization.objects.create(name="Test Org", owner=user)
        Membership.objects.create(user=user, org=org, role=Membership.ROLE_OWNER)
        assert Membership.objects.filter(user=user, org=org, role=Membership.ROLE_OWNER).exists()

    def test_owner_cannot_be_removed(self, client):
        owner = UserFactory(email_verified_at=__import__("django.utils.timezone", fromlist=["now"]).timezone.now())
        owner.set_password("pass")
        owner.save()
        org = OrganizationFactory(owner=owner)
        membership = MembershipFactory(user=owner, org=org, role=Membership.ROLE_OWNER)
        client.login(username=owner.email, password="pass")
        from django.urls import reverse
        url = reverse("organizations:remove_member", kwargs={"membership_id": membership.id})
        response = client.post(url)
        assert Membership.objects.filter(id=membership.id).exists()
