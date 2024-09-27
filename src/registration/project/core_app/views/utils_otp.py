from django.core.mail import send_mail
from datetime import timedelta
from django.utils import timezone

from ..serializers import OneTimePasswordSerializer
from..models import OneTimePassword

import random
import string
import os

def send_otp_email(username, action, password):
    try:
        subject = ' Confirm your action for your Transcendence account'
        link = os.environ.get('SERVER_URL') + f'/twofa_confirm?action={action}'

        message = f"""
        Hello,
    
        Please go to the following link to confirm your action: {action}
        {link}

        The code is: {password} and is valid for 5 minutes.
    
        Best regards,
        Your Transcendence team
        """
        send_mail(
            subject,
            message,
            "Your Transcendence team",
            [username],
            fail_silently=False,
            auth_user=None, # will use EMAIL_HOST_USER
            auth_password=None, # will use EMAIL_HOST_PASSWORD
            connection=None, #  optional email backend
            html_message=None, # will only be sent as plain text and not html
        )
    except Exception as e:
        raise Exception(f"send_otp_email: {str(e)}")

def create_one_time_password(related_user, action):
    try:
        for otp in OneTimePassword.objects.filter(related_user=related_user):
            otp.delete()
        password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        otp_data = {
            'related_user': related_user,
            'action': action,
            'password': password,
            'expire': timezone.now() + timedelta(minutes=5)
        }
        otp_s = OneTimePasswordSerializer(data=otp_data)
        if not otp_s.is_valid():
            raise Exception({'create_one_time_password serialiazer' : otp_s.errors})
        otp_s.save()
        return password
    except Exception as e:
        raise Exception({'create_one_time_password error': str(e)})

def check_one_time_password(related_user, action, password):
    try:
        otp = OneTimePassword.objects.get(related_user=related_user)
        if otp.expire < timezone.now():
            otp.delete()
            raise Exception ('otp expired')
        if otp.action != action:
            raise Exception ('wrong action')
        if otp.password != password:
            raise Exception ('wrong password')
        otp.delete()
        return True
    except Exception as e:
       return False
