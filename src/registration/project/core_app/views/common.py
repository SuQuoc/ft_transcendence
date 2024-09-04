from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from ..authenticate import AccessTokenAuthentication, RefreshTokenAuthentication
from .utils_jwt import generate_response_with_valid_JWT

@api_view(['GET'])
@authentication_classes([AccessTokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        response = Response(status=status.HTTP_200_OK)
        response.delete_cookie('access')
        response.delete_cookie('refresh')
        return response
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
        refresh_token.blacklist()
        user.delete()
        response = Response(status=status.HTTP_200_OK)
        return response
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
    return Response(status=status.HTTP_200_OK)
