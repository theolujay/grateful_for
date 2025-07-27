import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from api.models import JournalEntry


@pytest.mark.django_db
def test_journal_entry_creation():
    """
    Tests the basic creation of a JournalEntry instance and its default values.
    """
    user = get_user_model().objects.create_user(
        email="tester@example.com", password="password123"
    )
    entry = JournalEntry.objects.create(
        user=user, content="This is a test of the journal entry."
    )

    assert entry.user == user
    assert entry.content == "This is a test of the journal entry."
    assert entry.public is True
    assert entry.created_at is not None
    assert str(entry) == f"{user.email} - {timezone.localdate()}"
