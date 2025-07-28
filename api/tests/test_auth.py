import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from allauth.account.models import EmailAddress

User = get_user_model()


@pytest.mark.django_db
class TestAuthEndpoints:
    """Tests for authentication related endpoints."""

    @patch("api.serializers.send_verification_email_task")
    def test_user_registration_dispatches_email_task(
        self, mock_send_verification_email_task, test_user
    ):
        """
        Verify that user registration is successful and that the asynchronous
        email verification task is dispatched.
        """
        client = APIClient()
        url = reverse("v1:api_register")
        data = {
            "first_name": "New",
            "email": "newuser@example.com",
            "password1": "a-strong-password-123",
            "password2": "a-strong-password-123",
        }

        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED, response.data
        assert User.objects.count() == 2  # test_user + new_user
        user = User.objects.get(email="newuser@example.com")
        assert user.first_name == "New"
        assert EmailAddress.objects.filter(user=user, verified=False).exists()

        mock_send_verification_email_task.delay.assert_called_once_with(user.id)

    def test_user_login_success(self, test_user):
        """Verify that a user with correct credentials can log in and receive tokens."""
        client = APIClient()
        url = reverse("v1:api_login")
        data = {"email": "testuser@example.com", "password": "a-strong-password-123"}
        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "tokens" in response.data
        assert "access" in response.data["tokens"]
        assert "refresh" in response.data["tokens"]

    def test_user_login_failure_wrong_password(self, test_user):
        """Verify that login fails with an incorrect password."""
        client = APIClient()
        url = reverse("v1:api_login")
        data = {"email": "testuser@example.com", "password": "wrong-password"}
        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_login_inactive_user(self, test_user):
        """Verify that an inactive user cannot log in."""
        test_user.is_active = False
        test_user.save()

        client = APIClient()
        url = reverse("v1:api_login")
        data = {"email": "testuser@example.com", "password": "a-strong-password-123"}
        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_logout(self, test_user):
        """Verify that a user can log out by blacklisting their refresh token."""
        client = APIClient()
        login_url = reverse("v1:api_login")
        login_data = {"email": "testuser@example.com", "password": "a-strong-password-123"}
        login_response = client.post(login_url, login_data, format="json")
        refresh_token = login_response.data["tokens"]["refresh"]

        logout_url = reverse("v1:api_logout")
        logout_data = {"refresh_token": refresh_token}
        client.force_authenticate(user=test_user)
        logout_response = client.post(logout_url, logout_data, format="json")

        assert logout_response.status_code == status.HTTP_200_OK

    def test_password_reset_sends_email(self, test_user):
        """Verify that requesting a password reset sends an email."""
        client = APIClient()
        url = reverse("v1:api_password_reset")
        data = {"email": "testuser@example.com"}
        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to[0] == "testuser@example.com"