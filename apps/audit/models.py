import uuid

from django.conf import settings
from django.db import models


class AuditEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_events",
    )
    org = models.ForeignKey(
        "organizations.Organization",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_events",
    )
    action = models.CharField(max_length=100, db_index=True)
    resource_type = models.CharField(max_length=100, blank=True)
    resource_id = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["org", "created_at"]),
            models.Index(fields=["actor", "created_at"]),
            models.Index(fields=["action"]),
        ]

    def __str__(self):
        actor = self.actor.email if self.actor else "system"
        return f"{actor} — {self.action} @ {self.created_at:%Y-%m-%d %H:%M}"
