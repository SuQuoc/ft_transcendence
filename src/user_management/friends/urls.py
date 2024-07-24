from django.urls import path

from . import views

urlpatterns = [
    path("send/", views.sendFriendRequest),
    path("acc/", views.acceptFriendRequest),
    path("dec/", views.declineFriendRequest),
]
