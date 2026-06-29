from django.urls import path

from apps.billing import views

app_name = "billing"

urlpatterns = [
    path("", views.PricingView.as_view(), name="pricing"),
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("success/", views.CheckoutSuccessView.as_view(), name="success"),
    path("portal/", views.CustomerPortalView.as_view(), name="portal"),
    path("webhook/", views.WebhookView.as_view(), name="webhook"),
]
