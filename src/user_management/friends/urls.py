from django.urls import path

from . import views

urlpatterns = [
    path("send/", views.SendFriendRequestView.as_view(), name="send-friend-request"),
    path("acc/", views.AcceptFriendRequestView.as_view(), name="acc-friend-request"),
    path("dec/", views.DeclineFriendRequestView.as_view(), name="dec-friend-request"),
]
