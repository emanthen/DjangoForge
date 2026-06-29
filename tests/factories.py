import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from apps.organizations.models import Invitation, Membership, Organization

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    email_verified_at = None

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)


class OrganizationFactory(DjangoModelFactory):
    class Meta:
        model = Organization

    name = factory.Sequence(lambda n: f"Organization {n}")
    owner = factory.SubFactory(UserFactory)
    plan = Organization.PLAN_FREE
    is_active = True


class MembershipFactory(DjangoModelFactory):
    class Meta:
        model = Membership

    user = factory.SubFactory(UserFactory)
    org = factory.SubFactory(OrganizationFactory)
    role = Membership.ROLE_MEMBER


class InvitationFactory(DjangoModelFactory):
    class Meta:
        model = Invitation

    org = factory.SubFactory(OrganizationFactory)
    invited_by = factory.SubFactory(UserFactory)
    email = factory.Faker("email")
    role = Membership.ROLE_MEMBER

    @factory.lazy_attribute
    def expires_at(self):
        from django.utils import timezone
        return timezone.now() + timezone.timedelta(days=7)
