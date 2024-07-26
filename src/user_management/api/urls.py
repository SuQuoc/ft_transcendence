from django.urls import path

from . import views

urlpatterns = [
    path("user-creation/", views.CustomUserCreate.as_view(), name="user-creation"),  # discard when frontend is ready
    path("profile/<str:displayname>/", views.CustomUserProfile.as_view()),  # discard when frontend is ready
]
