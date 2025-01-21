from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..authenticate import AccessTokenAuthentication, BackupCodeAuthentication
from .utils import generate_response_with_valid_JWT
from .token import CustomTokenObtainPairSerializer
from ..models import RegistrationUser
import logging

@api_view(['POST'])
@authentication_classes([BackupCodeAuthentication])
@permission_classes([IsAuthenticated])
def login(request):
    try:
        user = request.user
        if not user.is_verified():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        token_s = CustomTokenObtainPairSerializer(data=request.data)
        return generate_response_with_valid_JWT(user, status.HTTP_200_OK, token_s, backup_codes=None, response_body=None)
    except Exception as e:
        return Response({'login error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([AccessTokenAuthentication])
@permission_classes([IsAuthenticated])
def rotate_codes(request):
    try:
        user = request.user
        return Response(user.generate_backup_codes(), status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error generating new backup codes': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

