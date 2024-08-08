# chat/consumers.py
import asyncio
import json
import time
import uuid

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer

from .game_code.ball import GameBall
from .game_code.lobby import Lobby
from .game_code.match import Match
from .game_code.pongPlayer import PongPlayer
from .game_code.storageClasses import SlotXy

# need asgiref
# NEED TO FIX X !!!!!!!!!!!!!!!!!!


class ChatConsumer(AsyncWebsocketConsumer):

    delay = 0.01  # set refresh rate of the game
    MOVE_SPEED = 4
    game_group_name = "game_group"

    # logic is we have a dict saved trow all instances of all socked/client connection
    # create a dict entry for every player
    # players: dict[str, PongPlayer] = {}
    players: dict[str, dict[str, PongPlayer]] = {}

    lobbies: dict[str, Lobby] = {}

    group_current_sizes: dict[str, int] = {}
    group_max_sizes: dict[str, int] = {}
    # PongPlayer should not be "global"
    update_lock = asyncio.Lock()

    map_size = SlotXy(800, 600)

    ball_width = 10
    ball_height = 10

    async def connect(self):

        self.player_id = None
        if len(self.players) > 10000:  # place holder for user logic
            return

        # create a random id
        self.player_id = str(uuid.uuid4())
        # set up rooms
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.group_name = f"chat_{self.room_name}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        # send to client that he has been accepted
        await self.send(text_data=json.dumps({"type": "playerId", "playerId": self.player_id}))
        # now lock and fill the players[id] dict
        await self.create_player_save_in_dict()

    async def create_player_save_in_dict(self):
        self.player = PongPlayer(self.player_id, self.map_size)
        lobby = None
        async with self.update_lock:
            lobby = self.lobbies.get(self.room_name, None)

        if lobby is None:

            # Now using a lobby class in a dict for better control
            self.lobby = Lobby(lobby_name=self.room_name, max_len=2)
            self.lobby.addPlayer(self.player)
            self.lobbies[self.room_name] = self.lobby
            print("Lobby created", self.lobby.lobby_name, self.lobby.len, self.lobby.max_len)
            return

        async with self.update_lock:

            self.lobby.addPlayer(self.player)

            if len(self.group_current_sizes[self.group_name]) >= self.group_max_size:
                print("[WARNING]\nGroup is full")
                # DISCONNECT LOGIC HERE !!! ?????????????????????????????????
                return
            self.group_current_sizes[self.group_name] += 1
            self.players[self.room_name][self.player_id] = self.player
            self.player.x = self.map_size.x - self.player.width

        print("aaaa", self.lobby.len, self.lobby.max_len)

        if self.lobby.len == self.lobby.max_len:
            matches = await self.lobby.startMatch()
            if matches is not None:
                print(matches)
                # start the match
                print("start match")
                # start the game

        # task is like a thread. Sends client a msg to start the game.
        task = asyncio.create_task(self.game_loop())
        if task is None:
            print("[ERROR] Task creation failed")
            return
        async with self.update_lock:
            self.player.task = task
        await self.channel_layer.group_send(
            self.group_name,
            {"type": "start.game", "startGame": True},
        )

    # ASYNC TASK WITH 0.05 S DELAY
    async def game_loop(self):
        async with self.update_lock:
            player_count = len(self.players[self.room_name])
        ball = GameBall(x=(self.map_size.x / 2), y=(self.map_size.y / 2), map_size=self.map_size, width=self.ball_width, height=self.ball_height)
        while player_count > 0:
            ball.hitWall()
            ball.move()
            async with self.update_lock:
                [await self.sendToClient(player, ball) for player in self.players[self.room_name].values()]
            await asyncio.sleep(self.delay)
            async with self.update_lock:
                player_count = len(self.players[self.room_name])

    async def sendToClient(self, player: PongPlayer, ball: GameBall):
        player.move(self.MOVE_SPEED)
        ball.paddlesHit(player)
        # Send to clients in django and then to JS
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",  # Massage type so js knows what he has to do with this strings
                "y": player.y,  # This will tell js where to draw the player
                "x": player.x,
                "playerId": player.id,  # Will tell js if it is the active player
                "ball_x": ball.x,  # This will tell js where to draw the ball
                "ball_y": ball.y,
                "match_points_left": ball.match_points["left"],
                "match_points_right": ball.match_points["right"],
            },
        )

    async def disconnect(self, close_code):

        if self.player_id is None:
            return

        async with self.update_lock:

            if self.player:
                del self.player

            if self.lobbies[self.room_name].players.get(self.player_id, None):
                self.lobbies[self.room_name].removePlayer(self.player_id)

            if self.lobbies.get(self.room_name, None):
                if self.lobbies[self.room_name].len == 0:
                    del self.lobbies[self.room_name]
                    self.lobbies.pop(self.room_name, None)

        print("Lobbies", self.lobbies)

        await self.channel_layer.group_discard(self.game_group_name, self.channel_name)

    # Receive message from WebSocket
    # Receive key up {up=1}
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)

        if text_data_json["type"] == "update":
            player_id = text_data_json["playerId"]
            player = self.players[self.room_name].get(player_id, None)

            if not player:
                return

            async with self.update_lock:
                player.up = text_data_json["up"]
                player.down = text_data_json["down"]

        elif text_data_json["type"] == "roomSize":
            self.group_max_size = int(text_data_json["roomSize"])

            # start here the room ?

            # print(self.room_size)

    # Receive message from room group
    async def chat_message(self, e):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "update",
                    "y": e["y"],
                    "x": e["x"],
                    "playerId": e["playerId"],
                    "ball_x": e["ball_x"],
                    "ball_y": e["ball_y"],
                    "match_points_left": e["match_points_left"],
                    "match_points_right": e["match_points_right"],
                }
            )
        )

    async def start_game(self, e):
        print("start game", self.channel_name)
        await self.send(text_data=json.dumps({"type": "startGame", "startGame": e["startGame"]}))


# Recurses

# https://channels.readthedocs.io/en/latest/tutorial/part_3.html#rewrite-the-consumer-to-be-asynchronous
# https://circumeo.io/blog/entry/django-websockets/
