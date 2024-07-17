from django.urls import path

from . import views

urlpatterns = [
    path("", views.CustomUserList.as_view()),  # discard when frontend is ready
    path("<int:pk>/", views.CustomUserDetail.as_view()),  # discard when frontend is ready
    path("send-friend-request/", views.sendFriendRequest),
    path("acc-friend-request/", views.acceptFriendRequest),
    path("dec-friend-request/", views.declineFriendRequest),
]
