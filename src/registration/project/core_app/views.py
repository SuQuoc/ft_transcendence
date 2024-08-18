# [aguilmea] this file has been created manually

from datetime import datetime
from datetime import timedelta

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
from .serializers import DeleteUserSerializer
from .serializers import LoginSerializer
from .serializers import UserSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    try:
        user_s = UserSerializer(data=request.data)
        if not user_s.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user_s.save()
        token_s = TokenObtainPairSerializer(data=request.data)
        if not token_s.is_valid():  # [aguilmea] not sure why this should happen and if i should keep the check
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


@api_view(['POST'])
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
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        if not token_s.is_valid():  # [aguilmea] not sure why this should happen and if i should keep the check
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
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        refresh = request.COOKIES.get('refresh')
        if not current_password or not new_password or not refresh:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if not user.check_password(current_password):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        refresh_token = RefreshToken(refresh)
        refresh_token.blacklist()

        new_refresh = RefreshToken.for_user(user)
        new_access = new_refresh.access_token
        
        response = Response({
            'access': str(new_access),
            'refresh': str(new_refresh)
        }, status=status.HTTP_200_OK)

        access_token_expiration = datetime.utcnow() + timedelta(minutes=5)
        response.set_cookie(
            key='access',
            value=str(new_access),
            expires=access_token_expiration,
            httponly=True
        )

        refresh_token_expiration = datetime.utcnow() + timedelta(days=1)
        response.set_cookie(
            key='refresh',
            value=str(new_refresh),
            expires=refresh_token_expiration,
            httponly=True
        )

        return response

    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.COOKIES.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logout successful'}, status=status.HTTP_205_RESET_CONTENT)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def refresh_token(request):
    try:
        refresh_token = request.COOKIES.get('refresh')
        if not refresh_token:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        token_s = TokenRefreshSerializer(data={'refresh': refresh_token})
        if not token_s.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_token(request):
    return Response({'message': 'Token is valid'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def set_oauth2(request):
    try:
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unset_oauth2(request):
    try:
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def login_oauth2(request):
    try:
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)