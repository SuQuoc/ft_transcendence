import uuid

from rest_framework import serializers

from .models import CustomUser


class CustomUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["user_id", "displayname"]

    # def validate_displayname(self, value):
    #    if CustomUser.objects.filter(displayname=value).exists():
    #        raise serializers.ValidationError(f"Displayname \"{value}\" already in use")
    #    return value


#
# def validate_user_id(self, value):
#    if CustomUser.objects.filter(user_id=value).exists():
#        raise serializers.ValidationError("User with this id already exists")
#    return value
#
# def validate(self, data):
#    if 'displayname' not in data:
#        raise serializers.ValidationError({"displayname": "This field is required."})
#    if 'user_id' not in data:
#        raise serializers.ValidationError({"user_id": "This field is required."})
#    return data
#
# def create(self, validated_data):
#    # Custom creation logic here
#    user_instance = CustomUser.objects.create(**validated_data)
#    # print(f"user_instance: {user_instance}")
#    return user_instance


class CustomUserProfileSerializer(serializers.ModelSerializer):
    # serializerMethodField https://www.youtube.com/watch?v=67mUq2pqF3Y
    is_self = serializers.SerializerMethodField()
    is_friend = serializers.SerializerMethodField()
    is_stranger = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ["displayname", "online", "is_self", "is_friend", "is_stranger"]  # +avatar

    def get_is_self(self, obj):
        return self.context.get('is_self', False)

    def get_is_friend(self, obj):
        return self.context.get('is_friend', False)

    def get_is_stranger(self, obj):
        return self.context.get('is_stranger', False)


class CustomUserEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["displayname"]  # +avatar


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
