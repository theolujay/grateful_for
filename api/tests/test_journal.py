import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from api.models import JournalEntry

User = get_user_model()


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
        other_user = User.objects.create_user(email="other@example.com", password="password")
        other_entry = JournalEntry.objects.create(user=other_user, content="Secret content")

        url = reverse("v1:api_entry_detail", kwargs={"entry_id": other_entry.id})
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND