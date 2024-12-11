from django.http import HttpResponse
from typing import Optional
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
from .serializers import ImageTooLargeError
from rest_framework.decorators import api_view
from rest_framework.views import APIView
import logging


@api_view(['POST'])
def get_displaynames(request):
    try:
        user_ids = request.data.get("user_ids")
        if not user_ids:
            return Response({'error': 'No user_ids provided'}, status=status.HTTP_400_BAD_REQUEST)
        users = CustomUser.objects.filter(user_id__in=user_ids)
        displaynames = {
            str(user.user_id): user.displayname for user in users
        }
        #logging.warning("displaynames: " + str(displaynames))
        return Response(displaynames, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'get_displaynames': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CustomUserCreate(generics.GenericAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserCreateSerializer

    def post(self, request):
        data = request.data
        data['user_id'] = request.user.user_id
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True) # will call the validate method in the serializer IF DEFINED
        except Exception as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)        


class CustomUserProfile(generics.GenericAPIView):
    parser_classes = [MultiPartParser, FormParser] # only used for patch, since GET and DELETE typically dont have a body
    queryset = CustomUser.objects.all()

    def get(self, request):
        user = get_user_from_jwt(request)
        other_id = request.query_params.get("profile_id", None)
        if other_id:
            other = get_object_or_404(CustomUser, user_id=other_id)
            serializer = CustomUserProfileSerializer(other)
        else:
            serializer = CustomUserProfileSerializer(user)

        return Response(serializer.data)


    def patch(self, request):
        user = get_user_from_jwt(request)
        serializer = CustomUserEditSerializer(user, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True) # will call the validate method in the serializer IF DEFINED
        except ImageTooLargeError as e:
            return Response({'error': str(e)}, status=e.status_code)
        except Exception as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        
        delete_claim  = request.auth.get('delete')
        if not delete_claim or delete_claim != True:
            return Response({'error': 'No delete parameter'}, status=status.HTTP_403_FORBIDDEN)
        user = get_user_from_jwt(request)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SearchUserView(generics.ListAPIView):
    queryset = CustomUser.objects.all()

    def get(self, request):
        user = get_user_from_jwt(request)

        searchterm = request.query_params.get("term", None)
        if searchterm is None:
            return Response({"error": "Please provide valid query key"}, status=status.HTTP_400_BAD_REQUEST)
        if searchterm == "":
            return Response({"error": "Search term is required."}, status=status.HTTP_400_BAD_REQUEST)

        results = CustomUser.objects.filter(displayname__icontains=searchterm)[:5]
        if not results:
            return Response({}, status=status.HTTP_200_OK)

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
                else:
                   relationships[found_u.user_id] = "stranger"

        context = {
            "relationships": relationships,
            "online_status": online_status,
            "friend_requests": friend_requests,
        }
        # print(friend_requests)
        serializer = UserRelationSerializer(results, many=True, context=context)
        return Response(serializer.data, status=status.HTTP_200_OK)

# HELPER functions
def get_pending_friend_request(*, me: CustomUser, other: CustomUser) -> tuple[str, Optional[int]]:
    fr_sent = FriendRequest.objects.filter(status=FriendRequest.PENDING, sender=me, receiver=other).first()  # using first to get the obj not a queryset, allthough there can only be one
    fr_received = FriendRequest.objects.filter(status=FriendRequest.PENDING, sender=other, receiver=me).first()
    if fr_sent:
        return "requested", fr_sent.id
    elif fr_received:
        return "received", fr_received.id
    else:
        return "", None


# OLD BACKUP
""" class CustomUserProfile(generics.GenericAPIView):
    parser_classes = [MultiPartParser, FormParser] # only used for patch, since GET and DELETE typically dont have a body
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserProfileSerializer

    def get(self, request, user_id):
        stalked_user = get_object_or_404(CustomUser, user_id=user_id)

        # print(f"TOKEN STUFF {token_user.user_id}")
        user = get_user_from_jwt(request)
        context = {}
        if user == stalked_user:
            context["relationship"] = "self"
            context["self"] = True
        elif stalked_user in user.friend_list.friends.all():
            context["relationship"] = "friend"
            context["friend"] = True
        else:
            context["relationship"] = "stranger"
            context["stranger"] = True

        serializer = self.serializer_class(stalked_user, context=context)
        return Response(serializer.data)

    # @parser_classes([MultiPartParser, FormParser])
    def patch(self, request, user_id):
        user_to_update = get_object_or_404(CustomUser, user_id=user_id)

        user = get_user_from_jwt(request)
        if user != user_to_update:
            raise PermissionDenied("You do not have permission to edit this user's profile. U sus")

        serializer = CustomUserEditSerializer(user_to_update, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, user_id):
        user_to_delete = get_object_or_404(CustomUser, user_id=user_id)

        user = get_user_from_jwt(request)
        if user != user_to_delete:
            raise PermissionDenied("You do not have permission to delete this user's profile. U sus")
        user_to_delete.delete()
        return Response(status=status.HTTP_204_NO_CONTENT) """