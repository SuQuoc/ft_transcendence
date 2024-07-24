import json
import uuid

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import generics
from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CustomUser
from .models import FriendRequest
from .serializers import CustomUserCreateSerializer
from .serializers import CustomUserDetailSerializer

# Create your views here.


def profile(request):
    return HttpResponse("This is the profile page")


# generics.ListCreateAPIView # to view all users
class CustomUserCreate(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserCreateSerializer

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


class CustomUserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserDetailSerializer


def getJsonKey(request, key):
    """
    Returns the corresponding python object from the request body with the given json key.
    """
    try:
        data = json.loads(request.body)
        value = data.get(key)
        if not value:
            return None, JsonResponse({"error": f"'{key}' not provided"}, status=400)
        return value, None
    except json.JSONDecodeError:
        return None, JsonResponse({"error": "Invalid JSON"}, status=400)


# @authentication_classes([TokenAuthentication]) # for auth a user with a token from regis service
# @permission_classes([IsAuthenticated])
def sendFriendRequest(request):
    if request.method == 'POST':
        # return JsonResponse({"message": "JUST A TEST"}, status=201)
        from_user = request.user
        user_id, error = getJsonKey(request, "userId")
        if error:
            return error
        try:
            to_user = CustomUser.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        if from_user == to_user:
            return JsonResponse({"error": "You can't send a friend request to yourself"}, status=400)
            # return HttpResponse("You can't send a friend request to yourself")

        friend_request, created = FriendRequest.objects.get_or_create(from_user=from_user, to_user=to_user, status=0)
        if created:
            return JsonResponse({"message": "friend request sent"}, status=201)
            # return HttpResponse("friend request sent")
        else:
            return JsonResponse({"message": "friend request sent"}, status=201)
            # return HttpResponse("friend request already sent, be patient")
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


def acceptFriendRequest(request):
    if request.method == 'POST':
        friend_request_id, error = getJsonKey(request, "friendRequestId")
        if error:
            return error
        try:
            friend_request = FriendRequest.objects.get(id=friend_request_id)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "Friend request not found"}, status=404)
            # return HttpResponse("Friend request not found")

        if friend_request.to_user == request.user:
            friend_request.to_user.friends.add(friend_request.from_user)
            friend_request.from_user.friends.add(friend_request.to_user)
            friend_request.status = 1  # accepted see FriendRequest model
            friend_request.save()  # storing changes, so only status
            # friend_request.delete() # i read that its better store all friend requests
        else:
            return JsonResponse({"error": "Friend request not for u (should never happen)"}, status=404)
            # return HttpResponse("Friend request not for you")
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


def declineFriendRequest(request):
    if request.method == 'POST':
        friend_request_id, error = getJsonKey(request, "friendRequestId")
        if error:
            return error
        try:
            friend_request = FriendRequest.objects.get(id=friend_request_id)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "Friend request not found"}, status=404)
            # return HttpResponse("Friend request not found")

        if friend_request.to_user == request.user:
            friend_request.status = 2  # declined, see FriendRequest model
            friend_request.save()  # storing changes, so only status
        else:
            return JsonResponse({"error": "Friend request not for u (should never happen)"}, status=404)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)
