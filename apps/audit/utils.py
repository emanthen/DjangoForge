import logging

logger = logging.getLogger(__name__)


def log_event(action, request=None, org=None, actor=None, resource=None, metadata=None):
    try:
        from apps.audit.models import AuditEvent

        ip_address = None
        user_agent = ""

        if request:
            if actor is None and request.user.is_authenticated:
                actor = request.user
            if org is None:
                org = getattr(request, "org", None)
            ip_address = _get_client_ip(request)
            user_agent = request.META.get("HTTP_USER_AGENT", "")[:500]

        resource_type = resource.__class__.__name__ if resource else ""
        resource_id = str(resource.pk) if resource else ""

        AuditEvent.objects.create(
            actor=actor,
            org=org,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )
    except Exception as e:
        logger.error("Failed to create audit event for action %s: %s", action, e)


def _get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
