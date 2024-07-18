from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import generics
from rest_framework import mixins
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import json
from django.http import JsonResponse


from .models import CustomUser
from .models import FriendRequest
from .serializers import CustomUserSerializer

# Create your views here.


def profile(request):
    return HttpResponse("This is the profile page")


class CustomUserList(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class CustomUserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


def getJsonKey(request, key):
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
        return JsonResponse({"message": "JUST A TEST HEHEHE"}, status=201)
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
            return HttpResponse("You can't send a friend request to yourself")

        friend_request, created = FriendRequest.objects.get_or_create(from_user=from_user, to_user=to_user, status=0)
        if created:
            return JsonResponse({"message": "friend request sent"}, status=201)
            return HttpResponse("friend request sent")
        else:
            return JsonResponse({"message": "friend request sent"}, status=201)
            return HttpResponse("friend request already sent, be patient")
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
            return HttpResponse("Friend request not found")

        if friend_request.to_user == request.user:
            friend_request.to_user.friends.add(friend_request.from_user)
            friend_request.from_user.friends.add(friend_request.to_user)
            friend_request.status = 1  # accepted see FriendRequest model
            friend_request.save()  # storing changes, so only status
            # friend_request.delete() # i read that its better store all friend requests
        else:
            return JsonResponse({"error": "Friend request not for u (should never happen)"}, status=404)
            return HttpResponse("Friend request not for you")
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
            return HttpResponse("Friend request not found")

        if friend_request.to_user == request.user:
            friend_request.status = 2  # declined, see FriendRequest model
            friend_request.save()  # storing changes, so only status
        else:
            return JsonResponse({"error": "Friend request not for u (should never happen)"}, status=404)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


# OLD APIS with mixins just for learning -----------------------
class UserListMixins(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class UserDetailMixins(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


# OLD APIS
class UserListOld(APIView):
    def get(self, request):
        users = CustomUser.objects.all()
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailOLD(APIView):
    """
    Retrieve, update or delete a CustomUser instance.
    ATM everyone can do this i think.
    """

    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = CustomUserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
