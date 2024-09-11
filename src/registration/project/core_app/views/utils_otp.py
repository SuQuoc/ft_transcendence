from django.core.mail import send_mail
from datetime import timedelta
from django.utils import timezone

from ..serializers import OneTimePasswordSerializer

import random
import string
import os

# [aguilmea] i do not pass the token as a parameter so it is more secure but it is not the easiest way for the user
# I am not sure if i should send the link or if the user should stay on the page
# FE should handle the get request and send me a post request (more secured) so that i can answer with a response
def send_twofa_email(username, action, password):
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
            auth_user=None, # [aguilmea] will use EMAIL_HOST_USER
            auth_password=None, # [aguilmea] will use EMAIL_HOST_PASSWORD
            connection=None, # [aguilmea] optional email backend
            html_message=None, # [aguilmea] will only be sent as plain text and not html
        )
    except Exception as e:
        raise Exception(f"send_twofa_email: {str(e)}")

def create_one_time_password(related_user, action):
    try:
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
