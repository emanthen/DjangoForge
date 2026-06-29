from rest_framework.permissions import BasePermission


class IsOrgMember(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and getattr(request, "org", None))


class IsOrgAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        membership = getattr(request, "membership", None)
        return bool(membership and membership.is_admin_or_owner)


class IsOrgOwner(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        membership = getattr(request, "membership", None)
        return bool(membership and membership.is_owner)
