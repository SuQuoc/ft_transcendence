

import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .pong import Pong







class PongGameConsumer(AsyncWebsocketConsumer):
    game_instance = None
    #game_loop_running = False
    
    players = []
    
    async def connect(self):
        #print(f"GameConsumer - connect")

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.game_group = f'game_{self.room_name}'
        
        await self.accept()
        await self.channel_layer.group_add(
                self.game_group,
                self.channel_name
        )

        self.players.append(self.channel_name)
        if len(self.players) == 2:
            PongGameConsumer.game_instance = Pong(self.players[0], self.players[1], points_to_win=5)
            await self.send_players_side()
            self.players.remove(self.players[0])
            self.players.remove(self.players[0])

            #PongGameConsumer.game_loop_running = True
            asyncio.create_task(self.game_loop())



    async def disconnect(self, close_code):
        #print(f"GameConsumer - disconnect")
        if self.channel_name in self.players:
            self.players.remove(self.channel_name)
        await self.channel_layer.group_discard(
            self.game_group,
            self.channel_name
        )
        await super().disconnect(close_code)


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        type = text_data_json['type']

        if type == 'up' or type == 'down' or type == 'stop':
            print(f"received: {type}")
            if PongGameConsumer.game_instance is None:
                return
            # changing the direction of the player that sent the message
            PongGameConsumer.game_instance.change_player_direction(self.channel_name, type) # maybe raise error if player_id is not in players !!!
        else:
            return

        
    async def game_loop(self):
        points_to_win = PongGameConsumer.game_instance.points_to_win
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
            if game_state['score_l'] == points_to_win or game_state['score_r'] == points_to_win:
                # send game end info to client
                break

            await asyncio.sleep(0.03)  # Update the game state every 50ms


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






""" class PongGameConsumer(AsyncWebsocketConsumer):
    game_instance = None
    #game_loop_running = False
    
    players = []
    
    async def connect(self):
        #print(f"GameConsumer - connect")

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.game_group = f'game_{self.room_name}'
        
        await self.accept()
        await self.channel_layer.group_add(
                self.game_group,
                self.channel_name
        )

        self.players.append(self.channel_name)
        if len(self.players) == 2:
            PongGameConsumer.game_instance = Pong(self.players[0], self.players[1])
            await self.send_players_side()
            self.players.remove(self.players[0])
            self.players.remove(self.players[0])

            #PongGameConsumer.game_loop_running = True
            asyncio.create_task(self.game_loop())



    async def disconnect(self, close_code):
        #print(f"GameConsumer - disconnect")
        self.players.remove(self.channel_name)
        await self.channel_layer.group_discard(
            self.game_group,
            self.channel_name
        )
        await super().disconnect(close_code)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        type = text_data_json['type']

        if type == 'up':
            direction = -1
        elif type == 'down':
            direction = 1
        else:
            return

        if PongGameConsumer.game_instance is None:
            return
        
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

            await asyncio.sleep(0.03)  # Update the game state every 50ms


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
 """