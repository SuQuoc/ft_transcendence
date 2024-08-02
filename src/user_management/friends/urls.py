from django.urls import path

from . import views

urlpatterns = [
    path("send/", views.sendFriendRequest, name="send-friend-request"),
    path("acc/", views.acceptFriendRequest, name="acc-friend-request"),
    path("dec/", views.declineFriendRequest, name="dec-friend-request"),
]
