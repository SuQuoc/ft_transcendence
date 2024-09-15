from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from ..authenticate import AccessTokenAuthentication, RefreshTokenAuthentication
from .utils import generate_response_with_valid_JWT, send_200_with_expired_cookies, send_delete_request_to_um
from .utils_otp import create_one_time_password, send_otp_email, check_one_time_password

@api_view(['POST'])
@authentication_classes([AccessTokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_user(request):
    try:
        current_password = request.data.get('password')
        if not current_password:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        #send_delete_request_to_game # [aguilmea] here because if we delete the statistics but not the user it is better
            # return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response = send_delete_request_to_um(request)
        if response.status_code != 200:
            return response
        user = request.user
        if not user.check_password(current_password):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user.delete()
        return send_200_with_expired_cookies()
    except Exception as e:
        return Response({'delete_user error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([AccessTokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        return send_200_with_expired_cookies()
    except Exception as e:
        return Response({'logout error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([AccessTokenAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request):
    try:
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        if not current_password or not new_password:
            return Response({1}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if not user or not user.check_password(current_password):
            return Response({2}, status=status.HTTP_401_UNAUTHORIZED)
        otp = request.data.get('otp')
        if not otp:
            otp = create_one_time_password(user.id, 'change_password')
            send_otp_email(user.username, 'change_password', otp)
            return Response({3}, status=status.HTTP_202_ACCEPTED)
        if not check_one_time_password(user, 'change_password', otp):
            return Response({4}, status=status.HTTP_401_UNAUTHORIZED)
        user.set_password(new_password)
        user.save()
        return send_200_with_expired_cookies()
    except Exception as e:
        return Response({'change_password error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
