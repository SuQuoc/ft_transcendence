

import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .pong import Pong
from enum import Enum
from .utils import get_user_id_from_jwt 


class GameMode(Enum):
    NORMAL = 'normal'
    tournament = 'tournament'

class PongGameConsumer(AsyncWebsocketConsumer):
    game_instance = None
    #game_loop_running = False
    players = []

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.mode = None # resolve from scope

    async def connect(self):
        #print(f"GameConsumer - connect")
        token = self.scope["cookies"]["access"]
        self.client_group = f"client_{get_user_id_from_jwt(token)}"

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.game_group = f'game_{self.room_name}'
        
        await self.channel_layer.group_add(self.client_group, self.channel_name)
        await self.channel_layer.group_add(
                self.game_group,
                self.channel_name
        ) # must be here since EACH consumer instance has unique channel_name, regardless if same client connects to N consumers
        await self.accept()

        self.players.append(self.channel_name)
        if len(self.players) == 2:
            PongGameConsumer.game_instance = Pong(self.players[0], self.players[1])
            await self.send_players_side()
            #self.players.remove(self.players[0])
            #self.players.remove(self.players[0])
            
            #PongGameConsumer.game_loop_running = True
            asyncio.create_task(self.game_loop())



    async def disconnect(self, close_code):
        #print(f"GameConsumer - disconnect")
        
        self.players.remove(self.channel_name)

        await self.channel_layer.group_discard(
            self.client_group, 
            self.channel_name
        )
        
        await self.channel_layer.group_discard(
            self.game_group,
            self.channel_name
        )
        await super().disconnect(close_code)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        type = text_data_json['type']
        
        #print(f"GameConsumer - receive:")
        #print(json.dumps(text_data))
        #print("\n")

        if type == 'up':
            direction = -1
        elif type == 'down':
            direction = 1
        else:
            return

        if PongGameConsumer.game_instance is None:
            return    

        ##print(self.channel_name)
        ##print(PongGameConsumer.game_instance.player_l)
        ##print(PongGameConsumer.game_instance.player_r)
        if self.channel_name == PongGameConsumer.game_instance.player_l:
            PongGameConsumer.game_instance.player_l_y += PongGameConsumer.game_instance.paddle_speed * direction
        elif self.channel_name == PongGameConsumer.game_instance.player_r:
            PongGameConsumer.game_instance.player_r_y += PongGameConsumer.game_instance.paddle_speed * direction
        else:
            raise ValueError('Should never happen')
            

    async def game_loop(self):
        while True:
            PongGameConsumer.game_instance.update_game_state()
            game_state = PongGameConsumer.game_instance.get_game_state()

            await self.channel_layer.group_send(
                self.game_group,
                {
                    'type': 'state_update',
                    'game_state': game_state
                }
            )
            if game_state['score_l'] == PongGameConsumer.game_instance.points_to_win or game_state['score_r'] == PongGameConsumer.game_instance.points_to_win:
                # send game end info to client
                break

            await asyncio.sleep(0.03)  # Update the game state every 30ms

        # TODO: 
        # save the result of the game in the database - must be done in a task and not in consumer
        # 1 match = 1 record in the database
        # send message to tournament consumer if applicable

    async def state_update(self, event):
        game_state = event['game_state']
        await self.send(text_data=json.dumps({
            'type': 'state_update',
            'game_state': game_state
        }))


    async def send_players_side(self):
        await self.channel_layer.send(
            self.players[0],
            {
                'type': 'your_side',
                'side': 'left'
            }
        )

        await self.channel_layer.send(
            self.players[1],
            {
                'type': 'your_side',
                'side': 'right'
            }
        )

    ### EVENTS - each Websocket sends message to frontend ###
    async def your_side(self, event):
        await self.send(text_data=json.dumps(event))