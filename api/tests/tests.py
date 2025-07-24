from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Entry
from datetime import date


class EntryModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        # Log in the test user
        self.client.login(username="testuser", password="testpassword")

    def test_entry_creation(self):
        # Log in the user
        self.client.login(username="testuser", password="password123")

        # Create an entry via POST request
        response = self.client.post(
            "/today/",
            {
                "title": "Test Entry",
                "content": "This is a test content.",
                "day_rating": 8,
            },
        )
        print(response.content.decode())

        # Check if the entry was created in the database
        self.assertEqual(Entry.objects.count(), 1)  # There should be 1 entry now
        entry = Entry.objects.first()
        self.assertEqual(entry.title, "Test Entry")
        self.assertEqual(entry.content, "This is a test content.")
        self.assertEqual(entry.day_rating, 8)
        self.assertEqual(entry.user, self.user)
