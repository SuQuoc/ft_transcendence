# chat/consumers.py
import asyncio
import json
import time
import uuid

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache  # Import Django"s cache

# from .game_code.ball import GameBall
# from .game_code.lobby import Lobby
# from .game_code.match import Match
# from .game_code.pongPlayer import PongPlayer
# from .game_code.storageClasses import SlotXy
# from .game_code.createMsg import SendToClient


LOBBIES = "lobbies"

# TYPES of messages
T_ON_TOURNAMENT_PAGE = "on_tournament_page"
T_CREATE_ROOM = "create_room"
T_NEW_ROOM = "new_room"

T_JOIN_ROOM = "join_room"
T_PLAYER_JOINED_ROOM = "player_joined_room"

T_LEAVE_ROOM = "leave_room"
T_PLAYER_LEFT_ROOM = "player_left_room"
T_DELETE_ROOM = "delete_room"

T_GET_TOURNAMENT_LIST = "get_tournament_list"
T_TOURNAMENT_LIST = "tournament_list"

T_GET_ROOM_INFO = "get_room_info"
T_ROOM_INFO = "room_info"

T_SUCCESS = "success"
T_ERROR = "error"

class Errors:
    NOT_IN_ROOM = "not_in_room"
    ROOM_NAME_TAKEN = "room_name_taken"
    ROOM_DOES_NOT_EXIST = "room_does_not_exist"
    ROOM_FULL = "room_full"
    ROOM_NAME_INVALID = "room_name_invalid"
    ALREADY_IN_ROOM = "already_in_room"

# MAY USE CLASSES FOR BETTER READABILITY
class LobbyRoom:
    def __init__(self, room_name, creator_name, players): # players is a list of players
        self.room_name = room_name
        self.players = players
        self.creator_name = None

    def to_json(self):
        return json.dumps({
            "name": self.name,
            "players": self.players
        })

    @staticmethod
    def from_json(json_str):
        data = json.loads(json_str)
        return LobbyRoom(data["room_name"], data["creator_name"], data["players"])
#######


