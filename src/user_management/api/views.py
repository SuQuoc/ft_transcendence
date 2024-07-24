import uuid

from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import generics
from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CustomUser
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
