# tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def sending_email_on_registration(user_email, user_name=None):
    """
    Sends a welcome email to a user after registration.
    
    Args:
        user_email (str): The email address of the new user.
        user_name (str, optional): The name of the user for a personalized message.
    """
    subject = "Welcome to Our Platform!"
    
    # If user_name is provided, personalize the message
    if user_name:
        message = f"Hi {user_name},\n\nThank you for registering at our platform. We're excited to have you onboard!"
    else:
        message = (
            "Hi there,\n\n"
            "Thank you for registering at our platform. We're excited to have you onboard!"
        )
    
    # sender email from Django settings
    from_email = settings.DEFAULT_FROM_EMAIL
    
    # send the email
    send_mail(
        subject,
        message,
        from_email,
        [user_email],
        fail_silently=False,  # raise exception if sending fails
    )
    
    return f"Email sent to {user_email}"
