from rest_framework import serializers
from .models import RegistrationUser, OneTimePassword, OauthTwo
from django.contrib.auth.password_validation import validate_password, password_changed
from .models import RegistrationUser
import logging

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationUser
        fields = ['id', 'username', 'password']
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True},
            'backup_code': {'read_only': True},
            'password_set': {'read_only': True},
            'email_verified': {'read_only': True},
        }

class OneTimePasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = OneTimePassword
        fields = ['related_user', 'action', 'password', 'expire']
        extra_kwargs = {
            'password': {'write_only': True},
        }

class OauthTwoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OauthTwo
        fields = ['id', 'related_user', 'state', 'next_step']
        extra_kwargs = {
            'id': {'read_only': True},
            'state': {'write_only': True},
        }
