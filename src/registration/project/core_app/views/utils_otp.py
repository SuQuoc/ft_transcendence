import logging

from asgiref.sync import async_to_sync
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from datetime import timedelta
from django.utils import timezone

from ..serializers import OneTimePasswordSerializer
from ..models import OneTimePassword, RegistrationUser
from ..common_utils import generate_random_string
import os
from celery import shared_task

@shared_task
def create_user_send_otp(data, action):
    try:
        logging.info(f"create_user_send_otp: Received action = {action}")
        if action == 'signup':
            data['password'] = make_password(data['password'])
            user_s = RegistrationUser.objects.create(**data)
        elif action == 'otp':
            user_s = RegistrationUser.objects.get(id=data['id'])
        else:
            raise Exception("create_user_send_otp: wrong type")
        created_otp = create_one_time_password(user_s.id, 'signup')
        send_otp_email.delay(user_s.username, 'signup', created_otp)
    except Exception as e:
        logging.warning(f"create_user_send_otp: {str(e)}")

@shared_task
def send_otp_email(username, action, password):
    try:
        subject = 'Confirm your action for your Transcendence account'
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
        #password = generate_random_string(16)
        password = '0000000000000000' # [aguilmea] for testing purposes, should be deleted in production
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
#    try:
        otp = OneTimePassword.objects.get(related_user=related_user, action=action)
        if otp.expire < timezone.now():
            otp.delete()
            raise Exception (action + ": " + 'otp expired')
        if otp.action != action:
            raise Exception (action + ": " + 'wrong action')
        if not otp.check_password(password):
            raise Exception (action + ': ' + 'wrong password')
        from ..tasks import delete_otp_task
        delete_otp_task.delay(otp.id)
        return True
#    except Exception as e:
#       return False
