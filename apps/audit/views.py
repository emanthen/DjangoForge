from django.views.generic import ListView

from apps.audit.models import AuditEvent
from apps.organizations.mixins import OrgAdminMixin


class AuditLogView(OrgAdminMixin, ListView):
    template_name = "audit/log.html"
    context_object_name = "events"
    paginate_by = 50

    def get_queryset(self):
        qs = AuditEvent.objects.filter(org=self.org).select_related("actor")

        action = self.request.GET.get("action")
        if action:
            qs = qs.filter(action=action)

        actor_email = self.request.GET.get("actor")
        if actor_email:
            qs = qs.filter(actor__email__icontains=actor_email)

        date_from = self.request.GET.get("date_from")
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)

        date_to = self.request.GET.get("date_to")
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["action_choices"] = (
            AuditEvent.objects.filter(org=self.org)
            .values_list("action", flat=True)
            .distinct()
            .order_by("action")
        )
        return ctx
