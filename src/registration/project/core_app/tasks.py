from celery import shared_task

from .models import OneTimePassword
import logging
from .models import RegistrationUser
from django.contrib.auth.hashers import make_password

from .views.token import CustomTokenObtainPairSerializer
from .views.utils import generate_response_with_valid_JWT
from .views.utils_otp import create_one_time_password, send_otp_email

from django.core.cache import cache
from rest_framework import status

@shared_task
def generate_jwt_task(user_data, request_data):
    token_s = CustomTokenObtainPairSerializer(data=request_data)
    if token_s.is_valid():
        jwt_response = generate_response_with_valid_JWT(status.HTTP_200_OK, token_s)
        cache.set(f"jwt_{user_data['id']}", jwt_response, timeout=300)
    else:
        cache.set(f"jwt_{user_data['id']}", None, timeout=300)

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
        if action == 'signup':
            data['password'] = make_password(data['password'])
            user_s = RegistrationUser.objects.create(**data)
        elif action == 'otp':
            user_s = RegistrationUser.objects.get(id=data['id'])
            action = 'signup'
        elif action == 'login':
            user_s = RegistrationUser.objects.get(id=data['id'])
        else:
            raise Exception(f"create_user_send_otp: wrong type: {action}")
        generate_jwt_task.delay({'id': user_s.id, 'username': user_s.username}, {'username': user_s.username, 'password': data['password']})
        created_otp = create_one_time_password(user_s.id, action)
        send_otp_email.delay(user_s.username, action, created_otp)
    except Exception as e:
        logging.warning(f"create_user_send_otp: {str(e)}")

