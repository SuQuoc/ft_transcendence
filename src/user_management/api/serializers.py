from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import CustomUser

MEGABYTE_LIMIT = 1


class CustomUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["displayname"]


class CustomUserProfileSerializer(serializers.ModelSerializer):
    # serializerMethodField https://www.youtube.com/watch?v=67mUq2pqF3Y
    relationship = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ["displayname", "online", "image", "relationship"]

    def get_relationship(self, obj):
        return self.context.get('relationship', "error: could not resolve [should never happen]")


def profile_image_validator(image):
    filesize = image.size

    # width, height = get_image_dimensions(image)
    # if width != REQUIRED_WIDTH or height != REQUIRED_HEIGHT:
    #     raise ValidationError(f"You need to upload an image with {REQUIRED_WIDTH}x{REQUIRED_HEIGHT} dimensions")

    if filesize > MEGABYTE_LIMIT * 1024 * 1024:
        raise ValidationError(f"Max file size is {MEGABYTE_LIMIT}MB")


# old
class CustomUserEditSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(validators=[profile_image_validator])

    class Meta:
        model = CustomUser
        fields = ["displayname", "image"]
