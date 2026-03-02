# urbanSecurity_app/utils/smtp.py
from django.core.mail import send_mail
from django.conf import settings


def send_otp_email(email, otp):
    """Send 6-digit OTP verification email to user."""
    subject = "UrbanSecure — Your Verification OTP"
    message = f"""
Hello,

Your OTP for UrbanSecure AI-ZeroTrust account verification is:

    {otp}

This OTP is valid for 10 minutes. Do not share this with anyone.

— UrbanSecure Security Team
"""
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
