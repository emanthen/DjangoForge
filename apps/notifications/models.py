import uuid

from django.conf import settings
from django.db import models


class Notification(models.Model):
    TYPE_INFO = "info"
    TYPE_SUCCESS = "success"
    TYPE_WARNING = "warning"
    TYPE_ERROR = "error"

    TYPE_CHOICES = [
        (TYPE_INFO, "Info"),
        (TYPE_SUCCESS, "Success"),
        (TYPE_WARNING, "Warning"),
        (TYPE_ERROR, "Error"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_INFO)
    title = models.CharField(max_length=200)
    message = models.TextField()
    read_at = models.DateTimeField(null=True, blank=True)
    action_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} → {self.user.email}"

    @property
    def is_read(self):
        return self.read_at is not None
