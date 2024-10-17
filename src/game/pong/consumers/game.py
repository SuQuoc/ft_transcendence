

from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
import json


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
class Ball:
    def __init__(self, pos_x, pos_y, vel_y, vel_x, size):
        self.pos = Vector(pos_x, pos_y)
        self.vel = Vector(vel_x, vel_y)
        self.size = size

class Player:
    def __init__ (self, pos_x, pos_y, width, height):
        self.pos = Vector(pos_x, pos_y)
        self.width = width
        self.height = height


def check_player_collision(ball: Ball, player1: Player, player2: Player):
    if ball.pos.x <= player1.pos.x:
        if ball.pos.y + ball.size < player1.pos.y or ball.pos.y > player1.pos.y + player1.height:
            ball.vel.x *= -1 
    elif ball.pos.x + ball.size >= player2.pos.x:
        if ball.pos.y + ball.size < player2.pos.y or ball.pos.y > player2.pos.y + player2.height:
            ball.vel.x *= -1

def start_game():
    canvas_width = 1000
    canvas_height = 600
    player_width = 10
    player_height = 60

    ball = Ball(canvas_width/2, canvas_height/2, 5, 5, 10)
    player1 = Player(player_width + 10, canvas_height/2 - player_height/2, player_width, player_height)
    player2 = Player(canvas_width - player_width - 10, canvas_height/2 - player_height/2, player_width, player_height)
    score1 = 0
    score2 = 0

    while score1 < 5 and score2 < 5:
        ball.pos.x += ball.vel.x
        ball.pos.y += ball.vel.y

        # reflect ball if it hits the top or bottom of canvas
        if ball.pos.y < 0 or ball.pos.y + ball.size > canvas_height:
            ball.vel.y *= -1
        # check if players scored
        if ball.pos.y < 0:
            score1 += 1
        if ball.pos.y + ball.size > canvas_height:
            score2 += 1
        
        # check collision with players
        check_player_collision(ball, player1, player2)

        if ball.pos.x < 0:
            score2 += 1
            ball = Ball(canvas_width/2, canvas_height/2, 5, 5, 10)
        elif ball.pos.x > canvas_width:
            score1 += 1
            ball = Ball(canvas_width/2, canvas_height/2, 5, 5, 10)

        # Check collision with player1
        if ball.pos.x < player1.pos.x + player1.width and ball.pos.y > player1.pos.y and ball.pos.y < player1.pos.y + player1.height:
            ball.vel.x *= -1

        # Check collision with player2
        if ball.pos.x > player2.pos.x - player2.width and ball.pos.y > player2.pos.y and ball.pos.y < player2.pos.y + player2.height:
            ball.vel.x *= -1

        await asyncio.sleep(0.1)

        # Send the new position of the ball and the players to the clients
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'send_position',
                'ball': ball.__dict__,
                'player1': player1.__dict__,
                'player2': player2.__dict__,
                'score1': score1,
                'score2': score2
            }
        )



class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs'].get('game_id')
        self.group_name = f"game_{self.game_id}"


        game = Game.objects.filter(id=self.game_id).first()
        await self.accept()

    async def disconnect(self):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, json_data):
        dict_data = json.loads(json_data)
        type = dict_data['type']

        if type == 'move':


        #await self.send(json_data=json.dumps({
        #    'message': message
        #}))