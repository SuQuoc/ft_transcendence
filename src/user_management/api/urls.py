from django.urls import path

from . import views

urlpatterns = [
    path("", views.profile),  # discard when frontend is ready
    path(
        "<int:pk>/", views.ProfileDetailApiView.as_view()
    ),  # discard when frontend is ready
]
