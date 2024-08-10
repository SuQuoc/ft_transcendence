class Match:

    def __init__(self, player1=None, player2=None, task=None, name=None) -> None:
        self.player1 = player1
        self.player2 = player2
        self.task = task
        self.name = name
        self.len = 0

    def addPlayer(self, player):
        if self.len == 2:
            return False
        if self.player1 is None:
            self.player1 = player
            self.len += 1
            return True
        if self.player2 is None:
            self.player2 = player
            self.len += 1
            return True
        return False

    def removePlayer(self, player):
        if self.player1 == player:
            self.player1 = None
            self.len -= 1
            return True
        if self.player2 == player:
            self.player2 = None
            self.len -= 1
            return True
        return False
