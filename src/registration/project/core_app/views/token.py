from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
#from django.contrib.auth import authenticate
from ..authenticate import UsernameAuthentication

import logging

from ..models import RegistrationUser


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the password field
        self.fields.pop('password', None)

    def validate(self, attrs):
        username = attrs.get('username')
        user_exists = RegistrationUser.objects.filter(username=username).exists()

        if not user_exists:
            raise serializers.ValidationError('No active account found with the given credentials')

        user = RegistrationUser.objects.get(username=username)
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
