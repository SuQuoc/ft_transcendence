

import json
import uuid
import random
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .pong import Pong
from .utils import get_user_id_from_jwt
from django.core.cache import cache
from .utils import create_match_access_list
from .pong_game_consumer import GameMode

games = {}

# TODO: Notion todo
class MatchmakingConsumer(AsyncWebsocketConsumer):
    lock = asyncio.Lock()
    players = [] # stores the channel names and user_ids
    # uuid.uuid4()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = None 

    async def connect(self):
        await self.accept()
        
        self.user_id = self.scope["user_id"]
        MatchmakingConsumer.players.append(
            {
                "channel_name": self.channel_name,
                "user_id": self.user_id
            })
        
        if len(MatchmakingConsumer.players) == 2:
            player1 = MatchmakingConsumer.players.pop(0)
            player2 = MatchmakingConsumer.players.pop(0)
                        
            match_id = create_match_access_list([player1["user_id"], player2["user_id"]], GameMode.NORMAL.value)
            
            await self.send_players_where_to_connect_to(match_id, player1["channel_name"])
            await self.send_players_where_to_connect_to(match_id, player2["channel_name"])
            
            await self.trigger_disconnection(player1["channel_name"])
            await self.trigger_disconnection(player2["channel_name"])


    async def disconnect(self, close_code):
        # using a dict instead of a list would be more efficient i think
        if any(self.channel_name in player.values() for player in MatchmakingConsumer.players):
            MatchmakingConsumer.players.remove(
                {
                    "channel_name": self.channel_name, 
                    "user_id": self.user_id
                })
        
        await super().disconnect(close_code)

    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']

        if message_type == 'cancel':
            await self.close()
            
    
    async def send_players_where_to_connect_to(self, match_id: str, channel_name):
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
    async def disconnect_from_matchmaking(self, event):
        await self.close()
