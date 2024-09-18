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

from .game_code.createMsg import SendToClient

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

    joinTournamentPage: dict[str, Lobby] = {}

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
        #self.player_id = str(uuid.uuid4())
        self.lobby = None
        # set up rooms
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        self.player = PongPlayer(self.player_id, self.map_size, channel_name=self.channel_name)

        if self.room_name == "match":
            return

        self.sendtoClient: SendToClient = SendToClient(self.group_name)
        await self.sendtoClient.sendLobbyStatus(self.joinTournamentPage)
        return

        # send to client that he has been accepted
        await self.send(text_data=json.dumps({"type": "playerId", "playerId": self.player_id}))
        # now lock and fill the players[id] dict
        await self.create_player_save_in_dict()

    async def create_player_save_in_dict(self):
        self.player = PongPlayer(self.player_id, self.map_size, channel_name=self.channel_name)
        lobby = None
        async with self.update_lock:
            lobby = self.joinTournamentPage.get(self.room_name, None)

        if lobby is None:

            # Now using a lobby class in a dict for better control
            self.lobby = Lobby(lobby_name=self.room_name, max_len=2)
            self.match: Match = self.lobby.addPlayer(self.player)

            await self.channel_layer.group_add(
                self.match.name,  # Replace with the actual group name
                self.channel_name
            )

            self.joinTournamentPage[self.room_name] = self.lobby
            print("Lobby created", self.lobby.lobby_name, self.lobby.len, self.lobby.max_len)
            return

        async with self.update_lock:

            self.lobby = self.joinTournamentPage[self.room_name]
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
    """ async def game_loop(self):
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
            async with self.update_lock:
                player_count = len(self.players[self.room_name]) """

    """ async def sendToClient(self, player: PongPlayer, ball: GameBall):
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
        ) """

    async def disconnect(self, close_code):

        async with self.update_lock:
            lobby_name = None
            if self.lobby:
                lobby_name = self.lobby.lobby_name

            if self.joinTournamentPage.get(lobby_name, None):
                await self.joinTournamentPage[lobby_name].removePlayer(self.player, self.channel_name)
                if self.joinTournamentPage[lobby_name].len == 0:
                    del self.joinTournamentPage[lobby_name]
                    self.joinTournamentPage.pop(lobby_name, None)

            if self.player:
                del self.player

        await self.channel_layer.group_discard(self.game_group_name, self.channel_name)
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Receive message from Client
    async def receive(self, text_data=None, bytes_data=None):
        msg = json.loads(text_data)

        match msg["type"]:

            case "update":
                if not self.player:
                    return
                async with self.update_lock:
                    self.player.up = msg["up"]
                    self.player.down = msg["down"]

            case "roomSize":
                self.group_max_size = int(msg["roomSize"])

            case "newClient":
                print(msg)

            case "createTournament":
                print("createTournament")
                await self.createTournament(msg)

            case "joinTournament":
                print("joinTournament")
                await self.joinTournament(msg)

            case "leaveTournament":
                await self.leaveTournament(msg)

            case "getUpdateLobbyPlayerList":
                print("getUpdateLobbyPlayerList")
                await self.sendtoClient.sendLobbyPlayerList(self.lobby)

            case None:
                print("[Warning] Received message with None type")

            case "onFindOpponentPage":
                await self.lookForOpponent(msg)

    async def lookForOpponent(self, msg):

        self.player_id = msg["user_id"]
        self.player.id = self.player_id
        self.players[self.player_id] = self.player

        match = Match(name=f"{self.player_id}_match")
        await match.addPlayer(self.player, channel_name=self.channel_name)
        if await match.findOpponent(self.players) is False:
            del match
            return

        self.players.pop(self.player_id)
        self.players.pop(match.player2.id)
        print("match.name: ", match.name)
        await self.channel_layer.group_send(match.name,{"type": "start.Pong"})
        await self.channel_layer.group_send(match.name,{"type": "player.Id", "player1": match.player1.id, "player2": match.player2.id})
        await match.startGame()
        print("start game")

    async def player_Id(self, e):
        print("player id", self.room_name)
        e["type"] = "playerId"
        await self.send(text_data=json.dumps(e))

    async def start_Pong(self, e):
        print("start pong", self.room_name)
        e["type"] = "startPong"
        await self.send(text_data=json.dumps(e))

    # JoinTournament
    async def joinTournament(self, msg):
        print("joinTournament")

        # Check if the tournament exists
        self.lobby = self.joinTournamentPage.get(msg["tournament_name"], None)
        if self.lobby is None:
            # send error message ?
            return

        # Add player to the tournament
        self.lobby = self.joinTournamentPage[msg["tournament_name"]]
        status = "false"
        if await self.lobby.addPlayer(self.player, self.channel_name):
            status = "true"
        await self.sendJoinTournament(status)

        # remove player to the tournaments joinTournamentPage group and send a update the lobby list
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.channel_layer.group_add(self.lobby.lobby_name, self.channel_name)
        await self.sendtoClient.sendLobbyStatus(self.joinTournamentPage)
        print("Tournament joined", self.lobby.lobby_name, self.lobby.len, self.lobby.max_len)

    # LeaveTournament
    async def leaveTournament(self, msg):
        print("leaveTournament")
        if self.lobby is None:
            return
        await self.lobby.removePlayer(self.player, self.channel_name)
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.sendtoClient.sendLobbyStatus(self.joinTournamentPage)
        await self.sendtoClient.sendLobbyPlayerList(self.lobby)

    # Create a Tournament
    async def createTournament(self, msg):
        # send if tournament already exists ?
        self.lobby = Lobby(msg["tournament_name"], int(msg["max_player_num"]))
        self.joinTournamentPage[msg["tournament_name"]] = self.lobby
        await self.lobby.addPlayer(self.player, self.channel_name)

        # Add player to the channel group of the tournament
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.channel_layer.group_add(self.lobby.lobby_name, self.channel_name)
        await self.sendtoClient.sendLobbyStatus(self.joinTournamentPage)

        print("Tournament created", self.lobby.lobby_name, self.lobby.len, self.lobby.max_len)

    async def update_tournamentList(self, e: dict):
        print("updateTournamentListSend")
        if e.get("type", None):
            e.pop("type")
        msg = { "type": "updateTournamentList",
                "tournaments": e }
        await self.send(text_data=json.dumps(msg))

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

    """ async def start_game(self, e):
        print("start game", self.room_name)
        await self.send(text_data=json.dumps({"type": "startGame", "startGame": e["startGame"]})) """

    async def sendJoinTournament(self, e) -> None:
        print("sendJoinTournament")
        await self.send(text_data=json.dumps(
            {
                "type": "joinTournament",
                "joined": e}
            ))

    async def update_LobbyPlayerList(self, e) -> None:
        print("hi dude")
        e["type"] = "updateLobbyPlayerList"
        print(e)
        await self.send(text_data=json.dumps(e))

