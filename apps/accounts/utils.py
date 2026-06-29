from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.accounts.tokens import email_verification_token

User = get_user_model()


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def send_verification_email(user, request):
    token = email_verification_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    domain = request.get_host()
    scheme = "https" if request.is_secure() else "http"

    context = {
        "user": user,
        "verification_url": f"{scheme}://{domain}/verify-email/{uid}/{token}/",
        "domain": domain,
    }

    subject = "Verify your email address"
    text_body = render_to_string("emails/verify_email.txt", context)
    html_body = render_to_string("emails/verify_email.html", context)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        to=[user.email],
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send(fail_silently=False)


def send_password_reset_email(user, request):
    from django.contrib.auth.forms import PasswordResetForm

    form = PasswordResetForm({"email": user.email})
    if form.is_valid():
        form.save(
            request=request,
            use_https=request.is_secure(),
            email_template_name="registration/password_reset_email.html",
        )
