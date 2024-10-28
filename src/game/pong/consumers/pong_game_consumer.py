import json
import time
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .pong import Pong


class PongGameConsumer(AsyncWebsocketConsumer):
    game_instance = None
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

        # count down
        for count in [5, 4, 3, 2, 1, 0]:
            await self.send_count_down(count)
            await asyncio.sleep(1)
        # send initial state again, so the ball is in the right position
        await self.send_initial_state(PongGameConsumer.game_instance.get_game_state())
        # game loop
        while True:
            start_time = time.time()
            PongGameConsumer.game_instance.update_game_state()

            game_state = PongGameConsumer.game_instance.get_game_state()
            await self.send_state_update(game_state)
            if game_state['score_l'] == points_to_win or game_state['score_r'] == points_to_win:
                # send game end info to client
                break
            await asyncio.sleep(tick_duration - (time.time() - start_time))
        print("end of game loop")
        await self.send_game_end()
        


###### sending #######
    async def send_count_down(self, count):
        await self.channel_layer.group_send(
            self.game_group,
            {
                'type': 'count_down',
                'count': count
            }
        )


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
    async def count_down(self, event):
        await self.send(text_data=json.dumps(event))


    async def initial_state(self, event):
        await self.send(text_data=json.dumps(event))


    async def state_update(self, event):
        await self.send(text_data=json.dumps(event))


    async def game_end(self, event):
        await self.send(text_data=json.dumps(event))
