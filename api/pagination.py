"""
Custom pagination class for consistent page size handling in API responses.
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination configuration using page numbers.

    - Default page size: 20 results per page
    - Client can override using `?page_size=` query param
    - Maximum allowed page size: 100
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


"""
Helper function for paginating querysets using DRF's pagination system.
"""


def paginate_queryset(queryset, request, serializer_class):
    """
    Paginates a queryset using the custom `StandardResultsSetPagination`.

    If pagination is applicable (based on the request), returns a paginated
    response. Otherwise, returns the full serialized data in a normal response.

    Args:
        queryset (QuerySet): The queryset to paginate.
        request (HttpRequest): The request object (used for pagination settings).
        serializer_class (Serializer): The DRF serializer class to serialize the data.

    Returns:
        Response: A paginated or full DRF response containing serialized data.
    """
    paginator = StandardResultsSetPagination()
    page = paginator.paginate_queryset(queryset, request)
    if page is not None:
        serializer = serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    serializer = serializer_class(queryset, many=True)
    return Response(serializer.data)
