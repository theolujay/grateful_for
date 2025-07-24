from django.contrib import admin
from .models import JournalEntry, CustomUser, FeatureFlag


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    """
    Admin interface for the User model.
    Displays key user details and allows filtering by active status.
    """

    list_display = (
        "email",
        "first_name",
        # "last_name",
        "is_active",
        "date_joined",
    )
    list_filter = ("is_active", "date_joined")
    search_fields = ("email", "first_name")


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    """
    Admin interface for the JournalEntry model.
    Displays question text, difficulty, and creator.
    """

    list_display = ("id", "content", "created_at", "updated_at")
    search_fields = ("content",)


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = (
        "key",
        "value",
    )
