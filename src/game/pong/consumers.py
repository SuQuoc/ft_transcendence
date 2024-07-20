# chat/consumers.py
import json
import uuid
import asyncio
import math
from .game_code.ball import gameBall
from .game_code.player import pong_player

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from .game_code.storageClasses import slotXy

# need asgiref

# NEED TO FIX X !!!!!!!!!!!!!!!!!!

class ChatConsumer(AsyncWebsocketConsumer):
    MOVE_SPEED = 20

    game_group_name = "game_group"

    # logic is we have a dict saved trow all instances of all socked/client connection
    # create a dict entry for every player
    players = {}

    # lock to get no data races
    update_lock = asyncio.Lock()

    map_size = slotXy(800, 600)

    async def connect(self):
        self.player_id = None
        if len(self.players) > 2: # place holder for user logic
            return

        # create a random id
        self.player_id = str(uuid.uuid4())

        # set up rooms
        # need more research on this
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.group_name = f"chat_{self.room_name}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

        # send to client that he has been accepted
        await self.send(
            text_data=json.dumps({"type": "playerId", "playerId": self.player_id})
        )
        # now lock and fill the players[id] dict
        async with self.update_lock:

            # dummy code for user manage t and match making logic #
            x = 0
            for player in self.players.values():
                if player.x == 0:
                    x = self.map_size.x

            # x will never change in pong just left and right player
            # logic is we have a struct saved trow all instances of all socked/client connection
            player = pong_player(self.player_id, x, self.map_size)

            self.players[self.player_id] = player
        
        # now create a task if the Game has no task. Still need to improve the logic
        async with self.update_lock:
            #look if already run game task
            for player in self.players.values():
                if player.task is not None:
                    return
            # save task into player struct to close it later
            self.players[self.player_id].task = asyncio.create_task(self.game_loop())
            if self.players[self.player_id].task is None:
                print("[ERROR] Task creation failed")

    # ASYNC TASK WITH 0.05 S DELAY
    async def game_loop(self):
        """ ball = { "x": 0, "y": 0,
                "turnDirection": -1, #// -1 if left +1 if right
                "walkDirection": -1, #// -1 if back +1 if front
                "rotationAngle": math.pi / 2,
                "moveSpeed": 0.1,
                } """
        ball = gameBall(x=300, y=200, map_size=self.map_size)

        # LOOOOOPPPPPPPP
        while len(self.players) > 0:
            async with self.update_lock:
                for player in self.players.values():
                    #ball["rotationAngle"] += ball["turnDirection"] * ball["rotationSpeed"]

                    # set new player pos
                    ball.move(player)
                    player.move(self.MOVE_SPEED)

                    # send to clients in django and then to JS
                    # update his game every 50 ms
                    await self.channel_layer.group_send(self.group_name,
                            {"type": "chat.message",
                                "y": player.y,
                                "x": player.x,
                                "playerId": player.id,
                                "ball_x": ball.x,
                                "ball_y": ball.y,
                            })
                    """ await self.send(text_data=json.dumps({"type": "update",
                                                          "y": player["y"],
                                                          "x": player["x"],
                                                          "playerId": player["id"]})) """
            await asyncio.sleep(0.04)

    async def disconnect(self):
        if self.player_id is None:
            return
        async with self.update_lock:
            if self.player_id in self.players:
                if self.players[self.player_id].task is not None:
                    self.players[self.player_id].task.cancel()
                del self.players[self.player_id]


        await self.channel_layer.group_discard(
            self.game_group_name, self.channel_name
        )

    # Receive message from WebSocket
    # Receive key up {up=1}
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)

        player_id = text_data_json["playerId"]
        player = self.players.get(player_id, None)
        if not player:
            return

        async with self.update_lock:
            player.up = text_data_json["up"]
            player.down = text_data_json["down"]

    # Receive message from room group
    async def chat_message(self, e):
        await self.send(text_data=json.dumps({"type": "update",
                                                "y": e["y"],
                                                "x": e["x"],
                                                "playerId": e["playerId"],
                                                "ball_x": e["ball_x"],
                                                "ball_y": e["ball_y"],
                                                }))

############################################### Recurses ###############################################

# https://channels.readthedocs.io/en/latest/tutorial/part_3.html#rewrite-the-consumer-to-be-asynchronous
# https://circumeo.io/blog/entry/django-websockets/
