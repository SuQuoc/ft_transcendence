import json

# Potential Room class for tournaments
class TournamentRoom:
    AVAILABLE = "available"
    FULL = "full"

    creation_keys = [
        "name",
        "creator_name",
        "points_to_win",
        "max_player_num",
    ]

    converting_keys = [
        "players",
        "cur_player_num",
        "status"
    ]

    @staticmethod
    def from_dict(data: dict):
    
        for key in TournamentRoom.converting_keys:
            if key not in data:
                raise ValueError(f"Missing required key for converting from dict: {key}")
    
        return TournamentRoom(**data)
    
    def to_dict(self):
        # json.dumps(
        return {
            "name": self.name,
            "creator_name": self.creator_name,
            "players": self.players,
            "points_to_win": self.points_to_win,
            "max_player_num": self.max_player_num,
            "cur_player_num": self.cur_player_num,
            "status": self.status
        }


    def __init__(self, **kwargs):

        for key in TournamentRoom.creation_keys:
            if key not in kwargs:
                raise ValueError(f"Missing required key: {key}")
        
        # creation keys
        self.name = kwargs.get("name")
        self.creator_name = kwargs.get("creator_name")
        self.points_to_win = int(kwargs.get("points_to_win"))
        self.max_player_num = int(kwargs.get("max_player_num"))

        # + converting keys
        self.cur_player_num = int(kwargs.get("cur_player_num", 1))
        self.players = kwargs.get("players", [self.creator_name])
        self.status = kwargs.get("status", TournamentRoom.AVAILABLE)

        if self.points_to_win <= 0:
            raise ValueError("points_to_win must be a positive integer")
        if self.max_player_num <= 0:
            raise ValueError("max_player_num must be a positive integer")

    def is_full(self):
        return self.cur_player_num == self.max_player_num
    
    def is_empty(self):
        return self.cur_player_num == 0
    
    def add_player(self, player_name):
        if self.is_full():
            raise ValueError(f"Lobby room '{self.name}' is max - SHOULD NEVER HAPPEN.")
            return False
        self.players.append(player_name)
        self.cur_player_num += 1
        if self.is_full():
            self.status = TournamentRoom.FULL
        return True
    
    def remove_player(self, player_name):
        if player_name not in self.players:
            return False
        self.players.remove(player_name)
        self.cur_player_num -= 1
        return True