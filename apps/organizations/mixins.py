from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


class OrgRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not hasattr(request, "org") or not request.org:
            return redirect("organizations:create")
        self.org = request.org
        self.membership = request.membership
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class OrgAdminMixin(OrgRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.user.is_authenticated and getattr(request, "org", None):
            if not self.membership or not self.membership.is_admin_or_owner:
                raise PermissionDenied
        return response


class OrgOwnerMixin(OrgRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.user.is_authenticated and getattr(request, "org", None):
            if not self.membership or not self.membership.is_owner:
                raise PermissionDenied
        return response
