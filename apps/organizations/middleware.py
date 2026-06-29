from apps.organizations.managers import set_current_org


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.org = None
        request.membership = None

        if request.user.is_authenticated:
            self._attach_org(request)

        set_current_org(request.org)
        response = self.get_response(request)
        set_current_org(None)
        return response

    def _attach_org(self, request):
        from apps.organizations.models import Membership, Organization

        active_org_id = request.session.get("active_org_id")

        if active_org_id:
            try:
                membership = (
                    Membership.objects.select_related("org")
                    .get(user=request.user, org__id=active_org_id, org__is_active=True)
                )
                request.org = membership.org
                request.membership = membership
                return
            except Membership.DoesNotExist:
                del request.session["active_org_id"]

        membership = (
            Membership.objects.select_related("org")
            .filter(user=request.user, org__is_active=True)
            .first()
        )

        if membership:
            request.org = membership.org
            request.membership = membership
            request.session["active_org_id"] = str(membership.org.id)
