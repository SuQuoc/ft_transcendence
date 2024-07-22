from .player import pong_player
import math
#from .ball import gameBall

class hitPadel:

    def __init__(self, newBallY, newBallX, player: pong_player) -> None:
        self.maximum_angle = self.degreeToRadiant(75)
        self.newBallY = newBallY
        self.newBallX = newBallX
        self.player = player

    def hitPadel(self, hit_box_x, hit_box_y) -> bool:
        if self.newBallX > hit_box_x:
            return False
        if self.newBallY >= self.player.y and self.newBallY < hit_box_y:
            return True
        return False

    def left(self, rotationAngle):
        hit_box_x = self.player.x + self.player.width
        hit_box_y = self.player.y + self.player.height
        if self.newBallX > hit_box_x:
            return rotationAngle

        if self.newBallY < self.player.y or self.newBallY > hit_box_y:
            return rotationAngle
        half_player_height = self.player.height / 2
        padel_hit_point = self.player.y + half_player_height - self.newBallY
        hit_angle = padel_hit_point / half_player_height
        bounce_angle = self.maximum_angle * hit_angle
        return bounce_angle

    def right(self, rotationAngle):
        hit_box_x = self.player.x - self.player.width
        hit_box_y = self.player.y + self.player.height
        if self.newBallX < hit_box_x:
            return rotationAngle

        if self.newBallY < self.player.y or self.newBallY > hit_box_y:
            return rotationAngle
        half_player_height = self.player.height / 2
        padel_hit_point = self.player.y + half_player_height - self.newBallY
        hit_angle = padel_hit_point / half_player_height
        bounce_angle = self.maximum_angle * hit_angle
        bounce_angle = math.pi - bounce_angle
        return bounce_angle

    def degreeToRadiant(self, degree):
        return degree * (math.pi / 180)
