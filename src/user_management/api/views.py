from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from friends.models import FriendList, FriendRequest
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,  # register service
)
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import CustomUser
from .serializers import CustomUserCreateSerializer
from .serializers import CustomUserEditSerializer
from .serializers import CustomUserProfileSerializer


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

def get_user_from_jwt(request):
    try:
        user = CustomUser.objects.get(user_id=request.user.user_id)
    except CustomUser.DoesNotExist:
        raise PermissionDenied("Invalid user ID in JWT (either our mistake or u sus)")


class CustomUserCreate(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserCreateSerializer

    # since already in settings not needed here
    # authentication_classes = [JWTTokenUserAuthentication]
    # permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.validated_data['user_id'] = self.request.user.user_id
        serializer.save()


# is_self, friend, stranger logic potentially ONLY for the SEARCH ENDPOINT
# because u may ONLY be able to view OWN PROFILE
class CustomUserProfile(generics.GenericAPIView):
    parser_classes = [MultiPartParser, FormParser]
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserProfileSerializer

    def get(self, request, displayname):

        stalked_user = get_object_or_404(CustomUser, displayname=displayname)

        # print(f"TOKEN STUFF {token_user.user_id}")
        user = get_object_or_404(CustomUser, user_id=request.user.user_id)
        context = {}
        if user == stalked_user:
            # Watching my own profile - Frontend: i see personal info, like my friend-list?
            context["relationship"] = "self"
            context["is_self"] = True
        elif stalked_user in user.friend_list.friends.all():
            # Watching a friends profile - Frontend: U guys are friends indicator
            context["relationship"] = "friend"
            context["is_friend"] = True
        else:
            # Watching random persons profile - Frontend: Friend request button
            context["relationship"] = "stranger"
            context["is_stranger"] = True

        serializer = self.serializer_class(stalked_user, context=context)
        return Response(serializer.data)

    # @parser_classes([MultiPartParser, FormParser])
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


class SearchUserView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserProfileSerializer

    def get(self, request):
        user = get_user_from_jwt(request)
        search_term = request.query_params.get("displayname", "")

        results = CustomUser.objects.filter(displayname__icontains=search_term)[:5]
        if not results:
            return Response({"detail": "No users found."}, status=status.HTTP_404_NOT_FOUND)
        
        relationships = {}
        friend_requests = {}
        online_status = {}
        for found_u in results:
            if found_u in user.friend_list.friends.all():
                relationships[found_u.user_id] = "friend"
                online_status[found_u.user_id] = {
                    'status': "online" if found_u.online else "offline",
                }
            else:
                fr_sent = FriendRequest.objects.filter(status=FriendRequest.PENDING, sender=user, receiver=found_u).first() # using first to get the obj not a queryset, allthough there can only be one
                fr_received = FriendRequest.objects.filter(status=FriendRequest.PENDING, sender=found_u, receiver=user).first()
                if fr_sent:
                    relationships[found_u.user_id] = "hePendsMe"
                    friend_requests[found_u.user_id] = fr_sent.id
                elif fr_received: 
                    relationships[found_u.user_id] = "iHaveOpenRequest"
                    friend_requests[found_u.user_id] = fr_received.id
                else:
                    relationships[found_u.user_id] = "stranger"
        
        context = {"relationships": relationships, 
                   "friend_requests": friend_requests,
                   "online_status": online_status,
        }
        serializer = self.serializer_class(results, many=True, context=context)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ListFriendRelationsView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserProfileSerializer

    def get(self, request, displayname):

        # user = get_object_or_404(CustomUser, displayname=displayname)

        user = get_object_or_404(CustomUser, user_id=request.user.user_id)
        if user.displayname != displayname:
            raise PermissionDenied("My friendlist is private, keep your nose out")
