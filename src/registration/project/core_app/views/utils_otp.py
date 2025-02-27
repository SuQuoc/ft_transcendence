import logging

from django.core.mail import send_mail
from datetime import timedelta
from django.utils import timezone

from ..serializers import OneTimePasswordSerializer
from ..models import OneTimePassword, RegistrationUser
from ..common_utils import generate_random_string
import os
from celery import shared_task

from django.conf import settings

"""
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
        generate_jwt_task.delay({'id': user_s.id, 'username': user_s.username}, {'username': user_s.username, 'password': data['password']})
    except Exception as e:
        logging.warning(f"create_user_send_otp: {str(e)}")
"""

@shared_task
def send_otp_email(username, action, password):
    try:
        subject = 'Confirm your action for your Transcendence account'
        link = os.environ.get('SERVER_URL')

        message = f"""
        Hello,

        You have tried to do the following action: {action}

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
        existing_otp = OneTimePassword.objects.filter(related_user=related_user, action=action)
        if existing_otp.exists():
            existing_otp.delete()

        if settings.MOCK_OTP == True:
            password = '0000000000000000'
        else:
            password = generate_random_string(16)
        otp_data = {
            'related_user': related_user,
            'action': action,
            'password': password,
            'expire': timezone.now() + timedelta(minutes=5)
        }
        otp_s = OneTimePasswordSerializer(data=otp_data)
        if not otp_s.is_valid():
            raise Exception({'create_one_time_password serializer' : otp_s.errors})
        otp_s.save()
        return password
    except Exception as e:
        raise Exception({'create_one_time_password error': str(e)})

def check_one_time_password(related_user, action, password, delete=True):
    try:
        otp = OneTimePassword.objects.get(related_user=related_user, action=action)
        if otp.expire < timezone.now():
            otp.delete()
            raise Exception ('otp expired')
        if not otp.check_password(password):
            raise Exception ('wrong otp')
        from ..tasks import delete_otp_task
        if delete:
            delete_otp_task.delay(otp.id)
        return True
    except Exception as e:
       return False
