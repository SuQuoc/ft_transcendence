from rest_framework import serializers
from .models import RegistrationUser, OneTimePassword, OauthTwo
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationUser
        fields = ['id', 'username', 'password']
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True},
            'backup_code': {'read_only': True},
        }

    def create(self, validated_data):
        # validate_password(validated_data['password'], user=None) # [aguilmea] not setup yet to make testing easier
        validated_data.pop('otp', None)
        password = validated_data.pop('password')
        user = RegistrationUser(**validated_data)
        user.set_password(password)
        user.save()
        # password_changed(password, user=user, password_validators=None)
        return user 

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None) 
        for attr, value in validated_data.items(): 
            setattr(instance, attr, value)
        if password:
            # validate password(password, user=instance) # [aguilmea] not setup yet to make testing easier
            instance.set_password(password) 
            # password_changed(password, user=instance, password_validators=None) #[aguilmea] password_changed is basically a way for Django to say to all password validators: "Hey, take note, the user's password has been changed to this value, so if you need to keep track of for some reason, do it now, because after this, I'll destroy the unhashed version of this password"
        instance.save()
        return instance

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
        fields = ['id', 'related_user', 'state', 'next_step', ]
        extra_kwargs = {
            'id': {'read_only': True},
            'state': {'write_only': True},
        }

    def create(self, validated_data):
        state = validated_data.pop('state')
        oauthtwo = OauthTwo(**validated_data)
        oauthtwo.state = make_password(state)
        oauthtwo.save()
        return oauthtwo