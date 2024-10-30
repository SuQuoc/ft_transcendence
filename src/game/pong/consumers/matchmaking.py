

import json
import uuid
import random
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .pong import Pong

games = {}

# TODO: Notion todo
class MatchmakingConsumer(AsyncWebsocketConsumer):
    lock = asyncio.Lock()
    group_matchm = 'matchmaking'
    players = [] # stores the channel names of the players

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(
                self.group_matchm,
                self.channel_name
        )

        MatchmakingConsumer.players.append(self.channel_name)
        if len(MatchmakingConsumer.players) == 2:
            player1 = MatchmakingConsumer.players.pop(0)
            player2 = MatchmakingConsumer.players.pop(0)
            uuid = uuid.uuid4()
            
            self.send_players_where_to_connect_to(uuid, player1)
            self.send_players_where_to_connect_to(uuid, player2)
            
            # could store who is allowed to join the game
            await self.disconnect(1000)
        
    
    async def send_players_where_to_connect_to(self, uuid, channel_name):
        await self.channel_layer.send(
            channel_name,
            {
                'type': 'match_found',
                'match_id': "uuid"
            })


    async def disconnect(self, close_code):
        if self.channel_name in MatchmakingConsumer.players:
            MatchmakingConsumer.players.remove(self.channel_name)
        
        await self.channel_layer.group_discard(
            self.group_matchm,
            self.channel_name
        )
        await super().disconnect(close_code)

    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']

        if message_type == 'cancel':
            await self.disconnect(1000)
            
            
