# chat/consumers.py
import asyncio
import json
import time
import uuid

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache  # Import Django's cache

# from .game_code.ball import GameBall
# from .game_code.lobby import Lobby
# from .game_code.match import Match
# from .game_code.pongPlayer import PongPlayer
# from .game_code.storageClasses import SlotXy
# from .game_code.createMsg import SendToClient


LOBBIES = "lobbies"

import json


# MAY USE CLASSES FOR BETTER READABILITY
class LobbyRoom:
    def __init__(self, room_name, creator_name, players): # players is a list of players
        self.room_name = room_name
        self.players = players
        self.creator_name = None

    def to_json(self):
        return json.dumps({
            'name': self.name,
            'players': self.players
        })

    @staticmethod
    def from_json(json_str):
        data = json.loads(json_str)
        return LobbyRoom(data['room_name'], data["creator_name"], data['players'])
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
        current_room = cache.get(f'current_room_{self.displayname}')
        if current_room:
            await self.leave_room(current_room)

        await self.channel_layer.group_discard(LOBBIES, self.channel_name)
        await super().disconnect(close_code)  # Ensure proper cleanup by calling the parent class's disconnect method

     ### WEBSOCKET MESSAGE HANDLER ###
    async def receive(self, text_data):
        dict_data = json.loads(text_data)
        type = dict_data.get('type')
        print(json.dumps(dict_data))
        
        # handle websocket message from client
        if type == 'on_tournament_page':
            self.displayname = dict_data.get('displayname')

        elif type == 'create_tournament':
            await self.create_room(dict_data)
            
        elif type == 'join_tournament':
            await self.join_room(dict_data)

        elif type == 'leave_tournament':
            #room_name = dict_data.get('room_name')
            await self.leave_tournament()

        elif type == 'get_tournament_list':
            await self.get_tournament_list()

    ### WEBSOCKET MESSAGES ###
    async def create_room(self, dict_data):
        print("create_room")
        room_name = dict_data.get('tournament_name') # Frontend
        points_to_win = dict_data.get('points_to_win') # Frontend
        max_player_num = dict_data.get('max_player_num') # Frontend

        if not room_name:
            raise ValueError("Room name is required for creating a lobby")

        async with self.update_lock: # to prevent race conditions on cache
            # Initialize lobbies in the cache
            lobbies = cache.get('lobbies', {})
            if room_name in lobbies:
                await self.send_error(f"Lobby '{room_name}' already exists.")
                return

            # Add the new lobby to the list of known lobbies
            lobbies[room_name] = dict()
            lobbies[room_name]["players"] = []
            
            lobbies[room_name]["creator_name"] = self.displayname
            lobbies[room_name]["players"].append(self.displayname)
            lobbies[room_name]["size"] = 1
            lobbies[room_name]["max_player_num"] = max_player_num
            lobbies[room_name]["points_to_win"] = points_to_win


            cache.set('lobbies', lobbies)

            cache.set(f'current_room_{self.displayname}', room_name)

        # Notify others about the new lobby
        await self.updateLobbies("new_room", room_name, 1)

        # add user to the channel group
        await self.channel_layer.group_add(f'lobby_{room_name}', self.channel_name)
        return

    async def join_room(self, dict_data):
        room_name = dict_data.get('room_name')

        async with self.update_lock:
            # Check if the room exists
            lobbies = cache.get('lobbies', {})
            if room_name not in lobbies:
                await self.send_error(f"Lobby room '{room_name}' does not exist.")
                return
    
            # Check if the user is already in a room
            current_room = cache.get(f'current_room_{self.displayname}')
            if current_room:
                await self.send(text_data=json.dumps({
                    'type': 'join_tournament',
                    "joined": "false",
                    # 'message': f"You are already in a lobby: '{current_room}'. Leave that lobby before joining a new one."
                }))
                return

            # Check room size !!!

            # CACHE: Add the user to the new lobby room 
            lobbies[room_name]["players"].append(self.displayname)
            lobbies[room_name]["size"] += 1
            room_size = lobbies[room_name]["size"]

            cache.set('lobbies', lobbies)
            cache.set(f'current_room_{self.displayname}', room_name)
        
        # Notify ALL in the LOBBIES group, including users who already are in a lobby-room
        # SIMPLE, adding and removing the users of the LOBBIES group frequently has also drawbacks
        
         # Send all in the lobbies page who joined !!!
        self.updateLobbies("room_size_update", room_name, room_size)
        
        # CHANNELS: Add user to the lobby room group
        await self.channel_layer.group_add(f'lobby_{room_name}', self.channel_name)

        # Send all in the lobby room who joined !!!
        self.updateLobbyRoom("playerJoinedLobby", room_name)
        

        # Send message to WebSocket Frontend
        await self.send(text_data=json.dumps({
            'type': 'join_tournament',
            "joined": "true",
        }))


    async def leave_tournament(self):
        """Helper method to remove a user from a lobby."""
        
        print("leave_tournament")
        async with self.update_lock:
            current_room = cache.get(f'current_room_{self.displayname}')
            lobbies = cache.get('lobbies', {})
            
            if current_room not in lobbies:
                print(f"Lobby room '{current_room}' does not exist.")
                await self.send_error(f"Lobby room '{current_room}' does not exist.")
                return 

            #if current_room != current_room:
            #    await self.send_error(f"You are not in lobby room '{current_room}'.")
            #    return 
                

            # CACHE: Remove the user from the lobby room
            lobbies[current_room]["players"].remove(self.displayname)
            cache.delete(f'current_room_{self.displayname}')
            
            lobbies[current_room]["size"] -= 1
            room_size = lobbies[current_room]["size"]

            if room_size <= 0:
                del lobbies[current_room]
            cache.set('lobbies', lobbies)
        

        if room_size <= 0:
            self.updateLobbies("delete_room", current_room)
        else:
            self.updateLobbies("room_size_update", current_room, room_size)
            await self.channel_layer.group_send(
                LOBBIES, 
                {
                    'type': 'room_size_update',
                    'room_name': current_room,
                    'size': room_size
                }
            )
        
        # CHANNELS: Remove user from the lobby room group
        await self.channel_layer.group_discard(
            f'lobby_{current_room}',
            self.channel_name
        )


    async def get_tournament_list(self):
        lobbies = cache.get('lobbies', {})
        text_data=json.dumps({
            'type': 'get_tournament_list',
            "lobbies": lobbies
        })
        print(f"get_tournament_list: {text_data}")
        await self.send(text_data=text_data)


    
    
    ### EVENTS ###
    async def new_room(self, event):
        room_name = event['room_name']
        size = event['size']
        creator_name = event['creator_name']

        # Send message to WebSocket Frontend
        await self.send(text_data=json.dumps({
            'type': 'new_room',
            'room_name': room_name,
            'creator_name': creator_name,
            'size': size
        }))

    async def delete_room(self, event):
        room_name = event['room_name']
        await self.send(text_data=json.dumps({
            'type': 'delete_room',
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

    async def playerJoinedLobby(self, event):
        displayname = event['displayname']
        await self.send(text_data=json.dumps({
            'type': 'playerJoinedLobby',
            'displayname': displayname
        }))
    
    ### Helper ###
    async def updateLobbies(self, type, room_name, room_size):
            """
            Handles all changes to the list of lobbies

            - new_room: A new lobby has been created
            - delete_room: A lobby has been deleted
            - room_size_update: The size of a lobby has changed
            """

            print(f"TRIGGER event: {type}")
            if type == "new_room":
                print(f"new_room: {room_name}")
                await self.channel_layer.group_send(
                    LOBBIES, {
                        'type': type,
                        'creator_name': self.displayname,
                        'room_name': room_name,
                        'size': room_size
                    })
                
            elif type == "delete_room":
                await self.channel_layer.group_send(
                    LOBBIES, {
                        'type': 'delete_room',
                        'room_name': room_name,
                    })
                
            elif type == 'room_size_update':
                print(f"room_size_update: {room_name}, size: {room_size}")
                await self.channel_layer.group_send(
                    LOBBIES, {
                        'type': type,
                        'room_name': room_name,
                        'size': room_size
                    })
                
    async def updateLobbyRoom(self, type, room_name):
        if type == 'playerJoinedLobby':
            await self.channel_layer.group_send(
                f'lobby_{room_name}',
                {
                    'type': 'playerJoinedLobby',
                    "displayname": self.displayname
                    # image
                    # size and room_name? then frontend doesnt need to count up themselves
                }
            )
        # elif type == 'join_tournament':
        #     await self.channel_layer.group_send(
        #         f'lobby_{room_name}',
        #         {
        #             'type': 'playerLeftLobby',
        #             "displayname": self.displayname
        #         }
        #     )


    async def send_error(self, message):
        await self.send(text_data=json.dumps({
            'error': message
        }))
