from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes , permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponseRedirect

from ..authenticate import AccessTokenAuthentication, NoTokenAuthentication

import os
import random
import string
import requests
import hashlib
import base64

def generate_code_verifier():
    return base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').rstrip('=')

def generate_code_challenge(code_verifier):
    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(code_challenge).decode('utf-8').rstrip('=')

@api_view(['GET'])
@authentication_classes([AccessTokenAuthentication])
@permission_classes([IsAuthenticated])
def send_oauth2_authorization_request(request):  # [aguilmea] this is the first part of the oauth2 flow - I prepare the url where the user should authenticate
    try:                        # [aguilmea] should it be done in the frontend? so that the state is verified there too?
        redirect_uri = os.environ.get('SERVER_URL') + '/registration/exchange_code_against_access_token'
        code_verifier = generate_code_verifier()
        state = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        
        request.session['code_verifier'] = code_verifier
        request.session['state'] = state

        authorize_url = requests.Request('GET', 'https://api.intra.42.fr/oauth/authorize', params={
            'client_id': os.environ.get('FT_CLIENT_ID'),
            'redirect_uri': redirect_uri,
            'scope': 'public',
            'state': state,
            'code_challenge': generate_code_challenge(code_verifier),
            'code_challenge_method': 'S256',
            'response_type': 'code'
        }).prepare().url
        return HttpResponseRedirect(authorize_url)
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([AccessTokenAuthentication])
@permission_classes([IsAuthenticated])
def exchange_code_against_access_token(request):
    try:
        authorization_code = request.query_params.get("code", "")
        returned_state = request.query_params.get("state", "")
        code_verifier = request.session.get('code_verifier')
        stored_state = request.session.get('oauth_state')

        if returned_state != stored_state:
            return HttpResponseRedirect('/error?message=Failed to retrieve user information')

        response = requests.post('https://api.intra.42.fr/oauth/token', data={
            'grant_type': 'authorization_code',
            'client_id': os.environ.get('FT_CLIENT_ID'),
            'client_secret': os.environ.get('FT_CLIENT_SECRET'),
            'code': authorization_code,
            'code_verifier': code_verifier,
            'redirect_uri': os.environ.get('SERVER_URL') + '/registration/set_oauth2'
        })
        access_token = response.json().get('access_token')
        headers = {'Authorization': f'Bearer {access_token}'}
    
        user_response = requests.get('https://api.intra.42.fr/v2/me', headers=headers)
        if (user_response.status_code != 200):
            return HttpResponseRedirect('/error?message=Failed to retrieve user information')
        user_details =user_response.json()
        id = user_details.get('id')
        setattr(request.user, 'ft_userid', id)
        redirect_url = os.environ.get('SERVER_URL')
        return HttpResponseRedirect(redirect_url)
    
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([AccessTokenAuthentication])
@permission_classes([IsAuthenticated])
def unset_oauth2(request):
    try:
        setattr(request.user, 'ft_userid', None)
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
@authentication_classes([NoTokenAuthentication])
@permission_classes([IsAuthenticated])
def login_oauth2(request):
    try:
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)