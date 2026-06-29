import logging

from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def _get_org_by_stripe_customer(customer_id):
    from apps.organizations.models import Organization
    return Organization.objects.filter(stripe_customer_id=customer_id).first()


def handle_subscription_created(event):
    data = event["data"]["object"]
    customer_id = data.get("customer")
    org = _get_org_by_stripe_customer(customer_id)
    if not org:
        logger.warning("No org found for Stripe customer %s", customer_id)
        return

    plan = _get_plan_from_metadata(data)
    if plan:
        org.plan = plan
    org.save(update_fields=["plan"])
    logger.info("Subscription created for org %s, plan %s", org.name, plan)


def handle_subscription_updated(event):
    data = event["data"]["object"]
    customer_id = data.get("customer")
    org = _get_org_by_stripe_customer(customer_id)
    if not org:
        return

    status = data.get("status")
    plan = _get_plan_from_metadata(data)

    if status == "trialing":
        import datetime
        trial_end = data.get("trial_end")
        if trial_end:
            from django.utils import timezone
            org.trial_ends_at = timezone.datetime.fromtimestamp(trial_end, tz=datetime.timezone.utc)
        if plan:
            org.plan = plan
    elif status == "active":
        org.trial_ends_at = None
        if plan:
            org.plan = plan
    elif status == "past_due":
        _send_payment_failed_email(org)

    org.save()
    logger.info("Subscription updated for org %s, status %s", org.name, status)


def handle_subscription_deleted(event):
    data = event["data"]["object"]
    customer_id = data.get("customer")
    org = _get_org_by_stripe_customer(customer_id)
    if not org:
        return

    org.plan = "free"
    org.save(update_fields=["plan"])
    _send_cancellation_email(org)
    logger.info("Subscription cancelled for org %s", org.name)


def handle_invoice_payment_succeeded(event):
    data = event["data"]["object"]
    customer_id = data.get("customer")
    org = _get_org_by_stripe_customer(customer_id)
    if not org:
        return

    amount = data.get("amount_paid", 0) / 100
    _send_payment_receipt_email(org, amount, data.get("hosted_invoice_url", ""))
    logger.info("Payment succeeded for org %s, amount %s", org.name, amount)


def handle_invoice_payment_failed(event):
    data = event["data"]["object"]
    customer_id = data.get("customer")
    org = _get_org_by_stripe_customer(customer_id)
    if not org:
        return

    attempt_count = data.get("attempt_count", 1)
    if attempt_count >= 3:
        org.plan = "free"
        org.save(update_fields=["plan"])

    _send_payment_failed_email(org)
    logger.warning("Payment failed for org %s, attempt %s", org.name, attempt_count)


def handle_customer_updated(event):
    data = event["data"]["object"]
    customer_id = data.get("id")
    org = _get_org_by_stripe_customer(customer_id)
    if not org:
        return
    logger.info("Customer updated for org %s", org.name)


def _get_plan_from_metadata(subscription_data):
    items = subscription_data.get("items", {}).get("data", [])
    if items:
        metadata = items[0].get("price", {}).get("metadata", {})
        return metadata.get("plan")
    return None


def _send_payment_receipt_email(org, amount, invoice_url):
    context = {"org": org, "amount": amount, "invoice_url": invoice_url}
    subject = f"Payment receipt for {org.name}"
    send_mail(
        subject=subject,
        message=render_to_string("emails/payment_receipt.txt", context),
        from_email=None,
        recipient_list=[org.owner.email],
        html_message=render_to_string("emails/payment_receipt.html", context),
        fail_silently=True,
    )


def _send_payment_failed_email(org):
    context = {"org": org}
    send_mail(
        subject="Action required: Payment failed",
        message=render_to_string("emails/payment_failed.txt", context),
        from_email=None,
        recipient_list=[org.owner.email],
        html_message=render_to_string("emails/payment_failed.html", context),
        fail_silently=True,
    )


def _send_cancellation_email(org):
    context = {"org": org}
    send_mail(
        subject="Your subscription has been cancelled",
        message=render_to_string("emails/subscription_cancelled.txt", context),
        from_email=None,
        recipient_list=[org.owner.email],
        html_message=render_to_string("emails/subscription_cancelled.html", context),
        fail_silently=True,
    )
