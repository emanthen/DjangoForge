from django.conf import settings
from django.db import models


class Flag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    enabled_globally = models.BooleanField(default=False)
    enabled_for_orgs = models.ManyToManyField(
        "organizations.Organization", blank=True, related_name="enabled_flags"
    )
    enabled_for_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="enabled_flags"
    )
    percentage_rollout = models.IntegerField(default=0, help_text="0-100")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def is_enabled_for(self, user, org=None):
        if self.enabled_globally:
            return True
        if org and self.enabled_for_orgs.filter(pk=org.pk).exists():
            return True
        if user and not user.is_anonymous and self.enabled_for_users.filter(pk=user.pk).exists():
            return True
        if self.percentage_rollout > 0 and user and not user.is_anonymous:
            return hash(str(user.id)) % 100 < self.percentage_rollout
        return False
