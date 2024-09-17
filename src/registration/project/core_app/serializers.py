# [aguilmea] file was created manually
from rest_framework import serializers

from .models import RegistrationUser, OneTimePassword


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationUser
        fields = ['id', 'username', 'password']
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        # validate_password(validated_data['password'], user=None) # [aguilmea] not setup yet to make testing easier
        validated_data.pop('otp')
        password = validated_data.pop('password')
        user = RegistrationUser(**validated_data)
        user.set_password(password)
        user.save()  
        return user 

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None) 
        for attr, value in validated_data.items(): 
            setattr(instance, attr, value)
        if password:
            # validate password(password, user=instance) # [aguilmea] not setup yet to make testing easier
            instance.set_password(password) 
        instance.save()
        return instance

class OneTimePasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = OneTimePassword
        fields = ['related_user', 'action', 'password', 'expire']
        extra_kwargs = {
            'password': {'write_only': True},
        }
