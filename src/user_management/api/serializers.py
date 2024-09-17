from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import APIException
from .models import CustomUser

MEGABYTE_LIMIT = 1

class CustomUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["displayname"]

# for deserilazing
class CustomUserProfileSerializer(serializers.ModelSerializer):
    # serializerMethodField https://www.youtube.com/watch?v=67mUq2pqF3Y
    relationship = serializers.SerializerMethodField(required=False)
    
    class Meta:
        model = CustomUser
        fields = ["displayname", "online", "image", "relationship"]
    
    def get_relationship(self, obj):
        return self.context.get('relationship', None)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if self.get_relationship(instance) != "friend":
            representation.pop('online')
            representation.pop('relationship')

        return representation


class ImageTooLargeError(APIException):
    status_code = 413
    default_detail = 'A custom validation error occurred.'
    default_code = 'custom_validation_error'

def profile_image_validator(image):
    filesize = image.size

    # width, height = get_image_dimensions(image)
    # if width != REQUIRED_WIDTH or height != REQUIRED_HEIGHT:
    #     raise ValidationError(f"You need to upload an image with {REQUIRED_WIDTH}x{REQUIRED_HEIGHT} dimensions")

    if filesize > MEGABYTE_LIMIT * 1024 * 1024:
        raise ImageTooLargeError(f"Max file size is {MEGABYTE_LIMIT}MB")



class UserRelationSerializer(serializers.ModelSerializer):
    # serializerMethodField https://www.youtube.com/watch?v=67mUq2pqF3Y
    relationship = serializers.SerializerMethodField()
    friend_request_id = serializers.SerializerMethodField()
    online = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ["user_id", "displayname", "online", "image", "relationship", "friend_request_id"]

    def get_relationship(self, obj):
        relationships = self.context.get('relationships', {})
        return relationships.get(obj.user_id, None) # view always provides user_id in dict so None should never happen
    
    def get_friend_request_id(self, obj):
        friend_request_id = self.context.get('friend_requests', {})
        return friend_request_id.get(obj.user_id, None)

    def get_online(self, obj):
        online_status = self.context.get('online_status', {})
        return online_status.get(obj.user_id, None)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # if representation.get('relationship') is None: SHOULD NEVER HAPPEN
        #     representation.pop('relationship')
        if representation.get('online') is None:
            representation.pop('online')
        return representation
    
class CustomUserEditSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(validators=[profile_image_validator])

    class Meta:
        model = CustomUser
        fields = ["displayname", "image"]




