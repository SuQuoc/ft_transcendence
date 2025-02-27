from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import APIException
from .models import CustomUser
from .validators import displayname_validator
from rest_framework.validators import UniqueValidator

MEGABYTE_LIMIT = 1

class CustomUserCreateSerializer(serializers.ModelSerializer):
    # NOTE: only needed because of write_only=True, 
    # if UUIDField is left out then the id is send with the response
    user_id = serializers.UUIDField(write_only=True, 
                                    validators=[
                                        UniqueValidator(
                                            queryset=CustomUser.objects.all()
                                        )
                                    ]
    ) 

    class Meta:
        model = CustomUser
        fields = ["displayname", "user_id"]

class CustomUserProfileSerializer(serializers.ModelSerializer):
    # serializerMethodField https://www.youtube.com/watch?v=67mUq2pqF3Y
    
    class Meta:
        model = CustomUser
        fields = ["displayname", "image"]


class UserRelationSerializer(serializers.ModelSerializer):
    # serializerMethodField https://www.youtube.com/watch?v=67mUq2pqF3Y
    relationship = serializers.SerializerMethodField()
    friend_request_id = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ["user_id", "displayname", "image", "relationship", "friend_request_id"] # "online",

    def get_relationship(self, obj):
        relationships = self.context.get('relationships', {})
        return relationships.get(obj.user_id, None) # view always provides user_id in dict so None should never happen
    
    def get_friend_request_id(self, obj):
        friend_request_id = self.context.get('friend_requests', {})
        return friend_request_id.get(obj.user_id, None)


class ImageTooLargeError(APIException):
    status_code = 413
    default_detail = 'A custom validation error occurred.'
    default_code = 'custom_validation_error'

def profile_image_validator(image):
    filesize = image.size

    if filesize > MEGABYTE_LIMIT * 1024 * 1024:
        raise ImageTooLargeError(f"Max file size is {MEGABYTE_LIMIT}MB")


class CustomUserEditSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(validators=[profile_image_validator])

    class Meta:
        model = CustomUser
        fields = ["displayname", "image"]

    def validate(self, data):
        if data.get('displayname') is None and data.get('image') is None:
            raise serializers.ValidationError("No valid field provided.")
        return data



