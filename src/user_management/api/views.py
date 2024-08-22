from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from friends.models import FriendList
from friends.models import FriendRequest
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from utils_jwt import get_user_from_jwt

from .models import CustomUser
from .serializers import CustomUserCreateSerializer
from .serializers import CustomUserEditSerializer
from .serializers import CustomUserProfileSerializer
from .serializers import UserRelationSerializer


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
            context["self"] = True
        elif stalked_user in user.friend_list.friends.all():
            # Watching a friends profile - Frontend: U guys are friends indicator
            context["relationship"] = "friend"
            context["friend"] = True
        else:
            # Watching random persons profile - Frontend: Friend request button
            context["relationship"] = "stranger"
            context["stranger"] = True

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

    def get(self, request):
        user = get_user_from_jwt(request)

        searchterm = request.query_params.get("term", "")

        results = CustomUser.objects.filter(displayname__icontains=searchterm)[:5]
        if not results:
            return Response({"detail": "No users found."}, status=status.HTTP_404_NOT_FOUND)

        relationships = {}
        online_status = {}
        friend_requests = {}
        for found_u in results:
            if user.friend_list.contains(found_u):
                relationships[found_u.user_id] = "friend"
                online_status[found_u.user_id] = found_u.get_online_status()
                friend_requests[found_u.user_id] = user.friend_list.get_friends_request_id(found_u)
            else:
                friend_request_relation, friend_request_id = get_pending_friend_request(me=user, other=found_u)
                if friend_request_relation:
                    relationships[found_u.user_id] = friend_request_relation
                    friend_requests[found_u.user_id] = friend_request_id
                # else:
                #    relationships[found_u.user_id] = "stranger"

        context = {
            "relationships": relationships,
            "online_status": online_status,
            "friend_requests": friend_requests,
        }
        # print(friend_requests)
        serializer = UserRelationSerializer(results, many=True, context=context)
        return Response(serializer.data, status=status.HTTP_200_OK)


def get_pending_friend_request(*, me, other):
    fr_sent = FriendRequest.objects.filter(status=FriendRequest.PENDING, sender=me, receiver=other).first()  # using first to get the obj not a queryset, allthough there can only be one
    fr_received = FriendRequest.objects.filter(status=FriendRequest.PENDING, sender=other, receiver=me).first()
    if fr_sent:
        return "requested", fr_sent.id
    elif fr_received:
        return "received", fr_received.id
    else:
        return None, None
