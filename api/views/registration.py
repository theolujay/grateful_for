"""
Customized registration view to ensure atomic transactions.
"""

from django.db import transaction
from django.utils.decorators import method_decorator

from dj_rest_auth.registration.views import RegisterView as BaseRegisterView


@method_decorator(transaction.atomic, name="dispatch")
class CustomRegisterView(BaseRegisterView):
    """
    Custom registration view that wraps the entire process in a single
    database transaction to ensure atomicity.
    """

    pass
