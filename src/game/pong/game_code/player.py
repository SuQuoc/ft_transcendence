from .storageClasses import slotXy

class pong_player:

    def __init__(self, player_id, x, map_size: slotXy) -> None:
        self.id = player_id
        self.x = x
        self.y = 0
        self.width = 20
        self.height = 100
        self.up = False
        self.down = False
        self.task = None
        self.map_size = map_size

    def move(self, MOVE_SPEED):
        new_y = self.y
        new_x = self.x

        if self.up is True:
            new_y -= MOVE_SPEED
        elif self.down is True:
            new_y += MOVE_SPEED

        if self.onMap(new_y) == True:
            self.y = new_y
        self.x = new_x

    def onMap(self, y):          
        if y < 0:
            return False
        if y > self.map_size.y:
            return False
        return True
