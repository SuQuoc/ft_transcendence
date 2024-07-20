
import math
from .player import pong_player


class gameBall:

    def __init__(self, x=300, y=300) -> None:
        self.x = x # use game height / 2
        self.y = y # use game with / 2
        self.turnDirection = 1 #// -1 if left +1 if right
        self.walkDirection = 1 #// -1 if back +1 if front
        self.rotationAngle = self.degreeToRadiant(0)
        self.moveSpeed = 20

    def move(self, player: pong_player):
        self.player = player

        self.newBallX = self.x + self.moveSpeed * math.cos(self.rotationAngle)
        self.newBallY = self.y - self.moveSpeed * math.sin(self.rotationAngle)

        self.padelHitPhysic()
        self.hitWall()

    def padelHitPhysic(self):
        self.hit_box_x = self.player.x + self.player.width
        self.hit_box_y = self.player.y + self.player.height
        if self.hitPadel() is False:
            return
        half_player_height = self.player.height / 2
        padel_hit_point = self.player.y + half_player_height - self.newBallY
        maximum_angle = self.degreeToRadiant(75)
        hit_angle = padel_hit_point / half_player_height
        bounce_angle = maximum_angle * hit_angle
        self.rotationAngle = bounce_angle
        print(self.radiantToDegree(bounce_angle))
        

    def hitPadel(self):
        if self.newBallX > self.hit_box_x:
            return False
        if self.newBallY > self.player.y and self.newBallY < self.hit_box_y:
            return True
        return False

    def hitWall(self):
        #Checks if ball hits the outside wall and inverts his direction
        if self.newBallY > (600 - 20):
            #self.turnDirection *= -1
            self.y = 580
            self.x = self.newBallX
            
            new_angele = self.overflowRadius(math.pi * 2 - self.rotationAngle)
            self.rotationAngle = new_angele

            
        elif self.newBallY < 0:
            #self.turnDirection *= -1
            new_angele = self.overflowRadius(math.pi * 2 - self.rotationAngle)
            self.rotationAngle = new_angele

            self.y = 0
            self.x = self.newBallX

        elif self.newBallX > (600 - 20):
            #self.walkDirection *= -1
            new_angele = self.overflowRadius(math.pi - self.rotationAngle)
            self.rotationAngle = new_angele
            
            self.x = 580
            self.Y = self.newBallY

        elif self.newBallX < 0:
            #self.walkDirection *= -1
            """ new_angele = self.overflowRadius(math.pi - self.rotationAngle)
            self.rotationAngle = new_angele
            
            self.x = 0
            self.Y = self.newBallY """

            self.x = 300
            self.y = 300
            self.rotationAngle = 0

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
