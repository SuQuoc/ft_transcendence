from django.urls import path

from . import views

urlpatterns = [
    path("send/", views.SendFriendRequestView.as_view(), name="send-friend-request"),
    path("answer/", views.AnswerFriendRequestView.as_view(), name="answer-friend-request"),
    path("friends", views.ListFriendRelationsView.as_view(), name="friends"),
]
