import uuid

from django.http import HttpResponse
from django.shortcuts import render
from friends.models import FriendList
from friends.models import FriendRequest
from friends.views import getJsonKey
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,  # register service
)
from rest_framework_simplejwt.views import TokenObtainPairView
from utils import getUser
from .models import CustomUser
from .serializers import CustomUserCreateSerializer
from .serializers import CustomUserEditSerializer
from .serializers import CustomUserProfileSerializer
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication

# JWT
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):  # register service
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['learning jwt'] = user.email
        # token['user_id'] = user.user_id
        # token['displayname'] = user.displayname

        return token


class MyTokenObtainPairView(TokenObtainPairView):  # register service
    serializer_class = MyTokenObtainPairSerializer


def profile(request):
    return HttpResponse("This is the profile page")


# generics.ListCreateAPIView # to view all users
class CustomUserCreate(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserCreateSerializer

    # since already in settings not needed here
    # authentication_classes = [JWTTokenUserAuthentication]
    # permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        custom_user = serializer.save()
        # Create a FriendList instance for the new custom user
        FriendList.objects.create(user=custom_user)


# only used when editing own profile, viewing own profile is separate
class CustomUserEdit(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserEditSerializer


# is_self, friend, stranger logic potentially ONLY for the SEARCH ENDPOINT
# because u may ONLY be able to view OWN PROFILE
class CustomUserProfile(generics.GenericAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserProfileSerializer

    def get(self, request, displayname):
        # print(f"Request received for displayname: {displayname}")

        context = {'is_self': False, 'is_friend': False, 'is_stranger': False}

        stalked_user = getUser("displayname", displayname)
        token_user = request.user
        # print(f"TOKEN STUFF {token_user.user_id}")
        user = getUser("user_id", token_user.user_id)
        if user == stalked_user:
            # Watching my own profile - Frontend: i see personal info, like my friend-list?
            context["is_self"] = True
        elif stalked_user in user.friend_list.friends.all():
            # Watching a friends profile - Frontend: U guys are friends indicator
            context["is_friend"] = True
        else:
            # Watching random persons profile - Frontend: Friend request button
            context["is_stranger"] = True

        serializer = self.serializer_class(stalked_user, context=context)
        return Response(serializer.data)

    def patch(self, request, displayname):
        user_to_update = getUser("displayname", displayname)

        user = getUser("user_id", request.user.user_id)
        if user != user_to_update:
            raise PermissionDenied("You do not have permission to edit this user's profile.")

        serializer = CustomUserProfileSerializer(user_to_update, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
