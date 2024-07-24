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
        self.moveSpeed = 1
        self.match_points = {"left": 0, "right": 0}

    def move(self):
        self.x = self.x + self.moveSpeed * math.cos(self.rotationAngle)
        self.y = self.y - self.moveSpeed * math.sin(self.rotationAngle)

    def paddlesHit(self, player: PongPlayer):
        paddle_physic = PaddlePhysic(self.newBallY, self.newBallX, player)
        if player.x == 0:
            self.rotationAngle = paddle_physic.left(self.rotationAngle)
        else:
            self.rotationAngle = paddle_physic.right(self.rotationAngle)

    def hitWall(self):
        # Checks if ball hits the outside wall and inverts his direction
        # First write it into a temp and check if we out or hit a wall
        self.newBallX = self.x + self.moveSpeed * math.cos(self.rotationAngle)
        self.newBallY = self.y - self.moveSpeed * math.sin(self.rotationAngle)

        if self.newBallY > (self.map_size.y - self.height):
            # Ball hit bottom
            self.invertRotationAngle()
            self.y = self.map_size.y - self.height
            self.x = self.newBallX

        elif self.newBallY < 0:
            # Ball hit top
            self.invertRotationAngle()
            self.y = 0
            self.x = self.newBallX

        elif self.newBallX > (self.map_size.x - self.width):
            # Ball out right
            self.reset_ball()
            self.count_points("left")

        elif self.newBallX < 0:
            # Ball out left
            self.reset_ball()
            self.count_points("right")

        # if we hit or not out nothing we write it into ball pos x/y
        else:
            self.x = self.newBallX
            self.y = self.newBallY

    def invertRotationAngle(self):
        new_angel = self.overflowRadius(math.pi * 2 - self.rotationAngle)
        self.rotationAngle = new_angel

    def count_points(self, side):
        if self.match_points[side] < 10000:
            self.match_points[side] += 1

    def reset_ball(self):
        self.x = self.map_size.x / 2
        self.y = self.map_size.y / 2
        self.rotationAngle = self.degreeToRadiant(0)

    # If radiant is bigger/smaller than pi
    def overflowRadius(self, radiant):
        circle = math.pi * 2
        if radiant > circle:
            return radiant - circle
        if radiant < 0:
            return circle + radiant
        return radiant

    def degreeToRadiant(self, degree):
        return degree * (math.pi / 180)

    def radiantToDegree(self, radiant):
        return radiant * 180 / math.pi