class LobbiesConsumer(AsyncWebsocketConsumer):
    update_lock = asyncio.Lock()
    displayname = None
    

    async def connect(self):
        #self.lobby_name = self.scope["url_route"]["kwargs"]["lobby_name"]
        #self.group_name = "group_%s" % self.room_name # django groups, a group of related channels

        await self.channel_layer.group_add(LOBBIES, self.channel_name)
        await self.accept()
        #print(self.scope["user"])

    async def disconnect(self, close_code): 
        print(f"disconnect - close_code: {close_code}")
        
        await self.leave_room()
        await self.channel_layer.group_discard(LOBBIES, self.channel_name)
        await super().disconnect(close_code)

     ### WEBSOCKET MESSAGE HANDLER ###
    async def receive(self, text_data):
        try:
            dict_data = json.loads(text_data) # convert message from client to dict
            type = dict_data.get("type")
            print(json.dumps(dict_data))

            # handle websocket message from client
            if type == T_ON_TOURNAMENT_PAGE:
                self.displayname = dict_data.get("displayname")

            elif type == T_CREATE_ROOM:
                await self.create_room(dict_data)

            elif type == T_JOIN_ROOM:
                await self.join_room(dict_data)

            elif type == T_LEAVE_ROOM:
                #room_name = dict_data.get("room_name")
                await self.leave_room()

            elif type == T_GET_ROOM_INFO:
                await self.send_room_info(dict_data)

            elif type == T_GET_TOURNAMENT_LIST:
                await self.get_tournament_list()

        except Exception as e:
            print(f"Exception: {e}")


    ### WEBSOCKET MESSAGES ###
    async def create_room(self, dict_data):
        print("create_room")
        room_name = dict_data.get("room_name")
        points_to_win = dict_data.get("points_to_win")
        max_player_num = dict_data.get("max_player_num")

        if not room_name:
            raise ValueError("Room name is required for creating a lobby")

        async with self.update_lock: # to prevent race conditions on cache
            # Initialize lobbies in the cache
            lobbies = cache.get("lobbies", {})
            current_room = cache.get(f"current_room_{self.displayname}")

            if room_name in lobbies:
                await self.send_error(Errors.ROOM_NAME_TAKEN)
                return
            
            if current_room is not None:
                await self.send_error(Errors.ALREADY_IN_ROOM)
                return
                
            # Add the new lobby to the list of known lobbies
            lobbies[room_name] = self.init_new_room(room_name, self.displayname, points_to_win, max_player_num)

            cache.set("lobbies", lobbies)
            cache.set(f"current_room_{self.displayname}", room_name)

        # Notify others about the new lobby
        await self.group_send_new_room(lobbies[room_name])

        # add user to the channel group
        await self.group_add(room_name)
        await self.send_success(room_name)
        return
    

    async def join_room(self, dict_data):
        room_name = dict_data.get("room_name")

        async with self.update_lock:
            lobbies = cache.get("lobbies", {})
            current_room_name = cache.get(f"current_room_{self.displayname}")

            # Check if the room exists
            if room_name not in lobbies: # SHOULD NEVER HAPPEN
                await self.send_error(Errors.ROOM_DOES_NOT_EXIST)
                return
            
            room = lobbies[room_name]
            if current_room_name is not None: # SHOULD NEVER HAPPEN
                await self.send_error(Errors.ALREADY_IN_ROOM)
                return

            room = await self.add_player_to_room(room_name, lobbies)

        # CHANNELS: Add user to the room group
        await self.updateLobbyRoom(T_PLAYER_JOINED_ROOM, room) # MUST SEND ALL IN GROUP THE MSG BEFORE ADDING THE USER TO GROUP
        await self.group_add(room_name)
        
    

    
    async def leave_room(self):
        """Helper method to remove a user from a lobby."""
        
        print(T_LEAVE_ROOM)
        async with self.update_lock:
            current_room_name = cache.get(f"current_room_{self.displayname}")
            lobbies = cache.get("lobbies", {})

            if current_room_name is None: # SHOULD NEVER HAPPEN
                await self.send_error(Errors.NOT_IN_ROOM)
                return
            
            if current_room_name not in lobbies: # SHOULD NEVER HAPPEN
                raise ValueError(Errors.ROOM_DOES_NOT_EXIST)

            # CACHE: Remove the user from the lobby room
            current_room = lobbies[current_room_name]
            current_room["players"].remove(self.displayname)
            current_room["cur_player_num"] -= 1
            cache.delete(f"current_room_{self.displayname}")

            # CHANNELS: Remove user from the lobby room group
            await self.group_remove(current_room["name"])

            if current_room["cur_player_num"] == 0:
                del lobbies[current_room["name"]]
                await self.group_send_delete_room(current_room["name"])
            elif current_room["cur_player_num"] < 0:
                raise ValueError(f"Lobby room '{current_room_name}' has negative size - SHOULD NEVER HAPPEN.")
            else:
                await self.group_send_room_size_update(current_room["name"], current_room["cur_player_num"])
                await self.updateLobbyRoom(T_PLAYER_LEFT_ROOM, current_room)
            
            cache.set("lobbies", lobbies)


    async def get_room_info(self, dict_data):
        room_name = dict_data.get("room_name")
        lobbies = cache.get("lobbies", {})
        room = lobbies.get(room_name)

        if room is None:
            await self.send_error(f"Room '{room_name}' does not exist.")
            return

        await self.send(text_data=json.dumps({
            "type": T_ROOM_INFO,
            "room": room
        }))
        

    # should only return lobbies that are not full !!!
    async def get_tournament_list(self):
        lobbies = cache.get("lobbies", {})
        text_data=json.dumps({
            "type": T_TOURNAMENT_LIST,
            "lobbies": lobbies
        })
        await self.send(text_data=text_data)


    async def group_send_new_room(self, room: dict):
        print(f"trigger new_room: {room["name"]}")
        await self.channel_layer.group_send(
                    LOBBIES, {
                        "type": "new_room",
                        "room": room
                    })
        
    async def group_send_delete_room(self, room_name):
        print(f"trigger delete_room: {room_name}")
        await self.channel_layer.group_send(
                    LOBBIES, {
                        "type": T_DELETE_ROOM,
                        "room_name": room_name,
                    })
        
    async def group_send_room_size_update(self, room_name, room_size):
        print(f"trigger room_size_update: {room_name}")
        await self.channel_layer.group_send(
            LOBBIES, {
                "type": "room_size_update",
                "room_name": room_name,
                "cur_player_num": room_size
            })
        
    async def updateLobbyRoom(self, type, room: dict):
        if type == T_PLAYER_JOINED_ROOM:
            await self.channel_layer.group_send(
                f"lobby_{room["name"]}",
                {
                    "type": "player_joined_room",
                    "displayname": self.displayname,
                    "cur_player_num": room["cur_player_num"],
                    # image
                }
            )

        if type == T_PLAYER_LEFT_ROOM:
            await self.channel_layer.group_send(
                f"lobby_{room["name"]}",
                {
                    "type": "player_left_room",
                    "displayname": self.displayname,
                    "cur_player_num": room["cur_player_num"],
                    # image
                }
            )

    ### EVENTS - each Websocket sends message to frontend ###
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


    ### Send to own websocket ###
    async def send_room_info(self, dict_data):
        room_name = dict_data.get("room_name")
        lobbies = cache.get("lobbies", {})
        room = lobbies.get(room_name)

        if room is None:
            await self.send_error(Errors.ROOM_DOES_NOT_EXIST)
            return

        await self.send(text_data=json.dumps({
            "type": T_ROOM_INFO,
            "room": room
        }))

    async def send_success(self, room_name: str):
        await self.send(text_data=json.dumps({
            "type": T_SUCCESS,
            "room_name": room_name
        }))
        

    async def send_error(self, error: str):
        print(f"ERROR: {error}=========================")
        await self.send(text_data=json.dumps({
            "type": T_ERROR,
            "error": error,
        }))


    ### Helper ###
    async def add_player_to_room(self, room_name, lobbies):
        room = lobbies[room_name]            

        # if a room is full, it should not be returned by get_tournament_list !!! (therefore raising an error should not happen regularly)
        if room["cur_player_num"] == room["max_player_num"]:
            print(f"Lobby room '{room["name"]}' is full.")
            await self.send_error(f"join_room - Lobby room '{room["name"]}' is full.")
            raise ValueError(f"Lobby room '{room["name"]}' is full.")

        # SHOULD NEVER HAPPEN
        if room["cur_player_num"] > room["max_player_num"]:
            raise ValueError(f"Lobby room '{room["name"]}' is max - SHOULD NEVER HAPPEN.")

        room["players"].append(self.displayname)
        room["cur_player_num"] += 1

        if room["cur_player_num"] == room["max_player_num"]:
            del lobbies[room_name]
            cache.set("lobbies", lobbies)
            full_rooms = cache.get("full_rooms", {})
            full_rooms[room["name"]] = room
            cache.set("full_rooms", full_rooms)
            await self.group_send_delete_room(room["name"])

        else:
            lobbies[room_name] = room
            cache.set("lobbies", lobbies)        
            # Notify ALL in the LOBBIES group, including users who already are in a lobby-room
            # SIMPLE, adding and removing the users of the LOBBIES group frequently has also drawbacks
            await self.group_send_room_size_update(room_name, room["cur_player_num"])
        
        await self.send_success(room_name)
        # CACHE: Set the current room of the user 
        cache.set(f"current_room_{self.displayname}", room_name)
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


    # maybe not in this class !!! self not needed also maybe as a class
    def init_new_room(self, room_name, creator_name, points_to_win, max_player_num):
        new_room = {
            "name": room_name,
            "creator_name": creator_name,
            "players": [creator_name],
            "points_to_win": int(points_to_win),
            "max_player_num": int(max_player_num),
            "cur_player_num": 1
        }
        return new_room


### other version ### Evenn if i use kwargs everytime
    """ async def updateLobbies(self, type, room_name, room_size, ptw=0, max_player_num=0):
            
            Handles all changes to the list of lobbies

            - new_room: A new lobby has been created
            - delete_room: A lobby has been deleted
            - room_size_update: The size of a lobby has changed
           
            try:
                print(f"TRIGGER event: {type}")
                if type == "new_room":
                    await self.channel_layer.group_send(
                    LOBBIES, {
                        "type": "new_room",
                        "creator_name": self.displayname,
                        "room_name": room_name,
                        "cur_player_num": room_size,
                        "points_to_win": ptw,
                        "max_player_num": max_player_num
                    })
                
                elif type == "delete_room":
                    pass

                elif type == "room_size_update":
                    print(f"room_size_update: {room_name}, size: {room_size}")
                    await self.group_send_room_size_update(room_name, room_size)

                else:
                    raise ValueError(f"Unknown event type '{type}'")
            
            except Exception as e:
                print(f"Error: {e}") """