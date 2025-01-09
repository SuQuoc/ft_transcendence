
from django.urls import re_path, path

from .online_status_consumer import OnlineStatusConsumer

websocket_urlpatterns = [
    # re_path(r"daphne/pong/(?P<room_name>\w+)/$", ChatConsumer.as_asgi()),
    re_path(r'um/online_status/?$', OnlineStatusConsumer.as_asgi()),
]

