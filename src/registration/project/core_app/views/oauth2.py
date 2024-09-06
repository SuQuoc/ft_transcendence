from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes , permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..authenticate import AccessTokenAuthentication, NoTokenAuthentication
from .utils_oauth2 import exchange_code_against_access_token, send_oauth2_authorization_request
import requests

@api_view(['GET'])
@authentication_classes([NoTokenAuthentication])
@permission_classes([IsAuthenticated])
def callback(request):
    try:
        ex = exchange_code_against_access_token(request)
        if (ex.status_code != 200):
            return ex.status_code
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([AccessTokenAuthentication])
@permission_classes([IsAuthenticated])
def set(request):
    try:
        send_oauth2_authorization_request(request)
        ft_access_token = request.session.get('ft_access_token')
        headers = {'Authorization': f'Bearer {ft_access_token}'}
        user_response = requests.get('https://api.intra.42.fr/v2/me', headers=headers)
        if (user_response.status_code != 200):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user_details =user_response.json()
        id = user_details.get('id')
        setattr(request.user, 'ft_userid', id)
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([AccessTokenAuthentication])
@permission_classes([IsAuthenticated])
def unset(request):
    try:
        setattr(request.user, 'ft_userid', None)
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([NoTokenAuthentication])
@permission_classes([IsAuthenticated])
def signup(request):
    try:
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([NoTokenAuthentication])
@permission_classes([IsAuthenticated])
def login(request):
    try:
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    