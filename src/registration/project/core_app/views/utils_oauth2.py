import os
import random
import string
import requests
import hashlib
import base64
from django.http import HttpResponseRedirect

def generate_code_verifier():
    return base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').rstrip('=')

def generate_code_challenge(code_verifier):
    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(code_challenge).decode('utf-8').rstrip('=')

def send_oauth2_authorization_request(request):  # [aguilmea] this is the first part of the oauth2 flow - I prepare the url where the user should authenticate
    try:                       
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
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            'redirect_uri': os.environ.get('SERVER_URL') + '/registration/set_oauth2'
        })
        ft_access_token = response.json().get('access_token')
        request.session['ft_access_token'] = ft_access_token  
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)