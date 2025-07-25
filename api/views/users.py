"""
Dashboard and account management views for users.
"""
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
    Retrieve or update the authenticated user's account information.

    - GET: Retrieve the current user's profile information.
    - PATCH: Update the current user's profile information.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        """
        Retrieve the profile data of the currently authenticated user.
        """
        serializer = UserSerializer(request.user)
        return Response(
            {
                "profile": serializer.data,
            }
        )

    def patch(self, request):
        """
        Partially update the authenticated user's data.
        """
        serializer = UserSerializer(request.user, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        return Response(
            {
                "message": "Account updated successfully",
                "profile": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
