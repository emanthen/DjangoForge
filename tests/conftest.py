import pytest
from django.test import Client


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def authenticated_client(client, db):
    from tests.factories import UserFactory
    from django.utils import timezone

    user = UserFactory(email_verified_at=timezone.now())
    user.set_password("testpass123")
    user.save()
    client.login(username=user.email, password="testpass123")
    client._user = user
    return client


@pytest.fixture
def user(db):
    from tests.factories import UserFactory
    from django.utils import timezone

    u = UserFactory(email_verified_at=timezone.now())
    u.set_password("testpass123")
    u.save()
    return u


@pytest.fixture
def org(db, user):
    from tests.factories import OrganizationFactory, MembershipFactory
    from apps.organizations.models import Membership

    o = OrganizationFactory(owner=user)
    MembershipFactory(user=user, org=o, role=Membership.ROLE_OWNER)
    return o
