from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User
from apps.accounts.utils import send_verification_email


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "full_name", "is_active", "has_verified_email", "date_joined"]
    list_filter = ["is_active", "is_staff", "date_joined"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["-date_joined"]
    readonly_fields = ["date_joined", "last_login", "email_verified_at", "last_login_ip"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "avatar")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            _("Activity"),
            {"fields": ("date_joined", "last_login", "email_verified_at", "last_login_ip")},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "first_name", "last_name", "password1", "password2"),
            },
        ),
    )

    actions = ["send_verification_email_action"]

    @admin.action(description="Send verification email")
    def send_verification_email_action(self, request, queryset):
        count = 0
        for user in queryset.filter(email_verified_at__isnull=True):
            send_verification_email(user, request)
            count += 1
        self.message_user(request, f"Sent {count} verification email(s).")
