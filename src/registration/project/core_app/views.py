# [aguilmea] this file has been created manually

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser
from .serializers import UserSerializer, LoginSerializer, DeleteUserSerializer

from datetime import datetime, timedelta


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    try:
        user_s = UserSerializer(data=request.data)
        if not user_s.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user_s.save()
        token_s = TokenObtainPairSerializer(data=request.data)
        if not token_s.is_valid(): # [aguilmea] not sure why this should happen and if i should keep the check
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        response = Response(status=status.HTTP_201_CREATED)
        
        response.data = token_s.validated_data
        
        access_token = token_s.validated_data['access']
        access_token_expiration = datetime.utcnow() + timedelta(minutes=5) 
        response.set_cookie(key='access', value=access_token, expires=access_token_expiration, httponly=True)

        refresh_token = token_s.validated_data['refresh']
        refresh_token_expiration = datetime.utcnow() + timedelta(days=1)
        response.set_cookie(key='refresh', value=refresh_token, expires=refresh_token_expiration, httponly=True)

        return response

    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request):
    user = request.user
    serializer = DeleteUserSerializer(data=request.data)
    if serializer.is_valid():
        try:
            current_password = serializer.validated_data['password']
            if not user.check_password(current_password):
                return Response({'error': 'password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': 'An error occurred: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    try:
        credentials_s = LoginSerializer(data=request.data)
        if not credentials_s.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = CustomUser.objects.filter(username=credentials_s.validated_data['username']).first()
        if user is None or not user.check_password(credentials_s.validated_data['password']):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        token_s = TokenObtainPairSerializer(data=request.data)
        if not token_s.is_valid(): # [aguilmea] not sure why this should happen and if i should keep the check
            return Response(token_s.errors, status=status.HTTP_400_BAD_REQUEST)
        
        response = Response(status=status.HTTP_200_OK)
        
        response.data = token_s.validated_data
        
        access_token = token_s.validated_data['access']
        access_token_expiration = datetime.utcnow() + timedelta(minutes=5) 
        response.set_cookie(key='access', value=access_token, expires=access_token_expiration, httponly=True)

        refresh_token = token_s.validated_data['refresh']
        refresh_token_expiration = datetime.utcnow() + timedelta(days=1)
        response.set_cookie(key='refresh', value=refresh_token, expires=refresh_token_expiration, httponly=True)

        return response

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    try:
        old_token = request.data.get('refresh_token')
        if not old_token:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
        new_token = RefreshToken(old_token)
        old_token.blacklist()
        return Response({'message': 'okay'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logout successful'}, status=status.HTTP_205_RESET_CONTENT)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TokenRefreshSerializer(data={'refresh': refresh_token})
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_token(request):
    return Response({'message': 'Token is valid'}, status=status.HTTP_200_OK)
