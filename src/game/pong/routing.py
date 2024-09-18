# chat/routing.py
from django.urls import re_path, path

from .consumers import ChatConsumer, LobbiesConsumer

websocket_urlpatterns = [
    re_path(r"daphne/pong/(?P<room_name>\w+)/$", ChatConsumer.as_asgi()),
    path('lobbies/', LobbiesConsumer.as_asgi(), name='lobbies-page'),
]

""" websocket_urlpatterns = [
    path("ws/chat/<int:room_id>/", consumers.ChatConsumer.as_asgi()),
] """
