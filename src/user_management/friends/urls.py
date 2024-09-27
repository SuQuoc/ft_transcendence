from django.urls import path
from django.urls import re_path

from . import views

urlpatterns = [
    re_path("send$|send/", views.SendFriendRequestView.as_view(), name="send-friend-request"),
    re_path("answer$|answer/", views.AnswerFriendRequestView.as_view(), name="answer-friend-request"),
    path("", views.ListFriendRelationsView.as_view(), name="friends"),
]
