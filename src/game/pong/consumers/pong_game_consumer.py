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
        self.mode = None
        self.user_id = None
        self.client_group = None
        self.game_group = None
        self.game = None
        self.in_game = False
    
    def set_instance_values(self):
        #print(f"GameConsumer - connect")
        # token = self.scope["cookies"]["access"]
        self.user_id = self.scope["user_id"]
        self.client_group = f"client_{self.user_id}"
        print(f"GAME CONSUMER client group: {self.client_group}")

        self.match_id = self.scope['url_route']['kwargs']['match_id']
        self.game_group = f'game_{self.match_id}'

        url_path = self.scope['path']
        print(f"url_path: {url_path}")
        if '/daphne/tournaments/' in url_path:
            self.mode = GameMode.TOURNAMENT

    async def connect(self):
        self.set_instance_values()

        if not self.valid_user_id():
            await self.send_error() # should i accept the connection just to inform client that his id is invalid?
            return

        await self.accept()
        await self.channel_layer.group_add(self.client_group, self.channel_name)
        await self.channel_layer.group_add(self.game_group, self.channel_name) # must be here since EACH consumer instance has unique channel_name, regardless if same client connects to N consumers

        await self.channel_layer.group_send(
            self.client_group,
            {
                "type": "test",
            })
        
        waiting_game = PongGameConsumer.waiting_games[self.match_id]
        if waiting_game is None:
            PongGameConsumer.waiting_games[self.match_id] = Match(self.channel_name)
        else:
            waiting_game.add_player(self.channel_name)
            
        if waiting_game.is_full():
            player1 = waiting_game.players[0]
            player2 = waiting_game.players[1]
            pong = Pong(player1, player2, points_to_win=1)

            PongGameConsumer.running_games[self.match_id] = pong
            PongGameConsumer.waiting_games.pop(self.match_id)

            await self.send_initial_state(pong.get_game_state())
            # self.players.remove(self.players[0])
            # self.players.remove(self.players[0])

            game_task = asyncio.create_task(self.game_loop())
            # NOTE: should also work with as a class method or any other method? doesnt need to be an instance method
            
            cache.delete(self.match_id)


    async def disconnect(self, close_code):
        #print(f"GameConsumer - disconnect")
        
        if self.in_game:
            # if the game was still running the other person wins

            pass
        else:
            waiting_game = PongGameConsumer.waiting_games[self.match_id]
            if waiting_game:
                waiting_game.rem_player(self.channel_name)


        # TODO: check if still needed
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
            if PongGameConsumer.running_games is None:
                return
            # changing the direction of the player that sent the message
            PongGameConsumer.running_games.change_player_direction(self.channel_name, text_data_json['move_to']) # maybe raise error if player_id is not in players !!! 
        else:
            return

        
    async def game_loop(self):
        points_to_win = PongGameConsumer.running_games.points_to_win
        tick_duration = 0.03
        start_time = time.time()

        while True:
            start_time = time.time()
            PongGameConsumer.running_games.update_game_state()

            game_state = PongGameConsumer.running_games.get_game_state()
            await self.send_state_update(game_state)
            if game_state['score_l'] == points_to_win or game_state['score_r'] == points_to_win:
                # send game end info to client
                break
            await asyncio.sleep(tick_duration - (time.time() - start_time))
        
        print("end of game loop")
        await self.send_game_end()            
        
        # NOTE: dont send THIS TO FRONTEND
        # if is_tournament:
        await self.channel_layer.group_send(
            self.game_group,
            {
                "type": "forward_match_result",
                "winner": "winner", 
                "loser": "loser",
                "winner_score": "winner_score",
                "loser_score": "loser_score"
            })
        print("end of game loop function !!!")
        # TODO: 
        # save the result of the game in the database - must be done in a task and not in consumer
        # 1 match = 1 record in the database
        
    def valid_user_id(self):
        allowed_user_ids = cache.get(self.match_id)
        if allowed_user_ids is None:
            raise ValueError("SNH - cache must be set by matchmaking or user_id")
        for id in allowed_user_ids:
            if id == self.user_id:
                return True
        return False

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
        game = PongGameConsumer.running_games

        # inform client about the result
        if (game.player_l.id == self.channel_name and game.player_l.score == game.points_to_win) \
            or (game.player_r.id == self.channel_name and game.player_r.score == game.points_to_win):
            await self.send(json.dumps(
                {
                    'type': 'game_end',
                    'status': "won"
                }
            ))
        else:
            await self.send(json.dumps(
                {
                    'type': 'game_end',
                    'status': "lost"
                }
            ))

        # cleanup the game in backend
        await self.channel_layer.group_send(
            self.game_group,
            {
                'type': Type.CLEANUP.value
            }
        )

    async def send_error(self):
        await self.send(json.dumps(
            {
                'type': 'error',
                'message': 'Invalid user id'
            }
        ))

    ### EVENTS - each Websocket sends message to frontend ###
    async def initial_state(self, event):
        self.in_game = True
        self.game = PongGameConsumer.running_games[self.match_id]
        if self.game is None:
            raise ValueError("Game not found")
        await self.send(text_data=json.dumps(event))


    async def state_update(self, event):
        await self.send(text_data=json.dumps(event))


    # EVENTS - no message to frontend
    async def test(self, event):
        print("Game consumer test event")
        pass
    
    async def cleanup(self, event):
        PongGameConsumer.running_games.pop(self.match_id) # removes the key if it exists, or do nothing if it does not
        if self.mode == GameMode.TOURNAMENT:
            await self.forward_match_result(event)
        
        self.close()

    async def forward_match_result(self, event):
        print("forward_match_result")
        await self.channel_layer.group_send(
            self.client_group,
            {
                'type': 'match_result',
                'winner': event['winner'],
                'loser': event['loser'],
                #'winner_score': event['winner_score'],
                #'loser_score': event['loser_score']
            })
    
    async def match_result(self, event):
        print("match_result in game consumer")
        pass
