

from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
import json
from django.core.cache import cache

MOVE_UP = 'move_up'
MOVE_DOWN = 'move_down'



class GameConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.displayname = None
        
    async def connect(self):
        print(f"GameConsumer - connect")

        #print(self.scope["url_route"])
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.game_name = f"game_{self.game_id}"

        await self.channel_layer.group_add(self.game_name, self.channel_name)

        #game = Game.objects.filter(id=self.game_id).first()
        await self.accept()

        


        cache.set(self.game_name, [self.channel_name], timeout=None) # is there still a cache timeout with redis? leaving timeout to remind mde
        game_info = cache.get(self.game_name, [])
        if len(game_info) == 2:
            # init game with ptw
            #room = cache.get(self.room_name)
            #if room is None:
            #    raise Exception("Room not found")
            #self.points_to_win = room['points_to_win'] # where to store the ptw
            pass
            # start game somehow

            
    async def disconnect(self, close_code):
        print(f"GameConsumer - disconnect")
        await self.channel_layer.group_discard(self.game_name, self.channel_name)
        await super().disconnect(close_code)
        
    async def receive(self, text_data):
        dict_data = json.loads(text_data)
        type = dict_data['type']

        print(f"GameConsumer - receive:")
        print(json.dumps(dict_data))
        print("\n")

        if type == MOVE_UP:
            await self.channel_layer.group_send(
                self.game_name,
                {
                    'type': MOVE_UP,
                }
            )

        elif type == MOVE_DOWN:
            await self.channel_layer.group_send(
                self.game_name,
                {
                    'type': MOVE_DOWN,
                }
            )


    async def move_up(self, event):
        pass

    async def move_down(self, event):
        pass
        #await self.send(json_data=json.dumps({
        #    'message': message
        #}))







# INTERNET

class MultiplayerConsumer(AsyncWebsocketConsumer):
    MAX_SPEED = 5
    THRUST = 0.2

    game_group_name = "game_group"
    players = {}

    update_lock = asyncio.Lock()

    async def connect(self):
        self.player_id = str(uuid.uuid4())
        await self.accept()

        await self.channel_layer.group_add(
            self.game_group_name, self.channel_name
        )

        await self.send(
            text_data=json.dumps({"type": "playerId", "playerId": self.player_id})
        )

        async with self.update_lock:
            self.players[self.player_id] = {
                "id": self.player_id,
                "x": 500,
                "y": 500,
                "facing": 0,
                "dx": 0,
                "dy": 0,
                "thrusting": False,
            }

        if len(self.players) == 1:
            asyncio.create_task(self.game_loop())

    async def disconnect(self, close_code):
        async with self.update_lock:
            if self.player_id in self.players:
                del self.players[self.player_id]

        await self.channel_layer.group_discard(
            self.game_group_name, self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get("type", "")

        player_id = text_data_json["playerId"]

        player = self.players.get(player_id, None)
        if not player:
            return

        if message_type == "mouseDown":
            player["thrusting"] = True
        elif message_type == "mouseUp":
            player["thrusting"] = False
        elif message_type == "facing":
            player["facing"] = text_data_json["facing"]

    async def state_update(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "stateUpdate",
                    "objects": event["objects"],
                }
            )
        )

    async def game_loop(self):
        while len(self.players) > 0:
            async with self.update_lock:
                for player in self.players.values():
                    if player["thrusting"]:
                        dx = self.THRUST * math.cos(player["facing"])
                        dy = self.THRUST * math.sin(player["facing"])
                        player["dx"] += dx
                        player["dy"] += dy

                        speed = math.sqrt(player["dx"] ** 2 + player["dy"] ** 2)
                        if speed > self.MAX_SPEED:
                            ratio = self.MAX_SPEED / speed
                            player["dx"] *= ratio
                            player["dy"] *= ratio

                    player["x"] += player["dx"]
                    player["y"] += player["dy"]

            await self.channel_layer.group_send(
                self.game_group_name,
                {"type": "state_update", "objects": list(self.players.values())},
            )
            await asyncio.sleep(0.05)
