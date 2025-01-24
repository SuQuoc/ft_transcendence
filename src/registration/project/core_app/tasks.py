from celery import shared_task
from django.shortcuts import render
from django.conf import settings
if settings.SILK:
    from silk.profiling.profiler import silk_profile

from .models import OneTimePassword
import logging
from .models import RegistrationUser
from django.contrib.auth.hashers import make_password

from .views.token import CustomTokenObtainPairSerializer
from .views.utils import generate_response_with_valid_JWT
from .views.utils_otp import create_one_time_password, send_otp_email

from django.core.cache import cache
from rest_framework import status
from rest_framework.renderers import JSONRenderer

from django.conf import settings
import base64, logging

@shared_task
def generate_jwt_task(user_data, request_data):
    try:
        token_s = CustomTokenObtainPairSerializer(data=request_data)
        if token_s.is_valid():
            token_data = {
                'access': token_s.validated_data['access'],
                'refresh': token_s.validated_data['refresh']
            }
            cache_key = f"jwt_{user_data['id']}"
            cache.set(cache_key, token_data, timeout=300)
            return True
        else:
            logging.warning(f"Token validation failed: {token_s.errors}")
            cache_key = f"jwt_{user_data['id']}"
            logging.warning(f"invalid token, setting cache for key {cache_key} to None")
            cache.set(cache_key, None, timeout=300)
            return False
    except Exception as e:
        logging.warning(f"generate_jwt_task error: {str(e)}")
        return False

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
            generate_backup_codes_task.delay({'id': user_s.id})
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
        logging.warning(f"unexpected create_user_send_otp error: {str(e)}")

@shared_task
def generate_backup_codes_task(user_data):
    try:
        from core_app.models import RegistrationUser
        from core_app.serializers import UserSerializer
        
        user = RegistrationUser.objects.get(id=user_data['id'])
        backup_codes = user.generate_backup_codes()
        
        cache_key = f"backup_codes_{user_data['id']}"
        logging.warning(f"Storing backup codes for user {user_data['id']}")
        encrypted_codes = []
        for code in backup_codes:
            encrypted_codes.append(base64.b64encode(code.encode('utf-8')).decode('utf-8'))
        cache.set(cache_key, encrypted_codes, timeout=300)
        return True
    except Exception as e:
        logging.warning(f"generate_backup_codes_task error: {str(e)}")

        return False