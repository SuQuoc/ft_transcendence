from datetime import datetime, timezone
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import os

def generate_response_with_valid_JWT(status_code, token_s):
    response = Response(status=status_code)
    if not token_s.is_valid():
        return Response(status=status.HTTP_400_BAD_REQUEST)
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
    return response

def generate_response_with_invalid_JWT(status_code, token_s):
    response = Response(status=status_code)
    if not token_s.is_valid():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    access_token = token_s.validated_data['access']
    access_token_expiration = datetime.now(timezone.utc)
    response.set_cookie(
        key='access',
        value=access_token,
        expires=access_token_expiration,
        domain=os.environ.get('DOMAIN'),
        httponly=True,
        secure=True,
        samesite = 'Strict')
    refresh_token = token_s.validated_data['refresh']
    refresh_token_expiration = datetime.now(timezone.utc)
    response.set_cookie(
        key='refresh',
        value=refresh_token,
        expires=refresh_token_expiration,
        domain=os.environ.get('DOMAIN'),
        httponly=True,
        secure=True,
        samesite = 'Strict')
    return response

