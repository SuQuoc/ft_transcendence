import json
import time
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .pong import Pong
from enum import Enum
from .utils import get_user_id_from_jwt
from django.core.cache import cache 
from .Room import Player
from typing import Dict

class GameMode(Enum):
    NORMAL = 'normal'
    TOURNAMENT = 'tournament'


class Type(Enum):
    MOVE = 'move'
    INITIAL_STATE = 'initial_state'
    STATE_UPDATE = 'state_update'
    GAME_END = 'game_end'
    ERROR = 'error'
    TEST = 'test'
    CLEANUP = 'cleanup'


class PongGameConsumer(AsyncWebsocketConsumer):
    all_games: Dict[str, Pong] = {}

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user_id = None
        
        self.client_group = None
        self.game_group = None

        self.match_id = None
        self.match_config = None
        self.game = None
        self.in_game = False
    
    def set_instance_values(self):
        self.user_id = self.scope["user_id"]
        
    async def connect(self):
        self.set_instance_values()
        await self.accept()
        
    async def disconnect(self, close_code):
        """ if not self.in_game: 
            game = PongGameConsumer.all_games.get(self.match_id)
            if game:
                game.rem_player(self.user_id) """
            
        if self.game_group:
            await self.channel_layer.group_discard(
                self.game_group,
                self.channel_name
            )

        if self.client_group:
            await self.channel_layer.group_discard(
                self.client_group, 
                self.channel_name
            )

        await super().disconnect(close_code)


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        type = text_data_json['type']

        if type == 'move':
            if self.game is None:
                return
            # changing the direction of the player that sent the message
            self.game.change_player_direction(self.user_id, text_data_json['move_to']) # maybe raise error if player_id is not in players !!! 
        elif type == 'connect_to_match':
            await self.connect_to_match(text_data_json)
        else:
            return
    

   
    async def connect_to_match(self, data):
        self.match_id = data.get('match_id')
        
        if not self.valid_match_id():
            await self.send_error()
            return
        
        self.game_mode = self.match_config.get('game_mode')
        """ if self.game_mode == GameMode.TOURNAMENT:
            print("GameConsumer: GAME MODE=TOURNAMENT")
            self.client_group = f"client_{self.user_id}"
            await self.channel_layer.group_add(self.client_group, self.channel_name) """ 
    
        self.game_group = f'game_{self.match_id}'
        await self.channel_layer.group_add(self.game_group, self.channel_name) # must be here since EACH consumer instance has unique channel_name, regardless if same client connects to N consumers
        
        
        game = PongGameConsumer.all_games.get(self.match_id)
        if game is None:
            ptw = self.match_config.get('points_to_win')
            if ptw is None:
                    ptw = 4
            PongGameConsumer.all_games[self.match_id] = Pong(self.game_group, self.user_id, ptw)
        else:
            game.add_player(self.user_id)
            
            # NOTE: in our case with only 2 players, this is almost always true,
            # maybe except what happens if a 1 client joins and disconnects before the 2nd even joins
            if game.is_full():                 
                game_task = asyncio.create_task(game.start_game_loop())
                callback_match_id = self.match_id # NOTE: just to ensure that the id stays the same NO MATTER WHAT
                game_task.add_done_callback(lambda t: self.cleanup(callback_match_id))


    async def reconnect_to_match(self, data):
        self.match_id = data.get('match_id')
        if not self.valid_match_id():
            await self.send_error()
            return

        self.game_group = f'game_{self.match_id}'
        await self.channel_layer.group_add(self.game_group, self.channel_name)


    def valid_match_id(self):
        """
        Checks provided match_id and sets self.match_config if valid
        """
        if self.match_id is None:
            return False
        
        match_config = cache.get(self.match_id)
        if match_config is None:
            return False

        allowed_user_ids = match_config.get('user_id_list')
        if allowed_user_ids is None:
            raise ValueError("SNH - cache must be set by matchmaking consumer or tournament consumer")
            return False
        for id in allowed_user_ids:
            if id == self.user_id:
                self.match_config = match_config
                return True
        return False


    async def send_error(self):
        await self.send(json.dumps(
            {
                'type': 'error',
                'message': 'Invalid match_id'
            }
        ))

    ### EVENTS - each Websocket sends message to frontend ###
    async def count_down(self, event):
        await self.send(text_data=json.dumps(event))


    async def initial_state(self, event):
        self.in_game = True
        self.game = PongGameConsumer.all_games[self.match_id]
        if self.game is None:
            raise ValueError("Game not found")
        await self.send(text_data=json.dumps(event))


    async def state_update(self, event):
        await self.send(text_data=json.dumps(event))


    async def game_end(self, event):
        game = self.game
        if (game.player_l.id == self.user_id and game.player_l.score == game.points_to_win) \
            or (game.player_r.id == self.user_id and game.player_r.score == game.points_to_win):
            await self.send(text_data=json.dumps(
                {
                    'type': 'game_end',
                    'status': "lost"
                }
            ))
        else:
            await self.send(text_data=json.dumps(
                {
                    'type': 'game_end',
                    'status': "won"
                }
            ))
        # self.cleanup(event)
    

    async def cleanup(self, data):
        PongGameConsumer.all_games.pop(self.match_id, None) # removes the key if it exists, or do nothing if it does not, since N consumers try to do this
        cache.delete(self.match_id)
        if self.game_mode == GameMode.TOURNAMENT:
            # NOTE: if parent-method is called via task callback, 
            # no duplicate messages will be sent to tournament consumer
            await self.forward_match_result(data)
        else:
            self.close(1000)

    ### EVENTS - Communication with other consumer
    async def forward_match_result(self, event):
        print("forward_match_result")

        client_group = f"client_{self.user_id}"
        await self.channel_layer.group_send(
            client_group,
            {
                'type': 'match_result',
                'winner': event['winner'],
                'loser': event['loser'],
                'winner_score': event['winner_score'],
                'loser_score': event['loser_score']
            }
        )
