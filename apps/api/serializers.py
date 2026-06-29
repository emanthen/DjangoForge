from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.organizations.models import Membership, Organization

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "full_name", "avatar_url", "date_joined"]
        read_only_fields = ["id", "email", "date_joined"]

    def get_avatar_url(self, obj):
        request = self.context.get("request")
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "avatar"]


class OrganizationSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ["id", "name", "slug", "plan", "member_count", "created_at"]
        read_only_fields = ["id", "slug", "created_at"]

    def get_member_count(self, obj):
        return obj.memberships.count()


class MembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Membership
        fields = ["id", "user", "role", "joined_at"]
        read_only_fields = ["id", "joined_at"]
