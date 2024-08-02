import json

from api.models import CustomUser
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from utils import getUser

from .models import FriendRequest
from .serializers import FriendRequestAnswerSerializer
from .serializers import FriendRequestSendSerializer

# Create your views here.


def get_json_key(request, key):
    """
    Returns the corresponding python object from the request body with the given json key.
    Main goal:
    - not hardcoding error based on key name
    - not checking manually if key was missing
    """
    value = request.data.get(key)
    if value is None:
        raise ParseError(detail=f"'{key}' not provided")
    return value


def getJsonKey(request, key):
    """
    Returns the corresponding python object from the request body with the given json key.
    """
    try:
        request_body = request.body
        # print(f"Request Body: {request_body}")  # Debugging: Print request body
        data = json.loads(request.body)
        value = data.get(key)
        if not value:
            return None, JsonResponse({"error": f"'{key}' not provided"}, status=400)
        return value, None
    except json.JSONDecodeError:
        return None, JsonResponse({"error": "Invalid JSON"}, status=400)


class SendFriendRequestView(generics.GenericAPIView):
    def post(self, request):
        sender = getUser("user_id", request.user.user_id)
        rec_name = request.data.get('receiver')
        receiver = get_object_or_404(CustomUser, displayname=rec_name)

        # is_self
        if sender == receiver:
            return JsonResponse({"error": "You can't send a friend request to yourself"}, status=400)

        friend_request, created = FriendRequest.objects.get_or_create(sender=sender, receiver=receiver)

        # is_stranger
        if created:
            # serializer = FriendRequestSendSerializer(friend_request)
            # return Response(serializer.data, status=status.HTTP_201_CREATED)
            return JsonResponse({"message": "friend request sent"}, status=201)

        elif friend_request.status == FriendRequest.PENDING:
            return JsonResponse({"message": "friend request already sent, be patient"}, status=200)  # maybe 409 Conflict more fitting ??

        elif friend_request.status == FriendRequest.DECLINED:
            friend_request.status = FriendRequest.PENDING
            friend_request.save()
            return JsonResponse({"message": "friend request sent"}, status=200)

        # is_friend
        elif friend_request.status == FriendRequest.ACCEPTED:
            return JsonResponse({"error": "You are best buds"}, status=400)


# @authentication_classes([TokenAuthentication]) # for auth a user with a token from regis service
# @permission_classes([IsAuthenticated])
@api_view(['POST'])
def sendFriendRequest(request):
    if request.method == 'POST':
        sender = getUser("user_id", request.user.user_id)
        rec_displayname, error = getJsonKey(request, "receiver")
        if error:
            return error
        receiver = getUser("displayname", rec_displayname)

        # is_self
        if sender == receiver:
            return JsonResponse({"error": "You can't send a friend request to yourself"}, status=400)

        # is_friend
        if receiver in sender.friend_list.friends.all():
            return JsonResponse({"error": "You are best buds"}, status=400)

        # is_stranger
        friend_request, created = FriendRequest.objects.get_or_create(sender=sender, receiver=receiver, status=FriendRequest.PENDING)
        if created:
            return JsonResponse({"message": "friend request sent"}, status=201)
        else:
            return JsonResponse({"message": "friend request already sent, be patient"}, status=200)  # maybe 409 Conflict more fitting ??
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


@api_view(['POST'])
def acceptFriendRequest(request):
    if request.method == 'POST':
        friend_request_id, error = getJsonKey(request, "friendRequestId")
        if error:
            return error
        try:
            friend_request = FriendRequest.objects.get(id=friend_request_id)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "Friend request not found"}, status=404)

        user = getUser("user_id", request.user.user_id)
        if friend_request.receiver == user:
            if friend_request.status == FriendRequest.PENDING:
                user.friend_list.addFriend(friend_request.sender)
                friend_request.sender.friend_list.addFriend(user)
                friend_request.status = FriendRequest.ACCEPTED
                friend_request.save()  # storing changes, so only status
                return JsonResponse({"message": "Friend request accepted"}, status=200)
                # bonus: message the sender
            else:
                return JsonResponse({"error": "No pending friend requests"}, status=404)
        else:
            return JsonResponse({"error": "Friend request not for u (should never happen)"}, status=404)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


def get_all_friend_requests():
    friend_requests = FriendRequest.objects.all()
    friend_request_ids = [fr.id for fr in friend_requests]
    print(friend_request_ids)


@api_view(['POST'])
def declineFriendRequest(request):
    if request.method == 'POST':
        friend_request_id, error = getJsonKey(request, "friendRequestId")
        if error:
            return error
        try:
            friend_request = FriendRequest.objects.get(id=friend_request_id)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "Friend request not found"}, status=404)

        user = getUser("user_id", request.user.user_id)
        if friend_request.receiver == user:
            if friend_request.status == FriendRequest.PENDING:
                friend_request.status = FriendRequest.DECLINED
                friend_request.save()  # storing changes, so only status
                return JsonResponse({"message": "Friend request declined"}, status=200)
            else:
                return JsonResponse({"error": "No pending friend requests"}, status=404)
        else:
            return JsonResponse({"error": "Friend request not for u (should never happen)"}, status=404)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)
