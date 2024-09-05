from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from ..authenticate import NoTokenAuthentication
from ..models import CustomUser
from ..serializers import UserSerializer
from .utils_jwt import generate_response_with_valid_JWT, send_reset_email

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
@authentication_classes([NoTokenAuthentication])
@permission_classes([AllowAny])
def forgot_password(request):
    try:
        username = request.data.get('username')
        if not username:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = CustomUser.objects.filter(username=username).first()
        if not user:
            return Response(status=status.HTTP_200_OK) # [aguilmea] because
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