import os
import random
import string
import requests
import hashlib
import base64
from rest_framework import status
from rest_framework.response import Response

from ..models import OauthTwo
from ..serializers import OauthTwoSerializer

# https://www.oauth.com/oauth2-servers/pkce/authorization-request/

def generate_code_challenge(code_verifier):
    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(code_challenge).decode('utf-8').rstrip('=')

def generate_code_verifier_and_challenge(related_user):
    if related_user is None:
        raise Exception('related_user is None')
    try:
        for oauth_token in OauthTwo.objects.filter(related_user=related_user):
            oauth_token.delete()
        code_verifier = ''.join(random.choices(string.ascii_uppercase + string.digits, k=128))
        code_challenge =  generate_code_challenge(code_verifier)
        state = ''.join(random.choices(string.ascii_uppercase + string.digits, k=128))
        oauth_token_data = {
            'related_user': related_user,
            'code_verifier': code_verifier,
            'code_challenge': code_challenge,
            'state': state
        }
        oauth_token_s = OauthTwoSerializer(data=oauth_token_data)
        if not oauth_token_s.is_valid():
            raise Exception({'generate_code_verifier serialiazer' : oauth_token_s.errors})
        oauth_token_s.save()
        return
    except Exception as e:
        raise Exception({'generate_code_verifier error': str(e)})


def exchange_code_against_access_token(request):
    try:
        authorization_code = request.query_params.get("code", "")
        returned_state = request.query_params.get("state", "")
        code_verifier = request.session.get('code_verifier')
        stored_state = request.session.get('oauth_state')

        if returned_state != stored_state:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        response = requests.post('https://api.intra.42.fr/oauth/token', data={
            'grant_type': 'authorization_code',
            'client_id': os.environ.get('FT_CLIENT_ID'),
            'client_secret': os.environ.get('FT_CLIENT_SECRET'),
            'code': authorization_code,
            'code_verifier': code_verifier,
            'redirect_uri': os.environ.get('SERVER_URL') + '/registration/set_oauthtwo'
        })
        ft_access_token = response.json().get('access_token')
        request.session['ft_access_token'] = ft_access_token  
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)