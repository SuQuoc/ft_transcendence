from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import os
import random
import string
import requests

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_oauth2_url(request):  # [aguilmea] this is the first part of the oauth2 flow - I prepare the url where the user should authenticate
    try:                        # [aguilmea] should it be done in the frontend? so that the state is verified there too?
        redirect_uri = os.environ.get('SERVER_URL') + '/callback'
        state = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        authorize_url = requests.Request('GET', 'https://api.intra.42.fr/oauth/authorize', params={
            'client_id': os.environ.get('FT_CLIENT_ID'),
            'redirect_uri': redirect_uri,
            'scope': 'public',
            'state': state,
            'response_type': 'code'
        }).prepare().url
        return Response({'url': authorize_url}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_oauth2(request):
    try:
        # [aguilmea] where do i check if state is the same as the one i sent in get_oauth2_url?
        code = request.data.get('code')
        response = requests.post('https://api.intra.42.fr/oauth/token', data={
            'grant_type': 'authorization_code',
            'client_id': os.environ.get('FT_CLIENT_ID'),
            'client_secret': os.environ.get('FT_CLIENT_SECRET'),
            'code': code,
            'redirect_uri': os.environ.get('SERVER_URL') + '/callback'
        })
        access_token = response.json().get('access_token')
        headers = {
        'Authorization': f'Bearer {access_token}'
    }
        user_response = requests.get('https://api.intra.42.fr/v2/me', headers=headers)
        if (user_response.status_code != 200):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user_details =user_response.json()
        id = user_details.get('id')
        setattr(request.user, 'ft_userid', id)
        return Response(status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unset_oauth2(request):
    try:
        setattr(request.user, 'ft_userid', None)
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