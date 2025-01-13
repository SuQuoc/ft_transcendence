
from django.urls import re_path, path

from .online_status_consumer import OnlineStatusConsumer

websocket_urlpatterns = [
    re_path(r'um/online_status/?$', OnlineStatusConsumer.as_asgi()),
]

