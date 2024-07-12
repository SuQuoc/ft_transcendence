import math

class gameBall:
    def __init__(self, x=0, y=0) -> None:
        self.x = x
        self.y = y
        self.turnDirection = 1 #// -1 if left +1 if right
        self.walkDirection = 1 #// -1 if back +1 if front
        self.rotationAngle = math.pi / 3
        self.moveSpeed = 10

    def move(self):

        #self.rotationAngle *= self.turnDirection

        moveStepX = self.walkDirection * self.moveSpeed
        moveStepY = self.turnDirection * self.moveSpeed
        newPlayerX = self.x + moveStepX * math.cos(self.rotationAngle)
        newPlayerY = self.y + moveStepY * math.sin(self.rotationAngle)

        ##### do collisoins here

        if newPlayerY > 600:
            self.turnDirection *= -1
        elif newPlayerY < 0:
            self.turnDirection *= -1
        elif newPlayerX > 600:
            self.walkDirection *= -1
        elif newPlayerX < 0:
            self.walkDirection *= -1
        else:
            self.x = newPlayerX
            self.y = newPlayerY


import math

class AgameBall:
    def __init__(self, x=0, y=0) -> None:
        self.x = x
        self.y = y
        self.turnDirection = 1 #// -1 if left +1 if right
        self.walkDirection = 1 #// -1 if back +1 if front
        self.rotationAngle = 0
        self.moveSpeed = 0.1

    def Amove(self):
        #ball["rotationAngle"] += ball["turnDirection"] * ball["rotationSpeed"]
        self.rotationAngle += self.turnDirection * self.rotationSpeed

        moveStep = self.walkDirection * self.moveSpeed
        newBallX = self.x + moveStep * math.cos(self.rotationAngle)
        newBallY = self.y + moveStep * math.sin(self.rotationAngle)

        ##### do collisoins here
        if newBallX > 600:
            self.turnDirection *= -1
            self.walkDirection *= -1
            self.turn_dir(math.pi)

        self.x = newBallX
        self.y = newBallY

    def Aturn_dir(self, rotation):
        r_angle = self.rotationAngle + rotation
        while r_angle > math.pi:
            r_angle -= math.pi
        self.rotationAngle = r_angle

    
