from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_invitation_email(invitation, request):
    domain = request.get_host()
    scheme = "https" if request.is_secure() else "http"
    accept_url = f"{scheme}://{domain}/orgs/invitations/{invitation.token}/accept/"

    context = {
        "invitation": invitation,
        "accept_url": accept_url,
        "org": invitation.org,
        "invited_by": invitation.invited_by,
    }

    subject = f"You've been invited to join {invitation.org.name} on DjangoForge"
    text_body = render_to_string("emails/invitation.txt", context)
    html_body = render_to_string("emails/invitation.html", context)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        to=[invitation.email],
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send(fail_silently=False)
