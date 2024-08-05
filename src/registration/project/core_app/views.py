# [aguilmea] this file has been created manually
import logging
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .serializers import UserSerializer
from .models import CustomUser
from rest_framework.authtoken.models import Token

logger = logging.getLogger('core_app')

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    logger.debug(f"Signup request data: {request.data}")
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        try:
            validated_data = serializer.validated_data
            logger.debug(f"Validated data: {validated_data}")

            # Extracting fields and adding logs to check if they exist
            username = validated_data.get('username')
            email = validated_data.get('email')
            first_name = validated_data.get('first_name')
            last_name = validated_data.get('last_name')
            password = validated_data.get('password')

            if not username:
                logger.debug("Username is missing in validated data")
            if not email:
                logger.debug("Email is missing in validated data")
            if not first_name:
                logger.debug("First name is missing in validated data")
            if not last_name:
                logger.debug("Last name is missing in validated data")
            if not password:
                logger.debug("Password is missing in validated data")

            if not (username and email and first_name and last_name and password):
                return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

            user = CustomUser(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            user.set_password(password)
            user.save()
            logger.debug(f"User created: {user.username}")

            token_serializer = TokenObtainPairSerializer(data={'username': username, 'password': password})
            if token_serializer.is_valid():
                token = token_serializer.validated_data
                return Response({'token': token, 'user': serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response(token_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception("An error occurred during user signup")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        logger.debug(f"Signup serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    try:
        username = request.data.get('username')
        password = request.data.get('password')

        logger.debug(f"Received login attempt with username: {username} and password: {password}")

        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.filter(username=username).first()
        logger.debug(f"Query result: {user}")

        if user is None:
            logger.debug(f"No user found with username: {username}")
            return Response({'error': 'Invalid username or password 1'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            logger.debug("Invalid password provided")
            return Response({'error': 'Invalid username or password 2'}, status=status.HTTP_401_UNAUTHORIZED)

        token, created = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(user)

        logger.debug(f"Token created: {token.key}")
        return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception("An error occurred during login")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    try:
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']

            logger.debug(f"Old password: {old_password}, New password: {new_password}")

            if not user.check_password(old_password):
                return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()

            return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.exception("An error occurred during password change")
        return Response({'error': 'An error occurred: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication



def obtain_token(request):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)

def refresh_token(request):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_token(request):
    return Response({'message': 'Token is valid'}, status=status.HTTP_200_OK)
