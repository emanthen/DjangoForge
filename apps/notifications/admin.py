from django.contrib import admin

from apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "type", "is_read", "created_at"]
    list_filter = ["type", "created_at"]
    search_fields = ["title", "user__email"]
    readonly_fields = ["created_at"]
