from django.conf import settings
from datetime import datetime, timezone
from rest_framework.response import Response
from rest_framework import status

from django.http import HttpResponseRedirect
if settings.SILK:
    from .utils_silk import conditional_silk_profile
from django.core.mail import send_mail

import os, requests, logging

def send_200_with_expired_cookies():
    response = Response(status=status.HTTP_200_OK)
    response.delete_cookie('access')
    response.delete_cookie('refresh')
    return response

def generate_response_with_valid_JWT(user, status_code, token_s, backup_codes=None, response_body=None):
    if not token_s.is_valid():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    response = Response(status=status_code)
    if response_body:
        response.data = response_body
    if backup_codes:
        response.data = {'backup_code': backup_codes}
    access_token = token_s.validated_data['access']
    access_token_expiration = datetime.now(timezone.utc) + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
    response.set_cookie(
        key='access',
        value=access_token,
        expires=access_token_expiration,
        domain=os.environ.get('DOMAIN'),
        httponly=True,
        secure=True,
        samesite = 'Strict')
    refresh_token = token_s.validated_data['refresh']
    refresh_token_expiration = datetime.now(timezone.utc) + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
    response.set_cookie(
        key='refresh',
        value=refresh_token,
        expires=refresh_token_expiration,
        domain=os.environ.get('DOMAIN'),
        httponly=True,
        secure=True,
        samesite = 'Strict')
    user.actualise_last_login(refresh_token)
    return response
#generate_response_with_valid_JWT = conditional_silk_profile(generate_response_with_valid_JWT, name=generate_response_with_valid_JWT)


def generate_redirect_with_state_cookie(hashed_state, authorize_url):
    response = HttpResponseRedirect(authorize_url)
    access_token_expiration = datetime.now(timezone.utc) + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
    response.set_cookie(
        key = 'state',
        value = hashed_state,
        expires=access_token_expiration,
        domain=os.environ.get('DOMAIN'),
        httponly=True,
        secure=True,
        samesite = 'Strict')
    return response


def send_delete_request_to_um(request, token_s):
    request_uri = 'http://usermanagement:8000/um/profile'
    headers = {'Content-Type': 'application/json',}
    access_token = token_s.validated_data['access']
    cookies = {
        'access': access_token,
    }
    response = requests.delete(request_uri, headers=headers, cookies=cookies)
    if response.status_code != 204:
        raise Exception('Error deleting user in UM')

def send_delete_request_to_game(request, token_s):
    request_uri = 'http://game:8000/daphne/delete_user_stats'
    headers = {'Content-Type': 'application/json',}
    access_token = token_s.validated_data['access']
    cookies = {
        'access': access_token,
    }
    response = requests.post(request_uri, headers=headers, cookies=cookies)
    if response.status_code != 204:
        raise Exception('Error deleting user in game: ' + str(response.status_code) + ' ' + str(response.text))
