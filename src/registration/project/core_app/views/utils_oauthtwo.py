import os, requests
import secrets

from rest_framework import status, serializers
from rest_framework.response import Response

from ..serializers import UserSerializer, OauthTwoSerializer
from ..models import RegistrationUser
from .utils import generate_response_with_valid_JWT

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .token import CustomTokenObtainPairSerializer
import time, logging

def generate_authorization_request_data(request, state):
    try:
        next_step = request.data.get('next_step')
        id = None
        if request.user:
            id = request.user.id
        data = {
            'next_step' : next_step,
            'related_user': id,
            'state': state
        }
        oauth_token_s = OauthTwoSerializer(data=data)
        if not oauth_token_s.is_valid():
            raise Exception({'generate_code_verifier serialiazer' : oauth_token_s.errors})
        oauth = oauth_token_s.save()
        return oauth.get_hashed_state()
    except Exception as e:
        raise Exception({'generate_authorization_request_data': str(e)})

def request_ft_token(returned_authorization_code):
    try:
        redirect_uri = os.environ.get('SERVER_URL') + '/callback'
        token_response = requests.post('https://api.intra.42.fr/oauth/token', data={
            'grant_type': 'authorization_code',
            'client_id': os.environ.get('FT_CLIENT_ID'),
            'client_secret': os.environ.get('FT_CLIENT_SECRET'),
            'code': returned_authorization_code,
            'redirect_uri': redirect_uri
        })
        if token_response.status_code != 200:
           raise Exception({'request_ft_user': token_response.json()})
        token_data = token_response.json()
        return token_data.get('access_token')
    except Exception as e:
        raise Exception({'request_ft_token': str(e)})

def request_ft_user(ft_access_token):
    try:
        response = requests.get('https://api.intra.42.fr/v2/me', headers={
            'Authorization': f'Bearer {ft_access_token}'
        })
        if response.status_code != 200:
            raise Exception({'request_ft_user': response.status_code()})
        return response.data.get('id')
    except Exception as e:
        raise Exception({'request_ft_user': str(e)})

def request_ft_email(ft_access_token):
    try:
        response = requests.get('https://api.intra.42.fr/v2/me', headers={
            'Authorization': f'Bearer {ft_access_token}'
        })
        if response.status_code != 200:
            raise Exception({'request_ft_email': response.status_code()})
        return response.data.get('id')
    except Exception as e:
        raise Exception({'request_ft_email': str(e)})

def login(email):
    try:
        user = RegistrationUser.objects.filter(username=email).first()
        if user is None:
            return Response({'login error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
        data = {
            'username': email,
            #'password': 'to be changed' # [aguilmea] I have to check how to send JWT without valid password and write a own TokenObtainSerializer
        }
        token_s = CustomTokenObtainPairSerializer(data=data)
        if not user.password_is_set():
            return generate_response_with_valid_JWT(status.HTTP_200_OK, token_s, response_body={'user_status': 'password not set'})
        return generate_response_with_valid_JWT(status.HTTP_200_OK, token_s)
    except Exception as e:
        return Response({'login error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_ft_email(ft_access_token):
    headers = {'Authorization': f'Bearer {ft_access_token}'}
    response = requests.get('https://api.intra.42.fr/v2/me', headers=headers)
    if response.status_code != 200:
        return Response({str(response)}, status=status.HTTP_401_UNAUTHORIZED)
    user_details = response.json()
    email = user_details.get('email')
    return email


def signup(email):
    try:
        data = {
            'username': email,
            'password': secrets.token_hex(16)
        }
        user_s = UserSerializer(data=data)
        logging.warning(f"signup: {data}")
        if not user_s.is_valid():
            logging.warning(f"signup: {user_s.errors}")
            return Response({'signup error': data}, status=status.HTTP_400_BAD_REQUEST)
        user_s.save()
        token_s = CustomTokenObtainPairSerializer(data=data)
        return generate_response_with_valid_JWT(status.HTTP_200_OK, token_s)
    except Exception as e:
        return Response({'signup error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
