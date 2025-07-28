import pytest
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
from rest_framework.test import APIClient

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