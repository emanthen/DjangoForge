from django.contrib import admin

from apps.billing.models import WebhookEvent


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ["stripe_id", "event_type", "status", "processed_at"]
    list_filter = ["status", "event_type", "processed_at"]
    search_fields = ["stripe_id", "event_type"]
    readonly_fields = ["stripe_id", "event_type", "processed_at", "status", "error_message"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
