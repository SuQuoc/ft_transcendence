from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from ..authenticate import CredentialsAuthentication, UsernameAuthentication, OneTimePasswordAuthentication
from ..serializers import UserSerializer
from ..models import RegistrationUser, OneTimePassword
from .utils import generate_response_with_valid_JWT, send_reset_email
from .utils_otp import create_one_time_password, send_otp_email, check_one_time_password

@api_view(['POST'])
@authentication_classes([CredentialsAuthentication]) # [aguilmea] change to Base Authentication? and delete the CredentialsAuthentication class
@permission_classes([IsAuthenticated])
def login(request):
    try:
        user = request.user
        if not user.is_verified():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        otp = request.data.get('otp')
        if not otp:
            created_otp = create_one_time_password(user.id, 'login')
            send_otp_email(user.username, 'login', created_otp)
            return Response(status=status.HTTP_202_ACCEPTED)
        if not check_one_time_password(user, 'login', otp):
           return Response(status=status.HTTP_400_BAD_REQUEST)
        token_s = TokenObtainPairSerializer(data=request.data)
        return generate_response_with_valid_JWT(status.HTTP_200_OK, token_s)
    except Exception as e:
        return Response({'login error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    try:
        username = request.data.get('username')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')
        if not username:
            return Response({1},status=status.HTTP_400_BAD_REQUEST)
        user = RegistrationUser.objects.filter(username=username).first()
        if not user or user.is_verified() is False:
            return Response({2},status=status.HTTP_400_BAD_REQUEST)
        if not otp:
            created_otp = create_one_time_password(user.id, 'reset_password')
            send_otp_email(username, 'reset_password', created_otp)
            return Response(status=status.HTTP_202_ACCEPTED)
        if not new_password or not check_one_time_password(user, 'reset_password', otp):
           return Response({3},status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'forgot_password error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        otp = request.data.get('otp')
        if not username or not password:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = RegistrationUser.objects.filter(username=username).first()
        if not user or user is None:
            user_s = UserSerializer(data=request.data)
            if not user_s.is_valid():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            user = user_s.create(request.data)
            created_otp = create_one_time_password(user.id, 'signup')
            send_otp_email(username, 'signup', created_otp)
            return Response(status=status.HTTP_201_CREATED)
        if user.is_verified() is True:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(password):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if not otp:
            created_otp = create_one_time_password(user.id, 'signup')
            send_otp_email(username, 'signup', created_otp)
            return Response(status=status.HTTP_200_OK)
        if not check_one_time_password(user, 'signup', otp):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user.set_verified( )
        token_s = TokenObtainPairSerializer(data=request.data)
        return generate_response_with_valid_JWT(status.HTTP_200_OK, token_s)
    except Exception as e:
        return Response({'signup error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
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
        created_otp = create_one_time_password(user.id, 'signup')
        send_otp_email(username, 'signup', created_otp)
        user.set_password(password)
        user.save()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'signup error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def signup_change_username(request):
    try:
        current_username = request.data.get('current_username')
        new_username = request.data.get('new_username')
        if not current_username or not new_username:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if (RegistrationUser.objects.filter(username=new_username).exists()):
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

