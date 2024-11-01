from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.exceptions import ValidationError

from .token import CustomTokenObtainPairSerializer
from ..authenticate import CredentialsAuthentication
from ..serializers import UserSerializer
from ..models import RegistrationUser, OneTimePassword
from .utils import generate_response_with_valid_JWT
from .utils_otp import create_one_time_password, send_otp_email, check_one_time_password
from ..tasks import create_user_send_otp, generate_jwt_task, generate_backup_codes_task

import logging
from silk.profiling.profiler import silk_profile
from django.core.cache import cache
import os
from datetime import datetime, timezone
from django.conf import settings

@api_view(['POST'])
@authentication_classes([CredentialsAuthentication])
@permission_classes([IsAuthenticated])
@silk_profile(name='login')
def login(request):
    try:
        user = request.user
        if not user.is_verified():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        otp = request.data.get('otp')
        if not otp:
            create_user_send_otp.delay({'id': user.id, 'username': user.username, 'password': request.data.get('password')}, 'login')
            return Response(status=status.HTTP_202_ACCEPTED)
        if not check_one_time_password(user, 'login', otp):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        cache_key = f'jwt_{user.id}'
        backup_codes_key = f'backup_codes_{user.id}'

        jwt_response = cache.get(cache_key)
        backup_codes = cache.get(backup_codes_key)
        if jwt_response:
            response = Response({'status': 'success', 'backup_codes': backup_codes}, status=status.HTTP_200_OK)
            access_token_expiration = datetime.now(timezone.utc) + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
            response.set_cookie(
                key='access',
                value=jwt_response['access'],
                expires=access_token_expiration,
                domain=os.environ.get('DOMAIN'),
                httponly=True,
                secure=True,
                samesite='Strict')
            refresh_token_expiration = datetime.now(timezone.utc) + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
            response.set_cookie(
                key='refresh',
                value=jwt_response['refresh'],
                expires=refresh_token_expiration,
                domain=os.environ.get('DOMAIN'),
                httponly=True,
                secure=True,
                samesite='Strict')
            return response
        logging.warning(f"no cached token for user {user.id}")
        token_s = CustomTokenObtainPairSerializer(data=request.data)
        return generate_response_with_valid_JWT(status.HTTP_200_OK, token_s, backup_codes)
    except Exception as e:
        return Response({'login error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@silk_profile(name='forgot_password')
def forgot_password(request):
    try:
        username = request.data.get('username')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')
        if not username:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = RegistrationUser.objects.filter(username=username).first()
        if not user or user.is_verified() is False:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if not otp:
            created_otp = create_one_time_password(user.id, 'reset_password')
            send_otp_email(username, 'reset_password', created_otp)
            return Response(status=status.HTTP_202_ACCEPTED)
        if not new_password or not check_one_time_password(user, 'reset_password', otp):
           return Response(status=status.HTTP_400_BAD_REQUEST)
        user.validate_password(new_password)
        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'forgot_password error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@silk_profile(name='signup')
def signup(request):
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        otp = request.data.get('otp')
        if not username or not password:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = RegistrationUser.objects.filter(username=username).first()
        if not user:
            if otp:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            user_s = UserSerializer(data=request.data)
            if not user_s.is_valid():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            user_data = user_s.validated_data
            create_user_send_otp.delay(user_data, 'signup')
            return Response(status=status.HTTP_201_CREATED)
        if user.is_verified() is True:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(password):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if not otp:
            create_user_send_otp.delay({'id': user.id, 'username': user.username, 'password': password}, 'otp')
            return Response(status=status.HTTP_200_OK)
        if not check_one_time_password(user, 'signup', otp):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user.set_verified()
        user.change_password_is_set()
        cache_key = f'jwt_{user.id}'
        backup_codes_key = f'backup_codes_{user.id}'

        jwt_response = cache.get(cache_key)
        backup_codes = cache.get(backup_codes_key)
        if jwt_response:
            response = Response({'status': 'success', 'backup_codes': backup_codes}, status=status.HTTP_200_OK)
            access_token_expiration = datetime.now(timezone.utc) + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
            response.set_cookie(
				key='access',
				value=jwt_response['access'],
				expires=access_token_expiration,
				domain=os.environ.get('DOMAIN'),
				httponly=True,
				secure=True,
				samesite = 'Strict')
            refresh_token_expiration = datetime.now(timezone.utc) + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
            response.set_cookie(
                key='refresh',
                value=jwt_response['refresh'],
                expires=refresh_token_expiration,
                domain=os.environ.get('DOMAIN'),
                httponly=True,
                secure=True,
                samesite = 'Strict')
            return response
        logging.warning(f"no cached token for user {user.id}")
        token_s = CustomTokenObtainPairSerializer(data=request.data)
        return generate_response_with_valid_JWT(status.HTTP_200_OK, token_s, backup_codes)
    except ValidationError as e:
        return Response({'signup error': e.messages}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'signup error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@silk_profile(name='signup_change_password')
def signup_change_password(request):
    try:
        username = request.data.get('username')
        password = request.data.get('new_password')
        if not username or not password:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = RegistrationUser.objects.filter(username=username).first()
        if not user:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if user.is_verified():
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user.validate_password(password)
        user.set_password(password)
        user.save()
        created_otp = create_one_time_password(user.id, 'signup')
        send_otp_email(username, 'signup', created_otp)
        return Response(status=status.HTTP_200_OK)
    except ValidationError as e:
        return Response({'signup error': e.messages}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'signup change password error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@silk_profile(name='signup_change_username')
def signup_change_username(request):
    try:
        current_username = request.data.get('current_username')
        new_username = request.data.get('new_username')
        if not current_username or not new_username:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if RegistrationUser.objects.filter(username=new_username).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = RegistrationUser.objects.filter(username=current_username).first()
        if not user:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if user.is_verified():
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        OneTimePassword.objects.filter(related_user=user).delete()
        user.username = new_username
        user.save()
        created_otp = create_one_time_password(user.id, 'signup')
        send_otp_email(new_username, 'signup', created_otp)
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'signup error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

