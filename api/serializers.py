"""
Serializers for converting model instances to and from JSON representations.
"""

from django.db import transaction

from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer

from .models import (
    CustomUser,
    JournalEntry,
)


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


class CustomRegisterSerializer(RegisterSerializer):
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
        user = super().save(request)
        user.first_name = self.validated_data.get("first_name", user.first_name)
        user.phone = self.validated_data.get("phone", user.phone)
        user.date_of_birth = self.validated_data.get(
            "date_of_birth", user.date_of_birth
        )
        user.save()
        return user
