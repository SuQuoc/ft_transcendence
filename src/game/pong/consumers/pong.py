import random # for old version of pong # maybe needed for ball in the new version (but i don't think so)!!
import json
import time # temporary !!
import math

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def calc_x(A: 'Vector', B: 'Vector', y) -> float:
        m = (B.y - A.y) / (B.x - A.x)
        return ((y - A.y) / m) + A.x
    
    @staticmethod
    def calc_y(A: 'Vector', B: 'Vector', x) -> float:
        m = (B.x - A.x) / (B.y - A.y)
        return ((x - A.x) / m) + A.y


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
        if self.move_to == -1 or self.move_to <= self.pos.y + self.speed / 2 and self.move_to >= self.pos.y - self.speed / 2:
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
        self.base_pos = Vector(pos_x, pos_y)    # first position the ball is in, currently used to reset the ball
        self.pos = Vector(pos_x, pos_y)     # position of the ball relative to the canvas
        self.vel = Vector(vel_x, vel_y)     # velocity (direction the ball moves | (0, 0) is ball.pos)
        self.size = size                    # width and height of the ball
        self.collision = 0      # used to keep track of how often the ball can move before it hits something
        self.speed = 11         # speed the ball moves at (is used to calculate vel)
    
    def move(self):
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y

    def in_range(self, angle) -> bool:
        """ Helper function for calc_vel.
            \n Returns True if the angle is too sharp or too flat, else False. """
        if self.vel.x > 0:
            if self.vel.y > 0:
                if angle < 30:
                    return True
                elif angle > 60:
                    return True
            else:
                if angle < 120:
                    return True
                elif angle > 150:
                    return True
        else:
            if self.vel.y < 0:
                if angle < 210:
                    return True
                elif angle > 240:
                    return True
            else:
                if angle < 300:
                    return True
                elif angle > 330:
                    return True
        return False

    def calc_vel(self, player: Player):
        """ Calculates new vel based on where the ball hits a player. """
        player_half = (player.height + self.size) / 2   # adding the ballsize because it bounces off even when only a pixel touches the player
        offset = (self.pos.y + (self.size / 2)) - player.pos.y - (self.size / 2)
        normalized_offset = (offset - player_half) / player_half

        # changing wether it adds or subtracts to the angle depending on which direction the ball comes from
        if self.vel.y < 0:
            normalized_offset *= -1

        # getting the current angle
        angle = math.atan2(self.vel.y, self.vel.x)
        # checking if the angle would be too sharp or too flat
        if self.in_range(math.degrees(abs(angle + (normalized_offset / 8)))):   # the 8 is an arbitrarily chosen number. it feels good when playing
            angle += (normalized_offset / 8)    # the 8 is an arbitrarily chosen number. it feels good when playing

        self.vel.x = self.speed * math.cos(angle)
        self.vel.y = self.speed * math.sin(angle)
        self.vel.x *= -1

    def reset(self):
        """ Resets the ball to it's base position. (The position passed when initializing it.) """
        self.pos.x = self.base_pos.x
        self.pos.y = self.base_pos.y
        self.vel = Vector(8, 8) # randomize direction ?!!!


