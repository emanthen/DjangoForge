import pytest
from django.core import mail
from django.urls import reverse

from tests.factories import UserFactory


@pytest.mark.django_db
class TestSignup:
    def test_successful_signup_sends_verification_email(self, client):
        url = reverse("accounts:signup")
        data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com",
            "password1": "securepassword123",
            "password2": "securepassword123",
        }
        response = client.post(url, data)
        assert response.status_code == 302
        assert len(mail.outbox) == 1
        assert "verify" in mail.outbox[0].subject.lower()

    def test_duplicate_email_returns_form_error(self, client):
        UserFactory(email="existing@example.com")
        url = reverse("accounts:signup")
        data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "existing@example.com",
            "password1": "securepassword123",
            "password2": "securepassword123",
        }
        response = client.post(url, data)
        assert response.status_code == 200
        assert "already exists" in response.content.decode()

    def test_password_mismatch_returns_error(self, client):
        url = reverse("accounts:signup")
        data = {
            "email": "new@example.com",
            "password1": "securepassword123",
            "password2": "differentpassword",
        }
        response = client.post(url, data)
        assert response.status_code == 200

    def test_verify_email_token_marks_verified(self, client):
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode
        from apps.accounts.tokens import email_verification_token

        user = UserFactory(email_verified_at=None)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_verification_token.make_token(user)
        url = reverse("accounts:verify_email", kwargs={"uidb64": uid, "token": token})
        response = client.get(url)
        assert response.status_code == 302
        user.refresh_from_db()
        assert user.email_verified_at is not None

    def test_expired_token_returns_error(self, client):
        user = UserFactory(email_verified_at=None)
        url = reverse("accounts:verify_email", kwargs={"uidb64": "invalid", "token": "badtoken"})
        response = client.get(url)
        assert response.status_code == 200
        assert b"invalid" in response.content.lower()

    def test_login_with_unverified_email_blocked(self, client):
        user = UserFactory(email_verified_at=None)
        user.set_password("password123")
        user.save()
        url = reverse("accounts:login")
        response = client.post(url, {"username": user.email, "password": "password123"})
        assert response.status_code == 302
        assert "verify" in response["Location"]
