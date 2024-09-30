

from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
import json


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs'].get('game_id')
        self.group_name = f"game_{self.game_id}"


        game = Game.objects.filter(id=self.game_id).first()
        await self.accept()

    async def disconnect(self):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, json_data):
        dict_data = json.loads(json_data)
        type = dict_data['type']

        #await self.send(json_data=json.dumps({
        #    'message': message
        #}))