from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from ..authenticate import AccessTokenAuthentication, RefreshTokenAuthentication
from .token import DeleteTokenObtainPairSerializer
from .utils import generate_response_with_valid_JWT, send_200_with_expired_cookies, send_delete_request_to_um, send_delete_request_to_game
from .utils_otp import create_one_time_password, send_otp_email, check_one_time_password
import logging

@api_view(['POST'])
@authentication_classes([AccessTokenAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request):
    try:
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        user = request.user
        if (not current_password and user.password_is_set()) or not new_password:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if not user or (user.password_is_set() and not user.check_password(current_password)):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        otp = request.data.get('otp')
        if user.validate_password(new_password) is False:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if user.password_is_set() and not otp:
            otp = create_one_time_password(user.id, 'change_password')
            send_otp_email(user.username, 'change_password', otp)
            return Response(status=status.HTTP_202_ACCEPTED)
        if user.password_is_set() and not check_one_time_password(user, 'change_password', otp):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user.validate_password(new_password)
        user.set_password(new_password)
        user.change_password_is_set()
        user.save()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'change_password error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([AccessTokenAuthentication])
@permission_classes([IsAuthenticated])
def change_username(request):
    try:
        new_username = request.data.get('new_username')
        if not new_username:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        otp_old = request.data.get('otp_old_email')
        otp_new = request.data.get('otp_new_email')
        backup_code = request.data.get('backup_code')
        if not otp_new:
            if otp_old is not None or backup_code is not None:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            otp_new = create_one_time_password(user.id, 'change_username_new')
            send_otp_email(new_username, 'change_username_new', otp_new)
            otp_old = create_one_time_password(user.id, 'change_username_old')
            send_otp_email(user.username, 'change_username_old', otp_old)
            return Response(status=status.HTTP_202_ACCEPTED)
        if otp_old is not None and backup_code is not None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if not check_one_time_password(user, 'change_username_new', otp_new):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if otp_old:
            if not check_one_time_password(user, 'change_username_old', otp_old):
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        elif not backup_code:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif not user.check_backup_code(backup_code):
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        user.username = new_username
        user.ft_userid = None
        user.save()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'change_username error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([AccessTokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_user(request):
    try:
        current_password = request.data.get('password')
        otp = request.data.get('otp')
        user = request.user
        if not current_password:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(current_password):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if otp is None:
            otp = create_one_time_password(user.id, 'delete_user')
            send_otp_email(user.username, 'delete_user', otp)
            return Response(status=status.HTTP_202_ACCEPTED)
        if not check_one_time_password(user, 'delete_user', otp):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        token_s = DeleteTokenObtainPairSerializer(data={'username': user.username})
        if not token_s.is_valid():
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        send_delete_request_to_game(request, token_s)
        send_delete_request_to_um(request, token_s)
        user.delete()
        return send_200_with_expired_cookies()
    except Exception as e:
        return Response({'delete_user error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([AccessTokenAuthentication])
@permission_classes([IsAuthenticated])
def get_email(request):
    try:
        user = request.user
        password_set = user.password_is_set()
        return Response({'email': user.username, 'password_set': password_set}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'get_email error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([AccessTokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        return send_200_with_expired_cookies()
    except Exception as e:
        return Response({'logout error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([AccessTokenAuthentication])
@permission_classes([IsAuthenticated])
def verify_token(request):
    try:
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'verify_token error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        return Response({'refresh_token error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
