import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from api.models import JournalEntry
from rest_framework import status

User = get_user_model()


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
        response = auth_client.patch(url, data, format="multipart")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["profile"]["first_name"] == "Updated Name"
        test_user.refresh_from_db()
        assert test_user.first_name == "Updated Name"
        assert test_user.phone == "1234567890"