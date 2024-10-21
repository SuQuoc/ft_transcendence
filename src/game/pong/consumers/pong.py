import random # for old version of pong # maybe needed for ball in the new version (but i don't think so)!!


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
class Ball:
    def __init__(self, pos_x, pos_y, vel_y, vel_x, size):
        self.base_pos = Vector(pos_x, pos_y)
        self.pos = Vector(pos_x, pos_y)
        self.vel = Vector(vel_x, vel_y)
        self.size = size
    
    def move(self):
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y

    def reset(self):
        self.pos.x = self.base_pos.x # need to do it like this so it is a copy
        self.pos.y = self.base_pos.y
        self.vel = Vector(5, 5) # randomize direction ?!!!

class Player:
    def __init__ (self, id, pos_x, pos_y, width, height, speed):
        self.id = id
        self.pos = Vector(pos_x, pos_y)
        self.width = width
        self.height = height
        self.speed = speed
        self.score = 0
        self.dir = "stop"

    def move(self, max_height):
        if self.dir == "up":
            self.pos.y -= self.speed
            if self.pos.y < 0:
                self.pos.y = 0
        elif self.dir == "down":
            self.pos.y += self.speed
            if self.pos.y + self.height > max_height:
                self.pos.y = max_height - self.height



class Pong:
    def __init__(self, player_l, player_r, points_to_win):
        self.points_to_win = points_to_win

        self.canvas_width = 1000
        self.canvas_height = 600
        self.player_width = 10
        self.player_height = 60

        self.ball = Ball(self.canvas_width/2, self.canvas_height/2, 5, 5, 10)
        self.player_l: Player = Player(id = player_l,
                                        pos_x = self.player_width + 10,
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
            'player_l_y': self.player_l.pos.y,
            'player_r_y': self.player_r.pos.y,
            'ball_x': self.ball.pos.x,
            'ball_y': self.ball.pos.y,
            'score_l': self.player_l.score,
            'score_r': self.player_r.score
        }


    def check_wall_collision(self, ball: Ball, canvas_width, canvas_height):
        # reflect ball if it hits the top or bottom of canvas
        if ball.pos.y <= 0 or ball.pos.y + ball.size >= canvas_height:
            ball.vel.y *= -1
        

    def check_player_collision(self, ball: Ball, player_l: Player, player_r: Player):
        if ball.pos.x <= player_l.pos.x:
            if ball.pos.y + ball.size > player_l.pos.y and ball.pos.y < player_l.pos.y + player_l.height:
                ball.vel.x *= -1 
        if ball.pos.x + ball.size >= player_r.pos.x:
            if ball.pos.y + ball.size > player_r.pos.y and ball.pos.y < player_r.pos.y + player_r.height:
                ball.vel.x *= -1


    def check_if_scored(self, ball: Ball, canvas_width):
        if ball.pos.x < 0:
            self.player_r.score += 1
            ball.reset()
        elif ball.pos.x > canvas_width:
            self.player_l.score += 1
            ball.reset()


    def change_player_direction(self, player_id, direction):
        if player_id == self.player_l.id:
            self.player_l.dir = direction
        elif player_id == self.player_r.id:
            self.player_r.dir = direction


    def update_game_state(self):
        self.ball.move()
        self.player_l.move(self.canvas_height)
        self.player_r.move(self.canvas_height)

        # check collision with players
        self.check_player_collision(self.ball, self.player_l, self.player_r)
        # check collision with walls or if players scored
        self.check_wall_collision(self.ball, self.canvas_width, self.canvas_height)
        # check if players scored
        self.check_if_scored(self.ball, self.canvas_width)







""" class Pong:
    def __init__(self, player_l, player_r):
        self.player_l = player_l
        self.player_r = player_r
        self.canvas_width = 1000
        self.canvas_height = 600
        self.paddle_size = 60
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
    
 """