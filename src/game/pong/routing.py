# chat/routing.py
from django.urls import re_path, path

from .consumers.lobbies import LobbiesConsumer
from .consumers.game_test import GameConsumer
from .consumers.pong_game_consumer import PongGameConsumer


websocket_urlpatterns = [
    # re_path(r"daphne/pong/(?P<room_name>\w+)/$", ChatConsumer.as_asgi()),
    path('daphne/lobbies', LobbiesConsumer.as_asgi(), name='UNUSED-lobbies-page'), # TODO change name from lobbies to tournaments, also "daphne" to game or smth else
    re_path(r'daphne/lobbies/(?P<room_name>\w+)/(?P<game_id>\d+)$', GameConsumer.as_asgi(), name='UNUSED-game-page'),
    re_path(r'daphne/lobbies/(?P<room_name>\w+)$', PongGameConsumer.as_asgi(), name='UNUSED-pong-page'),
    
    # re_path for matchmaking
    # re_path for matchmaking-game
]

""" websocket_urlpatterns = [
    path("ws/chat/<int:room_id>/", consumers.ChatConsumer.as_asgi()),
] """
