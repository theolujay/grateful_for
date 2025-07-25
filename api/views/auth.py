"""
Authentication-related API views for login, logout, and registration.
"""

import logging
import os
from typing import Optional

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate
from django.urls.exceptions import NoReverseMatch
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.throttling import SimpleRateThrottle
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_api_key.permissions import HasAPIKey  # type: ignore
from rest_framework.views import APIView
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

from ..serializers import (
    UserSerializer,
)

logger = logging.getLogger(__name__)


class CustomGoogleOAuth2Client(OAuth2Client):
    def __init__(
        self,
        request,
        consumer_key,
        consumer_secret,
        access_token_method,
        access_token_url,
        callback_url,
        _scope,  # This is fix for incompatibility between django-allauth==65.3.1 and dj-rest-auth==7.0.1
        scope_delimiter=" ",
        headers=None,
        basic_auth=False,
    ):
        super().__init__(
            request,
            consumer_key,
            consumer_secret,
            access_token_method,
            access_token_url,
            callback_url,
            scope_delimiter,
            headers,
            basic_auth,
        )


class GoogleLoginView(SocialLoginView):
    """
    Handles the callback from Google OAuth2. Accepts a `code` from Google,
    exchanges it for an access token, and logs in or creates a new user.
    Returns JWT tokens. This view handles both the GET redirect from Google
    and a POST from a frontend SPA.
    """

    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_CALLBACK_URL
    client_class = CustomGoogleOAuth2Client

    def get(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data={"code": request.GET.get("code")})
        self.serializer.is_valid(raise_exception=True)
        self.login()
        return self.get_response()


class LoginRateThrottle(SimpleRateThrottle):
    """Throttle for login attempts to prevent brute force attacks."""

    scope = "login"

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            return self.cache_format % {"scope": self.scope, "ident": request.user.pk}
        return self.cache_format % {
            "scope": self.scope,
            "ident": self.get_ident(request),
        }


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([LoginRateThrottle])
def login_api(request):
    """Authenticate user and return tokens + user info"""

    email = request.data.get("email", "").strip().lower()
    password = request.data.get("password", "")

    try:
        validate_email(email)
    except ValidationError:
        return Response(
            {"detail": "A valid email is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not password:
        return Response(
            {"detail": "Password is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(request, email=email, password=password)
    if user is None:
        logger.warning("Failed login attempt for email: %s", email)
        return Response(
            {"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        logger.warning("Login attempt for inactive account: %s", email)
        return Response(
            {"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )

    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token

    try:
        user_route = reverse("v1:api_dashboard", request=request)
    except NoReverseMatch:
        user_route = None

    logger.info("User %s logged in successfully", email)

    return Response(
        {
            "detail": "Login successful",
            "tokens": {"access": str(access_token), "refresh": str(refresh)},
            "user": UserSerializer(user).data,
            "user_route": user_route,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_api(request):
    """
    Logout user by blacklisting the refresh token.
    Client should send refresh token in request body.
    """
    try:
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Blacklist the refresh token
        token = RefreshToken(refresh_token)
        token.blacklist()

        logger.info("User %s logged out successfully", request.user.email)

        return Response({"detail": "Logout successful"}, status=status.HTTP_200_OK)

    except (TokenError, InvalidToken) as e:
        logger.warning(
            "Invalid token during logout for user %s: %s",
            request.user.email,
            type(e).__name__,
        )
        return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([AllowAny])
# @permission_classes([HasAPIKey])
def email_confirm_redirect(request, key):
    """Redirect to frontend email confirmation page."""
    return HttpResponseRedirect(f"{settings.EMAIL_CONFIRM_REDIRECT_BASE_URL}{key}/")


@api_view(["GET"])
@permission_classes([AllowAny])
def password_reset_confirm_redirect(request, uidb64, token):
    """Redirect to frontend password reset confirmation page."""
    return HttpResponseRedirect(
        f"{settings.PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL}{uidb64}/{token}/"
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def google_login_page(request):
    """
    Serves the simple HTML page with the "Sign in with Google" button.
    In a real-world scenario, this would be handled by your frontend framework.
    """
    google_client_id = None
    try:
        # Fetch the client_id from the SocialApp model in the database
        # This is the standard django-allauth way to store credentials
        google_app = SocialApp.objects.get(provider="google")
        google_client_id = google_app.client_id
    except SocialApp.DoesNotExist:
        logger.error(
            "Google SocialApp not configured in Django admin. Please add it in /admin/socialaccount/socialapp/"
        )

    # Get scope from settings to ensure consistency
    google_scope = settings.SOCIALACCOUNT_PROVIDERS.get("google", {}).get("SCOPE", [])

    return render(
        request,
        "login.html",
        {
            "google_client_id": google_client_id,
            "google_callback_url": settings.GOOGLE_CALLBACK_URL,
            "google_scope": " ".join(google_scope),
        },
    )
