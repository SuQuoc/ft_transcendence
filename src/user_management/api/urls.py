from django.urls import path, re_path

from . import views

urlpatterns = [
    re_path(r"user-creation/?$", views.CustomUserCreate.as_view(), name="user-creation"),
    path("profile", views.CustomUserProfile.as_view(), name="profile"),
    path("search", views.SearchUserView.as_view(), name="search"),
]
