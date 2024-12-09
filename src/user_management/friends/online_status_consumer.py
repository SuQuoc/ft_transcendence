
from channels.generic.websocket import AsyncWebsocketConsumer
from enum import Enum
import json
import base64
from collections import defaultdict
from .models import FriendList

connection_registry = defaultdict(str)

class Status(Enum):
    ONLINE = 'online'
    OFFLINE = 'offline'

class OnlineStatusConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = None

    async def connect(self):
        token = self.scope['cookies']['access']
        self.user_id = get_user_id_from_jwt(token)
        connection_registry[self.user_id] = self.channel_name # NOTE: use cache in prod?
        
        await self.accept()
        await self.send_status_to_friends(Status.ONLINE)

    async def disconnect(self, close_code):
        await self.send_status_to_friends(Status.OFFLINE)
        connection_registry[self.user_id] = self.channel_name
        await super().disconnect(close_code)
        
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        type = text_data_json['type']

        if type == 'get_friends_online_status': # TODO: might help? if not than just remove, problem if a friends get a added while im online
            await self.send_status_to_friends(Status.ONLINE)

    
    async def send_status_to_friends(self, status):
        friend_list = FriendList.objects.get(user=self.user_id)
        friends = friend_list.friends.all()

        message = {
            'type': 'online_status',
            'status': status,
            "sender_id": self.user_id
        }
        
        if status == Status.ONLINE: # NOTE: needed so friend can send back his status, if i go off he doesnt need to send me back
            message["sender_channel"] = self.channel_name

        for friend in friends:
            friend_channel = connection_registry.get(friend.user_id, None)
            if friend_channel:
                await self.channel_layer.send(friend_channel, message)


    async def send_friend_my_status(self, friends_channel):
        await self.channel_layer.send(friends_channel, {
                    'type': 'online_status',
                    'status': Status.ONLINE,
                    "sender_id": self.user_id 
                    # NOTE: dont include sender_channel, else: endless message loop
                })

    # EVENTS
    async def online_status(self, event: dict):
        if event.get('status', None) == Status.ONLINE:
            friends_channel = event.get('sender_channel', None)
            if friends_channel:
                await self.send_friend_my_status(friends_channel)
                event.pop('sender_channel') # NOTE: remove sensitive data before sending to client
        await self.send(text_data=json.dumps(event))


def get_user_id_from_jwt(jwt_token):
    try:
        # Split the token to get the payload part (YY)
        payload_part = jwt_token.split('.')[1]
        
        # Decode the payload from Base64
        payload_decoded = base64.urlsafe_b64decode(payload_part + '==').decode('utf-8')
        user_id = json.loads(payload_decoded)['user_id']
        # Return the last 30 characters of the decoded payload
        return user_id
    except (IndexError, ValueError, base64.binascii.Error) as e:
        print(f"Error decoding JWT payload: {e}")