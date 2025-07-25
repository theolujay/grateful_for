from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from dj_rest_auth.views import (
    PasswordResetConfirmView,
    PasswordResetView,
    UserDetailsView,
)
from dj_rest_auth.registration.views import (
    ResendEmailVerificationView,
    VerifyEmailView,
)

from .views import (
    auth,
    community,
    journal,
    registration,
    root,
    users,
)

app_name = "api"

urlpatterns = [
    path("", root.api_root, name="api_root"),
    path("auth/login/", auth.login_api, name="api_login"),
    path("auth/logout/", auth.logout_api, name="api_logout"),
    path("auth/token/", TokenObtainPairView.as_view(), name="api_token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="api_token_refresh"),
    path(
        "auth/registration/",
        registration.CustomRegisterView.as_view(),
        name="api_register",
    ),
    path("auth/user/", UserDetailsView.as_view(), name="api_user_details"),
    path(
        "auth/registration/resend-email/",
        ResendEmailVerificationView.as_view(),
        name="api_resend_email",
    ),
    path(
        "auth/registration/verify-email/",
        VerifyEmailView.as_view(),
        name="api_verify_email",
    ),
    path(
        "auth/registration/confirm-email/<str:key>/",
        auth.email_confirm_redirect,
        name="account_confirm_email",
    ),
    path(
        "auth/password/reset/", PasswordResetView.as_view(), name="api_password_reset"
    ),
    path(
        "auth/password/reset/confirm/<str:uidb64>/<str:token>/",
        auth.password_reset_confirm_redirect,
        name="password_reset_confirm",
    ),
    path(
        "auth/password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="api_password_reset_confirm",
    ),
    path("auth/google/", auth.GoogleLoginView.as_view(), name="api_google_login"),
    path("journal/entries/", journal.journal_entry, name="api_journal_entries"),
    path(
        "journal/entries/<int:entry_id>/",
        journal.entry_detail_api,
        name="api_entry_detail",
    ),
    path("journal/analytics/", journal.entry_analytics, name="api_journal_analytics"),
    path("journal/calendar/", journal.entry_calendar, name="api_journal_calendar"),
    path("community/feed/", community.community_feed_view, name="api_community_feed"),
    path("dashboard/", users.user_dashboard_api, name="api_dashboard"),
    path(
        "account-management/",
        users.AccountManagementView.as_view(),
        name="api_account_management",
    ),
]
