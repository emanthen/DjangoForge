from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import FormView, TemplateView, UpdateView
from django.urls import reverse_lazy

from apps.accounts.forms import DeleteAccountForm, LoginForm, ProfileForm, SignupForm
from apps.accounts.tokens import email_verification_token
from apps.accounts.utils import get_client_ip, send_verification_email
from apps.audit.utils import log_event

User = get_user_model()


class SignupView(FormView):
    template_name = "accounts/signup.html"
    form_class = SignupForm
    success_url = reverse_lazy("accounts:verify_email_sent")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("accounts:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        send_verification_email(user, self.request)
        log_event("user.signup", request=self.request, actor=user)
        return super().form_valid(form)


class VerifyEmailSentView(TemplateView):
    template_name = "accounts/verify_email_sent.html"


class VerifyEmailView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and email_verification_token.check_token(user, token):
            user.email_verified_at = timezone.now()
            user.save(update_fields=["email_verified_at"])
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            log_event("user.email_verified", request=request, actor=user)
            messages.success(request, "Email verified successfully! Welcome to DjangoForge.")
            return redirect("accounts:dashboard")

        messages.error(request, "The verification link is invalid or has expired.")
        return render(request, "accounts/verify_email_invalid.html")


class LoginView(FormView):
    template_name = "accounts/login.html"
    form_class = LoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("accounts:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        if not user.has_verified_email:
            messages.warning(
                self.request,
                "Please verify your email before logging in. Check your inbox.",
            )
            return redirect("accounts:verify_email_sent")

        user.last_login_ip = get_client_ip(self.request)
        user.save(update_fields=["last_login_ip"])
        login(self.request, user)
        next_url = self.request.GET.get("next", "")
        if next_url and next_url.startswith("/"):
            return redirect(next_url)
        return redirect("accounts:dashboard")

    def get_success_url(self):
        return self.request.GET.get("next") or reverse_lazy("accounts:dashboard")


class LogoutView(LoginRequiredMixin, View):
    def post(self, request):
        logout(request)
        return redirect("accounts:login")


class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = "accounts/profile.html"
    form_class = ProfileForm
    success_url = reverse_lazy("accounts:profile")

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        log_event("user.profile_updated", request=self.request, actor=self.request.user)
        messages.success(self.request, "Profile updated successfully.")
        return response


class DeleteAccountView(LoginRequiredMixin, FormView):
    template_name = "accounts/delete_account.html"
    form_class = DeleteAccountForm
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        user = self.request.user
        log_event("user.account_deleted", request=self.request, actor=user)
        logout(self.request)
        # Soft delete — anonymize the account
        user.is_active = False
        user.email = f"deleted+{user.pk}@djangoforge.dev"
        user.first_name = ""
        user.last_name = ""
        user.save(update_fields=["is_active", "email", "first_name", "last_name"])
        messages.info(self.request, "Your account has been deleted.")
        return super().form_valid(form)


class ChangePasswordRedirectView(LoginRequiredMixin, View):
    def get(self, request):
        return redirect("/accounts/password/change/")


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        from datetime import datetime
        from apps.audit.models import AuditEvent

        ctx = super().get_context_data(**kwargs)
        org = getattr(self.request, "org", None)
        if org:
            ctx["recent_events"] = AuditEvent.objects.filter(org=org).select_related("actor")[:10]
            ctx["member_count"] = org.memberships.count()

        hour = datetime.now().hour
        if hour < 12:
            ctx["greeting"] = "Good morning"
        elif hour < 17:
            ctx["greeting"] = "Good afternoon"
        else:
            ctx["greeting"] = "Good evening"
        return ctx
