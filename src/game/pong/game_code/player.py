
class pong_player:

    def __init__(self, player_id, x) -> None:
        self.id = player_id
        self.x = x
        self.y = 0
        self.width = 20
        self.height = 100
        self.up = False
        self.down = False
        self.task = None

    def move(self, MOVE_SPEED, map_y, map_x):
        new_y = self.y
        new_x = self.x
        self.map_y = map_y
        self.map_x = map_x

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
        if y > self.map_y:
            return False
        return True