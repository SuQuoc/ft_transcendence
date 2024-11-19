# chat/routing.py
from django.urls import re_path, path

from .consumers.lobbies import LobbiesConsumer
from .consumers.pong_game_consumer import PongGameConsumer
from .consumers.matchmaking_consumer import MatchmakingConsumer

websocket_urlpatterns = [
    # re_path(r"game/pong/(?P<room_name>\w+)/$", ChatConsumer.as_asgi()),
    # re_path(r'game/lobbies/(?P<room_name>\w+)/(?P<game_id>\d+)$', GameConsumer.as_asgi(), name='UNUSED-game-page'),
    re_path(r'game/tournament/?$', LobbiesConsumer.as_asgi()), # TODO: order of paths are important, maybe check in re_path if match id is in uuid format
    re_path(r'game/matchmaking/?$', MatchmakingConsumer.as_asgi()),
    re_path(r'game/match/?$', PongGameConsumer.as_asgi()),
]

""" websocket_urlpatterns = [
    path("ws/chat/<int:room_id>/", consumers.ChatConsumer.as_asgi()),
] """
