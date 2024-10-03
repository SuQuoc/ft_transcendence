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
T_PLAYER_JOINED_ROOM = "player_joined_room"
T_PLAYER_LEFT_ROOM = "player_left_room"

import json


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

    async def disconnect(self, close_code): # take a look at close_code !!!
        print("disconnect")
        
        await self.leave_room()
        await self.channel_layer.group_discard(LOBBIES, self.channel_name)
        await super().disconnect(close_code)  # Ensure proper cleanup by calling the parent class"s disconnect method

     ### WEBSOCKET MESSAGE HANDLER ###
    async def receive(self, text_data):
        try:
            dict_data = json.loads(text_data) # convert message from client to dict
            type = dict_data.get("type")
            print(json.dumps(dict_data))

            # handle websocket message from client
            if type == "on_tournament_page":
                self.displayname = dict_data.get("displayname")

            elif type == "create_tournament":
                await self.create_room(dict_data)

            elif type == "join_tournament":
                await self.join_room(dict_data)

            elif type == "leave_tournament":
                #room_name = dict_data.get("room_name")
                await self.leave_room()

            elif type == "get_tournament_list":
                await self.get_tournament_list()

        except Exception as e:
            print(f"Exception: {e}")
            # await self.send_error(f"Error: {e}")


    ### WEBSOCKET MESSAGES ###
    async def create_room(self, dict_data):
        print("create_room")
        room_name = dict_data.get("tournament_name")
        points_to_win = dict_data.get("points_to_win")
        max_player_num = dict_data.get("max_player_num")

        if not room_name:
            raise ValueError("Room name is required for creating a lobby")

        async with self.update_lock: # to prevent race conditions on cache
            # Initialize lobbies in the cache
            lobbies = cache.get("lobbies", {})
            current_room = cache.get(f"current_room_{self.displayname}")

            if room_name in lobbies:
                await self.send_error(f"Lobby '{room_name}' already exists.")
                return
            if current_room is not None:
                await self.send_error(f"You are already in a lobby: '{current_room}'. Leave that lobby before creating a new one.")
                return
                
            # Add the new lobby to the list of known lobbies
            lobbies[room_name] = self.init_new_room(room_name, self.displayname, points_to_win, max_player_num)

            cache.set("lobbies", lobbies)
            cache.set(f"current_room_{self.displayname}", room_name)

        # Notify others about the new lobby
        await self.group_send_new_room(room_name=room_name,
                                        room_size=1,
                                        ptw=points_to_win,
                                        max_player_num=max_player_num)

        # add user to the channel group
        await self.group_add(room_name)
        return
    

    async def join_room(self, dict_data):
        room_name = dict_data.get("room_name")

        async with self.update_lock:
            # Check if the room exists
            lobbies = cache.get("lobbies", {})
            current_room_name = cache.get(f"current_room_{self.displayname}")

            if room_name not in lobbies: # SHOULD NEVER HAPPEN
                await self.send_error(f"join_room - Lobby room '{room_name}' does not exist.")
                return
            
            room = lobbies[room_name]
            if room["creator_name"] == self.displayname: # u are the creator so only then if call is triggered
                await self.send_client_join_tournament("join_tournament", room)
                return

            if current_room_name is not None: # SHOULD NEVER HAPPEN
                await self.send(text_data=json.dumps({
                    "type": "join_tournament",
                    "joined": "false",
                    # "message": f"You are already in a lobby: "{current_room}". Leave that lobby before joining a new one."
                }))
                return

            room = await self.add_player_to_room(room_name, lobbies)

        # CHANNELS: Add user to the room group
        await self.updateLobbyRoom(T_PLAYER_JOINED_ROOM, room) # MUST SEND ALL IN GROUP THE MSG BEFORE ADDING THE USER TO GROUP
        await self.group_add(room_name)
        
        # Send message to WebSocket Frontend
        await self.send_client_join_tournament("join_tournament", room)

    

    async def add_player_to_room(self, room_name, lobbies):
        room = lobbies[room_name]            

        # if a room is full, it should not be returned by get_tournament_list !!! (therefore raising an error should not happen regularly)
        if room["size"] == room["max_player_num"]:
            print(f"Lobby room '{room["name"]}' is full.")
            await self.send_error(f"join_room - Lobby room '{room["name"]}' is full.")
            raise ValueError(f"Lobby room '{room["name"]}' is full.")

        # SHOULD NEVER HAPPEN
        if room["size"] > room["max_player_num"]:
            raise ValueError(f"Lobby room '{room["name"]}' is max - SHOULD NEVER HAPPEN.")

        room["players"].append(self.displayname)
        room["size"] += 1

        if room["size"] == room["max_player_num"]:
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
            await self.group_send_room_size_update(room_name, room["size"])
        
        
        # CACHE: Set the current room of the user 
        cache.set(f"current_room_{self.displayname}", room_name)
        return room

    

    async def leave_room(self):
        """Helper method to remove a user from a lobby."""
        
        print("leave_room")
        async with self.update_lock:
            current_room_name = cache.get(f"current_room_{self.displayname}")
            lobbies = cache.get("lobbies", {})

            if current_room_name is None: # SHOULD NEVER HAPPEN
                await self.send_error(f"You are not in any lobby room.")
                return
            
            if current_room_name not in lobbies: # SHOULD NEVER HAPPEN
                raise ValueError(f"Lobby room '{current_room_name}' does not exist in the cache - SHOULD NEVER HAPPEN.")

            # CACHE: Remove the user from the lobby room
            current_room = lobbies[current_room_name]
            current_room["players"].remove(self.displayname)
            current_room["size"] -= 1
            cache.delete(f"current_room_{self.displayname}")
            
            

            if current_room["size"] == 0:
                del lobbies[current_room["name"]]
            if current_room["size"] < 0:
                raise ValueError(f"Lobby room '{current_room_name}' has negative size - SHOULD NEVER HAPPEN.")
            cache.set("lobbies", lobbies)

        # CHANNELS: Remove user from the lobby room group
        await self.group_remove(current_room["name"])

        if current_room["size"] == 0:
            await self.group_send_delete_room(current_room["name"])
            #await self.updateLobbies("delete_room", current_room)
        else:
            await self.group_send_room_size_update(current_room["name"], current_room["size"])
            await self.updateLobbyRoom(T_PLAYER_LEFT_ROOM, current_room)
            #await self.updateLobbies("room_size_update", current_room, room_size)
            
        
    

    # should only return lobbies that are not full !!!
    async def get_tournament_list(self):
        lobbies = cache.get("lobbies", {})
        text_data=json.dumps({
            "type": "get_tournament_list",
            "lobbies": lobbies
        })

        print(f"get_tournament_list: {json.dumps({
            "type": "get_tournament_list",
            "lobbies": lobbies
        }, indent=4)}")
        await self.send(text_data=text_data)
    
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



    ### Helper ###
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


    async def group_send_new_room(self, *, room_name, room_size, ptw, max_player_num):
        print(f"trigger new_room: {room_name}")
        await self.channel_layer.group_send(
                    LOBBIES, {
                        "type": "new_room",
                        "creator_name": self.displayname,
                        "room_name": room_name,
                        "size": room_size,
                        "points_to_win": ptw,
                        "max_player_num": max_player_num
                    })
        
    async def group_send_delete_room(self, room_name):
        print(f"trigger delete_room: {room_name}")
        await self.channel_layer.group_send(
                    LOBBIES, {
                        "type": "delete_room",
                        "room_name": room_name,
                    })
        
    async def group_send_room_size_update(self, room_name, room_size):
        print(f"trigger room_size_update: {room_name}")
        await self.channel_layer.group_send(
            LOBBIES, {
                "type": "room_size_update",
                "room_name": room_name,
                "size": room_size
            })
    

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
                        "size": room_size,
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
        
    async def updateLobbyRoom(self, type, room: dict):
        if type == T_PLAYER_JOINED_ROOM:
            await self.channel_layer.group_send(
                f"lobby_{room["name"]}",
                {
                    "type": "player_joined_room",
                    "displayname": self.displayname,
                    # image
                    "size": room["size"],
                }
            )

        if type == T_PLAYER_LEFT_ROOM:
            await self.channel_layer.group_send(
                f"lobby_{room["name"]}",
                {
                    "type": "player_left_room",
                    "displayname": self.displayname,
                    # image
                    "room": room
                    # size and room_name? then frontend doesnt need to count up themselves
                }
            )
        # elif type == "join_tournament":
        #     await self.channel_layer.group_send(
        #         f"lobby_{room_name}",
        #         {
        #             "type": "playerLeftLobby",
        #             "displayname": self.displayname
        #         }
        #     )


    async def send_error(self, message):
        await self.send(text_data=json.dumps({
            "type": "error",
            "message": message
        }))


    async def send_client_join_tournament(self, type, room):
        if type == "join_tournament":
            await self.send(text_data=json.dumps({
                        "type": "join_tournament",
                        "joined": "true",
                        "room": room
                }))

    # maybe not in this class !!! self not needed also maybe as a class
    def init_new_room(self, room_name, creator_name, points_to_win, max_player_num):
        new_room = {
            "name": room_name,
            "creator_name": creator_name,
            "players": [creator_name],
            "points_to_win": int(points_to_win),
            "max_player_num": int(max_player_num),
            "size": 1
        }
        return new_room