# Recurses

# https://channels.readthedocs.io/en/latest/tutorial/part_3.html#rewrite-the-consumer-to-be-asynchronous
# https://circumeo.io/blog/entry/django-websockets/


LOOBIES = "lobbies"
from django.core.cache import cache  # Import Django's cache

class LobbiesConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.lobby_name = self.scope["url_route"]["kwargs"]["lobby_name"]
        #self.group_name = "group_%s" % self.room_name # django groups, a group of related channels

        await self.channel_layer.group_add(LOOBIES, self.channel_name)
        await self.accept()

    async def disconnect(self):
        current_room = cache.get(f'user_{self.channel_name}_room')
        if current_room:
            await self.leave_lobby(current_room)


        await self.channel_layer.group_discard(LOOBIES, self.channel_name)


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        type = text_data_json['type']

        if type == 'create_lobby':
            room_name = text_data_json.get('room_name')
            await self.create_lobby(room_name)

        elif type == 'join_lobby':
            room_name = text_data_json.get('room_name')




    async def create_lobby(self, room_name):
        if not room_name:
            raise ValueError("Room name is required for creating a lobby")

        # Initialize lobbies in the cache
        lobbies = cache.get('lobbies', {})
        if room_name in lobbies:
            raise ValueError(f"Lobby '{room_name}' already exists.")

        # Add the new lobby to the list of known lobbies
        lobbies[room_name] = set()
        cache.set('lobbies', lobbies)

        # Set initial room size to 0
        cache.set(f'lobby_{room_name}_size', 0)

        # Notify others about the new lobby
        await self.channel_layer.group_send(
            LOOBIES,
            {'type': 'new_room', 'room_name': room_name}
        )

        return
        await self.send(text_data=json.dumps({
            'type': 'lobby_created',
            'room_name': room_name
        }))

    async def join_lobby(self, room_name):
                    # Check if the lobby exists
            if room_name not in lobbies:
                raise ValueError(f"Lobby room '{room_name}' does not exist.")


            lobbies = cache.get('lobbies', {})

            # Check if the user is already in a room
            current_room = cache.get(f'user_{self.channel_name}_room')
            if current_room:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f"You are already in a lobby: '{current_room}'. Leave that lobby before joining a new one."
                }))
                return

            # Add the user to the new lobby
            lobbies[room_name].add(self.channel_name)
            cache.set('lobbies', lobbies)

            # Store the user's current room in the cache
            cache.set(f'user_{self.channel_name}_room', room_name)

            # Update room size
            room_size = cache.get(f'lobby_{room_name}_size', 0) + 1
            cache.set(f'lobby_{room_name}_size', room_size)


            # Notify others about the updated room size
            await self.channel_layer.group_send(
                'lobbies',
                {
                    'type': 'room_size_update',
                    'room_name': room_name,
                    'size': room_size
                }
            )


            # Add user to the lobby group
            await self.channel_layer.group_add(
                f'lobby_{room_name}',
                self.channel_name
            )

    async def leave_lobby(self, room_name):
        """Helper method to remove a user from a lobby."""
        lobbies = cache.get('lobbies', {})
        if room_name in lobbies:
            # Remove the user from the lobby
            lobbies[room_name].discard(self.channel_name)
            cache.set('lobbies', lobbies)

            # Remove the user's current room entry in the cache
            cache.delete(f'user_{self.channel_name}_room')

            # Update room size
            room_size = max(0, cache.get(f'lobby_{room_name}_size', 0) - 1)
            cache.set(f'lobby_{room_name}_size', room_size)

            # Notify others about the updated room size
            await self.channel_layer.group_send(
                'lobbies',
                {
                    'type': 'room_size_update',
                    'room_name': room_name,
                    'size': room_size
                }
            )

            # Remove user from the lobby group
            await self.channel_layer.group_discard(
                f'lobby_{room_name}',
                self.channel_name
            )


    async def new_room(self, event):
        room_name = event['room_name']
        await self.send(text_data=json.dumps({
            'type': 'new_room',
            'room_name': room_name
        }))

    async def room_size_update(self, event):
        room_name = event['room_name']
        size = event['size']
        await self.send(text_data=json.dumps({
            'type': 'room_size_update',
            'room_name': room_name,
            'size': size
        }))
