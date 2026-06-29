from apps.organizations.models import Membership


def org_context(request):
    if not request.user.is_authenticated:
        return {}

    current_org = getattr(request, "org", None)
    membership = getattr(request, "membership", None)

    user_orgs = list(
        Membership.objects.filter(user=request.user, org__is_active=True)
        .select_related("org")
        .values("org__id", "org__name", "org__slug", "role")
    )

    return {
        "current_org": current_org,
        "membership": membership,
        "user_orgs": user_orgs,
    }
