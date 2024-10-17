class Pong:
    def __init__(self, player_l, player_r):
        self.player_l = player_l
        self.player_r = player_r
        self.canvas_width = 1000
        self.canvas_height = 600
        self.paddle_size = 100
        self.ball_size = 20
        self.paddle_speed = 5
        self.ball_speed = 5
        
        self.score_l = 0
        self.score_r = 0
        self.points_to_win = 5
        self.reset_game()

    def reset_game(self):
        self.player_l_y = self.canvas_height // 2
        self.player_r_y = self.canvas_height // 2
        self.ball_x = self.canvas_width // 2
        self.ball_y = self.canvas_height // 2
        self.ball_dx = random.choice([-self.ball_speed, self.ball_speed])
        self.ball_dy = random.choice([-self.ball_speed, self.ball_speed])
       

    def update_game_state(self):
        # Update player positions
        self.player_l_y = max(0, min(self.canvas_height - self.paddle_size, self.player_l_y))
        self.player_r_y = max(0, min(self.canvas_height - self.paddle_size, self.player_r_y))

        # Update ball position
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        # Ball collision with top and bottom
        if self.ball_y <= 0 or self.ball_y >= self.canvas_height - self.ball_size:
            self.ball_dy *= -1

        # Ball collision with paddles
        if self.ball_x <= self.paddle_size and self.player_l_y <= self.ball_y <= self.player_l_y + self.paddle_size:
            self.ball_dx *= -1
        elif self.ball_x >= self.canvas_width - self.paddle_size - self.ball_size and self.player_r_y <= self.ball_y <= self.player_r_y + self.paddle_size:
            self.ball_dx *= -1

        # Ball out of bounds
        if self.ball_x <= 0:
            self.score_r += 1
            self.reset_ball()
        elif self.ball_x >= self.canvas_width - self.ball_size:
            self.score_l += 1
            self.reset_ball()

    def reset_ball(self):
        self.ball_x = self.canvas_width // 2
        self.ball_y = self.canvas_height // 2
        self.ball_dx = random.choice([-self.ball_speed, self.ball_speed])
        self.ball_dy = random.choice([-self.ball_speed, self.ball_speed])

    def get_game_state(self):
        return {
            'player_l_y': self.player_l_y,
            'player_r_y': self.player_r_y,
            'ball_x': self.ball_x,
            'ball_y': self.ball_y,
            'score_l': self.score_l,
            'score_r': self.score_r
        }
    


import json
import random
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .pong import Pong

class PongGameConsumer(AsyncWebsocketConsumer):
    game_instance = None
    #game_loop_running = False
    
    players = []
    
    async def connect(self):
        print(f"GameConsumer - connect")

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
            #PongGameConsumer.game_loop_running = True
            asyncio.create_task(self.game_loop())



    async def disconnect(self, close_code):
        print(f"GameConsumer - disconnect")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await super().disconnect(close_code)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        type = text_data_json['type']
        
        print(f"GameConsumer - receive:")
        print(json.dumps(text_data))
        print("\n")

        if type == 'up':
            direction = -1
        elif type == 'down':
            direction = 1
        else:
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
                self.room_group_name,
                {
                    'type': 'state_update',
                    'game_state': game_state
                }
            )
            if game_state['score_l'] == PongGameConsumer.game_instance.points_to_win or game_state['score_r'] == PongGameConsumer.game_instance.points_to_win:
                break

            await asyncio.sleep(0.05)  # Update the game state every 50ms

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

