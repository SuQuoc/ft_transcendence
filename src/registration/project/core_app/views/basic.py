from datetime import datetime, timezone

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated , AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from ..authenticate import AccessTokenAuthentication, RefreshTokenAuthentication, NoTokenAuthentication
from ..models import CustomUser
from ..serializers import UserSerializer
from .utils_jwt import generate_response_with_valid_JWT, generate_response_with_invalid_JWT
import os

@api_view(['POST'])
@authentication_classes([NoTokenAuthentication])
@permission_classes([AllowAny])
def signup(request):
    try:
        user_s = UserSerializer(data=request.data)
        if not user_s.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user_s.save()
        token_s = TokenObtainPairSerializer(data=request.data)
        return generate_response_with_valid_JWT(status.HTTP_201_CREATED, token_s)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([AccessTokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_user(request):

    try:
        current_password = request.data.get('current_password')
        refresh = request.COOKIES.get('refresh')
        if not current_password or not refresh:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if not user.check_password(current_password):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        refresh_token = RefreshToken(refresh)
        refresh_token.blacklist()
        user.delete()
        response = Response(status=status.HTTP_200_OK)
        return response
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([NoTokenAuthentication])
@permission_classes([AllowAny])
def login(request):
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = CustomUser.objects.filter(username=username).first()
        if user is None or not user.check_password(password):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        token_s = TokenObtainPairSerializer(data=request.data)
        return generate_response_with_valid_JWT(status.HTTP_200_OK, token_s)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([RefreshTokenAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request):
    try:
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        refresh = request.COOKIES.get('refresh', None)
        if not refresh or not current_password or not new_password:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if not user or not user.check_password(current_password):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user.set_password(new_password)
        user.save()
        response = Response(status=status.HTTP_200_OK)
        response.delete_cookie('access')
        response.delete_cookie('refresh')
        return response

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([AccessTokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        token_s = TokenObtainPairSerializer(data=request.data)
        return generate_response_with_invalid_JWT(status.HTTP_200_OK, token_s)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([RefreshTokenAuthentication])
@permission_classes([IsAuthenticated])
def refresh_token(request):
    try:
        refresh_token = request.COOKIES.get('refresh')
        if not refresh_token:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        token_s = TokenRefreshSerializer(data={'refresh': refresh_token})      
        return generate_response_with_valid_JWT(status.HTTP_200_OK, token_s)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([AccessTokenAuthentication])
@permission_classes([IsAuthenticated])
def verify_token(request):
    return Response({'message': 'Token is valid'}, status=status.HTTP_200_OK)

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


@api_view(['POST'])
@authentication_classes([NoTokenAuthentication])
@permission_classes([AllowAny])
def forgot_password(request):
    try:
        username = request.data.get('username')
        if not username:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = CustomUser.objects.filter(username=username).first()
        if not user:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        send_reset_email(user.username, token)
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# [aguilmea] https://simpleisbetterthancomplex.com/tutorial/2016/08/24/how-to-create-one-time-link.html
# according to source code the function make_hash value is doing more but i do not understand why the uid will be hashed
# do i really need a last login in my model? (needed by the PasswordResetTokenGenerator.make_token??)


@api_view(['POST'])
@authentication_classes([NoTokenAuthentication])
@permission_classes([AllowAny])
def forgot_password_reset(request):
    try:
        username = request.data.get('username')
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        if not username or not token or not new_password:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = CustomUser.objects.filter(username=username).first()
        if not user:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, token):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)