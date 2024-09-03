from datetime import datetime, timezone
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from django.core.mail import send_mail

import os

def generate_response_with_valid_JWT(status_code, token_s):
    response = Response(status=status_code)
    if not token_s.is_valid():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    access_token = token_s.validated_data['access']
    access_token_expiration = datetime.now(timezone.utc) + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
    response.set_cookie(
        key='access',
        value=access_token,
        expires=access_token_expiration,
        domain=os.environ.get('DOMAIN'),
        httponly=True,
        secure=True,
        samesite = 'Strict')
    refresh_token = token_s.validated_data['refresh']
    refresh_token_expiration = datetime.now(timezone.utc) + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
    response.set_cookie(
        key='refresh',
        value=refresh_token,
        expires=refresh_token_expiration,
        domain=os.environ.get('DOMAIN'),
        httponly=True,
        secure=True,
        samesite = 'Strict')
    return response


def send_reset_email(recipient, token):
    try:
        link = os.environ.get('SERVER_URL') + '/reset-password?token=' + token
        message = f"""
        Hello,

        Please go to the following link to reset your password for Transcendence:

        {link}

        Best regards,
        Your Transcendence team
        """
        send_mail(
            "Reset your password for Transcendence",
            message,
            "Your Transcendence team",
            [recipient],
            fail_silently=False,
            auth_user=None, # [aguilmea] will use EMAIL_HOST_USER
            auth_password=None, # [aguilmea] will use EMAIL_HOST_PASSWORD
            connection=None, # [aguilmea] optional email backend
            html_message=None, # [aguilmea] will only be sent as plain text and not html
        )
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
