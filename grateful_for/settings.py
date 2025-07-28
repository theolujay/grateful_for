"""
Django settings for grateful_for project.
"""

import sys
from django.core.exceptions import ImproperlyConfigured
import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv
import dj_database_url  # type:ignore


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(dotenv_path=str(BASE_DIR / ".env"))

BASE_URL = (os.getenv("BASE_URL") or "http://localhost:8000").rstrip("/")
FRONTEND_BASE_URL = (os.getenv("FRONTEND_BASE_URL") or "http://localhost:3000").rstrip(
    "/"
)

# In development, ensure BASE_URL uses http, as the dev server doesn't handle https.
# This prevents issues with link generation when using tools like Postman
# that might make requests over https.
if os.getenv("DEBUG") == "True" and BASE_URL.startswith("https://"):
    BASE_URL = "http" + BASE_URL[5:]

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = True if os.getenv("DEBUG") == "True" else False
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")
ROOT_URLCONF = "grateful_for.urls"
WSGI_APPLICATION = "grateful_for.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SITE_ID = 1
INTERNAL_IPS = ["127.0.0.1", "localhost"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "storages",
    "api",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "corsheaders",
    "debug_toolbar",
    "django_extensions",
    "django_filters",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "drf_yasg",
    "rest_framework",
    "rest_framework_api_key",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]



DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL"),
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True,
    )
}

if "test" in sys.argv or "pytest" in sys.argv[0]:
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
    
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": os.getenv("DB_NAME"),
#         "USER": os.getenv("DB_USER"),
#         "PASSWORD": os.getenv("DB_PASSWORD"),
#         "HOST": os.getenv("DB_HOST"),
#         "PORT": os.getenv("DB_PORT"),
#     }
# }

AUTH_USER_MODEL = "api.CustomUser"
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/London"
USE_I18N = True
USE_TZ = True

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "dj_rest_auth": "5/min",
        "anon": "100/day",
        "user": "1000/day",
        "login": "5/min",
        "burst": "20/min",
        "sustained": "100/hour",
    },
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ["v1"],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "dj_rest_auth.jwt_auth.JWTCookieAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_COOKIE": "_auth",
    "JWT_AUTH_REFRESH_COOKIE": "_refresh",
    "JWT_AUTH_HTTPONLY": False,
    "REGISTER_SERIALIZER": "api.serializers.CustomRegisterSerializer",
    "PASSWORD_RESET_SERIALIZER": "api.serializers.CustomPasswordResetSerializer",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
]

ACCOUNT_ADAPTER = "api.adapters.CustomAccountAdapter"
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
LOGIN_URL = "/admin"
SOCIALACCOUNT_LOGIN_ON_GET = True

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "offline",
        },
    }
}

# --- Email Configuration ---
# For development, you can use the console backend to see emails in the terminal:
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"  # Use SMTP for real emails
)
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
# Ensure required SMTP settings are present if that backend is used
if EMAIL_BACKEND == "django.core.mail.backends.smtp.EmailBackend" and not all(
    [EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD]
):
    raise ImproperlyConfigured(
        "When using the SMTP email backend, you must set EMAIL_HOST, EMAIL_HOST_USER, and EMAIL_HOST_PASSWORD in your .env file."
    )
EMAIL_CONFIRM_REDIRECT_BASE_URL = f"{FRONTEND_BASE_URL}/email/confirm/"
PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL = (
    f"{FRONTEND_BASE_URL}/password/reset/confirm/"
)
GOOGLE_CALLBACK_URL = f"{BASE_URL}/api/v1/auth/google/callback/"

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "allauth": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
        "dj_rest_auth": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}
GRAPH_MODELS = {
    "all_applications": True,
    "group_models": True,
}

SWAGGER_USE_COMPAT_RENDERERS = False

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "access_key": os.getenv("AWS_ACCESS_KEY_ID"),
            "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "bucket_name": os.getenv("AWS_STORAGE_BUCKET_NAME"),
            "region_name": os.getenv("AWS_S3_REGION_NAME"),
            "endpoint_url": os.getenv("AWS_ENDPOINT_URL"),
            "custom_domain": f"{os.getenv('AWS_STORAGE_BUCKET_NAME')}.s3.{os.getenv('AWS_S3_REGION_NAME')}.backblazeb2.com",
            "file_overwrite": False,
            "default_acl": None,
        },
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

