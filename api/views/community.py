import datetime
from django.core.cache import cache
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import random

from ..models import JournalEntry
from ..pagination import paginate_queryset
from ..serializers import JournalEntryListSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def community_feed_view(request):
    """
    Returns a randomized feed of public journal entries.

    Supports filtering by time period:
    - ?period=today: Show entries from today only
    - ?period=week: Show entries from the last 7 days (default)

    Uses caching to improve performance and provide a consistent
    random selection for a short period.
    """
    refresh = request.query_params.get("refresh", "").lower() == "true"
    period = request.query_params.get("period", "week").lower()
    if period not in ["today", "week"]:
        period = "week"

    cache_key = f"community_feed_random_{request.user.id}_{period}"
    if not refresh:
        cached_entries = cache.get(cache_key)
        if cached_entries is not None:
            return paginate_queryset(
                cached_entries, request, JournalEntryListSerializer
            )
    entries = _get_random_entries(period=period)
    cache.set(cache_key, entries, 900)

    return paginate_queryset(entries, request, JournalEntryListSerializer)


def _get_random_entries(period="week", limit=50):
    """
    Efficiently gets random public journal entries within a time period.

    Args:
        period (str): Time period filter ('today' or 'week')
        limit (int): Maximum number of entries to return

    Returns:
        QuerySet: Random selection of public journal entries
    """
    now = timezone.now()

    if period == "today":
        start_date = now.date()
        date_filter = {"created_at__gte": start_date}
    elif period == "week":
        start_date = now - datetime.timedelta(days=7)
        date_filter = {"created_at__gte": start_date}
    elif period == "month":
        start_date = now - datetime.timedelta(days=30)
        date_filter = {"created_at__gte": start_date}
    elif period == "year":
        start_date = now - datetime.timedelta(days=365)
        date_filter = {"created_at__gte": start_date}
    base_queryset = JournalEntry.objects.filter(public=True, **date_filter)
    total_count = base_queryset.count()

    if total_count == 0:
        return JournalEntry.objects.none()

    if total_count <= limit:
        return base_queryset.order_by("?")

    all_ids = list(base_queryset.values_list("id", flat=True))
    random_ids = random.sample(all_ids, limit)
    entries = JournalEntry.objects.filter(id__in=random_ids, public=True).order_by("?")

    return entries
