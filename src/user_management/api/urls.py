from django.urls import path

from . import views

urlpatterns = [
    path("user-creation/", views.CustomUserCreate.as_view(), name="user-creation"),
    path("profile/<str:displayname>/", views.CustomUserProfile.as_view(), name="profile"),
]
