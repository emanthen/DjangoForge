from django.contrib.auth import user_logged_in, user_logged_out
from django.dispatch import receiver

from apps.accounts.utils import get_client_ip


@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    ip = get_client_ip(request)
    user.last_login_ip = ip
    user.save(update_fields=["last_login_ip"])

    from apps.audit.utils import log_event
    log_event("user.login", request=request, actor=user)


@receiver(user_logged_out)
def on_user_logged_out(sender, request, user, **kwargs):
    if user:
        from apps.audit.utils import log_event
        log_event("user.logout", request=request, actor=user)
