# Billing

DjangoForge uses **Stripe** for subscription billing. The integration covers:
- Hosted Checkout (Stripe handles the payment UI)
- Customer Portal (Stripe-hosted self-serve billing management)
- Webhooks (subscription lifecycle events)
- Transactional billing emails

---

## Pricing plans

| Plan | Price | Stripe Product |
|------|-------|---------------|
| Free | $0/month | No Stripe subscription |
| Starter | $29/month or $290/year | `price_starter_monthly` / `price_starter_annual` |
| Pro | $79/month or $790/year | `price_pro_monthly` / `price_pro_annual` |

Plans are defined in `apps/billing/utils.py` and the pricing page at `templates/billing/pricing.html`.

---

## Setup

### 1. Create Stripe products and prices

In the [Stripe Dashboard](https://dashboard.stripe.com/products):
1. Create two products: "Starter" and "Pro"
2. For each product, create monthly and annual prices
3. Note the price IDs (e.g. `price_1234abcd`)

### 2. Add to settings

```python
# config/settings/base.py
STRIPE_PRICE_IDS = {
    "starter_monthly": env("STRIPE_PRICE_STARTER_MONTHLY", default=""),
    "starter_annual": env("STRIPE_PRICE_STARTER_ANNUAL", default=""),
    "pro_monthly": env("STRIPE_PRICE_PRO_MONTHLY", default=""),
    "pro_annual": env("STRIPE_PRICE_PRO_ANNUAL", default=""),
}
```

### 3. Configure webhook endpoint

In the Stripe Dashboard → Developers → Webhooks → Add endpoint:
- URL: `https://yourdomain.com/billing/webhook/`
- Events to listen to:
  - `checkout.session.completed`
  - `customer.subscription.created`
  - `customer.subscription.updated`
  - `customer.subscription.deleted`
  - `invoice.paid`
  - `invoice.payment_failed`

Copy the webhook signing secret and add to `.env`:
```dotenv
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxx
```

### 4. Local webhook forwarding

```bash
stripe listen --forward-to localhost:8000/billing/webhook/
```

---

## Checkout flow

1. User visits `/billing/pricing/`
2. Clicks "Upgrade" on a plan
3. HTMX posts to `CheckoutView` with `price_id`
4. Server creates a Stripe Checkout Session
5. User is redirected to Stripe's hosted checkout page
6. On completion, Stripe redirects to `/billing/success/`
7. Webhook fires asynchronously to update `Organization.plan`

```python
# apps/billing/views.py
class CheckoutView(OrgRequiredMixin, View):
    def post(self, request):
        price_id = request.POST.get("price_id")
        session = stripe.checkout.Session.create(
            customer=request.org.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=request.build_absolute_uri(reverse("billing:success")),
            cancel_url=request.build_absolute_uri(reverse("billing:pricing")),
            metadata={"org_id": str(request.org.id)},
        )
        return redirect(session.url)
```

---

## Customer Portal

Allows users to manage their subscription without building a custom UI:
- Change plan
- Update payment method
- Cancel subscription
- Download invoices

```python
class CustomerPortalView(OrgRequiredMixin, View):
    def post(self, request):
        session = stripe.billing_portal.Session.create(
            customer=request.org.stripe_customer_id,
            return_url=request.build_absolute_uri(reverse("billing:pricing")),
        )
        return redirect(session.url)
```

Accessible via the "Manage Billing" button on the pricing page (shown only if org has a `stripe_customer_id`).

---

## Webhook handling

The webhook endpoint is at `POST /billing/webhook/`. It is:
- Exempt from CSRF (`@csrf_exempt`) — protected by Stripe signature instead
- Signature-verified using `stripe.Webhook.construct_event()`
- Idempotent via `WebhookEvent` deduplication table

```python
class WebhookView(View):
    @method_decorator(csrf_exempt)
    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)

        # Deduplicate
        _, created = WebhookEvent.objects.get_or_create(stripe_id=event.id)
        if not created:
            return HttpResponse(status=200)  # already processed

        # Route to handler
        handlers = {
            "customer.subscription.updated": handle_subscription_updated,
            "customer.subscription.deleted": handle_subscription_deleted,
            "invoice.paid": handle_invoice_paid,
            "invoice.payment_failed": handle_invoice_payment_failed,
        }
        handler = handlers.get(event.type)
        if handler:
            handler(event)

        return HttpResponse(status=200)
```

### Webhook handlers

| Event | Handler | What it does |
|-------|---------|-------------|
| `checkout.session.completed` | `handle_checkout_completed` | Creates Stripe customer if new, links to org |
| `customer.subscription.updated` | `handle_subscription_updated` | Updates `org.plan` based on active price |
| `customer.subscription.deleted` | `handle_subscription_deleted` | Sets `org.plan = "free"`, sends cancellation email |
| `invoice.paid` | `handle_invoice_paid` | Sends payment receipt email |
| `invoice.payment_failed` | `handle_invoice_payment_failed` | Sends payment failed email |

---

## Stripe Customer

The first time an org completes checkout, a Stripe Customer is created and `org.stripe_customer_id` is set. Subsequent checkouts reuse the same customer (allows Stripe to remember payment methods).

```python
def get_or_create_stripe_customer(org):
    if org.stripe_customer_id:
        return org.stripe_customer_id
    customer = stripe.Customer.create(
        email=org.owner.email,
        name=org.name,
        metadata={"org_id": str(org.id)},
    )
    org.stripe_customer_id = customer.id
    org.save(update_fields=["stripe_customer_id"])
    return customer.id
```

---

## Test mode

During development, use Stripe test mode:
```dotenv
STRIPE_PUBLIC_KEY=pk_test_xxx
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_LIVE_MODE=False
```

Test card numbers:
| Scenario | Card number |
|----------|------------|
| Payment succeeds | `4242 4242 4242 4242` |
| Payment fails | `4000 0000 0000 0002` |
| 3D Secure required | `4000 0025 0000 3155` |

Use any future expiry date, any CVC, any ZIP.

---

## Billing emails

Sent via Celery tasks on webhook events:

| Email | Template | Trigger |
|-------|----------|---------|
| Payment receipt | `billing/emails/payment_receipt.html` | `invoice.paid` |
| Payment failed | `billing/emails/payment_failed.html` | `invoice.payment_failed` |
| Subscription cancelled | `billing/emails/subscription_cancelled.html` | `customer.subscription.deleted` |
| Trial ending soon | `billing/emails/trial_ending.html` | Daily cron, 3 days before trial end |

All templates use table-based inline CSS for email client compatibility.

---

## URL reference

| URL name | Path | Description |
|----------|------|-------------|
| `billing:pricing` | `/billing/pricing/` | Pricing page |
| `billing:checkout` | `/billing/checkout/` | Start Stripe Checkout |
| `billing:portal` | `/billing/portal/` | Stripe Customer Portal |
| `billing:success` | `/billing/success/` | Post-checkout success page |
| `billing:webhook` | `/billing/webhook/` | Stripe webhook receiver |
