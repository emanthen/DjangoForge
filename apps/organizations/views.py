from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, FormView, ListView, TemplateView, UpdateView

from apps.audit.utils import log_event
from apps.organizations.forms import (
    InviteMemberForm,
    OrganizationForm,
    TransferOwnershipForm,
)
from apps.organizations.mixins import OrgAdminMixin, OrgOwnerMixin, OrgRequiredMixin
from apps.organizations.models import Invitation, Membership, Organization
from apps.organizations.utils import send_invitation_email

User = get_user_model()


class CreateOrgView(LoginRequiredMixin, CreateView):
    template_name = "organizations/create.html"
    form_class = OrganizationForm
    success_url = reverse_lazy("accounts:dashboard")

    def form_valid(self, form):
        org = form.save(commit=False)
        org.owner = self.request.user
        org.save()
        Membership.objects.create(user=self.request.user, org=org, role=Membership.ROLE_OWNER)
        self.request.session["active_org_id"] = str(org.id)
        log_event("org.created", request=self.request, actor=self.request.user, org=org)
        messages.success(self.request, f'Organization "{org.name}" created successfully.')
        return redirect(self.success_url)


class OrgSettingsView(OrgAdminMixin, UpdateView):
    template_name = "organizations/settings.html"
    form_class = OrganizationForm
    success_url = reverse_lazy("organizations:settings")

    def get_object(self):
        return self.org

    def form_valid(self, form):
        response = super().form_valid(form)
        log_event("org.settings_updated", request=self.request, actor=self.request.user, org=self.org)
        messages.success(self.request, "Organization settings updated.")
        return response


class OrgSwitchView(LoginRequiredMixin, View):
    def post(self, request, slug):
        try:
            membership = Membership.objects.get(
                user=request.user, org__slug=slug, org__is_active=True
            )
            request.session["active_org_id"] = str(membership.org.id)
        except Membership.DoesNotExist:
            messages.error(request, "You are not a member of that organization.")
        return redirect(request.META.get("HTTP_REFERER", "accounts:dashboard"))


class MemberListView(OrgAdminMixin, ListView):
    template_name = "organizations/members.html"
    context_object_name = "memberships"

    def get_queryset(self):
        return Membership.objects.filter(org=self.org).select_related("user").order_by("joined_at")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["invite_form"] = InviteMemberForm()
        ctx["pending_invitations"] = Invitation.objects.filter(
            org=self.org, accepted_at__isnull=True
        ).order_by("-created_at")
        return ctx


class InviteMemberView(OrgAdminMixin, View):
    def post(self, request):
        form = InviteMemberForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"].lower()
            role = form.cleaned_data["role"]

            existing_user = User.objects.filter(email=email).first()
            if existing_user:
                _, created = Membership.objects.get_or_create(
                    user=existing_user, org=self.org, defaults={"role": role}
                )
                if created:
                    log_event(
                        "member.invited",
                        request=request,
                        actor=request.user,
                        org=self.org,
                        resource=existing_user,
                    )
                    messages.success(request, f"{email} has been added to the organization.")
                else:
                    messages.info(request, f"{email} is already a member.")
            else:
                invitation, created = Invitation.objects.get_or_create(
                    org=self.org,
                    email=email,
                    accepted_at__isnull=True,
                    defaults={
                        "invited_by": request.user,
                        "role": role,
                        "expires_at": timezone.now() + timezone.timedelta(days=7),
                    },
                )
                if created:
                    send_invitation_email(invitation, request)
                    log_event("member.invited", request=request, actor=request.user, org=self.org)
                    messages.success(request, f"Invitation sent to {email}.")
                else:
                    messages.info(request, f"An invitation is already pending for {email}.")

        return redirect("organizations:members")


class AcceptInvitationView(View):
    def get(self, request, token):
        invitation = get_object_or_404(Invitation, token=token, accepted_at__isnull=True)

        if invitation.is_expired:
            messages.error(request, "This invitation has expired.")
            return redirect("accounts:login")

        if not request.user.is_authenticated:
            return redirect(f"/signup/?next=/orgs/invitations/{token}/accept/")

        membership, created = Membership.objects.get_or_create(
            user=request.user,
            org=invitation.org,
            defaults={"role": invitation.role},
        )
        invitation.accepted_at = timezone.now()
        invitation.save(update_fields=["accepted_at"])
        request.session["active_org_id"] = str(invitation.org.id)

        log_event(
            "member.accepted_invitation",
            request=request,
            actor=request.user,
            org=invitation.org,
        )
        messages.success(request, f"Welcome to {invitation.org.name}!")
        return redirect("accounts:dashboard")


class RemoveMemberView(OrgAdminMixin, View):
    def post(self, request, membership_id):
        membership = get_object_or_404(Membership, id=membership_id, org=self.org)

        if membership.is_owner:
            messages.error(request, "Cannot remove the organization owner.")
            return redirect("organizations:members")

        if membership.user == request.user and not request.user == self.org.owner:
            messages.error(request, "You cannot remove yourself.")
            return redirect("organizations:members")

        removed_email = membership.user.email
        membership.delete()
        log_event(
            "member.removed",
            request=request,
            actor=request.user,
            org=self.org,
            metadata={"removed_email": removed_email},
        )
        messages.success(request, f"{removed_email} has been removed from the organization.")
        return redirect("organizations:members")


class ChangeMemberRoleView(OrgOwnerMixin, View):
    def post(self, request, membership_id):
        membership = get_object_or_404(Membership, id=membership_id, org=self.org)
        new_role = request.POST.get("role")

        if new_role not in dict(Membership.ROLES):
            messages.error(request, "Invalid role.")
            return redirect("organizations:members")

        if membership.is_owner:
            messages.error(request, "Cannot change the owner's role directly. Use transfer ownership.")
            return redirect("organizations:members")

        old_role = membership.role
        membership.role = new_role
        membership.save(update_fields=["role"])
        log_event(
            "member.role_changed",
            request=request,
            actor=request.user,
            org=self.org,
            metadata={"user": membership.user.email, "old_role": old_role, "new_role": new_role},
        )
        messages.success(request, f"Role updated for {membership.user.email}.")
        return redirect("organizations:members")


class TransferOwnershipView(OrgOwnerMixin, FormView):
    template_name = "organizations/transfer_ownership.html"
    form_class = TransferOwnershipForm
    success_url = reverse_lazy("organizations:settings")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["org"] = self.org
        kwargs["current_owner"] = self.request.user
        return kwargs

    def form_valid(self, form):
        new_owner = form.cleaned_data["new_owner"]
        old_owner = self.request.user

        Membership.objects.filter(user=old_owner, org=self.org).update(role=Membership.ROLE_ADMIN)
        Membership.objects.filter(user=new_owner, org=self.org).update(role=Membership.ROLE_OWNER)
        self.org.owner = new_owner
        self.org.save(update_fields=["owner"])

        log_event(
            "org.ownership_transferred",
            request=self.request,
            actor=old_owner,
            org=self.org,
            metadata={"new_owner": new_owner.email},
        )
        messages.success(self.request, f"Ownership transferred to {new_owner.email}.")
        return super().form_valid(form)
