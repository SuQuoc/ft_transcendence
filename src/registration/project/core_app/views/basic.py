from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from ..authenticate import CredentialsAuthentication, UsernameAuthentication, OneTimePasswordAuthentication
from ..serializers import UserSerializer
from ..models import RegistrationUser
from .utils import generate_response_with_valid_JWT, send_reset_email
from .utils_otp import create_one_time_password, send_otp_email, check_one_time_password

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
        if user is None:
            user_s = UserSerializer(data=request.data)
            if not user_s.is_valid():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            user = user_s.create(request.data)
            otp = create_one_time_password(user.id, 'signup')
            send_otp_email(username, 'signup', otp)
            return Response(status=status.HTTP_201_CREATED)
        if user.is_verified() is True:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(password):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if not otp:
            otp = create_one_time_password(user.id, 'signup')
            send_otp_email(username, 'signup', otp)
            return Response(status=status.HTTP_200_OK)
        if not check_one_time_password(user, 'signup', otp):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user.set_verified( )
        token_s = TokenObtainPairSerializer(data=request.data)
        return generate_response_with_valid_JWT(status.HTTP_200_OK, token_s)
    except Exception as e:
        return Response({'signup error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
            otp = create_one_time_password(user.id, 'login')
            send_otp_email(user.username, 'login', otp)
            return Response(status=status.HTTP_202_ACCEPTED)
        if not check_one_time_password(user, 'login', otp):
           return Response(status=status.HTTP_400_BAD_REQUEST)
        token_s = TokenObtainPairSerializer(data=request.data)
        return generate_response_with_valid_JWT(status.HTTP_200_OK, token_s)
    except Exception as e:
        return Response({'login error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([UsernameAuthentication])
@permission_classes([IsAuthenticated])
def forgot_password_send_email(request):
    try:
        user = request.user
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        send_reset_email(user.username, token)
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'forgot_password error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# [aguilmea] https://simpleisbetterthancomplex.com/tutorial/2016/08/24/how-to-create-one-time-link.html
# according to source code the function make_hash value is doing more but i do not understand why the uid will be hashed
# do i really need a last login in my model? (needed by the PasswordResetTokenGenerator.make_token??)

@api_view(['POST'])
@authentication_classes([OneTimePasswordAuthentication])
@permission_classes([IsAuthenticated])
def forgot_password_reset(request):
    try:
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        if not token or not new_password:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(request.user, token):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)