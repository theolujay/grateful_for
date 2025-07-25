from datetime import timedelta

from django.utils import timezone
from django.utils import timezone
from django.db import models

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from ..models import JournalEntry
from ..pagination import paginate_queryset
from ..serializers import JournalEntrySerializer, JournalEntryListSerializer


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def journal_entry(request):
    """
    List user's journal entries or create a new one.
    GET: Returns paginated list of user's entries
    POST: Creates a new journal entry (max 3 per day)
    """
    if request.method == "GET":
        entries = JournalEntry.objects.filter(user=request.user).order_by("-created_at")
        return paginate_queryset(entries, request, JournalEntryListSerializer)

    today = timezone.now().date()
    user_entries_today = JournalEntry.objects.filter(
        user=request.user, created_at__date=today
    )

    if user_entries_today.count() >= 3:
        return Response(
            {"detail": "You have already made three (3) entries today."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = JournalEntrySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def entry_detail_api(request, entry_id):
    """
    Retrieve, update, or delete a specific journal entry.

    - GET: Returns details of a specific entry
    - PATCH: Updates the entry data
    - DELETE: Deletes the entry

    Permissions: Only the owner can access their entries
    """
    try:
        entry = JournalEntry.objects.get(id=entry_id, user=request.user)
    except JournalEntry.DoesNotExist:
        return Response(
            {"detail": "Entry not found or you don't have permission to access it."},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == "GET":
        serializer = JournalEntrySerializer(entry)
        return Response(serializer.data)

    elif request.method == "PATCH":
        serializer = JournalEntrySerializer(entry, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        entry.delete()
        return Response(
            {"message": "Journal entry deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def entry_analytics(request):
    """
    Get analytics/stats about user's journal entries
    """
    user = request.user
    today = timezone.now().date()

    # --- Streak Calculation ---
    entry_dates = set(
        JournalEntry.objects.filter(user=user)
        .values_list("created_at__date", flat=True)
        .distinct()
    )
    current_streak = 0
    check_date = today
    while check_date in entry_dates:
        current_streak += 1
        check_date -= timedelta(days=1)

    # --- Aggregate Stats Calculation ---
    stats = JournalEntry.objects.filter(user=user).aggregate(
        total_entries=models.Count("id"),
        entries_this_month=models.Count(
            "id", filter=models.Q(created_at__year=today.year, created_at__month=today.month)
        ),
        entries_today=models.Count("id", filter=models.Q(created_at__date=today)),
    )

    return Response(
        {
            "total_entries": stats["total_entries"],
            "entries_this_month": stats["entries_this_month"],
            "current_streak": current_streak,
            "entries_today": stats["entries_today"],
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def entry_calendar(request):
    """
    Get calendar view of entries for a specific month/year
    """
    today = timezone.now().date()
    year = request.GET.get("year", today.year)
    month = request.GET.get("month", today.month)

    try:
        year = int(year)
        month = int(month)
    except (ValueError, TypeError):
        return Response(
            {"detail": "Invalid year or month parameter"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    entries = (
        JournalEntry.objects.filter(
            user=request.user, created_at__year=year, created_at__month=month
        )
        .values("created_at__date")
        .annotate(count=models.Count("id"))
    )

    # Format for calendar display
    calendar_data = {}
    for entry in entries:
        date_str = entry["created_at__date"].strftime("%Y-%m-%d")
        calendar_data[date_str] = entry["count"]

    return Response({"year": year, "month": month, "entries": calendar_data})
