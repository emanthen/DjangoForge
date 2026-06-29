from django.contrib import admin

from apps.flags.models import Flag


@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = ["name", "enabled_globally", "get_org_count", "get_user_count", "percentage_rollout"]
    search_fields = ["name", "description"]
    filter_horizontal = ["enabled_for_orgs", "enabled_for_users"]

    @admin.display(description="Orgs enabled")
    def get_org_count(self, obj):
        return obj.enabled_for_orgs.count()

    @admin.display(description="Users enabled")
    def get_user_count(self, obj):
        return obj.enabled_for_users.count()
