

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
    GROUP_ = 'matchmaking'
    group_matchm = 'matchmaking'
    players = []

    async def connect(self):
        
        # Trick: when performing the cpu task before IO i limit the len of the players list to be max of 2
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
            
            send_players_where_to_connect_to(uuid, player1, self.channel_name)
            await self.channel_layer.send(
            player1,
            {
                'type': 'game_room',
                'id': "uuid"
            })


            await self.disconnect(1000)
        
        
        


    async def disconnect(self, close_code):
        MatchmakingConsumer.players.remove(self.channel_name) # Trick: wont need this
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
            
            
