from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.contrib.auth.password_validation import validate_password, password_changed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ValidationError

from .token import CustomTokenObtainPairSerializer
from ..authenticate import CredentialsAuthentication
from ..serializers import UserSerializer
from ..models import RegistrationUser, OneTimePassword
from .utils import generate_response_with_valid_JWT
from .utils_otp import create_one_time_password, send_otp_email, check_one_time_password
from ..tasks import create_user_send_otp, generate_jwt_task, generate_backup_codes_task

import logging
from datetime import timezone
if settings.SILK:
    from silk.profiling.profiler import silk_profile
from django.core.cache import cache
import os
from datetime import datetime
from django.conf import settings
import base64

@api_view(['POST'])
@authentication_classes([CredentialsAuthentication])
@permission_classes([IsAuthenticated])
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

        jwt_response = cache.get(cache_key)
        if jwt_response:
            response = Response({'status': 'success'}, status=status.HTTP_200_OK)
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
            user.actualise_last_login(jwt_response['refresh'])
            return response
        logging.warning(f"no cached token for user {user.id}")
        token_s = CustomTokenObtainPairSerializer(data=request.data)
        return generate_response_with_valid_JWT(user, status.HTTP_200_OK, token_s)
    except Exception as e:
        return Response({str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([CredentialsAuthentication])
@permission_classes([AllowAny])
#@silk_profile(name='forgot_password')
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
        user.set_password(new_password)
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([CredentialsAuthentication])
@permission_classes([AllowAny])
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
                return Response({'no valid credentials'}, status=status.HTTP_400_BAD_REQUEST)
            user_s = UserSerializer(data=request.data)
            if not user_s.is_valid():
                return Response({'no valid credentials'}, status=status.HTTP_400_BAD_REQUEST)
            validate_password(password)
            user_data = user_s.validated_data
            create_user_send_otp.delay(user_data, 'signup')
            return Response(status=status.HTTP_201_CREATED)
        if user.is_verified() is True:
            return Response({'no valid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(password):
            return Response({'no valid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        if not otp:
            create_user_send_otp.delay({'id': user.id, 'username': user.username, 'password': password}, 'otp')
            return Response(status=status.HTTP_200_OK)
        if not check_one_time_password(user, 'signup', otp):
            return Response({'no valid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_verified()
        user.change_password_is_set()
        cache_key = f'jwt_{user.id}'
        backup_codes_key = f'backup_codes_{user.id}'

        jwt_response = cache.get(cache_key)
        backup_codes = cache.get(backup_codes_key)
        decrypted_codes = []
        for code in backup_codes:
            decrypted_codes.append(base64.b64decode(code.encode('utf-8')).decode('utf-8'))
        if jwt_response:
            response = Response({'status': 'success', 'backup_codes': decrypted_codes}, status=status.HTTP_200_OK)
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
            user.actualise_last_login(jwt_response['refresh'])
            return response
        logging.warning(f"no cached token for user {user.id}")
        token_s = CustomTokenObtainPairSerializer(data=request.data)
        return generate_response_with_valid_JWT(user, status.HTTP_200_OK, token_s, decrypted_codes)
    except ValidationError as e:
        return Response({str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([CredentialsAuthentication])
@permission_classes([AllowAny])
#@silk_profile(name='signup_change_password')
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
        user.set_password(password)
        created_otp = create_one_time_password(user.id, 'signup')
        send_otp_email(username, 'signup', created_otp)
        return Response(status=status.HTTP_200_OK)
    except ValidationError as e:
        return Response({e.messages}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([CredentialsAuthentication])
@permission_classes([AllowAny])
#@silk_profile(name='signup_change_username')
def signup_change_username(request):
    try:
        current_username = request.data.get('current_username')
        new_username = request.data.get('new_username')
        if not current_username or not new_username:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user_s = UserSerializer(data={'username': new_username})
        if not user_s.is_valid():
            return Response({'no valid email'}, status=status.HTTP_400_BAD_REQUEST)
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
        return Response({str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

