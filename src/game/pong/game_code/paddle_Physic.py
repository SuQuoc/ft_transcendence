from .player import pong_player
import math


""" 
    Class to do the hit paddle physic
    - set maximum angle to in or decrease the bounce angle
"""


class PaddlePhysic:


    def __init__(self, newBallY, newBallX, player: pong_player) -> None:
        self.maximum_angle = self.degreeToRadiant(75)
        self.newBallY = newBallY
        self.newBallX = newBallX
        self.player = player


    # LEFT PADDLE HIT LOGIC
    def left(self, rotationAngle):
        """
        When the ball hits the right paddle
        - RETURNS the rotationAngle that it already had if no paddle hit
        - player x y gives us just the the left upper point of the paddle need to calc the Hitbox 
        """
        hit_box_x = self.player.x + self.player.width
        hit_box_y = self.player.y + self.player.height
        
        # Looks for Ball x or y not hit the paddle 
        if self.newBallX > hit_box_x:
            return rotationAngle
        if self.newBallY < self.player.y or self.newBallY > hit_box_y:
            return rotationAngle
        return self.calcBounceAngle()


    # RIGHT PADDLE HIT LOGIC
    def right(self, rotationAngle):
        hit_box_x = self.player.x - self.player.width
        hit_box_y = self.player.y + self.player.height
        if self.newBallX < hit_box_x:
            return rotationAngle
        if self.newBallY < self.player.y or self.newBallY > hit_box_y:
            return rotationAngle

        # Here we invert the angle
        return (math.pi - self.calcBounceAngle())


    # Bounce angle is just the angle it bounces back from the paddle
    def calcBounceAngle(self):
        half_player_height = self.player.height / 2

        # Calc where the ball hits the paddle
        padel_hit_point = self.player.y + half_player_height - self.newBallY

        # Now calc the hit angle
        hit_angle = padel_hit_point / half_player_height

        # Finally calc the rotations angle
        return (self.maximum_angle * hit_angle)


    def degreeToRadiant(self, degree):
        return degree * (math.pi / 180)
