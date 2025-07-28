from celery import shared_task # type: ignore
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from allauth.account.models import EmailAddress, get_emailconfirmation_model

User = get_user_model()

@shared_task
def send_verification_email_task(user_id: int):
    """
    Sends a verification email to a user in the background.

    This task is decoupled from the request-response cycle and constructs
    the email manually to ensure it works robustly in a background worker.
    """
    try:
        user = User.objects.get(pk=user_id)
        # An EmailAddress record must exist for the user.
        email_address = EmailAddress.objects.get_primary(user)
        if not email_address:
            return

        EmailConfirmation = get_emailconfirmation_model()
        confirmation = EmailConfirmation.create(email_address)

        activate_url = f"{settings.EMAIL_CONFIRM_REDIRECT_BASE_URL}{confirmation.key}/"

        subject = "Please Confirm Your Email Address"
        message = f"Hi {user.first_name or user.email},\n\nThank you for registering for Grateful For. Please click the link below to verify your email address:\n\n{activate_url}\n\nIf you did not sign up for this account, you can ignore this email.\n\nThanks,\nThe Grateful For Team"

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
    except User.DoesNotExist:
        # User might have been deleted before task execution
        pass
    except EmailAddress.DoesNotExist:
        # This can happen if the user record was created but the email address
        # was not. Log this as a potential issue.
        pass
