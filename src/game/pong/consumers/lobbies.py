import asyncio
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache  # Import Django"s cache
from django.core.cache.backends.redis import RedisCache
from .Room import TournamentRoom
from enum import Enum

import time
# from rest_framework_simplejwt.tokens import UntypedToken
from .utils import get_user_id_from_jwt 

# from .game_code.ball import GameBall
# from .game_code.lobby import Lobby
# from .game_code.match import Match
# from .game_code.pongPlayer import PongPlayer
# from .game_code.storageClasses import SlotXy
# from .game_code.createMsg import SendToClient

# TYPES of messages
T_ON_TOURNAMENT_PAGE = "on_tournament_page"
T_CREATE_ROOM = "create_room"
T_NEW_ROOM = "new_room"
T_ROOM_SIZE_UPDATE = "room_size_update"

T_JOIN_ROOM = "join_room"
T_PLAYER_JOINED_ROOM = "player_joined_room"

T_LEAVE_ROOM = "leave_room"
T_PLAYER_LEFT_ROOM = "player_left_room"
T_DELETE_ROOM = "delete_room"

T_GET_TOURNAMENT_LIST = "get_tournament_list"
T_TOURNAMENT_LIST = "tournament_list"

T_GET_ROOM_INFO = "get_room_info"
T_ROOM_INFO = "room_info"

T_START_TOURNAMENT = "start_tournament"

T_SUCCESS = "success"
T_ERROR = "error"

# Cache keys
FULL_ROOMS = "full_rooms"
AVA_ROOMS = "available_rooms"

class Errors(Enum):
    NOT_IN_ROOM = "not_in_room"
    NO_CURRENT_ROOM = "no_current_room"
    ROOM_NAME_TAKEN = "room_name_taken"
    ROOM_DOES_NOT_EXIST = "room_does_not_exist"
    ROOM_FULL = "room_full"
    ROOM_NAME_INVALID = "room_name_invalid"
    ALREADY_IN_ROOM = "already_in_room"

