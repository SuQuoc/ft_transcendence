from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import RegistrationUser

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('password', None)

    def validate(self, attrs):
        username = attrs.get('username')
        user_exists = RegistrationUser.objects.filter(username=username).exists()

        if not user_exists:
            raise serializers.ValidationError('No active account found with the given credentials')

        user = RegistrationUser.objects.only('id', 'username').get(username=username)
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token.pop('password', None)
        token.pop('email', None)
        return token


class DeleteTokenObtainPairSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('password', None)

    def validate(self, attrs):
        username = attrs.get('username')
        user_exists = RegistrationUser.objects.filter(username=username).exists()

        if not user_exists:
            raise serializers.ValidationError('No active account found with the given credentials')

        user = RegistrationUser.objects.only('id', 'username').get(username=username)
        refresh = RefreshToken.for_user(user)

        return {
            'access': str(refresh.access_token),
		}

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['delete'] = 'True'
        token.pop('password', None)
        token.pop('email', None)
        return token