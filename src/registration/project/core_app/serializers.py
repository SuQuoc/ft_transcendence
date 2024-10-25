from rest_framework import serializers
from .models import RegistrationUser, OneTimePassword, OauthTwo
from django.contrib.auth.password_validation import validate_password, password_changed
from .models import RegistrationUser
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
            'twofa_enabled': {'read_only': True},
        }

    def create(self, validated_data):
        validate_password(validated_data['password'], user=None)
        validated_data.pop('otp', None)
        password = validated_data.pop('password')
        user = RegistrationUser(**validated_data)
        user.set_password(password)
        if not user.password_is_set():
            user.password_set = True
        user.save()
        password_changed(password, user=user, password_validators=None)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            validate_password(password, user=instance)
            instance.set_password(password)
            if not instance.password_is_set():
                instance.password_set = True
            password_changed(password, user=instance, password_validators=None) #[aguilmea] password_changed is basically a way for Django to say to all password validators: "Hey, take note, the user's password has been changed to this value, so if you need to keep track of for some reason, do it now, because after this, I'll destroy the unhashed version of this password"
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
        fields = ['id', 'related_user', 'state', 'next_step']
        extra_kwargs = {
            'id': {'read_only': True},
            'state': {'write_only': True},
        }
