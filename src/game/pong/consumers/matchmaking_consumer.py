

import json
import uuid
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .pong import Pong
from django.core.cache import cache
from .utils import create_match_config
from .pong_game_consumer import GameMode
from pong.um_request import get_displayname
from collections import OrderedDict
from .Room import Player

games = {}

class MatchmakingConsumer(AsyncWebsocketConsumer):
    lock = asyncio.Lock()
    players = OrderedDict() # using a dict to disconnect correct user
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
    
    async def connect(self):
        await self.accept()
        
        user_id = self.scope["user_id"]
        displayname = await get_displayname(self.scope.get("cookies"))
        self.user = Player(
                        channel_name=self.channel_name,
                        name=displayname,
                        id=user_id
        )


        MatchmakingConsumer.players[self.channel_name] = self.user
        
        if len(MatchmakingConsumer.players) == 2:
            playerL_channel, playerL = MatchmakingConsumer.players.popitem()
            playerR_channel, playerR = MatchmakingConsumer.players.popitem()

            match_id = create_match_config([playerL.id, playerR.id],
                                           [playerL.name, playerR.name],
                                           GameMode.NORMAL.value)
            
            await self.trigger_match_found(match_id, playerL_channel)
            await self.trigger_match_found(match_id, playerR_channel)
            await self.trigger_disconnection(playerL_channel)
            await self.trigger_disconnection(playerR_channel)


    async def disconnect(self, close_code):
        MatchmakingConsumer.players.pop(self.channel_name, None)
        print(f"Player {self.user.name} disconnected")
        await super().disconnect(close_code)

    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']

        if message_type == 'cancel': # NOTE: not implemented yet, not a must
            await self.disconnect(1000)
            
    
    async def trigger_match_found(self, match_id: str, channel_name):
        if not isinstance(match_id, str):
            match_id = str(match_id)

        await self.channel_layer.send(
            channel_name,
            {
                "type": "match_found",
                "match_id": match_id
            })


    async def trigger_disconnection(self, channel_name):
        await self.channel_layer.send(
            channel_name,
            {
                "type": "disconnect_from_matchmaking"
            })
        

    # EVENTS
    async def match_found(self, event):
        await self.send(text_data=json.dumps(event))

    async def disconnect_from_matchmaking(self, event):
        await self.disconnect(1000)
