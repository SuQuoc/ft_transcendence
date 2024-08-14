# [aguilmea] file was created manually
from rest_framework import serializers

from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'id', 'password']
        extra_kwargs = {
            'id': {'read_only': True},  # read-only so it's not required in POST requests
            'password': {'write_only': True},  # write-only so it's not returned in GET requests
        }

    def create(self, validated_data):
        password = validated_data.pop('password')  # Pop the password out of the validated_data dictionary
        user = CustomUser(**validated_data)  # Create a new user instance with the validated data
        user.set_password(password)  # Set the password for the user instance(it will be hased in this way)
        user.save()  # Save the user instance to the database
        return user  # Return the user instance

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)  # Pop the password out of the validated_data dictionary (if it exists)
        for attr, value in validated_data.items():  # Iterate over the validated_data dictionary and set each attribute on the user instance
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)  # Set the password for the user instance (if it exists)
        instance.save()
        return instance


class DeleteUserSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
