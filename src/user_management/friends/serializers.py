from rest_framework import serializers

from .models import FriendRequest


class FriendRequestSendSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ["receiver_name"]


class FriendRequestAnswerSerializer(serializers.ModelSerializer):
    friend_request_id = serializers.CharField(source='id')

    class Meta:
        model = FriendRequest
        fields = ["friend_request_id"]
