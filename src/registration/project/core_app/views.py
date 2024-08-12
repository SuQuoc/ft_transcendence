# [aguilmea] this file has been created manually
import logging

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import CustomUser
from .serializers import DeleteUserSerializer
from .serializers import UserSerializer

logger = logging.getLogger('core_app')

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    logger.debug(f"Signup request data: {request.data}")
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        try:
            validated_data = serializer.validated_data
            username = validated_data.get('username')
            email = validated_data.get('email')
            password = validated_data.get('password')
            if not (username and email and password):
                return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

            user = CustomUser(username=username, email=email)
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


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request):
    user = request.user
    serializer = DeleteUserSerializer(data=request.data)
    if serializer.is_valid():
        try:
            password = serializer.validated_data['password']
            if not user.check_password(password):
                return Response({'error': 'password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
            user.delete()
            return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.exception("An error occurred during the deletion of the user")
            return Response({'error': 'An error occurred: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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

        token_serializer = TokenObtainPairSerializer(data={'username': username, 'password': password})
        if token_serializer.is_valid():
            token = token_serializer.validated_data
            return Response({'token': token}, status=status.HTTP_200_OK)
        else:
            return Response(token_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.exception("An error occurred during login")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_token(request):
    return Response({'message': 'Token is valid'}, status=status.HTTP_200_OK)
