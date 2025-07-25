"""
Custom allauth adapter to override default behaviors.
"""

from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.urls import reverse


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        """
        Constructs the email confirmation url using settings.BASE_URL.
        """
        path = reverse("v1:account_confirm_email", args=[emailconfirmation.key])
        return f"{settings.BASE_URL}{path}"