class LobbiesConsumer(AsyncWebsocketConsumer):
    update_lock = asyncio.Lock()
    
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.displayname = None

    async def connect(self):
        #print(self.scope["user"])
        
        token = self.scope["cookies"]["access"]
        user_id = get_user_id_from_jwt(token)
        self.client_group = f"client_{user_id}"
        print(f"user_id: {user_id}")

        await self.channel_layer.group_add(self.client_group, self.channel_name)
        await self.channel_layer.group_add(AVA_ROOMS, self.channel_name)
        await self.accept()
        print(f"Lobbies-Consumer - connect")

        #time.sleep(100) # no can do anything with the consumer for the time 
        #await asyncio.sleep(10) # others can still connect instantly, but the client connecting has to wait T time for messages following connect to be handled
        #asyncio.sleep(10) # doesnt do anything 
        

    async def disconnect(self, close_code): 
        print(f"Lobbies-Consumer disconnect - close_code: {close_code}")
        if cache.get(f"current_room_{self.displayname}"):
            await self.leave_room()
        
        await self.channel_layer.group_discard(self.client_group, self.channel_name)
        await self.channel_layer.group_discard(AVA_ROOMS, self.channel_name)
        await super().disconnect(close_code)

    async def receive(self, text_data):
        """WEBSOCKET MESSAGE HANDLER"""
        try:
            dict_data = json.loads(text_data) # convert message from client to dict
            type = dict_data.get("type")
            #print(f"LOBBIES-Consumer - receive:")
            #print(json.dumps(dict_data))
            #print("\n")

            # handle websocket message from client
            if type == T_ON_TOURNAMENT_PAGE:
                self.displayname = dict_data.get("displayname")

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
        room_name = dict_data.get("room_name")
        points_to_win = dict_data.get("points_to_win")
        max_player_num = dict_data.get("max_player_num")
       
        if not room_name:
            raise ValueError("Room name is required for creating a lobby")

        async with self.update_lock: # to prevent race conditions on cache
            # Initialize available_rooms in the cache
            available_rooms = cache.get(AVA_ROOMS, {})
            current_room_name = cache.get(f"current_room_{self.displayname}")
            
            if current_room_name is not None:
                await self.send_error(Errors.ALREADY_IN_ROOM)
                return
            
            if room_name in available_rooms or room_name in cache.get(FULL_ROOMS, {}):
                await self.send_error(Errors.ROOM_NAME_TAKEN)
                return
        
            # Add the new lobby to the list of known available_rooms
            room = TournamentRoom(
                name            = room_name, 
                creator_name    = self.displayname, 
                points_to_win   = points_to_win,
                max_player_num  = max_player_num
            )

            available_rooms[room.name] = room.to_dict()
            cache.set(AVA_ROOMS, available_rooms)
            cache.set(f"current_room_{self.displayname}", room.name)

        # add user to the channel group
        await self.group_add(room_name)
        await self.send_success(room_name)

        # Notify others about the new lobby
        #await self.group_send_new_room(available_rooms[room_name])
        await self.group_send_AvailableTournaments(T_NEW_ROOM, room)
        
        print(f"ROOM_NAME: {room_name} - {self.displayname} created a room")


    async def join_room(self, dict_data):
        room_name = dict_data.get("room_name")

        async with self.update_lock:
            available_rooms = cache.get(AVA_ROOMS, {})
            current_room_name = cache.get(f"current_room_{self.displayname}")

            if current_room_name is not None: # SHOULD NEVER HAPPEN
                await self.send_error(Errors.ALREADY_IN_ROOM)
                return
            
            # Check if the room exists
            if room_name not in available_rooms: # SHOULD NEVER HAPPEN
                await self.send_error(Errors.ROOM_DOES_NOT_EXIST)
                return
            
            room = await self.add_player_to_room(room_name, available_rooms)

        print(f"ROOM_NAME: {json.dumps(room.to_dict())} - {self.displayname} joined")

       
    async def leave_room(self):
        """Helper method to remove a user from a lobby."""
        
        #print(T_LEAVE_ROOM)
        async with self.update_lock:
            room_name = cache.get(f"current_room_{self.displayname}")
            available_rooms = cache.get(AVA_ROOMS, {})
            full_rooms = cache.get(FULL_ROOMS, {})

            if room_name is None: # SHOULD NOT HAPPEN with our Frontend
                await self.send_error(Errors.NO_CURRENT_ROOM)
                return
            
            room_dict = get_room_dict(room_name, available_rooms, full_rooms)
            if room_dict is None:
                raise ValueError(Errors.ROOM_DOES_NOT_EXIST) # SHOULD NEVER HAPPEN
            
            room = TournamentRoom.from_dict(room_dict)
            if self.displayname not in room.players:
                raise ValueError(Errors.NOT_IN_ROOM) # SHOULD NEVER HAPPEN

            room.remove_player(self.displayname)
            cache.delete(f"current_room_{self.displayname}")
            
            # CHANNELS: Remove user from the tournament room group
            await self.group_remove(room_name)
            await self.group_send_Room(T_PLAYER_LEFT_ROOM, room) # if the group is empty no one receives the message, according to Ai the group is effectivly deleted ==> research !!

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
            
            print(f"ROOM_NAME: {room.name} - {self.displayname} left")

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

        if room is None:
            await self.send_error(Errors.ROOM_DOES_NOT_EXIST)
            return

        await self.send(text_data=json.dumps({
            "type": T_ROOM_INFO,
            "room": room
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
                    "room": room.to_dict()
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
                f"lobby_{room.name}",
                {
                    "type": type,
                    "displayname": self.displayname,
                    "cur_player_num": room.cur_player_num,
                    # image
                }
            )
        elif type == T_PLAYER_LEFT_ROOM:
            await self.channel_layer.group_send(
                f"lobby_{room.name}",
                {
                    "type": type,
                    "displayname": self.displayname,
                    "cur_player_num": room.cur_player_num,
                    # image
                }
            )
        elif type == T_START_TOURNAMENT:
            await self.channel_layer.group_send(
                f"lobby_{room.name}",
                {
                    "type": type, # TODO: change to type
                    "test": "test"
                }
            )

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

    async def start_tournament(self, event):
        await self.send(text_data=json.dumps(event))

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
            room.add_player(self.displayname)
            cache.set(f"current_room_{self.displayname}", room.name)
        except Exception as e:
            print(f"Exception: {e}") # IF CACHE FAILS

         # CHANNELS: Add user to the room group
        await self.group_send_Room(T_PLAYER_JOINED_ROOM, room) # MUST SEND ALL IN GROUP THE MSG BEFORE ADDING THE USER TO GROUP
        await self.group_add(room.name)
        await self.send_success(room.name)

        if room.is_full():
            del_room_from_cache(room.name, AVA_ROOMS, available_rooms)
            update_or_add_room_to_cache(room.to_dict(), FULL_ROOMS)
            await self.group_send_AvailableTournaments(T_DELETE_ROOM, room)
            await self.group_send_Room(T_START_TOURNAMENT, room)
            # asyncio.create_task(tournament_start(room))
        else:
            # Notify ALL in the AVA_ROOMS group, including users who already are in a lobby-room
            # SIMPLE, adding and removing the users of the AVA_ROOMS group frequently has also drawbacks
            update_or_add_room_to_cache(room.to_dict(), AVA_ROOMS, available_rooms)
            await self.group_send_AvailableTournaments(T_ROOM_SIZE_UPDATE, room)
        
        return room


    async def group_remove(self, group_name: str):
        """
        Remove the channel from the specified channel group.
        """
        await self.channel_layer.group_discard(f"lobby_{group_name}", self.channel_name)

    async def group_add(self, group_name):
        """
        Add the channel to the specified channel group.
        """
        await self.channel_layer.group_add(f"lobby_{group_name}", self.channel_name)


def update_or_add_room_to_cache(room: dict, cache_name, cached_data: dict=None, ):
    """
    Updates or adds a room to the cache. 
    If the cached_data is not provided, it gets the cached_data from the cache with the cache_name.
    """
    if not isinstance(room, dict):
        raise ValueError("room must be a dictionary.")
    if not cache_name:
        raise ValueError("cache_name must be provided.")
    if not cached_data:
        cached_data = cache.get(cache_name, {})

    cached_data.update({room["name"]: room})
    cache.set(cache_name, cached_data)


def del_room_from_cache(room_name, cache_name, cached_data: dict=None):
    """
    Deletes a room to the cache. 
    If the cached_data is not provided, it gets the cached_data from the cache with the cache_name.
    """
    
    if not cache_name:
        raise ValueError("cache_name must be provided.")
    if not cached_data:
        cached_data = cache.get(cache_name, {})

    del cached_data[room_name]
    cache.set(cache_name, cached_data)


def get_room_dict(room_name, available_rooms: dict, all_rooms: dict) -> dict:
    return available_rooms.get(room_name) or all_rooms.get(room_name)


""" import random

#asyncio.create_task()
async def start_tournament(room: TournamentRoom):
    # start the tournament

    players = room.players
    while len(players) > 3:
        random.shuffle(players)
        pairs = make_pairs(players)
        
        winners = []
        for pair in pairs:
            p1 = pair[0]
            p2 = pair[1]
            await send_match_id(p1, p1, p2)
            await send_match_id(p2, p1, p2)

            # result = wait for the GameConsumer to send the match result or a cancel message
            
            winners.append(result.winner)
        players = winners


async def send_match_id(self, channel_name):
    await self.channel_layer.send(
        channel_name,
        {
            'type': 'tournament_match',
            'match_id': "uuid",
            "player1": "player1",
            "player2": "player2"
        })
    

async def start_match(pair):
    # start the match
    pass

def make_pairs(list) -> list:
    return [list[i:i+2] for i in range(0, len(list), 2)] """