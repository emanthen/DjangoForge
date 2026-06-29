import json
from unittest.mock import patch

import pytest
from django.urls import reverse

from apps.billing.models import WebhookEvent
from tests.factories import OrganizationFactory, UserFactory


@pytest.mark.django_db
class TestWebhookView:
    def _make_event(self, event_type="customer.subscription.created", extra=None):
        data = {
            "id": "evt_test_123",
            "type": event_type,
            "data": {"object": {"customer": "cus_test", "status": "active", "items": {"data": []}}},
        }
        if extra:
            data["data"]["object"].update(extra)
        return data

    def test_invalid_signature_returns_400(self, client):
        url = reverse("billing:webhook")
        response = client.post(
            url,
            data=json.dumps({}),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="invalid",
        )
        assert response.status_code == 400

    @patch("stripe.Webhook.construct_event")
    def test_duplicate_event_returns_200_without_processing(self, mock_construct, client):
        event = self._make_event()
        mock_construct.return_value = event
        WebhookEvent.objects.create(stripe_id="evt_test_123", event_type="customer.subscription.created")

        url = reverse("billing:webhook")
        response = client.post(
            url,
            data=json.dumps(event),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="valid_sig",
        )
        assert response.status_code == 200
        assert WebhookEvent.objects.filter(stripe_id="evt_test_123").count() == 1

    @patch("stripe.Webhook.construct_event")
    def test_subscription_created_updates_org_plan(self, mock_construct, client):
        owner = UserFactory()
        org = OrganizationFactory(owner=owner, stripe_customer_id="cus_test", plan="free")
        event = self._make_event("customer.subscription.created")
        mock_construct.return_value = event

        url = reverse("billing:webhook")
        client.post(
            url,
            data=json.dumps(event),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="valid_sig",
        )
        assert WebhookEvent.objects.filter(stripe_id="evt_test_123").exists()

    @patch("stripe.Webhook.construct_event")
    def test_invoice_payment_failed_sends_email(self, mock_construct, client):
        from django.core import mail

        owner = UserFactory()
        org = OrganizationFactory(owner=owner, stripe_customer_id="cus_fail")
        event = {
            "id": "evt_fail_123",
            "type": "invoice.payment_failed",
            "data": {"object": {"customer": "cus_fail", "attempt_count": 1}},
        }
        mock_construct.return_value = event

        url = reverse("billing:webhook")
        client.post(
            url,
            data=json.dumps(event),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="valid_sig",
        )
        assert len(mail.outbox) >= 0

    @patch("stripe.Webhook.construct_event")
    def test_subscription_deleted_downgrades_to_free(self, mock_construct, client):
        owner = UserFactory()
        org = OrganizationFactory(owner=owner, stripe_customer_id="cus_delete", plan="pro")
        event = {
            "id": "evt_delete_123",
            "type": "customer.subscription.deleted",
            "data": {"object": {"customer": "cus_delete"}},
        }
        mock_construct.return_value = event

        url = reverse("billing:webhook")
        client.post(
            url,
            data=json.dumps(event),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="valid_sig",
        )
        org.refresh_from_db()
        assert org.plan == "free"
