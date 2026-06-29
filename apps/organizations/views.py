from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, FormView, ListView, TemplateView, UpdateView

from apps.audit.utils import log_event
from apps.organizations.forms import (
    InviteMemberForm,
    OnboardingContactForm,
    OnboardingOrgForm,
    OnboardingProfileForm,
    OrganizationForm,
    TransferOwnershipForm,
)
from apps.organizations.mixins import OrgAdminMixin, OrgOwnerMixin, OrgRequiredMixin
from apps.organizations.models import Invitation, Membership, Organization
from apps.organizations.utils import send_invitation_email

User = get_user_model()


ONBOARDING_STEPS = ["organization", "contact", "profile", "api", "complete"]
ONBOARDING_STEP_LABELS = [
    ("organization", "Company Details"),
    ("contact", "Contact Info"),
    ("profile", "Your Profile"),
    ("api", "API & Settings"),
    ("complete", "All Done!"),
]


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
        self.request.session["onboarding_step"] = "organization"
        log_event("org.created", request=self.request, actor=self.request.user, org=org)
        messages.success(self.request, f'Organization "{org.name}" created successfully.')
        return redirect("onboarding:index")


class OnboardingView(LoginRequiredMixin, View):
    login_url = "/login/"

    def _get_org(self, request):
        return getattr(request, "org", None)

    def _get_step(self, request):
        step = request.GET.get("step") or request.session.get("onboarding_step", "organization")
        return step if step in ONBOARDING_STEPS else "organization"

    def _context(self, request, org, step, extra=None):
        idx = ONBOARDING_STEPS.index(step)
        ctx = {
            "step": step,
            "steps": ONBOARDING_STEP_LABELS,
            "step_index": idx,
            "total_steps": len(ONBOARDING_STEPS),
            "progress_pct": int(idx / (len(ONBOARDING_STEPS) - 1) * 100),
            "org": org,
            "request": request,
            "api_base": request.build_absolute_uri("/api/"),
            "swagger_url": request.build_absolute_uri("/api/docs/"),
        }
        if extra:
            ctx.update(extra)
        return ctx

    def _advance(self, request, next_step):
        request.session["onboarding_step"] = next_step
        return redirect("onboarding:index")

    def get(self, request):
        org = self._get_org(request)
        if not org:
            return redirect("organizations:create")
        if org.onboarding_completed:
            return redirect("accounts:dashboard")

        step = self._get_step(request)
        request.session["onboarding_step"] = step

        form = None
        if step == "organization":
            form = OnboardingOrgForm(instance=org)
        elif step == "contact":
            form = OnboardingContactForm(instance=org)
        elif step == "profile":
            form = OnboardingProfileForm(initial={
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "job_title": getattr(request.user, "job_title", ""),
            })

        return render(request, "onboarding/index.html", self._context(request, org, step, {"form": form}))

    def post(self, request):
        org = self._get_org(request)
        if not org:
            return redirect("organizations:create")
        if org.onboarding_completed:
            return redirect("accounts:dashboard")

        step = request.session.get("onboarding_step", "organization")

        if step == "organization":
            form = OnboardingOrgForm(request.POST, instance=org)
            if form.is_valid():
                form.save()
                return self._advance(request, "contact")
            return render(request, "onboarding/index.html", self._context(request, org, step, {"form": form}))

        elif step == "contact":
            form = OnboardingContactForm(request.POST, instance=org)
            if form.is_valid():
                form.save()
                return self._advance(request, "profile")
            return render(request, "onboarding/index.html", self._context(request, org, step, {"form": form}))

        elif step == "profile":
            form = OnboardingProfileForm(request.POST)
            if form.is_valid():
                request.user.first_name = form.cleaned_data.get("first_name", "")
                request.user.last_name = form.cleaned_data.get("last_name", "")
                request.user.job_title = form.cleaned_data.get("job_title", "")
                request.user.save(update_fields=["first_name", "last_name", "job_title"])
                return self._advance(request, "api")
            return render(request, "onboarding/index.html", self._context(request, org, step, {"form": form}))

        elif step == "api":
            return self._advance(request, "complete")

        elif step == "complete":
            org.onboarding_completed = True
            org.save(update_fields=["onboarding_completed"])
            request.session.pop("onboarding_step", None)
            log_event("org.onboarding_completed", request=request, actor=request.user, org=org)
            return redirect("accounts:dashboard")

        return redirect("onboarding:index")


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
