"""
Serializers for converting model instances to and from JSON representations.
"""

from django.urls import reverse
from django.db import transaction

from rest_framework import serializers
from dj_rest_auth.registration.serializers import (
    RegisterSerializer as BaseRegisterSerializer,
)
from dj_rest_auth.serializers import (
    PasswordResetSerializer as BasePasswordResetSerializer,
)
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email, user_pk_to_url_str
from grateful_for import settings

from .models import (
    CustomUser,
    JournalEntry,
)
from .tasks import send_verification_email_task


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data model with email uniqueness validation"""

    class Meta:
        model = CustomUser
        fields = (
            "id",
            "email",
            "first_name",
            "phone",
            "date_of_birth",
            "date_joined",
        )
        read_only_fields = ("id", "date_joined")


class UserListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for user lists - only essential fields"""

    class Meta:
        model = CustomUser
        fields = (
            "id",
            "email",
            "first_name",
        )
        read_only_fields = ("id",)


class JournalEntrySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = JournalEntry
        fields = (
            "id",
            "content",
            "user",
            "photo",
            "public",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "user", "created_at", "updated_at")


class JournalEntryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = (
            "id",
            "content",
            "photo",
            "public",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class CustomRegisterSerializer(BaseRegisterSerializer):
    """Serializer for user registration with custom fields, extending dj-rest-auth."""

    username = None
    first_name = serializers.CharField(max_length=30, required=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)

    def __init__(self, *args, **kwargs):
        """
        Set _has_phone_field to False to prevent allauth adapter from
        trying to handle the phone field, as we do it manually in save().
        """
        super().__init__(*args, **kwargs)
        self._has_phone_field = False

    @transaction.atomic
    def save(self, request):
        # We override the save method to prevent the default synchronous email sending.
        # Instead, we replicate the user creation logic from allauth and then
        # dispatch our asynchronous Celery task.
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()

        # This populates the user instance with basic fields like email
        adapter.save_user(request, user, self)

        # Now, we add our custom fields
        user.first_name = self.validated_data.get("first_name", user.first_name)
        user.phone = self.validated_data.get("phone", user.phone)
        user.date_of_birth = self.validated_data.get(
            "date_of_birth", user.date_of_birth
        )
        user.save()

        # Create the EmailAddress record required by allauth
        setup_user_email(request, user, [])

        # Trigger the background task to send the verification email
        send_verification_email_task.delay(user.id)

        return user


def namespaced_password_reset_url_generator(request, user, temp_key):
    """
    Custom URL generator for password reset that respects the 'v1' namespace.
    """
    path = reverse(
        "v1:password_reset_confirm",
        args=[user_pk_to_url_str(user), temp_key],
    )
    # Use settings.BASE_URL to construct the absolute URI.
    # This avoids issues with reverse proxies or clients (like Postman)
    # sending requests over HTTPS to the dev server, which only supports HTTP.
    return f"{settings.BASE_URL}{path}"


class CustomPasswordResetSerializer(BasePasswordResetSerializer):
    def get_email_options(self):
        return {
            "url_generator": namespaced_password_reset_url_generator,
        }
