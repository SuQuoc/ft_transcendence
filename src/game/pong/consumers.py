# chat/consumers.py
import asyncio
import json
import time
import uuid

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer

from .game_code.ball import GameBall
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
    # all_players: dict[str, dict[str, PongPlayer]] = {}
    #         str s channel name | next key is id
    # lock to get no data races
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

        x = 0
        player = PongPlayer(self.player_id, x, self.map_size)

        async with self.update_lock:

            if self.players.get(self.room_name, None) is None:
                player_dict = {self.player_id: player}
                self.players[self.room_name] = player_dict
                self.players[self.room_name][self.player_id].task = asyncio.create_task(self.game_loop())
                if self.players[self.room_name][self.player_id].task is None:
                    print("[ERROR] Task creation failed")

            elif len(self.players[self.room_name]) == 1:
                player.x = self.map_size.x - player.width
                self.players[self.room_name][self.player_id] = player

        # async with self.update_lock:
        # dummy code for user manage t and match making logic #
        # x = 0
        # for player in self.players.values():
        #    if player.x == 0:
        #        x = self.map_size.x - player.width
        # logic is we have a struct saved all instances of all socked/client connection

        # now create a task if the Game has no task. Still need to improve the logic
        """ async with self.update_lock:
            # look if already run game task
            for player in self.players[self.room_name].values():
                if player.task is not None:
                    return
            # save task into player struct to close it later
            self.players[self.room_name][self.player_id].task = asyncio.create_task(self.game_loop())
            if self.players[self.room_name][self.player_id].task is None:
                print("[ERROR] Task creation failed") """

    # ASYNC TASK WITH 0.05 S DELAY
    async def game_loop(self):
        ball = GameBall(x=(self.map_size.x / 2), y=(self.map_size.y / 2), map_size=self.map_size, width=self.ball_width, height=self.ball_height)
        while len(self.players[self.room_name]) > 0:
            async with self.update_lock:
                ball.hitWall()
                ball.move()
                [await self.sendToClient(player, ball) for player in self.players[self.room_name].values()]

            await asyncio.sleep(self.delay)

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
            if self.player_id in self.players[self.room_name]:
                if self.players[self.room_name][self.player_id].task is not None:
                    self.players[self.room_name][self.player_id].task.cancel()
                del self.players[self.room_name][self.player_id]

                if self.players.get(self.room_name, None):
                    del self.players[self.room_name]

        await self.channel_layer.group_discard(self.game_group_name, self.channel_name)

    # Receive message from WebSocket
    # Receive key up {up=1}
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)

        player_id = text_data_json["playerId"]
        player = self.players[self.room_name].get(player_id, None)
        if not player:
            return

        async with self.update_lock:
            player.up = text_data_json["up"]
            player.down = text_data_json["down"]

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


# Recurses

# https://channels.readthedocs.io/en/latest/tutorial/part_3.html#rewrite-the-consumer-to-be-asynchronous
# https://circumeo.io/blog/entry/django-websockets/
