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
        # Get the user using the username
        #TODO: check why we get UsernameAuthentication.authenticate() got an unexpected keyword argument 'username'
        username = attrs.get('username')
        user = RegistrationUser.objects.filter(username=username).first()

        if user is None:
            logging.warning('No active account found with the given credentials')
            raise serializers.ValidationError('No active account found with the given credentials')

        # Create the token pair
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
