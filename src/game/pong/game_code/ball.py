import asyncio
import math

from .paddlePhysic import PaddlePhysic
from .pongPlayer import PongPlayer
from .storageClasses import SlotXy


class GameBall:

    def __init__(self, map_size: SlotXy, x=295, y=300, width=10, height=10) -> None:
        self.x = x  # use game height / 2
        self.y = y  # use game with / 2
        self.width = width
        self.height = height
        self.map_size = map_size
        self.rotationAngle = self.degreeToRadiant(0)
        self.moveSpeed = 5
        self.match_points = {"left": 0, "right": 0}

    def move(self):
        # player: pong_player
        # self.player = player

        self.x = self.x + self.moveSpeed * math.cos(self.rotationAngle)
        self.y = self.y - self.moveSpeed * math.sin(self.rotationAngle)
        # self.x += 1
        # self.y += 1
        # self.padelHitPhysic()
        # self.hitWall()

    def paddlesHit(self, player: PongPlayer) -> str | None:
        paddle_physic = PaddlePhysic(self.newBallY, self.newBallX, player)
        if player.x == 0:
            self.rotationAngle = paddle_physic.left(self.rotationAngle)
        else:
            self.rotationAngle = paddle_physic.right(self.rotationAngle)

    def hitWall(self):
        # Checks if ball hits the outside wall and inverts his direction

        self.newBallX = self.x + self.moveSpeed * math.cos(self.rotationAngle)
        self.newBallY = self.y - self.moveSpeed * math.sin(self.rotationAngle)

        if self.newBallY > (self.map_size.y - self.height):

            new_angele = self.overflowRadius(math.pi * 2 - self.rotationAngle)
            self.rotationAngle = new_angele

            self.y = self.map_size.y - self.height
            self.x = self.newBallX

        elif self.newBallY < 0:

            new_angele = self.overflowRadius(math.pi * 2 - self.rotationAngle)
            self.rotationAngle = new_angele

            self.y = 0
            self.x = self.newBallX

        elif self.newBallX > (self.map_size.x - self.width):

            self.x = self.map_size.x / 2
            self.y = self.map_size.y / 2
            self.rotationAngle = self.degreeToRadiant(0)
            self.match_points["left"] += 1

        elif self.newBallX < 0:

            self.x = self.map_size.x / 2
            self.y = self.map_size.y / 2
            self.rotationAngle = self.degreeToRadiant(0)
            self.match_points["right"] += 1

        else:
            self.x = self.newBallX
            self.y = self.newBallY

    def degreeToRadiant(self, degree):
        return degree * (math.pi / 180)

    def radiantToDegree(self, radiant):
        return radiant * 180 / math.pi

    # If radiant is bigger/smaller than pi
    def overflowRadius(self, radiant):
        circle = math.pi * 2
        if radiant > circle:
            return radiant - circle
        if radiant < 0:
            return circle + radiant
        return radiant
