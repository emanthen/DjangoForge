import json
import logging

import stripe
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from apps.billing.models import WebhookEvent
from apps.billing.utils import get_or_create_stripe_customer
from apps.organizations.mixins import OrgRequiredMixin

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

DEFAULT_PLANS = [
    {"name": "free", "price": 0, "features": ["1 organization", "3 team members", "Community support"]},
    {"name": "starter", "price": 29, "features": ["Unlimited members", "Priority support", "API access", "Feature flags"]},
    {"name": "pro", "price": 79, "features": ["Everything in Starter", "SSO", "Audit log", "Custom domains", "SLA"]},
]


class PricingView(TemplateView):
    template_name = "billing/pricing.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["stripe_publishable_key"] = settings.STRIPE_PUBLISHABLE_KEY
        current_org = getattr(self.request, "org", None)
        ctx["current_plan"] = current_org.plan if current_org else "free"
        ctx["default_plans"] = DEFAULT_PLANS
        ctx["plans"] = []
        return ctx


class CheckoutView(OrgRequiredMixin, View):
    def post(self, request):
        price_id = request.POST.get("price_id")
        if not price_id:
            return JsonResponse({"error": "price_id required"}, status=400)

        try:
            customer = get_or_create_stripe_customer(self.org)
            session = stripe.checkout.Session.create(
                customer=customer.id,
                payment_method_types=["card"],
                line_items=[{"price": price_id, "quantity": 1}],
                mode="subscription",
                success_url=request.build_absolute_uri("/billing/success/?session_id={CHECKOUT_SESSION_ID}"),
                cancel_url=request.build_absolute_uri("/billing/"),
                metadata={"org_id": str(self.org.id)},
            )
            return JsonResponse({"checkout_url": session.url})
        except stripe.error.StripeError as e:
            logger.error("Stripe checkout error: %s", e)
            return JsonResponse({"error": str(e)}, status=400)


class CheckoutSuccessView(OrgRequiredMixin, TemplateView):
    template_name = "billing/success.html"

    def get(self, request, *args, **kwargs):
        session_id = request.GET.get("session_id")
        if session_id:
            try:
                stripe.checkout.Session.retrieve(session_id)
            except stripe.error.StripeError:
                pass
        return super().get(request, *args, **kwargs)


class CustomerPortalView(OrgRequiredMixin, View):
    def post(self, request):
        try:
            customer = get_or_create_stripe_customer(self.org)
            session = stripe.billing_portal.Session.create(
                customer=customer.id,
                return_url=request.build_absolute_uri("/billing/"),
            )
            return redirect(session.url)
        except stripe.error.StripeError as e:
            logger.error("Stripe portal error: %s", e)
            return redirect("billing:pricing")


@method_decorator(csrf_exempt, name="dispatch")
class WebhookView(View):
    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.DJSTRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            logger.warning("Invalid Stripe webhook payload")
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            logger.warning("Invalid Stripe webhook signature")
            return HttpResponse(status=400)

        event_id = event["id"]
        event_type = event["type"]

        webhook_event, created = WebhookEvent.objects.get_or_create(
            stripe_id=event_id,
            defaults={"event_type": event_type},
        )

        if not created:
            return HttpResponse(status=200)

        try:
            self._dispatch(event)
            webhook_event.status = WebhookEvent.STATUS_PROCESSED
            webhook_event.save(update_fields=["status"])
        except Exception as e:
            logger.exception("Error processing webhook %s: %s", event_id, e)
            webhook_event.status = WebhookEvent.STATUS_FAILED
            webhook_event.error_message = str(e)
            webhook_event.save(update_fields=["status", "error_message"])

        return HttpResponse(status=200)

    def _dispatch(self, event):
        from apps.billing import handlers
        handlers_map = {
            "customer.subscription.created": handlers.handle_subscription_created,
            "customer.subscription.updated": handlers.handle_subscription_updated,
            "customer.subscription.deleted": handlers.handle_subscription_deleted,
            "invoice.payment_succeeded": handlers.handle_invoice_payment_succeeded,
            "invoice.payment_failed": handlers.handle_invoice_payment_failed,
            "customer.updated": handlers.handle_customer_updated,
        }
        handler = handlers_map.get(event["type"])
        if handler:
            handler(event)
