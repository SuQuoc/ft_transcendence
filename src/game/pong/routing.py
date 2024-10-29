# chat/routing.py
from django.urls import re_path, path

from .consumers.lobbies import LobbiesConsumer
from .consumers.game_test import GameConsumer
from .consumers.pong_game_consumer import PongGameConsumer


websocket_urlpatterns = [
    # re_path(r"daphne/pong/(?P<room_name>\w+)/$", ChatConsumer.as_asgi()),
    # re_path(r'daphne/lobbies/(?P<room_name>\w+)/(?P<game_id>\d+)$', GameConsumer.as_asgi(), name='UNUSED-game-page'),
    path('daphne/tournament', LobbiesConsumer.as_asgi(), name='UNUSED-lobbies-page'), # TODO: order of paths are important, maybe check in re_path if match id is in uuid format
    re_path(r'daphne/tournament/(?P<match_id>\w+)$', PongGameConsumer.as_asgi(), name='UNUSED-pong-page'), # for tournaments
    re_path(r'daphne/(?P<match_id>\w+)$', PongGameConsumer.as_asgi(), name='UNUSED-pong-page'), # for matchmaking
    
    # re_path for matchmaking
    # re_path for matchmaking-game
]

""" websocket_urlpatterns = [
    path("ws/chat/<int:room_id>/", consumers.ChatConsumer.as_asgi()),
] """
