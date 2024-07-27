import json

from api.models import CustomUser
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view

from .models import FriendRequest

# Create your views here.


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
@api_view(['POST'])
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
            # return HttpResponse("Friend request not found")

        if friend_request.to_user == request.user:
            friend_request.status = 2  # declined, see FriendRequest model
            friend_request.save()  # storing changes, so only status
        else:
            return JsonResponse({"error": "Friend request not for u (should never happen)"}, status=404)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)
