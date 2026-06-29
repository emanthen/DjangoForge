import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def get_or_create_stripe_customer(org):
    if org.stripe_customer_id:
        try:
            return stripe.Customer.retrieve(org.stripe_customer_id)
        except stripe.error.InvalidRequestError:
            pass

    customer = stripe.Customer.create(
        email=org.owner.email,
        name=org.name,
        metadata={"org_id": str(org.id), "org_slug": org.slug},
    )
    org.stripe_customer_id = customer.id
    org.save(update_fields=["stripe_customer_id"])
    return customer


def get_plan_from_price(price_id):
    price_to_plan = {
        "price_starter": "starter",
        "price_pro": "pro",
        "price_enterprise": "enterprise",
    }
    return price_to_plan.get(price_id, "free")
