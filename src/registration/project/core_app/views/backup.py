from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..authenticate import BackupCodeAuthentication
from .utils import generate_response_with_valid_JWT
from .token import CustomTokenObtainPairSerializer
import logging

@api_view(['POST'])
@authentication_classes([BackupCodeAuthentication])
@permission_classes([IsAuthenticated])
def login(request):
    try:
        user = request.user
        if not user.is_verified():
            return Response({1}, status=status.HTTP_400_BAD_REQUEST)
        token_s = CustomTokenObtainPairSerializer(data=request.data)
        return generate_response_with_valid_JWT(status.HTTP_200_OK, token_s)
    except Exception as e:
        return Response({'login error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
