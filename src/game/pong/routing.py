# chat/routing.py
from django.urls import re_path, path

from . import consumers

websocket_urlpatterns = [
    re_path(r"daphne/pong/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
]

""" websocket_urlpatterns = [
    path("ws/chat/<int:room_id>/", consumers.ChatConsumer.as_asgi()),
] """