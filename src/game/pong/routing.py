from django.urls import re_path, path

from .consumers.lobbies import LobbiesConsumer
from .consumers.pong_game_consumer import PongGameConsumer
from .consumers.matchmaking_consumer import MatchmakingConsumer

websocket_urlpatterns = [
    re_path(r'game/tournament/?$', LobbiesConsumer.as_asgi()),
    re_path(r'game/matchmaking/?$', MatchmakingConsumer.as_asgi()),
    re_path(r'game/match/?$', PongGameConsumer.as_asgi()),
]
