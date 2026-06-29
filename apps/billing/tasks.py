from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone


@shared_task(name="billing.send_trial_ending_reminders")
def send_trial_ending_reminders():
    from apps.organizations.models import Organization

    cutoff = timezone.now() + timezone.timedelta(days=3)
    orgs = Organization.objects.filter(
        trial_ends_at__lte=cutoff,
        trial_ends_at__gt=timezone.now(),
        plan=Organization.PLAN_FREE,
    )

    for org in orgs:
        context = {"org": org, "days_left": (org.trial_ends_at - timezone.now()).days}
        send_mail(
            subject=f"Your {org.name} trial ends in {context['days_left']} days",
            message=render_to_string("emails/trial_ending.txt", context),
            from_email=None,
            recipient_list=[org.owner.email],
            html_message=render_to_string("emails/trial_ending.html", context),
            fail_silently=True,
        )

    return f"Sent trial ending reminders to {orgs.count()} organizations"
