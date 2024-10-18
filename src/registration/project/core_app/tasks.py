from celery import shared_task
from .models import OneTimePassword
import logging
from .models import RegistrationUser
from django.contrib.auth.hashers import make_password
from .views.utils_otp import create_one_time_password, send_otp_email

@shared_task
def delete_otp_task(otp_id):
    try:
        otp = OneTimePassword.objects.get(id=otp_id)
        otp.delete()
    except OneTimePassword.DoesNotExist:
        pass

@shared_task
def create_user_send_otp(data, action):
    try:
        logging.info(f"create_user_send_otp: Received action = {action}")
        if action == 'signup':
            data['password'] = make_password(data['password'])
            user_s = RegistrationUser.objects.create(**data)
        elif action == 'otp':
            user_s = RegistrationUser.objects.get(id=data['id'])
            action = 'signup'
        elif action == 'login':
            user_s = RegistrationUser.objects.get(id=data['id'])
        else:
            raise Exception("create_user_send_otp: wrong type")
        created_otp = create_one_time_password(user_s.id, action)
        send_otp_email.delay(user_s.username, action, created_otp)
    except Exception as e:
        logging.warning(f"create_user_send_otp: {str(e)}")

