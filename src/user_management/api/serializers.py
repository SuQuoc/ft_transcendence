import uuid

from rest_framework import serializers

from .models import CustomUser

MEGABYTE_LIMIT = 5


class CustomUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["displayname"]


class CustomUserProfileSerializer(serializers.ModelSerializer):
    # serializerMethodField https://www.youtube.com/watch?v=67mUq2pqF3Y
    is_self = serializers.SerializerMethodField()
    is_friend = serializers.SerializerMethodField()
    is_stranger = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ["displayname", "online", "image", "is_self", "is_friend", "is_stranger"]  # +avatar

    def get_is_self(self, obj):
        return self.context.get('is_self', False)

    def get_is_friend(self, obj):
        return self.context.get('is_friend', False)

    def get_is_stranger(self, obj):
        return self.context.get('is_stranger', False)


from django.core.files.images import get_image_dimensions
from rest_framework.exceptions import ValidationError


def profile_image_validator(image):
    filesize = image.size

    # width, height = get_image_dimensions(image)
    # if width != REQUIRED_WIDTH or height != REQUIRED_HEIGHT:
    #     raise ValidationError(f"You need to upload an image with {REQUIRED_WIDTH}x{REQUIRED_HEIGHT} dimensions")

    if filesize > MEGABYTE_LIMIT * 1024 * 1024:
        raise ValidationError(f"Max file size is {MEGABYTE_LIMIT}MB")


class CustomUserEditSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(validators=[profile_image_validator])

    class Meta:
        model = CustomUser
        fields = ["displayname", "image"]


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
