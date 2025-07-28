import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from allauth.account.models import EmailAddress

# from django.conf import settings

from api.models import JournalEntry

User = get_user_model()


@pytest.fixture
def test_user(db):
    """Fixture to create a user and a verified email address."""
    user = User.objects.create_user(
        first_name="Test",
        email="testuser@example.com",
        password="a-strong-password-123",
    )
    EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=True)
    return user


@pytest.fixture
def auth_client(test_user):
    """Fixture to create an API client authenticated as the test_user."""
    client = APIClient()
    client.force_authenticate(user=test_user)
    return client


@pytest.mark.django_db
class TestAuthEndpoints:
    """Tests for authentication related endpoints."""

    @patch("api.serializers.send_verification_email_task")
    def test_user_registration_dispatches_email_task(
        self, mock_send_verification_email_task
    ):
        """
        Verify that user registration is successful and that the asynchronous
        email verification task is dispatched.
        """
        client = APIClient()
        url = reverse("v1:api_register")
        data = {
            "first_name": "Test",
            "email": "testuser@example.com",
            "password1": "a-strong-password-123",
            "password2": "a-strong-password-123",
        }

        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED, response.data
        assert User.objects.count() == 1
        user = User.objects.get(email="testuser@example.com")
        assert user.first_name == "Test"
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


@pytest.mark.django_db
class TestJournalEndpoints:
    """Tests for the Journal Entry CRUD endpoints."""

    def test_list_journal_unauthenticated(self):
        """Verify that unauthenticated users cannot access journal entries."""
        client = APIClient()
        url = reverse("v1:api_journal_entries")
        response = client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_journal_entry(self, auth_client):
        """Verify that an authenticated user can create a journal entry."""
        url = reverse("v1:api_journal_entries")
        data = {"content": "Today was a good day."}
        response = auth_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert JournalEntry.objects.count() == 1
        assert JournalEntry.objects.first().content == "Today was a good day."

    def test_list_journal_entries(self, auth_client, test_user):
        """Verify that a user can list their own journal entries."""
        JournalEntry.objects.create(user=test_user, content="First entry")
        JournalEntry.objects.create(user=test_user, content="Second entry")

        url = reverse("v1:api_journal_entries")
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        assert response.data["results"][0]["content"] == "Second entry"

    def test_retrieve_journal_entry(self, auth_client, test_user):
        """Verify that a user can retrieve a specific journal entry."""
        entry = JournalEntry.objects.create(user=test_user, content="Details here")
        url = reverse("v1:api_entry_detail", kwargs={"entry_id": entry.id})
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["content"] == "Details here"

    def test_update_journal_entry(self, auth_client, test_user):
        """Verify that a user can update their own journal entry."""
        entry = JournalEntry.objects.create(user=test_user, content="Original content")
        url = reverse("v1:api_entry_detail", kwargs={"entry_id": entry.id})
        data = {"content": "Updated content", "public": False}
        response = auth_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        entry.refresh_from_db()
        assert entry.content == "Updated content"
        assert entry.public is False

    def test_delete_journal_entry(self, auth_client, test_user):
        """Verify that a user can delete their own journal entry."""
        entry = JournalEntry.objects.create(user=test_user, content="To be deleted")
        url = reverse("v1:api_entry_detail", kwargs={"entry_id": entry.id})
        response = auth_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert JournalEntry.objects.count() == 0

    def test_cannot_access_other_user_entry(self, auth_client):
        """Verify a user cannot access another user's journal entry."""
        other_user = User.objects.create_user(
            email="other@example.com", password="password"
        )
        other_entry = JournalEntry.objects.create(
            user=other_user, content="Secret content"
        )

        url = reverse("v1:api_entry_detail", kwargs={"entry_id": other_entry.id})
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestUserEndpoints:
    """Tests for user-specific endpoints like dashboard and account management."""

    def test_get_dashboard(self, auth_client, test_user):
        """Verify that an authenticated user can retrieve their dashboard data."""
        JournalEntry.objects.create(user=test_user, content="An entry for the dashboard")
        url = reverse("v1:api_dashboard")
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Test"
        assert response.data["total_entries"] == 1
        assert len(response.data["recent_entries"]) == 1

    def test_get_account_management_details(self, auth_client, test_user):
        """Verify a user can retrieve their own account details."""
        url = reverse("v1:api_account_management")
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["profile"]["email"] == "testuser@example.com"
        assert response.data["profile"]["first_name"] == "Test"

    def test_patch_account_management_details(self, auth_client, test_user):
        """Verify a user can update their own account details."""
        url = reverse("v1:api_account_management")
        data = {"first_name": "Updated Name", "phone": "1234567890"}
        response = auth_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["profile"]["first_name"] == "Updated Name"
        test_user.refresh_from_db()
        assert test_user.first_name == "Updated Name"
        assert test_user.phone == "1234567890"