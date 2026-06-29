from django.contrib import admin

from apps.audit.models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ["actor", "org", "action", "resource_type", "ip_address", "created_at"]
    list_filter = ["action", "created_at"]
    search_fields = ["actor__email", "action", "resource_type", "resource_id"]
    readonly_fields = [
        "id", "actor", "org", "action", "resource_type", "resource_id",
        "metadata", "ip_address", "user_agent", "created_at",
    ]
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
