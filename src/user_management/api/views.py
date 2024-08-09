from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from friends.models import FriendList
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,  # register service
)
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import CustomUser
from .serializers import CustomUserCreateSerializer
from .serializers import CustomUserEditSerializer
from .serializers import CustomUserProfileSerializer
from rest_framework.parsers import MultiPartParser, FormParser


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


class CustomUserCreate(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserCreateSerializer

    # since already in settings not needed here
    # authentication_classes = [JWTTokenUserAuthentication]
    # permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.validated_data['user_id'] = self.request.user.user_id

        with transaction.atomic():
            new_user = serializer.save()
            # Create a FriendList instance for the new custom user
            FriendList.objects.create(user=new_user)


# only used when editing own profile, viewing own profile is separate
class CustomUserEdit(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserEditSerializer


# is_self, friend, stranger logic potentially ONLY for the SEARCH ENDPOINT
# because u may ONLY be able to view OWN PROFILE
class CustomUserProfile(generics.GenericAPIView):
    parser_classes = [MultiPartParser, FormParser]
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserProfileSerializer

    def get(self, request, displayname):
        context = {'is_self': False, 'is_friend': False, 'is_stranger': False}

        stalked_user = get_object_or_404(CustomUser, displayname=displayname)

        # print(f"TOKEN STUFF {token_user.user_id}")
        user = get_object_or_404(CustomUser, user_id=request.user.user_id)
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

    #@parser_classes([MultiPartParser, FormParser])
    def patch(self, request, displayname):
        user_to_update = get_object_or_404(CustomUser, displayname=displayname)

        user = get_object_or_404(CustomUser, user_id=request.user.user_id)
        if user != user_to_update:
            raise PermissionDenied("You do not have permission to edit this user's profile.")

        serializer = CustomUserEditSerializer(user_to_update, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, displayname):
        user_to_delete = get_object_or_404(CustomUser, displayname=displayname)

        user = get_object_or_404(CustomUser, user_id=request.user.user_id)
        if user != user_to_delete:
            raise PermissionDenied("You do not have permission to edit this user's profile.")
        user_to_delete.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
