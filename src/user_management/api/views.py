import uuid

from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render
from friends.models import FriendList
from friends.models import FriendRequest
from friends.views import getJsonKey
from rest_framework import generics
from rest_framework import mixins
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from utils import getUserByDisplayname

from .models import CustomUser
from .serializers import CustomUserCreateSerializer
from .serializers import CustomUserEditSerializer
from .serializers import CustomUserProfileSerializer

# Create your views here.


def profile(request):
    return HttpResponse("This is the profile page")


# generics.ListCreateAPIView # to view all users
class CustomUserCreate(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserCreateSerializer

    def perform_create(self, serializer):
        custom_user = serializer.save()
        # Create a FriendList instance for the new custom user
        FriendList.objects.create(user=custom_user)

    # django serializer already does the unique validation for me
    # def create(self, request, *args, **kwargs):
    #    displayname = request.data.get('displayname')
    #    user_id = request.data.get('user_id')
    #    # if not displayname or not user_id:
    #    #     return Response({"error": "Both displayname and id must be provided"}, status=status.HTTP_400_BAD_REQUEST)
    #    # if CustomUser.objects.filter(displayname=displayname).exists():
    #    #     return Response({"error": "User with this displayname already exists"}, status=status.HTTP_400_BAD_REQUEST)
    #    # if CustomUser.objects.filter(user_id=user_id).exists():
    #    #     return Response({"error": "User with this id already exists"}, status=status.HTTP_400_BAD_REQUEST)
    #    return super().create(request, *args, **kwargs)


# only used when editing own profile, viewing own profile is separate
class CustomUserEdit(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserEditSerializer


# is_self, friend, stranger logic potentially ONLY for the SEARCH ENDPOINT
# because u may ONLY be able to view OWN PROFILE
class CustomUserProfile(APIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserProfileSerializer

    def get(self, request, displayname):
        stalked_user = getUserByDisplayname(displayname)
        context = {'is_self': False, 'is_friend': False, 'is_stranger': False}

        user = request.user
        if user == stalked_user:
            # Watching my own profile
            # Frontend: i see sensitive info, like my friend-list?
            context["is_self"] = True
        elif stalked_user in user.friend_list.friends.all():
            # Watching a friends profile
            # Frontend: U guys are friends indicator
            context["is_friend"] = True
        else:
            # Watching random persons profile
            # Frontend: Friend request button
            context["is_stranger"] = True

        serializer = self.serializer_class(stalked_user, context=context)
        return Response(serializer.data)

    def patch(self, request, displayname):
        user_to_update = getUserByDisplayname(displayname)

        if request.user != user_to_update:
            raise PermissionDenied("You do not have permission to edit this user's profile.")

        serializer = CustomUserProfileSerializer(user_to_update, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
