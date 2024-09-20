from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes , permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import redirect

from ..authenticate import AccessTokenAuthentication
from .utils_oauthtwo import exchange_code_against_access_token, generate_code_verifier_and_challenge
from ..models import OauthTwo

import requests
import os

@api_view(['POST'])
@permission_classes([AllowAny])
def callback(request):
    try:
        ex = exchange_code_against_access_token(request)
        if (ex.status_code != 200):
            return ex.status_code
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'oauthtwo_callback error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# [aguilmea] this will not work for signup and login 
@api_view(['GET'])
@authentication_classes([AccessTokenAuthentication])
@permission_classes([IsAuthenticated])
def send_authorization_request(request):  # [aguilmea] this is the first part of the oauth2 flow - I prepare the url where the user should authenticate
    try:
        user = request.user
        redirect_uri = os.environ.get('SERVER_URL') + '/registration/exchange_code_against_access_token'
        generate_code_verifier_and_challenge(request.user.id)
        state = OauthTwo.objects.get(related_user=user).state
        code_chalenge = OauthTwo.objects.get(related_user=user).code_challenge
        authorize_url = requests.Request('GET', 'https://api.intra.42.fr/oauth/authorize', params={
            'client_id': os.environ.get('FT_CLIENT_ID'),
            'redirect_uri': redirect_uri,
            'scope': 'public',
            'state': state,
            'code_challenge': code_chalenge,
            'code_challenge_method': 'S256',
            'response_type': 'code'
        }).prepare().url
        redirect(authorize_url) # Redirect the user to the authorization URL
        return Response({authorize_url}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'oauthtwo_send_authorization_request error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([AccessTokenAuthentication])
@permission_classes([IsAuthenticated])
def set(request):
    try:
#        oauthtwo_send_authorization_request(request)
        ft_access_token = request.session.get('ft_access_token')
        headers = {'Authorization': f'Bearer {ft_access_token}'}
        user_response = requests.get('https://api.intra.42.fr/v2/me', headers=headers)
        if (user_response.status_code != 200):
            return Response({str(user_response)}, status=status.HTTP_401_UNAUTHORIZED)
        user_details =user_response.json()
        id = user_details.get('id')
        setattr(request.user, 'ft_userid', id)
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'oauthwo_set error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([AccessTokenAuthentication])
@permission_classes([IsAuthenticated])
def unset(request):
    try:
        setattr(request.user, 'ft_userid', None)
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'oauthtwo_unset error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    try:
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'oauthtwo_signup error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    try:
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'oauth2_login error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    