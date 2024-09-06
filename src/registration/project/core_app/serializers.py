# [aguilmea] file was created manually
from rest_framework import serializers

from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password', 'enabledtwofa', 'ft_userid']
        extra_kwargs = {
            'id': {'read_only': True},          # [aguilmea] read-only so it's not necessary for creation
            'password': {'write_only': True},   # [aguilmea] write-only so it's not returned in get requests
        }                                       # [aguilmea] I should have a regex or something like that just like in CustomUser model

    def create(self, validated_data):
        password = validated_data.pop('password') 
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()  
        return user 

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None) 
        for attr, value in validated_data.items(): 
            setattr(instance, attr, value)
        if password:
            instance.set_password(password) 
        instance.save()
        return instance

