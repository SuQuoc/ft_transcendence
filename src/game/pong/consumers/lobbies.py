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
        current_room = cache.get(f'current_room_{self.displayname}')
        if current_room:
            await self.leave_room(current_room)

        await self.channel_layer.group_discard(LOBBIES, self.channel_name)
        await super().disconnect(close_code)  # Ensure proper cleanup by calling the parent class's disconnect method


    async def receive(self, text_data):
        dict_data = json.loads(text_data)
        type = dict_data.get('type')
        
        # handle websocket message from client
        if type == 'onTournamentPage':
            self.displayname = dict_data.get('displayname')
            print(json.dumps(dict_data))
            print(self.displayname)

        if type == 'createTournament': # Frontend
            room_name = dict_data.get('tournament_name') # Frontend
            
            print(json.dumps(dict_data))
            await self.create_room(room_name)
            
        elif type == 'join_room':
            room_name = dict_data.get('room_name')
            await self.join_room(room_name)

        elif type == 'leave_room':
            room_name = dict_data.get('room_name')
            await self.leave_room(room_name)

        elif type == 'getTournamentList':
            await self.get_tournament_list()



    async def create_room(self, room_name):
        if not room_name:
            raise ValueError("Room name is required for creating a lobby")

        async with self.update_lock: # to prevent race conditions on cache
            # Initialize lobbies in the cache
            lobbies = cache.get('lobbies', {})
            if room_name in lobbies:
                await self.send_error(f"Lobby '{room_name}' already exists.")
                return
                raise ValueError(f"Lobby '{room_name}' already exists.")

            # Add the new lobby to the list of known lobbies
            lobbies[room_name] = dict()
            
            lobbies[room_name]["creator_name"] = (self.displayname)
            lobbies[room_name]["players"] = {self.displayname}

            cache.set('lobbies', lobbies)
            cache.set(f'current_room_{self.displayname}', room_name)


        print("CREATE_ROOM")

        
        # Notify others about the new lobby
        self.updateLobbies("new_room", room_name)

        # add user to the channel group
        await self.channel_layer.group_add(f'lobby_{room_name}', self.channel_name)
        
        return

    async def join_room(self, room_name):
        # Check if the lobby exists
        async with self.update_lock:
            lobbies = cache.get('lobbies', {})
            if room_name not in lobbies:
                await self.send_error(f"Lobby room '{room_name}' does not exist.")
                return
    
            # Check if the user is already in a room
            current_room = cache.get(f'current_room_{self.displayname}')
            if current_room:
                await self.send(text_data=json.dumps({
                    'type': 'joinTournament',
                    "joined": "false",
                    # 'message': f"You are already in a lobby: '{current_room}'. Leave that lobby before joining a new one."
                }))
                return

            # Check room size !!!

            # CACHE: Add the user to the new lobby room 
            lobbies[room_name].add(self.displayname)
            cache.set('lobbies', lobbies)
            cache.set(f'current_room_{self.displayname}', room_name)
            room_size = len(lobbies[room_name])
        
        # Notify ALL in the LOBBIES group, including users who already are in a lobby-room
        # SIMPLE, adding and removing the users of the LOBBIES group frequently has also drawbacks
        
        
        self.updateLobbies(room_name, room_size)
        
        # CHANNELS: Add user to the lobby room group
        await self.channel_layer.group_add(f'lobby_{room_name}', self.channel_name)

        # Send all in the lobby room who joined !!!
        self.updateRoom(room_name)
        

        # Send message to WebSocket Frontend
        await self.send(text_data=json.dumps({
            'type': 'joinTournament',
            "joined": "true",
        }))


        


    async def leave_room(self, room_name):
        """Helper method to remove a user from a lobby."""

        async with self.update_lock:
            lobbies = cache.get('lobbies', {})
            if room_name not in lobbies:
                await self.send_error(f"Lobby room '{room_name}' does not exist.")
                return 

            current_room = cache.get(f'current_room_{self.displayname}')
            if current_room != room_name:
                await self.send_error(f"You are not in lobby room '{room_name}'.")
                return 
                

            # CHACHE: Remove the user from the lobby room
            lobbies[room_name]["players"].discard(self.displayname)
            cache.delete(f'current_room_{self.displayname}')
            room_size = len(lobbies[room_name]["players"])
            if room_size == 0:
                del lobbies[room_name]
            cache.set('lobbies', lobbies)
        

        if room_size == 0:
            # Notify others about the deleted room
            await self.channel_layer.group_send(
                LOBBIES, 
                {
                    'type': 'deleteRoom',
                    'room_name': room_name,
                }
            )
        else:
            # Notify others about the updated room size
            await self.channel_layer.group_send(
                LOBBIES, 
                {
                    'type': 'room_size_update',
                    'room_name': room_name,
                    'size': room_size
                }
            )
        

        # CHANNELS: Remove user from the lobby room group
        await self.channel_layer.group_discard(
            f'lobby_{room_name}',
            self.channel_name
        )

    async def get_tournament_list(self):
        lobbies = cache.get('lobbies', {})
        print(lobbies)
        return lobbies


    # Helper
    async def updateLobbies(self, type, room_name, room_size=1):
            if type == 'new_room':
                await self.channel_layer.group_send(
                    LOBBIES,
                    {
                        'type': type,
                        'creator_name': self.displayname,
                        'room_name': room_name,
                        'size': room_size
                    })

            elif type == 'room_size_update':
                await self.channel_layer.group_send(
                    LOBBIES,
                    {
                        'type': type,
                        'room_name': room_name,
                        'size': room_size
                    }
                )


    

    async def updateRoom(self, room_name):
            await self.channel_layer.group_send(
                f'lobby_{room_name}',
                {
                    'type': 'playerJoinedLobby',
                    "displayname": self.displayname
                    # image
                    # size and room_name? then frontend doesnt need to count up themselves
                }
            )
    
    # Events
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

    async def room_size_update(self, event):
        room_name = event['room_name']
        size = event['size']
        await self.send(text_data=json.dumps({
            'type': 'room_size_update',
            'room_name': room_name,
            'size': size
        }))


    async def send_error(self, message):
        await self.send(text_data=json.dumps({
            'error': message
        }))

    async def playerJoinedLobby(self, event):
        displayname = event['displayname']
        await self.send(text_data=json.dumps({
            'type': 'playerJoinedLobby',
            'displayname': displayname
        }))





    def message(type) -> dict:
       
        if type == 'createTournament':
            return {
                'type': type
            }
        
        if type == 'joinTournament':
            return {
                'type': type
            }
        
        if type == 'leaveTournament':
            pass

        if type == "new":
            return {
                'type': type, 
                'creator_name': "BANE",
                'room_name': "sa",
                'size': 1
            }
        
