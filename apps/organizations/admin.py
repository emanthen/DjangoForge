from django.contrib import admin

from apps.organizations.models import Invitation, Membership, Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "plan", "get_member_count", "is_active", "created_at"]
    list_filter = ["plan", "is_active", "created_at"]
    search_fields = ["name", "owner__email", "slug"]
    readonly_fields = ["slug", "created_at", "updated_at"]

    @admin.display(description="Members")
    def get_member_count(self, obj):
        return obj.memberships.count()


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "org", "role", "joined_at"]
    list_filter = ["role", "joined_at"]
    search_fields = ["user__email", "org__name"]
    readonly_fields = ["joined_at"]


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ["email", "org", "role", "invited_by", "is_expired", "accepted_at", "created_at"]
    list_filter = ["role", "created_at"]
    search_fields = ["email", "org__name"]
    readonly_fields = ["token", "created_at"]

    @admin.display(boolean=True)
    def is_expired(self, obj):
        return obj.is_expired
