import json
import time
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
            PongGameConsumer.game_instance = Pong(self.players[0], self.players[1], points_to_win=1)
            #await self.send_players_side()
            await self.send_initial_state(PongGameConsumer.game_instance.get_game_state())
            self.players.remove(self.players[0])
            self.players.remove(self.players[0])

            #PongGameConsumer.game_loop_running = True
            asyncio.create_task(self.game_loop())



    async def disconnect(self, close_code):
        #print(f"GameConsumer - disconnect")
        if self.channel_name in self.players:
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

        if type == 'move':
            if PongGameConsumer.game_instance is None:
                return
            # changing the direction of the player that sent the message
            PongGameConsumer.game_instance.change_player_direction(self.channel_name, text_data_json['move_to']) # maybe raise error if player_id is not in players !!! 
        else:
            return

        
    async def game_loop(self):
        points_to_win = PongGameConsumer.game_instance.points_to_win
        tick_duration = 0.03
        start_time = time.time()

        while True:
            start_time = time.time()
            PongGameConsumer.game_instance.update_game_state()

            game_state = PongGameConsumer.game_instance.get_game_state()
            await self.send_state_update(game_state)
            if game_state['score_l'] == points_to_win or game_state['score_r'] == points_to_win:
                # send game end info to client
                break
            await asyncio.sleep(tick_duration - (time.time() - start_time))  # Update the game state every 50ms
        print("end of game loop")
        await self.send_game_end()
        # TODO: 
        # save the result of the game in the database - must be done in a task and not in consumer
        # 1 match = 1 record in the database
        # send message to tournament consumer if applicable

        





###### sending #######
    async def send_initial_state(self, game_state):
        await self.channel_layer.group_send(
            self.game_group,
            {
                'type': 'initial_state',
                'game_state': game_state
            }
        )
            
    
    async def send_state_update(self, game_state):
        await self.channel_layer.group_send(
            self.game_group,
            {
                'type': 'state_update',
                'game_state': game_state
            }
        )


    async def send_game_end(self):
        await self.channel_layer.group_send(
            self.game_group,
            {
                'type': 'game_end'
            }
        )

    ### EVENTS - each Websocket sends message to frontend ###
    async def initial_state(self, event):
        await self.send(text_data=json.dumps(event))


    async def state_update(self, event):
        await self.send(text_data=json.dumps(event))


    async def game_end(self, event):
        await self.send(text_data=json.dumps(event))
