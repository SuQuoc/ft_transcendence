import asyncio
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache  # Import Django"s cache
from django.core.cache.backends.redis import RedisCache
from .Room import TournamentRoom, Player
from .utils import *
# from .bracket_tournament_logic import start_tournament
# from rest_framework_simplejwt.tokens import UntypedToken

# from .game_code.ball import GameBall
# from .game_code.lobby import Lobby
# from .game_code.match import Match
# from .game_code.pongPlayer import PongPlayer
# from .game_code.storageClasses import SlotXy
# from .game_code.createMsg import SendToClient


class LobbiesConsumer(AsyncWebsocketConsumer):
    update_lock = asyncio.Lock()
    room_queues = {}
    
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.current_room = None

    async def connect(self):
        #print(self.scope["user"])
        self.user = Player(channel_name=self.channel_name)
        
        token = self.scope["cookies"]["access"]
        user_id = get_user_id_from_jwt(token)
        self.client_group = f"client_{user_id}"
        print(f"LOBBIE CONSUMER: client group {self.client_group}")

        await self.channel_layer.group_add(self.client_group, self.channel_name)
        await self.channel_layer.group_add(AVA_ROOMS, self.channel_name)
        await self.accept()
        print(f"Lobbies-Consumer - connect")

        #time.sleep(100) # no can do anything with the consumer for the time 
        #await asyncio.sleep(10) # others can still connect instantly, but the client connecting has to wait T time for messages following connect to be handled
        #asyncio.sleep(10) # doesnt do anything 
        

    async def disconnect(self, close_code): 
        print(f"Lobbies-Consumer disconnect - close_code: {close_code}")
        if self.current_room: # cache.get(f"current_room_{self.user.name}"):
            await self.leave_room()
        
        await self.channel_layer.group_discard(self.client_group, self.channel_name)
        await self.channel_layer.group_discard(AVA_ROOMS, self.channel_name)
        await super().disconnect(close_code)

    async def receive(self, text_data):
        """WEBSOCKET MESSAGE HANDLER"""
        try:
            dict_data = json.loads(text_data) # convert message from client to dict
            type = dict_data.get("type")
            print(f"LOBBIES-Consumer - receive:")
            print(json.dumps(dict_data))
            print("\n")

            # handle websocket message from client
            if type == T_ON_TOURNAMENT_PAGE:
                self.user.name = dict_data.get("displayname")

            elif type == T_CREATE_ROOM:
                await self.create_room(dict_data)

            elif type == T_JOIN_ROOM:
                await self.join_room(dict_data)

            elif type == T_LEAVE_ROOM:
                await self.leave_room()

            elif type == T_GET_ROOM_INFO:
                await self.send_room_info(dict_data)

            elif type == T_GET_TOURNAMENT_LIST:
                await self.get_tournament_list()

            else:
                print(f"Unknown message type: {type}")
                # send an error to client
        except Exception as e:
            print(f"Exception: {e}")


    ### Client MESSAGES ###
    async def create_room(self, dict_data):
        print("CREATE ROOOOOOOOOM")

        room_name = dict_data.get("room_name")
        points_to_win = dict_data.get("points_to_win")
        max_player_num = dict_data.get("max_player_num")
       
        if not room_name:
            raise ValueError("Room name is required for creating a lobby")

        async with self.update_lock: # to prevent race conditions on cache
            # Initialize available_rooms in the cache
            available_rooms = cache.get(AVA_ROOMS, {})
            # current_room_name = cache.get(f"current_room_{self.user.name}")
            
            
            if self.current_room is not None:
                await self.send_error(Errors.ALREADY_IN_ROOM)
                return
            
            if room_name in available_rooms or room_name in cache.get(FULL_ROOMS, {}):
                await self.send_error(Errors.ROOM_NAME_TAKEN)
                return
        
            # Add the new lobby to the list of known available_rooms
            room = TournamentRoom(
                name            = room_name, 
                creator         = self.user.to_dict(),
                points_to_win   = points_to_win,
                max_player_num  = max_player_num
            )

            available_rooms[room_name] = room.to_dict()
            cache.set(AVA_ROOMS, available_rooms)
            self.current_room = room_name
            # cache.set(f"current_room_{self.user.name}", room.name)

        # add user to the channel group
        await self.group_add(get_room_group(room_name))
        print("sending success")
        await self.send_success(room_name)

        # Notify others about the new lobby
        #await self.group_send_new_room(available_rooms[room_name])
        await self.group_send_AvailableTournaments(T_NEW_ROOM, room)
        
        print(f"ROOM_NAME: {room_name} - {self.user.name} created a room")


    async def join_room(self, dict_data):
        room_name = dict_data.get("room_name")

        async with self.update_lock:
            available_rooms = cache.get(AVA_ROOMS, {})
            #current_room_name = cache.get(f"current_room_{self.user.name}")

            if self.current_room is not None: # SHOULD NEVER HAPPEN
                await self.send_error(Errors.ALREADY_IN_ROOM)
                return
            
            # Check if the room exists
            if room_name not in available_rooms: # SHOULD NEVER HAPPEN
                await self.send_error(Errors.ROOM_DOES_NOT_EXIST)
                return
            
            room = await self.add_player_to_room(room_name, available_rooms)
        print(f"ROOM_NAME: {json.dumps(room.to_dict())} - {self.user.name} joined")

       
    async def leave_room(self):
        """Helper method to remove a user from a lobby."""
        
        #print(T_LEAVE_ROOM)
        async with self.update_lock:
            # room_name = cache.get(f"current_room_{self.user.name}")
            available_rooms = cache.get(AVA_ROOMS, {})
            full_rooms = cache.get(FULL_ROOMS, {})

            if self.current_room is None: # SHOULD NOT HAPPEN with our Frontend
                await self.send_error(Errors.NO_CURRENT_ROOM)
                return
            
            room_dict = get_room_dict(self.current_room, available_rooms, full_rooms)
            if room_dict is None:
                raise ValueError(Errors.ROOM_DOES_NOT_EXIST) # SHOULD NEVER HAPPEN
            
            room = TournamentRoom.from_dict(room_dict)
            if self.user not in room.players:
                raise ValueError(Errors.NOT_IN_ROOM) # SHOULD NEVER HAPPEN

            room.remove_player(self.user)
            # cache.delete(f"current_room_{self.user.name}")
            
            # CHANNELS: Remove user from the tournament room group
            await self.group_remove(get_room_group(self.current_room))
            await self.group_send_Room(T_PLAYER_LEFT_ROOM, room) # if the group is empty no one receives the message, according to Ai the group is effectivly deleted ==> research !!
            self.current_room = None

            if room.status == TournamentRoom.AVAILABLE:
                if room.is_empty():
                    del_room_from_cache(room.name, AVA_ROOMS, available_rooms)
                    await self.group_send_AvailableTournaments(T_DELETE_ROOM, room)
                else:
                    update_or_add_room_to_cache(room.to_dict(), AVA_ROOMS, available_rooms)
                    await self.group_send_AvailableTournaments(T_ROOM_SIZE_UPDATE, room)             
            
            elif room.status == TournamentRoom.FULL: # just indicates that it was full at some point
                if room.is_empty():
                    del_room_from_cache(room.name, FULL_ROOMS, full_rooms)
                else:
                    update_or_add_room_to_cache(room.to_dict(), FULL_ROOMS, full_rooms)
            
            print(f"ROOM_NAME: {room.name} - {self.user.name} left")

    async def get_tournament_list(self):
        """Sends the list of AVAILABLE tournament rooms to the client."""

        available_rooms = cache.get(AVA_ROOMS, {})
        text_data=json.dumps({
            "type": T_TOURNAMENT_LIST,
            "tournaments": available_rooms
        })
        await self.send(text_data=text_data)
    

    async def send_room_info(self, dict_data):
        """
        Sends the information of a room to the client who joined a room and requested info.
        """
        room_name = dict_data.get("room_name")
        available_rooms = cache.get(AVA_ROOMS, {})
        full_rooms = cache.get(FULL_ROOMS, {})
        room = get_room_dict(room_name, available_rooms, full_rooms)
        room = TournamentRoom.from_dict(room)

        if room is None:
            await self.send_error(Errors.ROOM_DOES_NOT_EXIST)
            return

        await self.send(text_data=json.dumps({
            "type": T_ROOM_INFO,
            "room": room.to_data_for_client()
        }))


    # GROUP SENDS-------------------------------------------------    
    async def group_send_AvailableTournaments(self, type, room: TournamentRoom):
        if not isinstance(room, TournamentRoom):
            raise ValueError("room must be a TournamentRoom object.")

        if type == T_NEW_ROOM:
            await self.channel_layer.group_send(
                AVA_ROOMS,
                {
                    "type": type,
                    "room": room.to_data_for_client()
                })
            
        elif type == T_DELETE_ROOM:
            await self.channel_layer.group_send(
                AVA_ROOMS,
                {
                    "type": type,
                    "room_name": room.name
                })
            
        elif type == T_ROOM_SIZE_UPDATE:
            await self.channel_layer.group_send(
                AVA_ROOMS,
                {
                    "type": type,
                    "room_name": room.name,
                    "cur_player_num": room.cur_player_num
                })

    async def group_send_Room(self, type, room: TournamentRoom):
        if not isinstance(room, TournamentRoom):
            raise ValueError("room must be a TournamentRoom object.")            
        if type == T_PLAYER_JOINED_ROOM:
            await self.channel_layer.group_send(
                get_room_group(room.name),
                {
                    "type": type,
                    "displayname": self.user.name,
                    "cur_player_num": room.cur_player_num,
                    # image
                }
            )
        elif type == T_PLAYER_LEFT_ROOM:
            await self.channel_layer.group_send(
                get_room_group(room.name),
                {
                    "type": type,
                    "displayname": self.user.name,
                    "cur_player_num": room.cur_player_num,
                    # image
                }
            )
        """ elif type == T_START_TOURNAMENT:
            await self.channel_layer.group_send(
                get_room_group(room.name),
                {
                    "type": type, # TODO: change to type
                    "test": "test"
                }
            ) """

    ### EVENTS - each Websocket in the group sends message to it's client ###
    async def new_room(self, event):
        await self.send(text_data=json.dumps(event))

    async def delete_room(self, event):
        await self.send(text_data=json.dumps(event))

    async def room_size_update(self, event):
        await self.send(text_data=json.dumps(event))
        
    async def player_joined_room(self, event):
        await self.send(text_data=json.dumps(event))

    async def player_left_room(self, event):
        await self.send(text_data=json.dumps(event))

    # async def start_tournament(self, event):
    #     await self.send(text_data=json.dumps(event))

    async def match_result(self, event):
        """Puts the match result into the shared queue for the tournament task"""    
        
        queue = LobbiesConsumer.room_queues[self.current_room]
        print(f"EVENT IN match_result: {json.dumps(event)}")
        await queue.put(json.dumps(event))
        # await self.send(text_data=json.dumps(event))
        # NOTE: i could store the queue from the dict as a self.variable so every consumer sets it when the tournament starts
    

    async def tournament_bracket(self, event):
        """Sends the list of matches to the client."""
        await self.send(text_data=json.dumps(event))

    #async def start_tournament(self, event):
    #    await self.send(text_data=json.dumps(event))

    async def test(self, event):
        print("Lobbie consumer test event")
        pass



    ## Send to own websocket ##
    async def send_success(self, room_name: str):
        await self.send(text_data=json.dumps({
            "type": T_SUCCESS,
            "room_name": room_name
        }))
        

    async def send_error(self, error: Enum):
        # print(f"ERROR: {error}=========================")
        await self.send(text_data=json.dumps({
            "type": T_ERROR,
            "error": error.value,
        }))


    # Helper----------------------------------------------------------------
    async def add_player_to_room(self, room_name, available_rooms):
        room = TournamentRoom.from_dict(available_rooms[room_name])
        
        if room.is_full():
            await self.send_error(f"Tournament room '{room.name}' is full.") # NOTE: could happen with a lot clients when 2 want to join as the last person i guess
            return
        try:
            room.add_player(self.user)
            self.current_room = room.name
            # cache.set(f"current_room_{self.user.name}", room.name)
        except Exception as e:
            print(f"Exception: {e}") # IF CACHE FAILS

         # CHANNELS: Add user to the room group
        await self.group_send_Room(T_PLAYER_JOINED_ROOM, room) # MUST SEND ALL IN GROUP THE MSG BEFORE ADDING THE USER TO GROUP
        await self.group_add(get_room_group(room.name))
        await self.send_success(room.name)
        # NOTE: this await block may be a candidate for asyncio.gather() OR NOT
        # since sending the message to the clients and adding the new client to the channel group can happen at the same time
        # independent from each other but i dont want to send the T_PLAYER_JOINED_ROOM message 
        # to the JOINING CLIENT which may happen if the group_add happens before the send room the user is in the group

        if room.is_full():
            del_room_from_cache(room.name, AVA_ROOMS, available_rooms)
            update_or_add_room_to_cache(room.to_dict(), FULL_ROOMS)
            await self.group_send_AvailableTournaments(T_DELETE_ROOM, room)
            
            # self.start_tournament(room)
            # await self.group_send_Room(T_START_TOURNAMENT, room)
            # asyncio.create_task(tournament_start(room))
        else:
            # Notify ALL in the AVA_ROOMS group, including users who already are in a lobby-room
            # SIMPLE, adding and removing the users of the AVA_ROOMS group frequently has also drawbacks
            update_or_add_room_to_cache(room.to_dict(), AVA_ROOMS, available_rooms)
            await self.group_send_AvailableTournaments(T_ROOM_SIZE_UPDATE, room)
            # await asyncio.sleep(1) # NOTE: frontend hasnt loaded from JoinTournamentPage to TournamentLobbyPage
            # self.start_tournament(room) # NOTE: ONLY FOR TESTING
            
        return room

    def start_tournament(self, room: TournamentRoom):
        from .bracket_tournament_logic import tournament_loop

        # for player in room.players:
        print("1) start tournament - creating queue")
        LobbiesConsumer.room_queues[room.name] = asyncio.Queue() # or a queue for each player?
        asyncio.create_task(tournament_loop(room, LobbiesConsumer.room_queues[room.name]))


    async def group_remove(self, group_name: str):
        """
        Remove the channel from the specified channel group.
        """
        await self.channel_layer.group_discard(group_name, self.channel_name)

    async def group_add(self, group_name: str):
        """
        Add the channel to the specified channel group.
        """
        await self.channel_layer.group_add(group_name, self.channel_name)
