"""
List of api endpoints
"""

from django.urls.exceptions import NoReverseMatch
from django.views.decorators.cache import cache_page

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse


@cache_page(60 * 15)
@api_view(["GET"])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """API entry point with discoverable endpoints"""

    def generate_url_with_placeholder(name, placeholder, param, dummy_value):
        """Generate URL with placeholder for dynamic endpoints"""
        try:
            url = reverse(
                name,
                kwargs={param: dummy_value},
                request=request,
                format=format,
            )
            return url.replace(str(dummy_value), placeholder)
        except NoReverseMatch:
            return None

    def safe_reverse(name, **kwargs):
        """Safely generate URLs, return None if route doesn't exist"""
        try:
            return reverse(name, request=request, format=format, **kwargs)
        except NoReverseMatch:
            return None

    return Response(
        {
            "authentication": {
                "login": safe_reverse("v1:api_login"),
                "logout": safe_reverse("v1:api_logout"),
                "register": safe_reverse("v1:api_register"),
                "token": {
                    "obtain": safe_reverse("v1:token_obtain_pair"),
                    "refresh": safe_reverse("v1:token_refresh"),
                },
                "social_login": {
                    "google": safe_reverse("v1:google_login"),
                },
                "email_verification": {
                    "verify": safe_reverse("v1:rest_verify_email"),
                    "resend": safe_reverse("v1:rest_resend_email"),
                },
                "password_reset": {
                    "request": safe_reverse("v1:rest_password_reset"),
                    "confirm": safe_reverse("v1:rest_password_reset_confirm_api"),
                },
            },
            "journal": {
                "entries": safe_reverse("v1:api_journal_entries"),
                "entry_detail": generate_url_with_placeholder(
                    "v1:api_entry_detail",
                    "<entry_id>",
                    "entry_id",
                    "99999",
                ),
                "analytics": safe_reverse("v1:api_journal_analytics"),
                "calendar": safe_reverse("v1:api_journal_calendar"),
            },
            "community": {
                "feed": safe_reverse("v1:api_community_feed"),
            },
            "user": {
                "dashboard": safe_reverse("v1:api_dashboard"),
                "account_management": safe_reverse("v1:api_account_management"),
            },
        }
    )
