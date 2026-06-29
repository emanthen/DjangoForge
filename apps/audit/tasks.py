from celery import shared_task
from django.conf import settings
from django.utils import timezone


@shared_task(name="audit.cleanup_old_audit_events")
def cleanup_old_audit_events():
    from apps.audit.models import AuditEvent

    retention_days = getattr(settings, "AUDIT_LOG_RETENTION_DAYS", 90)
    cutoff = timezone.now() - timezone.timedelta(days=retention_days)
    deleted_count, _ = AuditEvent.objects.filter(created_at__lt=cutoff).delete()
    return f"Deleted {deleted_count} audit events older than {retention_days} days"
