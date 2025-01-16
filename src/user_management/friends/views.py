from api.models import CustomUser
from api.serializers import UserRelationSerializer
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from utils_jwt import get_user_from_jwt

from .models import FriendRequest
from .serializers import FriendRequestAnswerSerializer
from .serializers import FriendRequestSendSerializer

from rest_framework.exceptions import AuthenticationFailed
from rest_framework import serializers

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .online_status_consumer import Status, get_online_consumer_group


class SendFriendRequestView(generics.GenericAPIView):
    serializer_class = FriendRequestSendSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            sender = get_user_from_jwt(request)

            rec_name = serializer.validated_data.get('receiver')
            receiver = get_object_or_404(CustomUser, displayname=rec_name)

            if sender == receiver:
                return Response({"error": "You can't send a friend request to yourself"}, status=status.HTTP_400_BAD_REQUEST)

            friend_request = FriendRequest.objects.filter(sender=receiver, receiver=sender).first()
            created = None
            if not friend_request:
                friend_request, created = FriendRequest.objects.get_or_create(sender=sender, receiver=receiver)

            if created:
                return Response({"message": "friend request sent"}, status=status.HTTP_201_CREATED)
            if friend_request.status in (FriendRequest.UNFRIENDED, FriendRequest.DECLINED):
                friend_request.set_sender_and_receiver(sender=sender, receiver=receiver)
                return Response({"message": "friend request sent"}, status=status.HTTP_202_ACCEPTED)
            if friend_request.status == FriendRequest.PENDING:
                if friend_request.sender == sender:
                    return Response({"message": "friend request already sent, be patient"}, status=status.HTTP_202_ACCEPTED)  # maybe 409 Conflict more fitting ??
                else:
                    return Response({"message": "The other person send u a request already, check friend requests"}, status=status.HTTP_202_ACCEPTED)  # maybe 409 Conflict more fitting ??
            elif friend_request.status == FriendRequest.ACCEPTED:
                return Response({"error": "You are best buds"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise ValidationError(serializer.errors)


class AnswerFriendRequestView(generics.GenericAPIView):
    serializer_class = FriendRequestAnswerSerializer

    def post(self, request):
        try:
            self.user = get_user_from_jwt(request)
        
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            friend_request_id = serializer.validated_data.get("id")
            action = serializer.validated_data.get("action")
            
            friend_request = get_object_or_404(FriendRequest, id=friend_request_id)
            if friend_request.receiver != self.user and action != self.serializer_class.UNFRIEND:
                return Response({"error": "Friend request not for u (should never happen)"}, status=status.HTTP_404_NOT_FOUND)
            response = self.act_on_friend_request(friend_request, action)
            return response
        
        except AuthenticationFailed as e:
            return Response({"error": str(e)}, status=e.status_code)
        except serializers.ValidationError as e: 
            return Response({"error": e.detail["action"]}, status=e.status_code) # all validation errors return HTTP_400

    def act_on_friend_request(self, friend_request: FriendRequest, action: str):
        channel_layer = get_channel_layer()

        if friend_request.status == FriendRequest.PENDING:
            if action == self.serializer_class.ACCEPT:
                friend_request.accept()
                self.update_online_status(friend_request.sender.user_id, Status.ONLINE)
                return Response({"message": "Friend request accepted"}, status=status.HTTP_200_OK)
            elif action == self.serializer_class.DECLINE:
                friend_request.decline()
                return Response({"message": "Friend request declined"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "No other action allowed on pending requests"}, status=status.HTTP_400_BAD_REQUEST)

        elif friend_request.status == FriendRequest.ACCEPTED:
            if action == self.serializer_class.UNFRIEND:
                if self.user == friend_request.sender:
                    friend_id = str(friend_request.receiver.user_id)
                else:
                    friend_id = str(friend_request.sender.user_id)
                self.update_online_status(friend_id, Status.OFFLINE)
                friend_request.unfriend()
                return Response({"message": "Unfriended user"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Action not allowed on ACCEPTED friend request"}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"error": "No pending friend requests"}, status=status.HTTP_404_NOT_FOUND)

    def update_online_status(self, friend_id, status: Status):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
                    get_online_consumer_group(self.user.user_id),  
                    {
                        'type': 'send_status_to_single_friend',
                        'friend_id': str(friend_id),
                        'status': status.value
                    }
                )

class ListFriendRelationsView(generics.ListAPIView):
    queryset = CustomUser.objects.all()

    def get(self, request):
        user = get_user_from_jwt(request)

        relationships = {}
        friend_requests = {}

        friends = user.friend_list.friends.all()
        for friend in friends:
            relationships[friend.user_id] = "friend"
            friend_requests[friend.user_id] = user.friend_list.get_friends_request_id(friend)
        all_people = list(friends)

        frs_sent = user.get_pending_requested_friend_requests()
        for friend_request in frs_sent:
            person = friend_request.receiver
            relationships[person.user_id] = "requested"
            friend_requests[person.user_id] = friend_request.id
            all_people.append(person)

        frs_received = user.get_pending_received_friend_requests()
        for friend_request in frs_received:
            person = friend_request.sender
            relationships[person.user_id] = "received"
            friend_requests[person.user_id] = friend_request.id
            all_people.append(person)

        context = {
            "relationships": relationships,
            "friend_requests": friend_requests,
        }
        serializer = UserRelationSerializer(all_people, many=True, context=context)
        return Response(serializer.data, status=status.HTTP_200_OK)
