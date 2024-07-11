import math

class gameBall:
    def __init__(self, x=0, y=0) -> None:
        self.x = x
        self.y = y
        self.turnDirection = -1 #// -1 if left +1 if right
        self.walkDirection = -1 #// -1 if back +1 if front
        self.rotationAngle = math.pi / 2
        self.moveSpeed = 0.1

    def move(self):
        #ball["rotationAngle"] += ball["turnDirection"] * ball["rotationSpeed"]

        moveStep = self.walkDirection * self.moveSpeed
        newPlayerX = self.x + moveStep * math.cos(self.rotationAngle)
        newPlayerY = self.y + moveStep * math.sin(self.rotationAngle)

        ##### do collisoins here
        self.x = newPlayerX
        self.y = newPlayerY
