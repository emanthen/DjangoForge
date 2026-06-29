import threading

from django.db import models

_thread_local = threading.local()


def set_current_org(org):
    _thread_local.current_org = org


def get_current_org():
    return getattr(_thread_local, "current_org", None)


class OrgScopedManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        org = get_current_org()
        if org is not None:
            return qs.filter(org=org)
        return qs
