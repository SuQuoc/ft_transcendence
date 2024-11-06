import random # for old version of pong # maybe needed for ball in the new version (but i don't think so)!!
import json

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Player:
    def __init__ (self, id, pos_x, pos_y, width, height, speed):
        self.id = id
        self.pos = Vector(pos_x, pos_y)
        self.width = width
        self.height = height
        self.speed = speed
        self.score = 0
        self.move_to = -1

    def move(self, max_height):
        if self.move_to == -1 or self.move_to <= self.pos.y + self.speed / 2 and self.move_to >= self.pos.y - self.speed / 2 :
            return
        if self.pos.y > self.move_to:
            self.pos.y -= self.speed
            if self.pos.y < 0:
                self.pos.y = 0
        elif self.pos.y < self.move_to:
            self.pos.y += self.speed
            if self.pos.y + self.height > max_height:
                self.pos.y = max_height - self.height


class Ball:
    def __init__(self, pos_x, pos_y, vel_y, vel_x, size):
        self.base_pos = Vector(pos_x, pos_y)
        self.pos = Vector(pos_x, pos_y)
        self.vel = Vector(vel_x, vel_y)
        self.size = size
    
    def move(self):
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y


    def check_wall_collision(self, canvas_height):
        """ reflect ball if it hits the top or bottom of canvas """
        if self.pos.y <= 0:
            self.pos.y = 0
            self.vel.y *= -1
        if self.pos.y + self.size >= canvas_height:
            self.pos.y = canvas_height - self.size
            self.vel.y *= -1
        

    def check_player_collision(self, player_l: Player, player_r: Player):
        """ reflect ball if it hits a player """
        if self.pos.x <= player_l.pos.x + player_l.width:
            if self.pos.y + self.size > player_l.pos.y and self.pos.y < player_l.pos.y + player_l.height:
                self.pos.x = player_l.pos.x + player_l.width
                self.vel.x *= -1
        elif self.pos.x + self.size >= player_r.pos.x:
            if self.pos.y + self.size > player_r.pos.y and self.pos.y < player_r.pos.y + player_r.height:
                self.pos.x = player_r.pos.x - self.size
                self.vel.x *= -1

        # this doesn't work because we don't know what sides were crossed
        """  if bx < px + pw
                # checking if the ball is in the upper half of the player
                if by + bs >= py and by <= py + ph / 2
                    by = py - bs
                    bvy *= -1
                # checking if the ball is in the lower half of the player
                elif by + bs >= py + ph / 2 and by <= py + ph
                    by = py + ph
                    bvy *= -1
        """


    def reset(self):
        self.pos.x = self.base_pos.x
        self.pos.y = self.base_pos.y
        self.vel = Vector(8, 8) # randomize direction ?!!!


class Pong:
    from channels.layers import get_channel_layer
    CHANNEL_LAYER = get_channel_layer()

    def __init__(self, channel_group, player_l, player_r, points_to_win=1):
        self.channel_group = channel_group # Messaging to Game Consumer

        self.points_to_win = points_to_win

        self.canvas_width = 1000
        self.canvas_height = 600
        self.player_width = 10
        self.player_height = 60

        self.ball = Ball(self.canvas_width/2 - 5, self.canvas_height/2 - 5, 8, 8, 10)
        self.player_l: Player = Player(id = player_l,
                                        pos_x = 10,
                                        pos_y = self.canvas_height/2 - self.player_height/2,
                                        width = self.player_width,
                                        height = self.player_height,
                                        speed = 10)
        self.player_r: Player  =  Player(id = player_r,
                                        pos_x = self.canvas_width - self.player_width - 10,
                                        pos_y = self.canvas_height/2 - self.player_height/2,
                                        width = self.player_width,
                                        height = self.player_height,
                                        speed = 10)


    def get_game_state(self):
        return {
            'ball_pos_x': self.ball.pos.x,
            'ball_pos_y': self.ball.pos.y,
            'player_l_y': self.player_l.pos.y,
            'player_r_y': self.player_r.pos.y,
            'score_l': self.player_l.score,
            'score_r': self.player_r.score,
        }


    def check_if_scored(self, ball: Ball, canvas_width):
        """ checks if ball is out of bounds and updates score """
        if ball.pos.x < 0:
            self.player_r.score += 1
            ball.reset()
        if ball.pos.x > canvas_width:
            self.player_l.score += 1
            ball.reset()


    def change_player_direction(self, player_id, move_to):
        if player_id == self.player_l.id:
            self.player_l.move_to = move_to
        elif player_id == self.player_r.id:
            self.player_r.move_to = move_to


    def update_game_state(self):
        self.ball.move()
        self.player_l.move(self.canvas_height)
        self.player_r.move(self.canvas_height)

        self.ball.check_player_collision(self.player_l, self.player_r)
        self.ball.check_wall_collision(self.canvas_height)
        self.check_if_scored(self.ball, self.canvas_width)


    async def save_game_to_db(self):
        from asgiref.sync import sync_to_async
        from pong.models import MatchRecord

        winner_id = None
        loser_id = None
        winner_score = None
        loser_score = None
        await sync_to_async(MatchRecord.objects.create)(
            winner          = winner_id,
            loser           = loser_id,
            winner_score    = winner_score,
            loser_score     = loser_score)

    async def start_game_loop(self):
        import time
        import asyncio
        # needs only the group_name to message all the clients in the group
        tick_duration = 0.03
        start_time = time.time()

        # count down
        for count in [5, 4, 3, 2, 1, 0]:
            await self.send_count_down(count)
            await asyncio.sleep(1)
        # send initial state again, so the ball is in the right position
        await self.send_initial_state(self.get_game_state())
        # game loop
        while True:
            start_time = time.time()
            self.update_game_state()

            game_state = self.get_game_state()
            await self.send_state_update(game_state)
            if self.game_over():
                break
            await asyncio.sleep(tick_duration - (time.time() - start_time))
        
        
        print("end of game loop")
        # save game to db()
        await self.send_game_end()

    def game_over(self):
        if self.player_l.score == self.points_to_win or self.player_r.score == self.points_to_win:
            return True
        return False
    
    
    # Sending messages to the Game Consumer
    async def send_count_down(self, count):
        await Pong.CHANNEL_LAYER.group_send(
            self.channel_group,
            {
                'type': 'count_down',
                'count': count
            }
        )


    async def send_initial_state(self, game_state):
        await Pong.CHANNEL_LAYER.group_send(
            self.channel_group,
            {
                'type': 'initial_state',
                'game_state': game_state
            }
        )
    
    async def send_state_update(self, game_state):
        await Pong.CHANNEL_LAYER.group_send(
            self.channel_group,
            {
                'type': 'state_update',
                'game_state': game_state
            }
        )

    async def send_game_end(self):
        await Pong.CHANNEL_LAYER.group_send(
            self.channel_group,
            {
                'type': 'game_end',
                "winner": "winner",
                "loser": "loser"
            })