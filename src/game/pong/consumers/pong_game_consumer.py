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

# TODO: should be in the Pong class, no need to have that separate
# Problem: Pong class requires 2 players to be created, but we need to create it with 1 player
class Match:
    def __init__(self, channel_name):
        self.size = 1
        self.players = [channel_name]

    def add_player(self, channel_name):
        self.players.append(channel_name)
        self.size += 1

    def rem_player(self, channel_name):
        self.players.remove(channel_name)
        self.size -= 1

    def is_full(self):
        return self.size == 2

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
    running_games: Dict[str, Pong] = {}
    waiting_games: Dict[str, Match] = {}
    players = []

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
        
        # TODO: does the game consumer must be in the group? 
        # I could just send without him in the group, 
        # if only game consumer needs to send message to tournament
        

    async def disconnect(self, close_code):
        if self.in_game:
            # if the game was still running set other persons score to max
            pass
        else:
            waiting_game = PongGameConsumer.waiting_games.get(self.match_id)
            if waiting_game:
                waiting_game.rem_player(self.channel_name)
            
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
            self.game.change_player_direction(self.channel_name, text_data_json['move_to']) # maybe raise error if player_id is not in players !!! 
        elif type == 'connect_to_match':
            await self.connect_to_match(text_data_json)
        else:
            return
    

    def get_match_config(self):
        match = cache.get(self.match_id)
        if match is None:
            raise ValueError("SNH")
        return match

    async def connect_to_match(self, data):
        self.match_id = data.get('match_id')
        if self.match_id is None:
            raise ValueError("SNH - match_id is not provided")
        
        self.match_config = self.get_match_config()

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
        
        
        waiting_game = PongGameConsumer.waiting_games.get(self.match_id)
        if waiting_game is None:
            PongGameConsumer.waiting_games[self.match_id] = Match(self.channel_name)
        else:
            waiting_game.add_player(self.channel_name)
            
            # NOTE: in our case with only 2 players, this is alomost always true,
            # maybe except what happens if a 1 client joins and disconnects before the 2nd even joins
            if waiting_game.is_full(): 
                player1 = waiting_game.players[0]
                player2 = waiting_game.players[1]
                ptw     = self.match_config.get('points_to_win')
                if ptw is None:
                    ptw = 4
                
                pong = Pong(self.game_group, player1, player2, ptw)

                PongGameConsumer.running_games[self.match_id] = pong
                PongGameConsumer.waiting_games.pop(self.match_id)
                
                game_task = asyncio.create_task(pong.start_game_loop())

        
    def valid_match_id(self):
        """
        Checks if user provided correct match_id
        """
        
        allowed_user_ids = self.match_config.get('user_id_list')
        if allowed_user_ids is None:
            raise ValueError("SNH - cache must be set by matchmaking consumer or tournament consumer")
        for id in allowed_user_ids:
            if id == self.user_id:
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
        self.game = PongGameConsumer.running_games[self.match_id]
        if self.game is None:
            raise ValueError("Game not found")
        await self.send(text_data=json.dumps(event))


    async def state_update(self, event):
        await self.send(text_data=json.dumps(event))


    async def game_end(self, event):
        game = self.game
        if (game.player_l.id == self.channel_name and game.player_l.score == game.points_to_win) \
            or (game.player_r.id == self.channel_name and game.player_r.score == game.points_to_win):
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
        self.cleanup(event)
    

    async def cleanup(self, data):
        PongGameConsumer.running_games.pop(self.match_id, None) # removes the key if it exists, or do nothing if it does not, since N consumers try to do this
        cache.delete(self.match_id)
        if self.game_mode == GameMode.TOURNAMENT:
            await self.forward_match_result(data)
        else:
            self.close()

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
