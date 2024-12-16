
from channels.generic.websocket import AsyncWebsocketConsumer
from enum import Enum
import json
import base64
from .models import FriendList
from asgiref.sync import sync_to_async

connection_registry = {}

class Status(Enum):
    ONLINE = 'online'
    OFFLINE = 'offline'

class OnlineStatusConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = None

    async def connect(self):
        token = self.scope['cookies']['access']
        self.user_id = self.scope["user_id"]
        connection_registry[self.user_id] = self.channel_name # NOTE: use cache in prod?
        await self.accept()
        await self.send_status_to_friends(Status.ONLINE)

    async def disconnect(self, close_code):
        await self.send_status_to_friends(Status.OFFLINE)
        del connection_registry[self.user_id]
        await super().disconnect(close_code)
        
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        type = text_data_json['type']

        if type == 'get_friends_online_status': # TODO: might help? if not than just remove, problem if a friends get a added while im online
            await self.send_status_to_friends(Status.ONLINE)
        if type == 'send_online_status':
            friend_id = text_data_json.get(id)
            await self.send_status_to_single_friend(friend_id, Status.ONLINE)


    async def send_status_to_friends(self, status: Status):
        message = {
            'type': 'online_status',
            'status': status.value,
            "sender_id": self.user_id
        }
        
        if status.value == Status.ONLINE.value: # NOTE: needed so friend can send back his status, if i go off he doesnt need to send me back
            message["sender_channel"] = self.channel_name
        
        channels = await self.get_online_friends_channels()
        for friend_channel in channels:
            await self.channel_layer.send(friend_channel, message)


    async def send_status_to_single_friend(self, friend_id, status: Status):
        message = {
            'type': 'online_status',
            'status': status.value,
            "sender_id": self.user_id
        }
        
        if status.value == Status.ONLINE.value: # NOTE: needed so friend can send back his status, if i go off he doesnt need to send me back
            message["sender_channel"] = self.channel_name
        
        friend_channel = await self.get_friend_channel(friend_id)
        await self.channel_layer.send(friend_channel, message)


    # EVENTS
    async def online_status(self, event):
        print("\n-----------------\nONLINE STATUS EVENT")
        print(json.dumps(event))
        if event.get('status') == Status.ONLINE.value:
            friends_channel = event.get('sender_channel')
            if friends_channel:
                print("send friend im on")
                await self.send_status_back(friends_channel)
                event.pop('sender_channel') # NOTE: remove sensitive data before sending to client
            else:
                print("Some friend is online")
        await self.send(text_data=json.dumps(event))
        print("----------------- ")


    async def send_status_back(self, friends_channel):
        await self.channel_layer.send(friends_channel, {
                    'type': 'online_status',
                    'status': Status.ONLINE.value,
                    "sender_id": self.user_id 
                    # NOTE: dont include sender_channel, 
                    # else: endless message loop
                })
        

    # HELPERS
    @sync_to_async
    def get_online_friends_channels(self):
        try:
            friend_list = FriendList.objects.get(user=self.user_id) # table is created with first friend
        except FriendList.DoesNotExist:
            return []
        
        friends = friend_list.friends.all()
        channels = []
        for friend in friends:
            id = str(friend.user_id)
            friend_channel = connection_registry.get(id)
            if friend_channel:
                channels.append(friend_channel)
        return channels
    
    @sync_to_async
    def get_friend_channel(self, friend_id):
        friend_list = FriendList.objects.get(user=self.user_id)
        friend = friend_list.friends.filter(user_id=friend_id)
        id = str(friend.user_id)
        friend_channel = connection_registry.get(id)
        return friend_channel
