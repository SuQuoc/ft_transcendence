import random

class Pong:
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
    
