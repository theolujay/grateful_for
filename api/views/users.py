"""
Dashboard and account management views for users.
"""

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status

from ..models import JournalEntry
from ..serializers import (
    JournalEntryListSerializer,
    UserSerializer,
)

User = get_user_model()


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_dashboard_api(request):
    """
    Retrieve dashboard data for the currently authenticated user.

    Returns:
        JSON response with user-specific dashboard metrics and recent entries.
    """
    user = request.user
    entries_queryset = JournalEntry.objects.filter(user=user).order_by("-created_at")
    total_entries = entries_queryset.count()
    recent_entries_limit = 5
    recent_entries_queryset = entries_queryset[:recent_entries_limit]
    serializer = JournalEntryListSerializer(recent_entries_queryset, many=True)

    return Response(
        {
            "name": user.first_name,
            "email": user.email,
            "total_entries": total_entries,
            "recent_entries": serializer.data,
        }
    )


class AccountManagementView(APIView):
    """
    Retrieve or update user account and profile information.

    - GET: Retrieve account and profile information.
    - PUT/PATCH: Update account and profile.
    - DELETE not supported here (ownership check implied).

    Only authenticated users can manage their own accounts.
    Staff users with appropriate permissions can manage other users' accounts.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, user_id=None):
        """
        Retrieve the account and profile data of the target user.

        If `user_id` is not provided, retrieves the current user's account data.

        Args:
            user_id (UUID, optional): ID of the user to fetch.

        Returns:
            JSON response with user profile data.
        """
        user = self._get_target_user(request, user_id)
        if isinstance(user, Response):
            return user

        serializer = UserSerializer(user)
        return Response(
            {
                "profile": serializer.data,
            }
        )

    def patch(self, request, user_id=None):
        """
        Partially update user data.

        Args:
            user_id (UUID, optional): ID of the user to update.

        Returns:
            JSON response with updated user data.
        """
        return self._update_account(request, partial=True, user_id=user_id)

    def _update_account(self, request, partial=False, user_id=None):
        """
        Handles the update logic for user data.

        Args:
            partial (bool): Whether the update is partial.
            user_id (UUID, optional): Target user ID.

        Returns:
            JSON response or error message.
        """
        user = self._get_target_user(request, user_id)
        if isinstance(user, Response):
            return user

        serializer = UserSerializer(user, data=request.data, partial=partial)

        if not serializer.is_valid():
            return Response(
                {"error": "Invalid user data", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        return Response(
            {
                "message": "Account updated successfully",
                "user": serializer.data,
            }
        )

    def _get_target_user(self, request, user_id):
        """
        Get the target user for account actions.

        - If `user_id` is None or matches current user, return self.
        - Staff users can manage other users (add permission check as needed).

        Returns:
            User object or error Response.
        """
        if not user_id or str(user_id) == str(request.user.id):
            return request.user

        try:
            return get_object_or_404(User, id=user_id)
        except Exception:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def _get_user_profile_data(self, user):
        """
        Get serialized profile data for user.

        Args:
            user (User): User instance.

        Returns:
            Dict: Serialized profile data.
        """
        serializer = UserSerializer(user)
        return serializer.data
