from rest_framework import serializers

from api.models import CustomUser
from friends.models import FriendRequest


class FriendRequestSendSerializer(serializers.ModelSerializer):
    receiver = serializers.CharField(
        max_length=CustomUser._meta.get_field('displayname').max_length,  # to use the constraints of the CustomUser model, test pending
    )

    class Meta:
        model = FriendRequest
        fields = ["receiver"]


class FriendRequestAnswerSerializer(serializers.ModelSerializer):
    ACCEPT = "accept"
    DECLINE = "decline"
    UNFRIEND = "unfriend"

    friend_request_id = serializers.IntegerField(source='id')
    action = serializers.CharField(write_only=True)
    class Meta:
        model = FriendRequest
        fields = ["friend_request_id", "action"]

    def validate_action(self, value):
        if value not in [self.ACCEPT, self.DECLINE, self.UNFRIEND]:
            raise serializers.ValidationError("Invalid action. Must be 'accept' or 'decline'.") # results in HTTP_400
        return value