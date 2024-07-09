from rest_framework import serializers

from .models import CustomUser
from .models import MatchRecord


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "online", "friends"]
