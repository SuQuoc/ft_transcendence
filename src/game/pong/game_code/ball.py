
from .storageClasses import slotXy
from .player import pong_player
from .paddle_Physic import PaddlePhysic
import math

class gameBall:

    def __init__(self, map_size: slotXy, x=295, y=300, width=10, height=10) -> None:
        self.x = x # use game height / 2
        self.y = y # use game with / 2
        self.width = width
        self.height = height
        self.map_size = map_size
        self.rotationAngle = self.degreeToRadiant(0)
        self.moveSpeed = 10

        self.walkDirection = 1 #// -1 if back +1 if front
        self.turnDirection = 1 #// -1 if left +1 if right
    
    def move(self):
        # player: pong_player
        # self.player = player

        self.x = self.x + self.moveSpeed * math.cos(self.rotationAngle)
        self.y = self.y - self.moveSpeed * math.sin(self.rotationAngle)
        #self.x += 1
        #self.y += 1
        #self.padelHitPhysic()
        #self.hitWall()

    def paddlesHit(self, player: pong_player):
        paddle_physic = PaddlePhysic(self.newBallY, self.newBallX, player)
        if player.x == 0:
            self.rotationAngle = paddle_physic.left(self.rotationAngle)
        else:
            self.rotationAngle = paddle_physic.right(self.rotationAngle)

    def hitWall(self):
        #Checks if ball hits the outside wall and inverts his direction

        self.newBallX = self.x + self.moveSpeed * math.cos(self.rotationAngle)
        self.newBallY = self.y - self.moveSpeed * math.sin(self.rotationAngle)

        if self.newBallY > (self.map_size.y - self.height):
            #self.turnDirection *= -1
            
            new_angele = self.overflowRadius(math.pi * 2 - self.rotationAngle)
            self.rotationAngle = new_angele

            self.y = self.map_size.y - self.height
            self.x = self.newBallX
            
        elif self.newBallY < 0:
            #self.turnDirection *= -1
            new_angele = self.overflowRadius(math.pi * 2 - self.rotationAngle)
            self.rotationAngle = new_angele

            self.y = 0
            self.x = self.newBallX

        elif self.newBallX > (self.map_size.x - self.width):
            #self.walkDirection *= -1
            """ new_angele = self.overflowRadius(math.pi - self.rotationAngle)
            self.rotationAngle = new_angele
            
            self.x = self.map_size.x - self.width
            self.Y = self.newBallY """

            self.x = self.map_size.x / 2
            self.y = self.map_size.y / 2
            self.rotationAngle = self.degreeToRadiant(0)

            print("OUT RIGHT")

        elif self.newBallX < 0:
            #self.walkDirection *= -1
            """ new_angele = self.overflowRadius(math.pi - self.rotationAngle)
            self.rotationAngle = new_angele
            
            self.x = 0
            self.Y = self.newBallY """

            self.x = self.map_size.x / 2
            self.y = self.map_size.y / 2
            self.rotationAngle = self.degreeToRadiant(0)

            print("OUT")
        
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
