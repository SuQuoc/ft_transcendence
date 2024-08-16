from rest_framework import serializers

from .models import CustomUser
from .models import FriendRequest


class FriendRequestSendSerializer(serializers.ModelSerializer):
    receiver = serializers.CharField(
        max_length=CustomUser._meta.get_field('displayname').max_length,  # to use the constraints of the CustomUser model, test pending
    )

    class Meta:
        model = FriendRequest
        fields = ["receiver"]


class FriendRequestAnswerSerializer(serializers.ModelSerializer):
    friend_request_id = serializers.IntegerField(source='id') # renaming id to friend_request_id

    class Meta:
        model = FriendRequest
        fields = ["friend_request_id"]
