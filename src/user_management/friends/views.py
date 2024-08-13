from api.models import CustomUser
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import FriendRequest
from .serializers import FriendRequestAnswerSerializer
from .serializers import FriendRequestSendSerializer


class SendFriendRequestView(generics.GenericAPIView):
    serializer_class = FriendRequestSendSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            sender = get_object_or_404(CustomUser, user_id=request.user.user_id)

            rec_name = serializer.validated_data.get('receiver')
            receiver = get_object_or_404(CustomUser, displayname=rec_name)

            # is_self
            if sender == receiver:
                return Response({"error": "You can't send a friend request to yourself"}, status=status.HTTP_400_BAD_REQUEST)

            friend_request, created = FriendRequest.objects.get_or_create(sender=sender, receiver=receiver)

            # is_stranger
            if created:
                # serializer = FriendRequestSendSerializer(friend_request)
                return Response({"message": "friend request sent"}, status=status.HTTP_201_CREATED)

            elif friend_request.status == FriendRequest.PENDING:
                return Response({"message": "friend request already sent, be patient"}, status=status.HTTP_200_OK)  # maybe 409 Conflict more fitting ??

            elif friend_request.status == FriendRequest.DECLINED:
                friend_request.status = FriendRequest.PENDING
                friend_request.save()
                return Response({"message": "friend request sent"}, status=status.HTTP_200_OK)

            # is_friend
            elif friend_request.status == FriendRequest.ACCEPTED:
                return Response({"error": "You are best buds"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise ValidationError(serializer.errors)


# might be better as patch method not post
class AcceptFriendRequestView(generics.GenericAPIView):
    serializer_class = FriendRequestAnswerSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            friend_request_id = serializer.validated_data["id"]
            friend_request = get_object_or_404(FriendRequest, id=friend_request_id)

            user = get_object_or_404(CustomUser, user_id=request.user.user_id)

            if friend_request.receiver == user:
                if friend_request.status == FriendRequest.PENDING:
                    user.friend_list.addFriend(friend_request.sender)
                    friend_request.sender.friend_list.addFriend(user)
                    friend_request.status = FriendRequest.ACCEPTED
                    friend_request.save()  # storing changes, so only status
                    return Response({"message": "Friend request accepted"}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "No pending friend requests"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error": "Friend request not for u (should never happen)"}, status=status.HTTP_404_NOT_FOUND)
        else:
            raise ValidationError(serializer.errors)


class DeclineFriendRequestView(generics.GenericAPIView):
    serializer_class = FriendRequestAnswerSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            id = serializer.validated_data.get("id")
            friend_request = get_object_or_404(FriendRequest, id=id)

            user = get_object_or_404(CustomUser, user_id=request.user.user_id)
            if friend_request.receiver == user:
                if friend_request.status == FriendRequest.PENDING:
                    friend_request.status = FriendRequest.DECLINED
                    friend_request.save()  # storing changes, so only status
                    return Response({"message": "Friend request declined"}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "No pending friend requests"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error": "Friend request not for u (should never happen)"}, status=status.HTTP_404_NOT_FOUND)
        else:
            raise ValidationError(serializer.errors)


""" OLD
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
 """
