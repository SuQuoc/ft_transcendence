
from channels.generic.websocket import AsyncWebsocketConsumer
from enum import Enum
import json
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
        self.group_name = get_online_consumer_group(self.user_id)
        connection_registry[self.user_id] = self.channel_name
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        await self.send_status_to_friends(Status.ONLINE)

    async def disconnect(self, close_code):
        await self.send_status_to_friends(Status.OFFLINE)
        del connection_registry[self.user_id]
        await super().disconnect(close_code)
        
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        type = text_data_json['type']

    async def send_status_to_friends(self, status: Status):
        message = {
            'type': 'online_status',
            'status': status.value,
            "sender_id": self.user_id
        }
        
        # NOTE: needed so friend can send back his status, if i go off he doesnt need to send me back
        if status.value == Status.ONLINE.value:
            message["sender_channel"] = self.channel_name
        
        channels = await self.get_online_friends_channels()
        for friend_channel in channels:
            await self.channel_layer.send(friend_channel, message)


    # EVENTS
    async def send_status_to_single_friend(self, event): 
        # triggered by api endpoint
        status = event.get('status')
        friend_id = event.get('friend_id')

        message = {
            'type': 'online_status',
            'status': status,
            'sender_id': self.user_id
        }
        
        if status == Status.ONLINE.value:
            message["sender_channel"] = self.channel_name
    
        # NOTE: api endpoint using this method MUST provide correct id of friend
        # ELSE: online status sent to stranger
        friend_channel = self.get_friend_channel(friend_id) 
        if friend_channel:
            await self.channel_layer.send(friend_channel, message)


    async def online_status(self, event):
        if event.get('status') == Status.ONLINE.value:
            friends_channel = event.get('sender_channel')
            if friends_channel:
                await self.send_status_back(friends_channel)
                event.pop('sender_channel') # NOTE: removing channel name before sending data to client
        await self.send(text_data=json.dumps(event))


    # HELPERS
    async def send_status_back(self, friends_channel):
        await self.channel_layer.send(friends_channel, {
                    'type': 'online_status',
                    'status': Status.ONLINE.value,
                    "sender_id": self.user_id 
                    # NOTE: dont include sender_channel, 
                    # else: endless message loop
        })
    
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
    def get_friend(self, friend_id):
        friend_list = FriendList.objects.get(user=self.user_id)
        friend = friend_list.friends.filter(user_id=friend_id).first()
        return friend
    
    def get_friend_channel(self, friend_id):
        id = str(friend_id)
        friend_channel = connection_registry.get(id)
        return friend_channel


def get_online_consumer_group(user_id):
    return f"online_{user_id}"