class Pong:
    from channels.layers import get_channel_layer
    CHANNEL_LAYER = get_channel_layer()

    def __init__(self, channel_group, player_l, points_to_win=1):
        self.channel_group = channel_group # Messaging to Game Consumer
        self.size = 1
        self.running = False
        self.result = {}
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
        self.player_r: Player  =  None
        

    def add_player(self, player_r):
        self.player_r = Player(id = player_r,
                                pos_x = self.canvas_width - self.player_width - 10,
                                pos_y = self.canvas_height/2 - self.player_height/2,
                                width = self.player_width,
                                height = self.player_height,
                                speed = 10)
        self.size += 1
        
        
    def rem_player(self, player):
        if player == self.player_l.id:
            self.player_l = None
        elif player == self.player_r.id:
            self.player_r = None
        self.size -= 1


    def is_full(self):
        return self.size == 2
    

    def get_game_state(self):
        return {
            'ball_pos_x': self.ball.pos.x,
            'ball_pos_y': self.ball.pos.y,
            'player_l_y': self.player_l.pos.y,
            'player_r_y': self.player_r.pos.y,
            'score_l': self.player_l.score,
            'score_r': self.player_r.score,
        }


    def change_player_direction(self, player_id, move_to):
        """ Sets 'self.player_l.move_to' of the player with the right 'player_id' to 'move_to'. """
        if player_id == self.player_l.id:
            self.player_l.move_to = move_to
        elif player_id == self.player_r.id:
            self.player_r.move_to = move_to


    def player_scored(self) -> bool:
        """ Checks if a player scored. 
            \n Increases 'self.player_r.score' or 'self.player_l.score' by 1 if they scored.
            \n Returns 'True' if a player scored and 'False' if not. """
        if self.ball.pos.x < 0 or self.ball.pos.x > self.canvas_width: #if scored
            if self.ball.vel.x < 0:  # check if the right player scored
                self.player_r.score += 1
            else:                    # else the left player scored
                self.player_l.score += 1
            return True


    def get_player(self) -> Player:
        if self.ball.vel.x < 0:
            return self.player_l
        else:
            return self.player_r


    def collision_with_player(self, player: Player, ball_pos: Vector, x_vel: int) -> bool:
        """ Checks if the ball would hit (is on the same y as) a player. (Be careful, this doesn't check x).
            \n Returns 'True' if it does and 'False' if it doesn't. """
        if ball_pos.y + self.ball.size > player.pos.y and ball_pos.y < player.pos.y + player.height:
            return True
        return False


    def move_out_of_player(self, player: Player) -> Vector:
        """ Checks if the ball is in the player (only on the y axis) and if it is, it moves it out (again, only the y axis). 
            \n Returns the next_pos of the ball. """
        ball_top = self.ball.pos.y
        ball_bot = self.ball.pos.y + self.ball.size
        player_top = player.pos.y
        player_middle = player.pos.y + player.height / 2
        player_bot = player.pos.y + player.height

        if ball_bot > player_top and ball_bot < player_middle:
            self.ball.pos.y = player.pos.y - self.ball.size
        elif ball_top > player_middle and ball_top < player_bot:
            self.ball.pos.y = player_bot
        return Vector(self.ball.pos.x + self.ball.vel.x, self.ball.pos.y + self.ball.vel.y)


    def go_to_wall(self, pos: Vector, vel: Vector, wall: Vector) -> Vector:
        """ Calculates the position of the ball if it collides with a wall.
            \n wall.x should be the next wall on the x axis the ball could hit, the same with wall.y respectfully. 
            \n If this function calculates the collision on wall.x or wall.y depends on 'self.wall_to_be_hit. (self.wall_to_be_hit should be either set to 'x' or 'y'.)
            \n Returns the position of the ball where it collides with the closest wall. """
        B = Vector(pos.x + vel.x, pos.y + vel.y)

        if self.wall_to_be_hit == "x":
            next_pos = Vector(wall.x, Vector.calc_y(pos, B, wall.x))
            if next_pos.y < 0:
                next_pos.y = 0
            elif next_pos.y > self.canvas_height:
                next_pos.y = self.canvas_height
            return next_pos
        else:
            next_pos = Vector(Vector.calc_x(pos, B, wall.y), wall.y)
            if next_pos.x < 0:
                next_pos.x = 0
            elif next_pos.x > self.canvas_width:
                next_pos.x = self.canvas_width
            return next_pos
        

    def go_to_player_top_bottom(self, player: Player, pos: Vector, vel: Vector) -> Vector:
        """ Checks which edge of the player the ball is closer to.
            \n Returns the position where the ball should collide with the player. """
        B = Vector(pos.x + vel.x, pos.y + vel.y)

        top_edge_distance = player.pos.y - self.ball.size - self.ball.pos.y
        bot_edge_distance = player.pos.y + player.height - self.ball.pos.y
        if abs(top_edge_distance) < abs(bot_edge_distance):
            x = Vector.calc_x(pos, B, player.pos.y - self.ball.size)
            return Vector(x, player.pos.y - self.ball.size)
        else:
            x = Vector.calc_x(pos, B, player.pos.y + player.height)
            return Vector(x, player.pos.y + player.height)


    def calc_next_collision(self, pos: Vector, vel: Vector, wall) -> int:
        """ Calculates the next collision with wall.x and wall.y. Also sets self.wall_to_be_hit to either 'x' or 'y', depending on which wall will be hit first.
            \n Returns the amount of times the ball can move without hitting anything. """
        collision_x = (wall.x - pos.x) / vel.x
        collision_y = (wall.y - pos.y) / vel.y

        if (collision_x < collision_y):
            self.wall_to_be_hit = "x"
            return int(collision_x + 1) # the +1 is needed to compensate for the -1 at the beginning of the update_game_state() function
        else:
            self.wall_to_be_hit = "y"
            return int(collision_y + 1) # the +1 is needed to compensate for the -1 at the beginning of the update_game_state() function


    def get_wall(self, vel: Vector) -> Vector:
        """Returns a Vector with the x (left or right) and y (top or bottom) wall values that could be hit depending on the ball velocity."""
        if vel.x > 0 and vel.y > 0:
            return Vector(self.player_r.pos.x - self.ball.size, self.canvas_height - self.ball.size)
        elif vel.x < 0 and vel.y > 0:
            return Vector(self.player_l.pos.x + self.player_width, self.canvas_height - self.ball.size)
        elif vel.x < 0 and vel.y < 0:
            return Vector(self.player_l.pos.x + self.player_width, 0)
        else:
            return Vector(self.player_r.pos.x - self.ball.size, 0)


    def update_game_state(self):
        #start_time = time.time()
        next_pos = Vector(self.ball.pos.x + self.ball.vel.x, self.ball.pos.y + self.ball.vel.y)

        # move players
        self.player_l.move(self.canvas_height)
        self.player_r.move(self.canvas_height)
        self.collision -= 1

        if self.collision == 0:
            wall = self.get_wall(self.ball.vel)
            if self.wall_to_be_hit == "y": # if hit top or bottom wall
                next_pos = self.go_to_wall(self.ball.pos, self.ball.vel, wall)
                self.ball.vel.y *= -1
                wall = self.get_wall(self.ball.vel)
                self.collision = self.calc_next_collision(next_pos, self.ball.vel, wall)

            else: # if going into player lane
                if self.collision_with_player(self.get_player(), next_pos, self.ball.vel.x):
                    next_pos = self.go_to_wall(self.ball.pos, self.ball.vel, wall)
                    self.ball.calc_vel(self.get_player()) # calculate new vel
                    wall = self.get_wall(self.ball.vel)
                    self.collision = self.calc_next_collision(next_pos, self.ball.vel, wall)
                else: # moving in the player lane without hitting player
                    self.collision -= 1 # decrementing collision so we know we are in a player lane

        if self.collision < 0:
            # checking player top and bottom collision
            player = self.get_player()
            next_pos = self.move_out_of_player(player) # checks if the player moved into the ball and if it did, it moves the ball out
            if self.collision_with_player(player, next_pos, self.ball.vel.x):
                next_pos = self.go_to_player_top_bottom(player, self.ball.pos, self.ball.vel)
                self.ball.vel.y *= -1

            if self.player_scored():
                self.ball.reset()
                ### maybe put this in a function and or make it more variable ###
                self.wall_to_be_hit = "y" # !!
                wall = self.get_wall(self.ball.vel)
                self.collision = self.calc_next_collision(self.ball.pos, self.ball.vel, wall)
                ################
                return
            
        # move ball
        self.ball.pos.x = next_pos.x
        self.ball.pos.y = next_pos.y
        #print(f"calculation time: {time.time() - start_time}")


    async def start_game_loop(self):
        import time     #!!
        import asyncio  #!!
        
        if not self.is_full():
            raise Exception("Not enough players to start game")
        
        self.wall_to_be_hit = "y" # !!
        wall = self.get_wall(self.ball.vel)
        self.collision = self.calc_next_collision(self.ball.pos, self.ball.vel, wall)
        
        self.running = True # NOTE: check if needed at the end of project
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
            #print(f"one tick: {time.time() - start_time}")
            start_time = time.time()
            self.update_game_state()

            game_state = self.get_game_state()
            await self.send_state_update(game_state)
            if self.game_over():
                break
            await asyncio.sleep(tick_duration - (time.time() - start_time))
        
        print("end of game loop")
        self.set_result()
        await self.save_game_to_db()
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

    def set_result(self):
        if self.player_l.score == self.points_to_win:
            self.result['winner'] = self.player_l.id
            self.result['winner_score'] = self.player_l.score
            self.result['loser'] = self.player_r.id
            self.result['loser_score'] = self.player_r.score
        else:
            self.result['winner'] = self.player_r.id
            self.result['winner_score'] = self.player_r.score
            self.result['loser'] = self.player_l.id
            self.result['loser_score'] = self.player_l.score

    async def save_game_to_db(self):
        from asgiref.sync import sync_to_async
        from pong.models import MatchRecord

        await sync_to_async(MatchRecord.objects.create)(**self.result)

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