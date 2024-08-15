# chat/consumers.py
import asyncio
import json
import time
import uuid

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer

from .game_code.createMsg import createLobbyStatusDict
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
        self.lobby = None
        # set up rooms
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.group_name = f"chat_{self.room_name}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        self.player = PongPlayer(self.player_id, self.map_size)
        await self.updateLobbyList()
        return
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
            self.match: Match = self.lobby.addPlayer(self.player)
            
            await self.channel_layer.group_add(
                self.match.name,  # Replace with the actual group name
                self.channel_name
            )

            self.lobbies[self.room_name] = self.lobby
            print("Lobby created", self.lobby.lobby_name, self.lobby.len, self.lobby.max_len)
            return

        async with self.update_lock:
            
            self.lobby = self.lobbies[self.room_name]
            self.match: Match = self.lobby.addPlayer(self.player)


        if self.lobby.len == self.lobby.max_len:
            # matches : list[Match] = self.lobby.startMatch()
            # if matches is not None:
                #print("match p1 = ", matches[0].player1.id)
                #print("match p2 = ", matches[0].player2.id)
                #matches[0].name = self.room_name + "_match1"
            # self.match = self.matches[0]
            print(self.player.id)
            # start the match
            print("start match")
            # start the game

        # task is like a thread. Sends client a msg to start the game.
            await self.channel_layer.group_add(
                self.match.name,  # Replace with the actual group name
                self.channel_name
            )

            task = asyncio.create_task(self.game_loop())
            if task is None:
                print("[ERROR] Task creation failed")
                return
            async with self.update_lock:
                self.match.task = task
            await self.channel_layer.group_send(
                self.match.name,
                {"type": "start.game", "startGame": True},
            )

    # ASYNC TASK WITH 0.05 S DELAY
    async def game_loop(self):
        print("game loop started")
        ball = GameBall(x=(self.map_size.x / 2), y=(self.map_size.y / 2), map_size=self.map_size, width=self.ball_width, height=self.ball_height)
        print(self.match.len)
        while self.match.len == 2:
            ball.hitWall()
            ball.move()
            async with self.update_lock:
                await self.sendToClient(self.match.player1, ball)
                await self.sendToClient(self.match.player2, ball)
                # [await self.sendToClient(player, ball) for player in self.players[self.room_name].values()]
            await asyncio.sleep(self.delay)
            """ async with self.update_lock:
                player_count = len(self.players[self.room_name]) """

    async def sendToClient(self, player: PongPlayer, ball: GameBall):
        print("send to client")
        player.move(self.MOVE_SPEED)
        ball.paddlesHit(player)
        # Send to clients in django and then to JS
        await self.channel_layer.group_send(
            self.match.name,
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
        print("send to client done")

    async def disconnect(self, close_code):

        async with self.update_lock:
            lobby_name = None
            if self.lobby:
                lobby_name = self.lobby.lobby_name

            if self.lobbies.get(lobby_name, None):
                self.lobbies[lobby_name].removePlayer(self.player)
                if self.lobbies[lobby_name].len == 0:
                    del self.lobbies[lobby_name]
                    self.lobbies.pop(lobby_name, None)

            if self.player:
                del self.player

        await self.channel_layer.group_discard(self.game_group_name, self.channel_name)
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Receive message from WebSocket
    # Receive key up {up=1}
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        if text_data_json["type"] == "update":
            if not self.player:
                return
            async with self.update_lock:
                self.player.up = text_data_json["up"]
                self.player.down = text_data_json["down"]

        elif text_data_json["type"] == "roomSize":
            self.group_max_size = int(text_data_json["roomSize"])

        elif text_data_json["type"] == "newClient":
            print(text_data_json)
        elif text_data_json["type"] == "createTournament":
            await self.createTournament(text_data_json)

        elif text_data_json["type"] == "joinTournament":
            await self.joinTournament(text_data_json)

    async def joinTournament(self, msg):
        print("joinTournament")
        self.lobby = self.lobbies.get(msg["tournament_name"], None)
        if self.lobby is None:
            # send error message ?
            return
        self.lobby = self.lobbies[msg["tournament_name"]]
        status = "false"
        if self.lobby.addPlayer(self.player):
            status = "true"
        await self.sendJoinTournament(status)

        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.updateLobbyList()
        print("Tournament joined", self.lobby.lobby_name, self.lobby.len, self.lobby.max_len)

    # Receive message from WebSocket
    async def createTournament(self, msg):
        # Create a new tournament
        # send if tournament already exists ?
        self.lobby = Lobby(msg["tournament_name"], int(msg["max_player_num"]))
        self.lobbies[msg["tournament_name"]] = self.lobby
        self.lobby.addPlayer(self.player)

        # Add player to the channel group of the tournament
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.updateLobbyList()

        print("Tournament created", self.lobby.lobby_name, self.lobby.len, self.lobby.max_len)

    async def updateLobbyList(self):
        print("updateLobbyList")
        msg = await createLobbyStatusDict(self.lobbies)
        if msg is None:
            return
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "update.tournamentList",
                "tournaments": msg,
            })

    async def update_tournamentList(self, e):
        print("updateTournamentListSend")
        await self.send(
            text_data=json.dumps(
                {
                    "type": "updateTournamentList",
                    "tournaments": e["tournaments"],
                }
            )
        )

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
        print("start game", self.room_name)
        await self.send(text_data=json.dumps({"type": "startGame", "startGame": e["startGame"]}))

    async def sendJoinTournament(self, e) -> None:
        print("sendJoinTournament")
        await self.send(text_data=json.dumps(
            {
                "type": "joinTournament",
                "joined": e}
            ))

# Recurses

# https://channels.readthedocs.io/en/latest/tutorial/part_3.html#rewrite-the-consumer-to-be-asynchronous
# https://circumeo.io/blog/entry/django-websockets/
